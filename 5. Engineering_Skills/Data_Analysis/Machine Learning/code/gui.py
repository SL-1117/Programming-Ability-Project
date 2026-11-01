"""Tkinter GUI: pick a ticker, run the three methods, see metrics / confusion matrices / K-line.

Run:  python gui.py
"""
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import pandas as pd

from data import DEFAULT_TICKERS, load_prices
from main import summary_row
from models import format_summary, run_experiment, sweep_thresholds
from plots import draw_candles, draw_results, draw_sweep


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("K-line pattern stock prediction")
        self.geometry("1180x760")
        self.q = queue.Queue()

        side = ttk.Frame(self, padding=10)
        side.pack(side="left", fill="y")

        def row(label, widget):
            ttk.Label(side, text=label).pack(anchor="w", pady=(8, 0))
            widget.pack(fill="x")
            return widget

        self.ticker = row("Ticker (Yahoo Finance)", ttk.Combobox(side, values=DEFAULT_TICKERS, width=14))
        self.ticker.set("2330.TW")
        self.small = row("Small threshold % (Flat if |r| <=)", ttk.Spinbox(side, from_=0.0, to=5.0, increment=0.1, width=8))
        self.small.set("0.5")
        self.big = row("Big threshold % (Big if |r| >)", ttk.Spinbox(side, from_=0.5, to=10.0, increment=0.5, width=8))
        self.big.set("3.0")
        self.mode = row("Threshold mode", ttk.Combobox(side, values=["fixed", "quantile"], width=14, state="readonly"))
        self.mode.set("fixed")
        self.k = row("k (similarity neighbours)", ttk.Spinbox(side, from_=1, to=101, width=8))
        self.k.set("15")
        self.train_end = row("Train until", ttk.Entry(side))
        self.train_end.insert(0, "2025-12-31")
        self.test_start = row("Test from", ttk.Entry(side))
        self.test_start.insert(0, "2026-01-01")

        self.extra = tk.BooleanVar()
        self.refresh = tk.BooleanVar()
        self.demo = tk.BooleanVar()
        self.sweep = tk.BooleanVar()
        for text, var in [("Add extra indicators (bonus)", self.extra),
                          ("Also run Flat-band sweep (slower)", self.sweep),
                          ("Re-download data", self.refresh),
                          ("Demo data (offline test)", self.demo)]:
            ttk.Checkbutton(side, text=text, variable=var).pack(anchor="w", pady=(8, 0))

        self.btn = ttk.Button(side, text="Run", command=self.run)
        self.btn.pack(fill="x", pady=(16, 4))
        self.btn_all = ttk.Button(side, text="Run all 11 tickers", command=self.run_all)
        self.btn_all.pack(fill="x", pady=(0, 4))
        self.all_res = {}  # ticker -> (df, res), filled by "Run all"
        self.status = ttk.Label(side, text="Ready", wraplength=170, foreground="gray")
        self.status.pack(anchor="w")

        tabs = ttk.Notebook(self)
        tabs.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        self.fig_res, self.fig_k, self.fig_sw = Figure(figsize=(8, 6)), Figure(figsize=(8, 6)), Figure(figsize=(8, 6))
        self.cv_res = self._tab(tabs, "Results", self.fig_res)
        self.cv_k = self._tab(tabs, "K-line", self.fig_k)
        self.cv_sw = self._tab(tabs, "Flat-band sweep", self.fig_sw)
        all_frame = ttk.Frame(tabs)
        tabs.add(all_frame, text="All tickers")
        self.cols = [("ticker", "Ticker", 80), ("baseline_acc", "Base acc", 70), ("baseline_bal", "Base bal", 70),
                     ("sim_acc", "kNN acc", 70), ("sim_bal", "kNN bal", 70),
                     ("clf_acc", "RF acc", 70), ("clf_bal", "RF bal", 70), ("clf_f1", "RF F1", 70),
                     ("reg_rmse", "Reg RMSE", 75), ("const_rmse", "Const RMSE", 80), ("reg_r2", "Reg R2", 70),
                     ("beats", "RF beats base?", 100)]
        self.tree = ttk.Treeview(all_frame, columns=[c[0] for c in self.cols], show="headings", height=14)
        for key, title, w in self.cols:
            self.tree.heading(key, text=title)
            self.tree.column(key, width=w, anchor="center")
        self.tree.pack(fill="both", expand=True)
        ttk.Label(all_frame, foreground="gray", wraplength=700,
                  text="bal = balanced accuracy. 'beats' = RF balanced accuracy above the always-majority baseline. "
                       "Double-click a row to show that ticker in the other tabs. "
                       "The table is also saved to results/summary.csv.").pack(anchor="w", pady=4)
        self.tree.bind("<Double-1>", self._pick_row)
        txt_frame = ttk.Frame(tabs)
        tabs.add(txt_frame, text="Summary")
        self.text = tk.Text(txt_frame, font=("Courier New", 10), wrap="none")
        self.text.pack(fill="both", expand=True)

        self.after(100, self._poll)

    def _tab(self, tabs, name, fig):
        frame = ttk.Frame(tabs)
        tabs.add(frame, text=name)
        cv = FigureCanvasTkAgg(fig, master=frame)
        cv.get_tk_widget().pack(fill="both", expand=True)
        return cv

    def _args(self):
        return dict(ticker=self.ticker.get().strip(), small=float(self.small.get()), big=float(self.big.get()),
                    mode=self.mode.get(), sweep=self.sweep.get(), k=int(self.k.get()),
                    train_end=self.train_end.get().strip(), test_start=self.test_start.get().strip(),
                    extra=self.extra.get(), refresh=self.refresh.get(), demo=self.demo.get())

    def _busy(self, text):
        self.btn.state(["disabled"])
        self.btn_all.state(["disabled"])
        self.status.config(text=text)

    def run(self):
        try:
            args = self._args()
        except ValueError:
            messagebox.showerror("Input error", "Thresholds and k must be numbers.")
            return
        self._busy("Downloading data and training...")
        threading.Thread(target=self._work, args=(args,), daemon=True).start()

    def run_all(self):
        try:
            args = self._args()
        except ValueError:
            messagebox.showerror("Input error", "Thresholds and k must be numbers.")
            return
        self._busy("Running all tickers...")
        threading.Thread(target=self._work_all, args=(args,), daemon=True).start()

    def _fit(self, ticker, a):
        df = load_prices(ticker, demo=a["demo"], refresh=a["refresh"])
        res = run_experiment(df, ticker, extra=a["extra"], small=a["small"], big=a["big"],
                             mode=a["mode"], k=a["k"],
                             train_end=a["train_end"], test_start=a["test_start"])
        return df, res

    def _work(self, a):  # runs in a background thread; never touch widgets here
        try:
            df, res = self._fit(a["ticker"], a)
            sw = None
            if a["sweep"]:
                sw = sweep_thresholds(df, extra=a["extra"], k=a["k"],
                                      train_end=a["train_end"], test_start=a["test_start"])
            self.q.put(("ok", df, res, sw))
        except Exception as e:
            self.q.put(("err", str(e)))

    def _work_all(self, a):
        results, failed = {}, []
        for i, t in enumerate(DEFAULT_TICKERS, 1):
            self.q.put(("prog", f"{i}/{len(DEFAULT_TICKERS)}  {t} ..."))
            try:
                results[t] = self._fit(t, a)
            except Exception as e:  # keep going if one ticker fails
                failed.append(f"{t}: {e}")
        self.q.put(("all", results, failed))

    def _show(self, df, res, sw=None):
        draw_results(self.fig_res, res)
        self.cv_res.draw()
        draw_candles(self.fig_k, df, 60, f"{res['ticker']} last 60 trading days")
        self.cv_k.draw()
        if sw is not None:
            draw_sweep(self.fig_sw, sw, f"{res['ticker']}: Flat-band sweep")
            self.cv_sw.draw()
        self.text.delete("1.0", "end")
        self.text.insert("1.0", format_summary(res))

    def _fill_table(self, results):
        self.tree.delete(*self.tree.get_children())
        rows = []
        for t, (df, res) in results.items():
            r = summary_row(res)
            r["beats"] = "yes" if r["clf_bal"] > r["baseline_bal"] else "no"
            rows.append(r)
            self.tree.insert("", "end", iid=t, values=[
                r[k] if isinstance(r[k], str) else f"{r[k]:.3f}" for k, _, _ in self.cols])
        out = Path(__file__).parent / "results"
        out.mkdir(exist_ok=True)
        pd.DataFrame(rows).round(4).to_csv(out / "summary.csv", index=False)

    def _pick_row(self, _event):
        sel = self.tree.selection()
        if sel and sel[0] in self.all_res:
            df, res = self.all_res[sel[0]]
            self._show(df, res)
            self.ticker.set(sel[0])

    def _poll(self):
        try:
            msg = self.q.get_nowait()
        except queue.Empty:
            self.after(100, self._poll)
            return
        if msg[0] == "prog":
            self.status.config(text=msg[1])
            self.after(100, self._poll)
            return
        self.btn.state(["!disabled"])
        self.btn_all.state(["!disabled"])
        if msg[0] == "err":
            self.status.config(text="Failed")
            messagebox.showerror("Error", msg[1])
        elif msg[0] == "all":
            _, results, failed = msg
            self.all_res = results
            if results:
                self._fill_table(results)
                first = next(iter(results))
                self._show(*results[first])
            self.status.config(text=f"Done: {len(results)} ok, {len(failed)} failed")
            if failed:
                messagebox.showwarning("Some tickers failed", "\n".join(failed))
        else:
            _, df, res, sw = msg
            self._show(df, res, sw)
            self.status.config(text="Done")
        self.after(100, self._poll)


if __name__ == "__main__":
    App().mainloop()

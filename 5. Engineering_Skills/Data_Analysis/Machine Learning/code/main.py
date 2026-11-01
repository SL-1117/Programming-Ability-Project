"""Run the experiment for many tickers and save a summary table + figures.

Examples
    python main.py                       # 10 stocks + TAIEX, real data from yfinance
    python main.py --tickers 2330.TW ^TWII --extra
    python main.py --demo                # offline smoke test with synthetic data
"""
import argparse
from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure

from data import DEFAULT_TICKERS, load_prices
from models import format_summary, run_experiment, sweep_thresholds
from plots import draw_candles, draw_results, draw_sweep


def summary_row(res):
    s, c, r, b = res["similarity"], res["classification"], res["regression"], res["baseline"]
    nd = res["next_day"] or {}
    return {
        "ticker": res["ticker"], "n_train": res["n_train"], "n_test": res["n_test"],
        "small_%": res["small"], "big_%": res["big"],
        "baseline_acc": b["accuracy"], "baseline_bal": b["balanced_acc"],
        "sim_acc": s["cls"]["accuracy"], "sim_bal": s["cls"]["balanced_acc"], "sim_f1": s["cls"]["f1_macro"],
        "sim_rmse": s["reg"]["rmse"], "sim_r2": s["reg"]["r2"],
        "clf_acc": c["cls"]["accuracy"], "clf_bal": c["cls"]["balanced_acc"], "clf_f1": c["cls"]["f1_macro"],
        "reg_rmse": r["reg"]["rmse"], "reg_r2": r["reg"]["r2"],
        "reg_cls_acc": r["cls"]["accuracy"], "reg_cls_bal": r["cls"]["balanced_acc"],
        "reg_cls_f1": r["cls"]["f1_macro"],
        "const_rmse": b["rmse"],
        "next_day_clf": nd.get("classification"), "next_day_reg_%": nd.get("regression_return"),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    p.add_argument("--extra", action="store_true", help="add RSI/MACD/MA/volatility features (bonus)")
    p.add_argument("--small", type=float, default=0.5, help="|next-day return| <= this %% is 'Flat'")
    p.add_argument("--big", type=float, default=3.0, help="|next-day return| > this %% is 'Big' up/down")
    p.add_argument("--mode", choices=["fixed", "quantile"], default="fixed",
                   help="fixed: use --small/--big; quantile: derive them from training returns (balanced classes)")
    p.add_argument("--sweep", action="store_true", help="also run the Flat-band sweep (accuracy vs balanced accuracy)")
    p.add_argument("--k", type=int, default=15, help="neighbours for similarity matching")
    p.add_argument("--train-start", default="2020-01-01")
    p.add_argument("--train-end", default="2025-12-31")
    p.add_argument("--test-start", default="2026-01-01")
    p.add_argument("--refresh", action="store_true", help="re-download data instead of using the cache")
    p.add_argument("--demo", action="store_true", help="synthetic data (offline test only)")
    p.add_argument("--out", default="results")
    a = p.parse_args()

    out = Path(a.out)
    out.mkdir(exist_ok=True)
    rows = []
    for t in a.tickers:
        try:
            df = load_prices(t, start=a.train_start, demo=a.demo, refresh=a.refresh)
            res = run_experiment(df, t, extra=a.extra, small=a.small, big=a.big, mode=a.mode, k=a.k,
                                 train_start=a.train_start, train_end=a.train_end,
                                 test_start=a.test_start)
        except Exception as e:  # keep going if one ticker fails
            print(f"!! {t}: {e}\n")
            continue
        print(format_summary(res), "\n" + "=" * 78 + "\n")
        rows.append(summary_row(res))
        safe = t.replace("^", "_")
        fig = Figure(figsize=(10, 7))
        draw_results(fig, res)
        fig.savefig(out / f"{safe}_results.png", dpi=130)
        fig = Figure(figsize=(10, 5))
        draw_candles(fig, df, 60, f"{t} last 60 trading days")
        fig.savefig(out / f"{safe}_kline.png", dpi=130)
        if a.sweep:
            sw = sweep_thresholds(df, extra=a.extra, k=a.k, train_start=a.train_start,
                                  train_end=a.train_end, test_start=a.test_start)
            sw.round(4).to_csv(out / f"{safe}_sweep.csv", index=False)
            fig = Figure(figsize=(8, 5))
            draw_sweep(fig, sw, f"{t}: Flat-band sweep")
            fig.savefig(out / f"{safe}_sweep.png", dpi=130)

    if rows:
        table = pd.DataFrame(rows).round(4)
        table.to_csv(out / "summary.csv", index=False)
        print(table.to_string(index=False))
        print(f"\nSaved summary.csv and figures to ./{out}/")


if __name__ == "__main__":
    main()

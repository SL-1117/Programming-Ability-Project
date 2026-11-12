"""
Stock Trend / Price Prediction - Midterm Assignment
Based on the assignment slides:
- 10 candlestick features
- Similarity matching, classification, and regression
- Chronological train/test split
- Classification: confusion matrix + F1 score
- Regression: RMSE + R2
- Include Taiwan market index (^TWII)

Important:
This is an educational analysis tool, not financial advice. Predictions are uncertain.
"""

from __future__ import annotations

import threading
import traceback
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score, f1_score, confusion_matrix, classification_report,
    mean_squared_error, r2_score
)

APP_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = APP_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Ten features based on pages 5 and 8 of the provided slides.
FEATURES = [
    "upper_shadow_pct",
    "lower_shadow_pct",
    "body_pct",
    "prev_upper_shadow_pct",
    "prev_lower_shadow_pct",
    "prev_body_pct",
    "open_style_pct",
    "close_style_pct",
    "volume_vs_5d_pct",
    "trend_5d_pct",
]

LABELS = {-1: "Down", 0: "Flat", 1: "Up"}
LABEL_ORDER = [-1, 0, 1]


@dataclass
class RunResult:
    ticker: str
    test_data: pd.DataFrame
    classification_metrics: dict
    regression_metrics: dict
    similarity_metrics: dict
    latest_prediction: dict
    index_ticker: str


def download_prices(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download daily OHLCV data. yfinance end date is exclusive."""
    data = yf.download(
        ticker, start=start, end=end, interval="1d",
        auto_adjust=False, progress=False, threads=False
    )
    if data is None or data.empty:
        raise ValueError(
            f"No data returned for {ticker}. Check the ticker, dates, or internet connection."
        )

    # yfinance may return MultiIndex columns depending on version/ticker.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing columns for {ticker}: {missing}")

    data = data[required].copy()
    data.index = pd.to_datetime(data.index)
    if getattr(data.index, "tz", None) is not None:
        data.index = data.index.tz_localize(None)
    data = data[~data.index.duplicated(keep="last")].sort_index()
    data = data.apply(pd.to_numeric, errors="coerce")
    data = data.dropna(subset=["Open", "High", "Low", "Close"])
    return data


def make_features(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Create the ten features described on slides 5 and 8.
    O=Open, H=High, L=Low, C=Close, V=Volume, CT-1=previous close.
    """
    df = prices.copy()
    O, H, L, C, V = df["Open"], df["High"], df["Low"], df["Close"], df["Volume"]
    prev_close = C.shift(1)

    # Use today's close as denominator, following the slide formulas.
    denom = C.replace(0, np.nan)
    upper = (H - np.maximum(O, C)) / denom * 100
    lower = (np.minimum(O, C) - L) / denom * 100
    body = (C - O) / denom * 100

    df["upper_shadow_pct"] = upper
    df["lower_shadow_pct"] = lower
    df["body_pct"] = body
    df["prev_upper_shadow_pct"] = upper.shift(1)
    df["prev_lower_shadow_pct"] = lower.shift(1)
    df["prev_body_pct"] = body.shift(1)

    # Opening/closing pattern relative to previous day's close.
    df["open_style_pct"] = (O - prev_close) / denom * 100
    df["close_style_pct"] = (C - prev_close) / denom * 100

    # Slide formula: (V - 5-day average volume) / V.
    avg_volume_5d = V.rolling(5).mean()
    volume_denom = V.replace(0, np.nan)
    df["volume_vs_5d_pct"] = (V - avg_volume_5d) / volume_denom * 100

    # Slide formula: (close two days ago - close seven days ago) / close seven days ago.
    df["trend_5d_pct"] = (C.shift(2) - C.shift(7)) / C.shift(7).replace(0, np.nan) * 100

    return df


def prepare_dataset(stock: pd.DataFrame, market: pd.DataFrame, flat_threshold_pct: float):
    """Join stock/index features and create next-trading-day target labels."""
    stock_features = make_features(stock)
    market_close = market[["Close"]].rename(columns={"Close": "market_close"})
    market_close["market_return_pct"] = market_close["market_close"].pct_change() * 100

    df = stock_features.join(market_close, how="left")
    # Add the market's recent trend as an extra feature (assignment bonus).
    df["market_trend_5d_pct"] = (
        df["market_close"].shift(2) - df["market_close"].shift(7)
    ) / df["market_close"].shift(7).replace(0, np.nan) * 100

    # Target is the next trading session's close-to-close return.
    df["next_return_pct"] = (df["Close"].shift(-1) / df["Close"] - 1) * 100
    df["target_class"] = np.select(
        [
            df["next_return_pct"] > flat_threshold_pct,
            df["next_return_pct"] < -flat_threshold_pct,
        ],
        [1, -1],
        default=0,
    )
    # The ten required features are the base; index fields are added as optional extra predictors.
    model_features = FEATURES + ["market_return_pct", "market_trend_5d_pct"]
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=FEATURES + ["next_return_pct", "target_class"])
    # Keep rows with missing index values out of models; TAIEX should normally overlap.
    df = df.dropna(subset=["market_return_pct", "market_trend_5d_pct"])
    return df, model_features


def chronological_split(df: pd.DataFrame, test_year: int):
    """Use all rows before test_year for training and test_year onward for testing."""
    train = df[df.index.year < test_year].copy()
    test = df[df.index.year >= test_year].copy()
    if train.empty or test.empty:
        raise ValueError(
            f"Cannot split data at test year {test_year}. "
            f"Available years: {df.index.min().year}-{df.index.max().year}. "
            "Choose a test year that leaves data on both sides."
        )
    if len(train) < 100 or len(test) < 10:
        raise ValueError(
            f"Not enough rows after splitting (train={len(train)}, test={len(test)}). "
            "Choose a longer date range or a different test year."
        )
    return train, test


def make_classifier():
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3,
            class_weight="balanced_subsample", random_state=42, n_jobs=-1
        )),
    ])


def make_regressor():
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", RandomForestRegressor(
            n_estimators=300, min_samples_leaf=3,
            random_state=42, n_jobs=-1
        )),
    ])


def similarity_predictions(X_train, y_train, X_test, k=25):
    """
    Similarity method: standardize using training data, find k nearest historical
    feature vectors, then use their majority class. All neighbours come from training data.
    """
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=min(k, len(X_train)), weights="distance")),
    ])
    model.fit(X_train, y_train)
    return model.predict(X_test)


def evaluate(stock_ticker: str, index_ticker: str, start: str, end: str,
             test_year: int, flat_threshold_pct: float) -> RunResult:
    stock = download_prices(stock_ticker, start, end)
    market = download_prices(index_ticker, start, end)
    df, model_features = prepare_dataset(stock, market, flat_threshold_pct)
    train, test = chronological_split(df, test_year)

    X_train = train[model_features]
    X_test = test[model_features]
    y_train = train["target_class"].astype(int)
    y_test = test["target_class"].astype(int)

    classifier = make_classifier()
    classifier.fit(X_train, y_train)
    pred_class = classifier.predict(X_test)

    regressor = make_regressor()
    regressor.fit(X_train, train["next_return_pct"])
    pred_return = regressor.predict(X_test)

    pred_similarity = similarity_predictions(X_train, y_train, X_test)

    test_result = test.copy()
    test_result["actual_class"] = y_test
    test_result["classification_prediction"] = pred_class
    test_result["similarity_prediction"] = pred_similarity
    test_result["predicted_return_pct"] = pred_return
    test_result["actual_label"] = test_result["actual_class"].map(LABELS)
    test_result["predicted_label"] = test_result["classification_prediction"].map(LABELS)
    test_result["similarity_label"] = test_result["similarity_prediction"].map(LABELS)

    labels_present = [v for v in LABEL_ORDER if v in set(y_test) | set(pred_class)]
    cm = confusion_matrix(y_test, pred_class, labels=labels_present)
    class_metrics = {
        "accuracy": accuracy_score(y_test, pred_class),
        "macro_f1": f1_score(y_test, pred_class, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_test, pred_class, average="weighted", zero_division=0),
        "confusion_matrix": cm,
        "labels_present": labels_present,
        "report": classification_report(
            y_test, pred_class, labels=labels_present,
            target_names=[LABELS[x] for x in labels_present],
            zero_division=0
        ),
        "similarity_accuracy": accuracy_score(y_test, pred_similarity),
        "similarity_macro_f1": f1_score(y_test, pred_similarity, average="macro", zero_division=0),
    }

    rmse = float(np.sqrt(mean_squared_error(test["next_return_pct"], pred_return)))
    try:
        r2 = float(r2_score(test["next_return_pct"], pred_return))
    except Exception:
        r2 = float("nan")
    reg_metrics = {"rmse": rmse, "r2": r2}

    # Fit on all available labelled rows for a separate next-session estimate.
    # The last row has features but no next_return target; it is excluded from training.
    full_features = df[model_features]
    last_valid = make_features(stock).join(
        market[["Close"]].rename(columns={"Close": "market_close"}), how="left"
    )
    last_valid["market_return_pct"] = last_valid["market_close"].pct_change() * 100
    last_valid["market_trend_5d_pct"] = (
        last_valid["market_close"].shift(2) - last_valid["market_close"].shift(7)
    ) / last_valid["market_close"].shift(7).replace(0, np.nan) * 100
    last_valid = last_valid.replace([np.inf, -np.inf], np.nan)
    latest_row = last_valid.dropna(subset=model_features).iloc[[-1]]

    final_classifier = make_classifier().fit(full_features, df["target_class"].astype(int))
    final_regressor = make_regressor().fit(full_features, df["next_return_pct"])
    latest_class = int(final_classifier.predict(latest_row[model_features])[0])
    latest_return = float(final_regressor.predict(latest_row[model_features])[0])

    # Similarity classifier trained on all labelled rows.
    final_similarity = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("knn", KNeighborsClassifier(n_neighbors=min(25, len(full_features)), weights="distance")),
    ]).fit(full_features, df["target_class"].astype(int))
    latest_similarity = int(final_similarity.predict(latest_row[model_features])[0])

    latest_prediction = {
        "as_of": str(latest_row.index[-1].date()),
        "classification": LABELS[latest_class],
        "similarity": LABELS[latest_similarity],
        "predicted_return_pct": latest_return,
        "estimated_next_close": float(latest_row["Close"].iloc[0] * (1 + latest_return / 100)),
        "last_close": float(latest_row["Close"].iloc[0]),
    }

    result = RunResult(
        ticker=stock_ticker, test_data=test_result,
        classification_metrics=class_metrics, regression_metrics=reg_metrics,
        similarity_metrics={
            "accuracy": class_metrics["similarity_accuracy"],
            "macro_f1": class_metrics["similarity_macro_f1"],
        },
        latest_prediction=latest_prediction, index_ticker=index_ticker
    )

    safe_ticker = stock_ticker.replace("^", "").replace(".", "_")
    test_result.to_csv(OUTPUT_DIR / f"{safe_ticker}_test_predictions.csv", encoding="utf-8-sig")
    return result


class StockPredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Trend / Price Prediction — Midterm Project")
        self.root.geometry("1120x820")
        self.root.minsize(900, 650)
        self.result = None
        self._build_ui()

    def _build_ui(self):
        outer = ttk.Frame(self.root, padding=12)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="Stock Trend / Price Prediction",
                  font=("Arial", 18, "bold")).pack(anchor="w")
        ttk.Label(
            outer,
            text="Ten candlestick features + similarity matching + classification + regression",
            foreground="#555"
        ).pack(anchor="w", pady=(2, 12))

        controls = ttk.LabelFrame(outer, text="Settings", padding=10)
        controls.pack(fill="x")

        self.ticker_var = tk.StringVar(value="2330.TW")
        self.index_var = tk.StringVar(value="^TWII")
        self.start_var = tk.StringVar(value="2018-01-01")
        self.end_var = tk.StringVar(value=date.today().isoformat())
        self.test_year_var = tk.StringVar(value="2026")
        self.threshold_var = tk.StringVar(value="0.5")

        fields = [
            ("Stock ticker", self.ticker_var),
            ("Market index", self.index_var),
            ("Start date", self.start_var),
            ("End date (exclusive)", self.end_var),
            ("Test year starts", self.test_year_var),
            ("Flat threshold (%)", self.threshold_var),
        ]
        for i, (label, var) in enumerate(fields):
            r, c = divmod(i, 3)
            cell = ttk.Frame(controls)
            cell.grid(row=r, column=c, sticky="ew", padx=5, pady=5)
            ttk.Label(cell, text=label).pack(anchor="w")
            ttk.Entry(cell, textvariable=var, width=22).pack(fill="x")
        for c in range(3):
            controls.columnconfigure(c, weight=1)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=10)
        self.run_button = ttk.Button(actions, text="Run prediction", command=self.start_run)
        self.run_button.pack(side="left")
        ttk.Button(actions, text="Export test results as CSV", command=self.export_csv).pack(side="left", padx=8)
        ttk.Button(actions, text="Save report text", command=self.save_report).pack(side="left")

        self.status_var = tk.StringVar(value="Ready. Internet access is required to download market data.")
        ttk.Label(outer, textvariable=self.status_var, foreground="#333").pack(anchor="w", pady=(0, 8))

        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill="both", expand=True)
        self.summary_tab = ttk.Frame(self.notebook, padding=10)
        self.chart_tab = ttk.Frame(self.notebook, padding=6)
        self.metrics_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.summary_tab, text="Summary")
        self.notebook.add(self.chart_tab, text="Prediction chart")
        self.notebook.add(self.metrics_tab, text="Evaluation metrics")
        self.summary_text = tk.Text(self.summary_tab, wrap="word", font=("Consolas", 10), height=20)
        self.summary_text.pack(fill="both", expand=True)
        self.metrics_text = tk.Text(self.metrics_tab, wrap="none", font=("Consolas", 10))
        self.metrics_text.pack(fill="both", expand=True)

    def start_run(self):
        try:
            start = self.start_var.get().strip()
            end = self.end_var.get().strip()
            test_year = int(self.test_year_var.get())
            threshold = float(self.threshold_var.get())
            if threshold < 0:
                raise ValueError("Flat threshold must be zero or positive.")
            if pd.Timestamp(start) >= pd.Timestamp(end):
                raise ValueError("Start date must be earlier than end date.")
        except Exception as exc:
            messagebox.showerror("Invalid settings", str(exc))
            return

        self.run_button.config(state="disabled")
        self.status_var.set("Downloading data and training models…")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", "Please wait. This may take a minute depending on the data source.\n")

        def worker():
            try:
                result = evaluate(
                    self.ticker_var.get().strip(),
                    self.index_var.get().strip(),
                    start, end, test_year, threshold
                )
                self.root.after(0, lambda: self.show_result(result))
            except Exception as exc:
                details = f"{exc}\n\n{traceback.format_exc()}"
                self.root.after(0, lambda: self.show_error(details))
        threading.Thread(target=worker, daemon=True).start()

    def show_error(self, details):
        self.run_button.config(state="normal")
        self.status_var.set("Run failed.")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", details)
        messagebox.showerror("Could not complete prediction", details.split("\n")[0])

    def show_result(self, result):
        self.result = result
        self.run_button.config(state="normal")
        self.status_var.set(f"Finished. Test rows: {len(result.test_data)}. CSV saved in output folder.")
        p = result.latest_prediction
        cm = result.classification_metrics
        rm = result.regression_metrics

        summary = [
            f"Stock: {result.ticker}",
            f"Market index: {result.index_ticker}",
            f"Latest available session: {p['as_of']}",
            "",
            "NEXT-SESSION ESTIMATE (not financial advice)",
            f"  Classification model: {p['classification']}",
            f"  Similarity model:      {p['similarity']}",
            f"  Predicted return:      {p['predicted_return_pct']:.3f}%",
            f"  Last close:            {p['last_close']:.2f}",
            f"  Estimated next close:  {p['estimated_next_close']:.2f}",
            "",
            "OUT-OF-SAMPLE TEST PERFORMANCE",
            f"  Classification accuracy: {cm['accuracy']:.4f}",
            f"  Classification macro F1: {cm['macro_f1']:.4f}",
            f"  Similarity accuracy:     {cm['similarity_accuracy']:.4f}",
            f"  Similarity macro F1:     {cm['similarity_macro_f1']:.4f}",
            f"  Regression RMSE (%):     {rm['rmse']:.4f}",
            f"  Regression R²:           {rm['r2']:.4f}",
            "",
            "Notes:",
            "- The test period begins in the selected test year; earlier rows are training data.",
            "- 'Flat' means the next-day return is within the chosen +/- threshold.",
            "- Model results do not guarantee future performance.",
        ]
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("end", "\n".join(summary))
        self._show_metrics()
        self._show_chart()

    def _show_metrics(self):
        if not self.result:
            return
        r = self.result
        cm = r.classification_metrics
        text = []
        text.append("CLASSIFICATION REPORT (Random Forest)")
        text.append(cm["report"])
        text.append("")
        text.append("CONFUSION MATRIX")
        text.append("Rows = actual class; columns = predicted class")
        names = [LABELS[x] for x in cm["labels_present"]]
        text.append("Actual\\Pred " + " | ".join(f"{x:>8}" for x in names))
        for label, row in zip(names, cm["confusion_matrix"]):
            text.append(f"{label:>11} " + " | ".join(f"{int(v):8d}" for v in row))
        text.append("")
        text.append("REGRESSION")
        text.append(f"RMSE: {r.regression_metrics['rmse']:.6f} percentage points")
        text.append(f"R²:   {r.regression_metrics['r2']:.6f}")
        text.append("")
        text.append("SIMILARITY MATCHING (k-nearest neighbours)")
        text.append(f"Accuracy: {r.similarity_metrics['accuracy']:.6f}")
        text.append(f"Macro F1: {r.similarity_metrics['macro_f1']:.6f}")
        self.metrics_text.delete("1.0", "end")
        self.metrics_text.insert("end", "\n".join(text))

    def _show_chart(self):
        for widget in self.chart_tab.winfo_children():
            widget.destroy()
        data = self.result.test_data.tail(250)
        fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
        ax.plot(data.index, data["next_return_pct"], label="Actual next-day return (%)", linewidth=1)
        ax.plot(data.index, data["predicted_return_pct"], label="Predicted return (%)", linewidth=1)
        ax.axhline(0, linewidth=0.8)
        ax.set_title(f"{self.result.ticker}: actual vs predicted next-day return")
        ax.set_ylabel("Return (%)")
        ax.set_xlabel("Test date")
        ax.legend()
        ax.grid(True, alpha=0.25)
        fig.autofmt_xdate()
        canvas = FigureCanvasTkAgg(fig, master=self.chart_tab)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def export_csv(self):
        if self.result is None:
            messagebox.showinfo("No results", "Run a prediction first.")
            return
        default_name = f"{self.result.ticker.replace('.', '_').replace('^', '')}_test_predictions.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile=default_name,
            filetypes=[("CSV files", "*.csv")]
        )
        if path:
            self.result.test_data.to_csv(path, encoding="utf-8-sig")
            messagebox.showinfo("Export complete", f"Saved to:\n{path}")

    def save_report(self):
        if self.result is None:
            messagebox.showinfo("No results", "Run a prediction first.")
            return
        p = self.result.latest_prediction
        cm = self.result.classification_metrics
        rm = self.result.regression_metrics
        content = f"""Stock Trend / Price Prediction — Result Summary

Stock ticker: {self.result.ticker}
Market index: {self.result.index_ticker}
Latest data date: {p['as_of']}

Latest estimates (educational only):
- Classification: {p['classification']}
- Similarity matching: {p['similarity']}
- Predicted next-day return: {p['predicted_return_pct']:.4f}%
- Last close: {p['last_close']:.4f}
- Estimated next close: {p['estimated_next_close']:.4f}

Out-of-sample evaluation:
- Classification accuracy: {cm['accuracy']:.4f}
- Classification macro F1: {cm['macro_f1']:.4f}
- Similarity accuracy: {cm['similarity_accuracy']:.4f}
- Similarity macro F1: {cm['similarity_macro_f1']:.4f}
- Regression RMSE: {rm['rmse']:.4f} percentage points
- Regression R²: {rm['r2']:.4f}

Classification report:
{cm['report']}

Limitations:
- Historical price patterns may not repeat.
- Results are sensitive to the selected period, features, and thresholds.
- This tool is for a course assignment, not investment advice.
"""
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="prediction_report.txt",
            filetypes=[("Text files", "*.txt")]
        )
        if path:
            Path(path).write_text(content, encoding="utf-8")
            messagebox.showinfo("Report saved", f"Saved to:\n{path}")


def main():
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    StockPredictionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

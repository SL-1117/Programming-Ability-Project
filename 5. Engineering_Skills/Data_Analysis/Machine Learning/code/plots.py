"""Matplotlib drawing helpers (work on a Figure, so they run in the GUI and from the CLI)."""
import numpy as np

from features import CLASS_LABELS, CLASS_NAMES

UP, DOWN = "#d62728", "#2ca02c"  # Taiwan convention: red = up, green = down


def _confusion(ax, cm, title):
    n = len(CLASS_LABELS)
    ax.imshow(cm, cmap="Blues")
    names = [CLASS_NAMES[c] for c in CLASS_LABELS]
    ax.set_xticks(range(n), names, fontsize=6, rotation=30)
    ax.set_yticks(range(n), names, fontsize=6)
    ax.set_xlabel("Predicted", fontsize=7)
    ax.set_ylabel("Actual", fontsize=7)
    ax.set_title(title, fontsize=8)
    top = cm.max() if cm.max() > 0 else 1
    for i in range(n):
        for j in range(n):
            ax.text(j, i, int(cm[i, j]), ha="center", va="center", fontsize=8,
                    color="white" if cm[i, j] > top / 2 else "black")


def _t(name, m):
    return f"{name}  acc {m['accuracy']:.2f}  bal {m['balanced_acc']:.2f}  F1 {m['f1_macro']:.2f}"


def draw_results(fig, res):
    """2x2 panel: three confusion matrices + actual vs predicted next-day return."""
    fig.clear()
    ax = fig.subplots(2, 2)
    s, c, r = res["similarity"], res["classification"], res["regression"]
    _confusion(ax[0, 0], s["cls"]["cm"], _t("Similarity kNN", s["cls"]))
    _confusion(ax[0, 1], c["cls"]["cm"], _t("Classification RF", c["cls"]))
    _confusion(ax[1, 0], r["cls"]["cm"], _t("Regression RF (class)", r["cls"]))

    a = ax[1, 1]
    a.plot(res["test_index"], res["y_test_ret"], color="gray", lw=1, label="actual")
    a.plot(res["test_index"], r["ret_pred"], color="tab:blue", lw=1.2, label="RF predicted")
    a.axhline(0, color="black", lw=0.5)
    a.set_title(f"Next-day return %  RMSE {r['reg']['rmse']:.2f}  R2 {r['reg']['r2']:.3f}", fontsize=9)
    a.legend(fontsize=7)
    a.tick_params(axis="x", labelrotation=30, labelsize=7)
    b = res["baseline"]
    fig.suptitle(f"{res['ticker']}  (test {res['test_range'][0]:%Y-%m-%d} ~ {res['test_range'][1]:%Y-%m-%d})"
                 f"   baseline acc {b['accuracy']:.2f} / bal {b['balanced_acc']:.2f}", fontsize=10)
    fig.tight_layout()


def draw_candles(fig, df, n=60, title=""):
    """Candlestick chart of the last n days with volume bars."""
    fig.clear()
    ax, axv = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    d = df.tail(n)
    x = np.arange(len(d))
    color = np.where(d["Close"] >= d["Open"], UP, DOWN)
    ax.vlines(x, d["Low"], d["High"], colors=color, linewidth=1)
    body = (d["Close"] - d["Open"]).abs().clip(lower=d["Close"].mean() * 1e-4)
    ax.bar(x, body, bottom=np.minimum(d["Open"], d["Close"]), color=color, width=0.6)
    axv.bar(x, d["Volume"], color=color, width=0.6)
    step = max(1, len(d) // 8)
    axv.set_xticks(x[::step], [f"{t:%m-%d}" for t in d.index[::step]], fontsize=7)
    ax.set_title(title or f"Last {len(d)} trading days", fontsize=10)
    axv.set_ylabel("Volume", fontsize=8)
    fig.tight_layout()


def draw_sweep(fig, sw, title=""):
    """Plain accuracy vs balanced accuracy as the Flat band gets wider (3 classes)."""
    fig.clear()
    ax = fig.subplots(1, 1)
    x = sw["flat_pct"]
    ax.plot(x, sw["baseline_acc"], "k--", marker="o", label="baseline acc (always majority)")
    ax.plot(x, sw["rf_acc"], color="tab:blue", marker="o", label="RF accuracy")
    ax.plot(x, sw["rf_bal_acc"], color="tab:blue", ls=":", marker="s", label="RF balanced acc")
    ax.plot(x, sw["knn_acc"], color="tab:orange", marker="o", label="kNN accuracy")
    ax.plot(x, sw["knn_bal_acc"], color="tab:orange", ls=":", marker="s", label="kNN balanced acc")
    ax.set_xlabel("Flat band: |next-day return| <= x %")
    ax.set_ylabel("score")
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, loc="lower right")
    ax.set_title(title or "Wider Flat band -> higher accuracy, but not a better model", fontsize=10)
    fig.tight_layout()

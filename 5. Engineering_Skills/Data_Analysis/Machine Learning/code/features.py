"""Candlestick features (the 10 features from assignment 1) and prediction targets.

Per day t (O,H,L,C,V = open, high, low, close, volume):
  1  upper_shadow       (H - max(O,C)) / C * 100
  2  lower_shadow       (min(O,C) - L) / C * 100
  3  body               (C - O) / C * 100
  4-6 prev_*            the same three values for the previous day
  7  open_gap           (O - C[t-1]) / C * 100
  8  close_gap          (C - C[t-1]) / C * 100
  9  vol_ratio          (V - 5-day mean volume) / V
  10 trend5             (C[t-2] - C[t-7]) / C[t-7]

Targets (what we try to predict) are about the NEXT trading day:
  y_ret  next-day return in %          -> regression
  y_cls  five classes                  -> classification
            -2 Big Down   return < -big
            -1 Down       -big <= return < -small
             0 Flat       |return| <= small
            +1 Up         small < return <= big
            +2 Big Up     return > big
  (small / big are in %, e.g. small = 0.5, big = 3.0)
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

BASE_FEATURES = [
    "upper_shadow", "lower_shadow", "body",
    "prev_upper_shadow", "prev_lower_shadow", "prev_body",
    "open_gap", "close_gap", "vol_ratio", "trend5",
]
# Bonus: extra technical indicators (assignment item 3)
EXTRA_FEATURES = ["rsi14", "macd_hist", "ma5_gap", "ma20_gap", "volatility10"]

CLASS_LABELS = [-2, -1, 0, 1, 2]
CLASS_NAMES = {-2: "BigDown", -1: "Down", 0: "Flat", 1: "Up", 2: "BigUp"}
CLASS_ZH = {-2: "大跌", -1: "小跌", 0: "持平", 1: "小漲", 2: "大漲"}


def build_features(df, extra=False):
    o, h, l, c, v = df["Open"], df["High"], df["Low"], df["Close"], df["Volume"]
    prev_c = c.shift(1)

    f = pd.DataFrame(index=df.index)
    f["upper_shadow"] = (h - np.maximum(o, c)) / c * 100
    f["lower_shadow"] = (np.minimum(o, c) - l) / c * 100
    f["body"] = (c - o) / c * 100
    for name in ["upper_shadow", "lower_shadow", "body"]:
        f["prev_" + name] = f[name].shift(1)
    f["open_gap"] = (o - prev_c) / c * 100
    f["close_gap"] = (c - prev_c) / c * 100
    # index data can have zero volume -> avoid division by zero; clip extreme ratios
    f["vol_ratio"] = ((v - v.rolling(5).mean()) / v.replace(0, np.nan)).clip(-5, 1)
    f["trend5"] = (c.shift(2) - c.shift(7)) / c.shift(7)

    if extra:
        delta = c.diff()
        gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
        loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
        f["rsi14"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
        macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
        f["macd_hist"] = (macd - macd.ewm(span=9, adjust=False).mean()) / c * 100
        f["ma5_gap"] = (c / c.rolling(5).mean() - 1) * 100
        f["ma20_gap"] = (c / c.rolling(20).mean() - 1) * 100
        f["volatility10"] = c.pct_change().rolling(10).std() * 100

    return f.replace([np.inf, -np.inf], np.nan)


def label_from_return(ret, small, big):
    """Map next-day return (%) to -2 / -1 / 0 / +1 / +2 (see module docstring)."""
    r = np.asarray(ret, dtype=float)
    return np.select(
        [r > big, r > small, r >= -small, r >= -big],
        [2, 1, 0, -1],
        default=-2,
    )


def quantile_thresholds(ret, p_small=0.33, p_big=0.80):
    """Data-driven thresholds from |return| of the TRAINING data only.

    Flat ~ the smallest 33% of moves, Big ~ the largest 20%, the rest Small.
    This keeps the five classes reasonably balanced, so accuracy is not inflated
    by one huge 'Flat' class.
    """
    a = np.abs(np.asarray(ret, dtype=float))
    return float(np.quantile(a, p_small)), float(np.quantile(a, p_big))


@dataclass
class Dataset:
    X: pd.DataFrame        # features of every day that has a known next-day outcome
    y_ret: pd.Series       # next-day return in %
    latest: pd.DataFrame   # features of the most recent day (outcome unknown) or None
    feature_names: list


def build_dataset(df, extra=False):
    """Features + next-day return. Class labels are made later (they depend on thresholds)."""
    feats = build_features(df, extra).dropna()
    names = list(feats.columns)
    nxt = ((df["Close"].shift(-1) / df["Close"] - 1) * 100).rename("y")

    latest = feats.iloc[[-1]] if len(feats) and feats.index[-1] == df.index[-1] else None
    labeled = feats.join(nxt).dropna(subset=["y"])
    return Dataset(labeled[names], labeled["y"], latest, names)

"""Download / cache daily OHLCV data.

Real data comes from yfinance and is cached in ./data/<ticker>.csv so you do not
hit Yahoo on every run (use refresh=True to re-download, e.g. to get new 2026 days).
`demo=True` generates synthetic random-walk prices so you can test the program
offline. Demo data is pure noise: do not put demo results in your report.
"""
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

CACHE_DIR = Path(__file__).parent / "data"

# 10 Taiwan stocks + the market index (the assignment asks for the index too)
DEFAULT_TICKERS = [
    "^TWII",    # TAIEX (market index)
    "2330.TW",  # TSMC
    "2317.TW",  # Hon Hai
    "2454.TW",  # MediaTek
    "2412.TW",  # Chunghwa Telecom
    "2881.TW",  # Fubon Financial
    "2882.TW",  # Cathay Financial
    "1301.TW",  # Formosa Plastics
    "2303.TW",  # UMC
    "2603.TW",  # Evergreen Marine
    "2308.TW",  # Delta Electronics
]


def load_prices(ticker, start="2020-01-01", end=None, demo=False, refresh=False):
    """Return a DataFrame indexed by date with Open, High, Low, Close, Volume."""
    if demo:
        return make_demo_prices(ticker, start, end)

    CACHE_DIR.mkdir(exist_ok=True)
    f = CACHE_DIR / f"{ticker.replace('^', '_')}.csv"
    if f.exists() and not refresh:
        return pd.read_csv(f, index_col=0, parse_dates=True)

    import yfinance as yf  # imported here so --demo works without it

    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df is None or df.empty:
        raise ValueError(f"No data returned for {ticker}. Check the ticker / your connection.")
    if isinstance(df.columns, pd.MultiIndex):  # newer yfinance returns MultiIndex columns
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    df.index.name = "Date"
    df.to_csv(f)
    return df


def make_demo_prices(ticker, start="2020-01-01", end=None):
    rng = np.random.default_rng(zlib.crc32(ticker.encode()))
    idx = pd.bdate_range(start, end or pd.Timestamp.today().normalize())
    n = len(idx)
    close = 100 * np.exp(np.cumsum(rng.normal(0.0003, 0.015, n)))
    prev = np.r_[close[0], close[:-1]]
    open_ = prev * (1 + rng.normal(0, 0.005, n))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, n)))
    volume = rng.lognormal(15, 0.4, n)
    df = pd.DataFrame(
        {"Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume}, index=idx
    )
    df.index.name = "Date"
    return df

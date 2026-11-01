# K-line pattern stock prediction (Data Mining midterm)

Predicts the next trading day's trend (Big Down / Down / Flat / Up / Big Up, i.e. 大跌/小跌/持平/小漲/大漲)
and return (%) from the
10 candlestick features of assignment 1, using three methods:
1. similarity matching (kNN), 2. classification (RandomForest), 3. regression (RandomForest).

## Setup in VS Code
```
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```
Select the `.venv` interpreter (Ctrl+Shift+P -> "Python: Select Interpreter").
tkinter ships with the python.org installers; on Linux: `sudo apt install python3-tk`.

## Run
```
python gui.py                 # GUI (take your screenshots here)
python main.py                # 10 stocks + ^TWII, writes results/summary.csv + PNG figures
python main.py --extra        # bonus: add RSI / MACD / MA gap / volatility features
python main.py --refresh      # re-download data (do this to pick up new 2026 days)
python main.py --demo         # offline smoke test with synthetic data (NOT for the report)
```
Useful options: `--small 0.5` (|return| <= this % is Flat), `--big 3.0` (|return| > this % is Big up/down),
`--mode quantile` (derive both from the training returns so classes are balanced), `--sweep`
(Flat-band sweep, see below), `--k 15`, `--train-end 2025-12-31`, `--test-start 2026-01-01`.

## The "wide Flat range inflates accuracy" problem
If the Flat band is wide, most days are Flat and "always predict Flat" already gets a high accuracy
(e.g. 90%+), so accuracy alone says nothing. What this project does about it:
- reports a majority-class baseline next to every model,
- reports balanced accuracy (mean recall per class), macro-F1 and per-class precision/recall,
- RandomForest uses class_weight="balanced"; kNN votes are divided by class frequency,
- `--mode quantile` picks thresholds from the training |returns| (Flat = smallest 33%, Big = largest 20%)
  so the classes stay balanced,
- `--sweep` / GUI "Flat-band sweep" widens the Flat band step by step and plots accuracy vs balanced accuracy.

## Files
- data.py      yfinance download + CSV cache (./data)
- features.py  the 10 features, optional extra indicators, targets
- models.py    three methods, metrics, next-day prediction, text summary
- plots.py     confusion matrices, return plot, candlestick chart
- main.py      batch runner; gui.py  Tkinter GUI

## Notes for the report
- Split is by date (train 2020-2025, test 2026), no shuffling, so there is no look-ahead.
- Judge models by balanced accuracy / F1 and by how much they beat the baseline, not by raw accuracy.
- A baseline (always predict the majority class / the mean return) is reported. Daily
  stock moves are very noisy: if a model barely beats the baseline, say so honestly and
  discuss why (and try --extra for the bonus).
- Output is educational, not investment advice.

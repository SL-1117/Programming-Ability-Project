"""The three prediction methods required by the midterm (now with 5 classes).

Classes: Big Down / Down / Flat / Up / Big Up  (see features.py for the thresholds).

1. Similarity matching  - kNN on standardized candlestick features: find the k most
                          similar historical days, vote on their next-day class
                          (votes are divided by class frequency so rare classes are not
                          drowned out) and average their next-day return.
2. Classification       - RandomForest predicts the 5 classes (class_weight="balanced").
3. Regression           - RandomForest predicts the next-day return (%); the predicted
                          return is turned into a class to get a confusion matrix.

Accuracy alone is misleading when one class (usually "Flat") is huge: a model that always
says "Flat" scores high. So every method is reported with
  accuracy, BALANCED accuracy (mean recall per class), macro-F1, and per-class precision/recall,
next to a majority-class baseline. `sweep_thresholds` shows the effect directly.

Train/test split is by date, so the model never sees the future.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (accuracy_score, balanced_accuracy_score, confusion_matrix,
                             f1_score, mean_absolute_error, mean_squared_error,
                             precision_recall_fscore_support, r2_score)
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

from features import (CLASS_LABELS, CLASS_NAMES, build_dataset, label_from_return,
                      quantile_thresholds)


# ----------------------------------------------------------------- metrics
def cls_metrics(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    present = sorted(set(y_true) | set(y_pred))
    p, r, f, sup = precision_recall_fscore_support(
        y_true, y_pred, labels=CLASS_LABELS, zero_division=0)
    # balanced accuracy = mean recall over the classes that actually occur in y_true
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_acc": float(balanced_accuracy_score(y_true, y_pred)),
        "f1_macro": float(f1_score(y_true, y_pred, labels=present, average="macro", zero_division=0)),
        "per_class": {CLASS_NAMES[c]: {"precision": float(p[i]), "recall": float(r[i]),
                                       "f1": float(f[i]), "support": int(sup[i])}
                      for i, c in enumerate(CLASS_LABELS)},
        "cm": confusion_matrix(y_true, y_pred, labels=CLASS_LABELS),
    }


def reg_metrics(y_true, y_pred):
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


# ------------------------------------------------------- similarity (kNN)
def knn_predict(Xtr_s, ycls_tr, yret_tr, Xq_s, k):
    """Return (class prediction, return prediction, neighbour indices) for each query row."""
    k = min(k, len(Xtr_s))
    _, idx = NearestNeighbors(n_neighbors=k).fit(Xtr_s).kneighbors(Xq_s)
    freq = np.array([max((ycls_tr == c).mean(), 1e-3) for c in CLASS_LABELS])
    votes = np.stack([(ycls_tr[idx] == c).sum(axis=1) for c in CLASS_LABELS], axis=1) / freq
    cls_pred = np.array(CLASS_LABELS)[votes.argmax(axis=1)]
    ret_pred = yret_tr[idx].mean(axis=1)
    return cls_pred, ret_pred, idx


def _rf_clf(seed, n=300):
    return RandomForestClassifier(n_estimators=n, min_samples_leaf=5, class_weight="balanced",
                                  n_jobs=-1, random_state=seed)


def _rf_reg(seed, n=300):
    return RandomForestRegressor(n_estimators=n, min_samples_leaf=5, n_jobs=-1, random_state=seed)


def _thresholds(mode, small, big, ret_train):
    """fixed: use the numbers given.  quantile: derive them from the training returns."""
    if mode == "quantile":
        return quantile_thresholds(ret_train)
    return float(small), float(big)


# ------------------------------------------------------------- experiment
def run_experiment(df, ticker="", extra=False, small=0.5, big=3.0, mode="fixed", k=15,
                   train_start="2020-01-01", train_end="2025-12-31", test_start="2026-01-01",
                   seed=42):
    ds = build_dataset(df, extra=extra)
    X, y_ret = ds.X, ds.y_ret.values

    tr = (X.index >= train_start) & (X.index <= train_end)
    te = X.index >= test_start
    if tr.sum() < 100:
        raise ValueError(f"{ticker}: only {tr.sum()} training days, need at least 100.")
    if te.sum() < 10:
        raise ValueError(f"{ticker}: only {te.sum()} test days (refresh the data?).")

    # thresholds come from TRAINING data only (matters for mode="quantile")
    small, big = _thresholds(mode, small, big, y_ret[tr])
    if big <= small:
        raise ValueError(f"big threshold ({big:.2f}) must be larger than small ({small:.2f}).")
    y_cls = label_from_return(y_ret, small, big)

    Xtr, Xte = X[tr].values, X[te].values
    ytr_c, yte_c = y_cls[tr], y_cls[te]
    ytr_r, yte_r = y_ret[tr], y_ret[te]

    scaler = StandardScaler().fit(Xtr)
    Xtr_s, Xte_s = scaler.transform(Xtr), scaler.transform(Xte)

    # baseline: always predict the most common class of the training set
    majority = pd.Series(ytr_c).mode()[0]
    baseline = cls_metrics(yte_c, np.full_like(yte_c, majority))
    baseline["majority"] = CLASS_NAMES[int(majority)]
    baseline["rmse"] = float(np.sqrt(np.mean((yte_r - ytr_r.mean()) ** 2)))  # constant-mean forecast

    # 1) similarity matching
    sim_c, sim_r, _ = knn_predict(Xtr_s, ytr_c, ytr_r, Xte_s, k)
    similarity = {"cls_pred": sim_c, "ret_pred": sim_r,
                  "cls": cls_metrics(yte_c, sim_c), "reg": reg_metrics(yte_r, sim_r)}

    # 2) classification
    clf = _rf_clf(seed).fit(Xtr, ytr_c)
    clf_pred = clf.predict(Xte)
    classification = {"cls_pred": clf_pred, "cls": cls_metrics(yte_c, clf_pred)}

    # 3) regression (+ class confusion matrix from the predicted return)
    reg = _rf_reg(seed).fit(Xtr, ytr_r)
    reg_pred = reg.predict(Xte)
    reg_dir = label_from_return(reg_pred, small, big)
    regression = {"ret_pred": reg_pred, "reg": reg_metrics(yte_r, reg_pred),
                  "cls_pred": reg_dir, "cls": cls_metrics(yte_c, reg_dir)}

    importances = pd.Series(clf.feature_importances_, index=ds.feature_names).sort_values(ascending=False)

    res = {
        "ticker": ticker, "small": small, "big": big, "mode": mode, "k": k, "extra": extra,
        "features": ds.feature_names, "feature_importance": importances,
        "train_range": (X.index[tr][0], X.index[tr][-1]), "n_train": int(tr.sum()),
        "test_range": (X.index[te][0], X.index[te][-1]), "n_test": int(te.sum()),
        "test_index": X.index[te], "y_test_ret": yte_r, "y_test_cls": yte_c,
        "train_class_counts": {CLASS_NAMES[c]: int((ytr_c == c).sum()) for c in CLASS_LABELS},
        "test_class_counts": {CLASS_NAMES[c]: int((yte_c == c).sum()) for c in CLASS_LABELS},
        "baseline": baseline,
        "similarity": similarity, "classification": classification, "regression": regression,
    }
    res["next_day"] = _predict_next_day(ds, y_cls, small, big, k, seed)
    return res


def _predict_next_day(ds, y_cls, small, big, k, seed):
    """Fit on ALL labeled days and predict the day after the most recent candle."""
    if ds.latest is None:
        return None
    Xall, xq = ds.X.values, ds.latest.values
    yc, yr = y_cls, ds.y_ret.values
    sc = StandardScaler().fit(Xall)
    s_c, s_r, idx = knn_predict(sc.transform(Xall), yc, yr, sc.transform(xq), k)
    clf = _rf_clf(seed).fit(Xall, yc)
    reg = _rf_reg(seed).fit(Xall, yr)
    proba = dict(zip(clf.classes_, clf.predict_proba(xq)[0]))
    nn_dates = ds.X.index[idx[0][:5]]
    return {
        "as_of": ds.latest.index[0],
        "similarity_class": CLASS_NAMES[int(s_c[0])], "similarity_return": float(s_r[0]),
        "similar_days": [(d, float(yr[i])) for d, i in zip(nn_dates, idx[0][:5])],
        "classification": CLASS_NAMES[int(clf.predict(xq)[0])],
        "class_proba": {CLASS_NAMES[c]: float(proba.get(c, 0.0)) for c in CLASS_LABELS},
        "regression_return": float(reg.predict(xq)[0]),
        "regression_class": CLASS_NAMES[int(label_from_return(reg.predict(xq), small, big)[0])],
    }


# ------------------------------------------------- threshold sweep (the 'big range' problem)
def sweep_thresholds(df, smalls=(0.25, 0.5, 1.0, 1.5, 2.0, 3.0), extra=False, k=15,
                     train_start="2020-01-01", train_end="2025-12-31", test_start="2026-01-01",
                     seed=42):
    """Widen the Flat band step by step and record accuracy vs balanced accuracy / F1.

    Shows that a wide Flat range raises plain accuracy (and the 'always Flat' baseline)
    without making the model any better. Uses 3 classes: Down / Flat / Up (big = inf).
    """
    ds = build_dataset(df, extra=extra)
    X, y_ret = ds.X, ds.y_ret.values
    tr = (X.index >= train_start) & (X.index <= train_end)
    te = X.index >= test_start
    Xtr, Xte = X[tr].values, X[te].values
    sc = StandardScaler().fit(Xtr)
    rows = []
    for s in smalls:
        y = label_from_return(y_ret, s, 1e9)   # only Down / Flat / Up
        ytr, yte = y[tr], y[te]
        maj = pd.Series(ytr).mode()[0]
        base = cls_metrics(yte, np.full_like(yte, maj))
        rf = cls_metrics(yte, _rf_clf(seed, 150).fit(Xtr, ytr).predict(Xte))
        knn_c, _, _ = knn_predict(sc.transform(Xtr), ytr, y_ret[tr], sc.transform(Xte), k)
        kn = cls_metrics(yte, knn_c)
        rows.append({
            "flat_pct": s, "flat_share": float((yte == 0).mean()),
            "baseline_acc": base["accuracy"],
            "rf_acc": rf["accuracy"], "rf_bal_acc": rf["balanced_acc"], "rf_f1": rf["f1_macro"],
            "knn_acc": kn["accuracy"], "knn_bal_acc": kn["balanced_acc"], "knn_f1": kn["f1_macro"],
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------- text report
def _per_class_table(m, title):
    lines = [f"    {title}", f"      {'class':<9s}{'prec':>7s}{'recall':>8s}{'f1':>7s}{'n':>6s}"]
    for name, v in m["per_class"].items():
        lines.append(f"      {name:<9s}{v['precision']:7.2f}{v['recall']:8.2f}{v['f1']:7.2f}{v['support']:6d}")
    return lines


def format_summary(res):
    b, s, c, r = res["baseline"], res["similarity"], res["classification"], res["regression"]
    d = lambda t: f"{t[0]:%Y-%m-%d} ~ {t[1]:%Y-%m-%d}"
    how = "quantile of training |return|" if res["mode"] == "quantile" else "fixed"
    lines = [
        f"Ticker: {res['ticker']}    extra indicators: {'yes' if res['extra'] else 'no'}",
        f"Classes ({how}): Flat |r|<={res['small']:.2f}%, Small {res['small']:.2f}~{res['big']:.2f}%, "
        f"Big >{res['big']:.2f}%",
        f"Train: {res['n_train']} days ({d(res['train_range'])})  classes: {res['train_class_counts']}",
        f"Test : {res['n_test']} days ({d(res['test_range'])})  classes: {res['test_class_counts']}",
        f"Features ({len(res['features'])}): {', '.join(res['features'])}",
        "",
        f"Baseline (always '{b['majority']}'): accuracy {b['accuracy']:.3f}  balanced acc {b['balanced_acc']:.3f}  "
        f"F1 {b['f1_macro']:.3f}  | constant-mean RMSE {b['rmse']:.3f}",
        "  -> a model must beat the baseline accuracy AND its balanced accuracy / F1 to be useful.",
        "",
        f"[1] Similarity matching (kNN, k={res['k']})",
        f"    accuracy {s['cls']['accuracy']:.3f}  balanced acc {s['cls']['balanced_acc']:.3f}  "
        f"F1 {s['cls']['f1_macro']:.3f}",
        f"    regression: RMSE {s['reg']['rmse']:.3f}  R2 {s['reg']['r2']:.3f}",
        "[2] Classification (RandomForest)",
        f"    accuracy {c['cls']['accuracy']:.3f}  balanced acc {c['cls']['balanced_acc']:.3f}  "
        f"F1 {c['cls']['f1_macro']:.3f}",
        "[3] Regression (RandomForest)",
        f"    RMSE {r['reg']['rmse']:.3f}  MAE {r['reg']['mae']:.3f}  R2 {r['reg']['r2']:.3f}",
        f"    class (from predicted return): accuracy {r['cls']['accuracy']:.3f}  "
        f"balanced acc {r['cls']['balanced_acc']:.3f}  F1 {r['cls']['f1_macro']:.3f}",
        "",
    ]
    lines += _per_class_table(c["cls"], "Per-class precision / recall (RandomForest classifier)")
    lines += ["", "Top feature importances (classifier):"]
    lines += [f"    {n:<20s}{v:.3f}" for n, v in res["feature_importance"].head(5).items()]
    nd = res["next_day"]
    if nd:
        lines += [
            "",
            f"Prediction for the trading day after {nd['as_of']:%Y-%m-%d} (models fit on all data):",
            f"    similarity     : {nd['similarity_class']} (avg neighbour return {nd['similarity_return']:+.2f}%)",
            f"    classification : {nd['classification']}  "
            + "  ".join(f"{k} {v:.0%}" for k, v in nd["class_proba"].items()),
            f"    regression     : {nd['regression_return']:+.2f}% -> {nd['regression_class']}",
            "    most similar past days: "
            + ", ".join(f"{dt:%Y-%m-%d} ({ret:+.1f}%)" for dt, ret in nd["similar_days"]),
            "(Educational model output, not investment advice.)",
        ]
    return "\n".join(lines)

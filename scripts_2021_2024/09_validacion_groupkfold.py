"""Validate unseen-institution performance with the protocol from analysis 09.

Run after 03: .venv/bin/python scripts_2021_2024/09_validacion_groupkfold.py
Writes docs_2021_2024/09_validacion_groupkfold.md and prints fold metrics.
This canonical implementation accepts both the 64-column output of 03 and
its 62-column deduplicated variant, without modifying the input CSV.
"""

import hashlib
import platform

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    balanced_accuracy_score, confusion_matrix, f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from common import (
    DATE_COLUMN, LABELS, LEAKAGE_COLUMNS, PROCESSED_DATA, RANDOM_STATE,
    REPORT_DIR, load_features, read_csv,
)

REPORT = REPORT_DIR / "09_validacion_groupkfold.md"
GROUP = "inst_cod_institucion"
N_SPLITS = 5
N_ESTIMATORS = 300
REFERENCE_YEAR = 2024
EXPECTED_ROWS = 30738
EXCLUDED_B = (
    "inst_cod_institucion", "inst_origen", "inst_caracter_academico",
    "estu_prgm_codmunicipio", "estu_prgm_municipio", "estu_prgm_departamento",
    "estu_inst_codmunicipio", "estu_inst_municipio", "estu_inst_departamento",
    "estu_cod_mcpio_presentacion", "estu_mcpio_presentacion",
    "estu_cod_depto_presentacion", "estu_depto_presentacion",
    "estu_nacionalidad", "estu_pais_reside", "estu_exterior",
)


def make_model(columns):
    """Create fresh train-only preprocessing and a balanced forest per fold."""
    categorical = [column for column in columns if column != "edad"]
    preprocessing = ColumnTransformer([
        ("age", SimpleImputer(strategy="median"), ["edad"]),
        ("categories", Pipeline([
            ("impute", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            ("encode", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ]), categorical),
    ])
    return Pipeline([
        ("preprocessing", preprocessing),
        ("forest", RandomForestClassifier(
            n_estimators=N_ESTIMATORS, class_weight="balanced",
            random_state=RANDOM_STATE, n_jobs=-1,
        )),
    ])


def scores(truth, predicted):
    """Return macro F1 and balanced accuracy in report order."""
    return (
        f1_score(truth, predicted, labels=LABELS, average="macro", zero_division=0),
        balanced_accuracy_score(truth, predicted),
    )


def detailed_metrics(truth, predicted):
    """Render per-class metrics and the confusion matrix without personal data."""
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predicted, labels=LABELS, zero_division=0,
    )
    lines = ["| Level | Precision | Recall | F1 | Support |", "|---|---:|---:|---:|---:|"]
    for index, label in enumerate(LABELS):
        lines.append(f"| {label} | {precision[index]:.4f} | {recall[index]:.4f} | "
                     f"{f1[index]:.4f} | {support[index]} |")
    matrix = confusion_matrix(truth, predicted, labels=LABELS)
    if matrix.sum() != len(truth):
        raise ValueError("Confusion matrix does not account for every observation")
    lines += ["", "Rows = actual level; columns = predicted level.", "",
              "| Actual / Predicted | 1 | 2 | 3 | 4 |", "|---|---:|---:|---:|---:|"]
    for label, row in zip(LABELS, matrix):
        lines.append(f"| {label} | " + " | ".join(map(str, row)) + " |")
    return lines


def main():
    """Evaluate the same five institutional folds under scenarios A and B."""
    frame = read_csv(PROCESSED_DATA)
    if len(frame) != EXPECTED_ROWS or len(frame.columns) not in (62, 64):
        raise ValueError(f"Unexpected dataset shape: {frame.shape}")
    X, y = load_features(frame)
    if not set(EXCLUDED_B).issubset(X.columns):
        raise ValueError("Missing expected ablation fields")
    groups = X[GROUP].copy()
    birth = pd.to_datetime(X.pop(DATE_COLUMN), format="%d/%m/%Y", errors="raise")
    X["edad"] = REFERENCE_YEAR - birth.dt.year
    if not X["edad"].between(0, 120).all():
        raise ValueError("Age outside 0–120 years; inspect data before modeling")
    for column in X.columns.drop("edad"):
        X[column] = X[column].map(lambda value: str(value) if pd.notna(value) else np.nan)
    folds = list(GroupKFold(n_splits=N_SPLITS).split(X, y, groups))
    seen = np.zeros(len(y), dtype=int)
    for train, test in folds:
        if not set(groups.iloc[train]).isdisjoint(set(groups.iloc[test])):
            raise ValueError("Institution leakage between training and test folds")
        if set(y.iloc[train]) != set(LABELS) or set(y.iloc[test]) != set(LABELS):
            raise ValueError("Every fold must contain all four levels in train and test")
        seen[test] += 1
    if not np.all(seen == 1):
        raise ValueError("Every row must receive exactly one out-of-fold prediction")

    lines = [
        "# Unseen-institution validation — GroupKFold", "",
        "Continuation of [08_shap.md](08_shap.md). This tests institutional, not temporal, generalization.", "",
        "## Reproducible protocol", "", "```bash",
        ".venv/bin/python scripts_2021_2024/09_validacion_groupkfold.py", "```", "",
        f"- Input: {len(frame):,} rows, {len(frame.columns)} columns, {groups.nunique()} institutions; no rows removed.",
        f"- CSV SHA-256: `{hashlib.sha256(PROCESSED_DATA.read_bytes()).hexdigest()}`.",
        f"- Environment: Python {platform.python_version()}, pandas {pd.__version__}, "
        f"NumPy {np.__version__}, scikit-learn {sklearn.__version__}.",
        f"- Target: nivel_desempeno (1–4). GroupKFold: {N_SPLITS} folds, no shuffle, groups={GROUP}; identical folds for A/B.",
        f"- Random forest: {N_ESTIMATORS} trees, class_weight='balanced', random_state={RANDOM_STATE}, n_jobs=-1; other defaults unchanged.",
        f"- edad = {REFERENCE_YEAR} - birth year; approximate age at the end of 2024, not age at examination. Replaces the birth date.",
        "- Dates use day/month/year and ages must fall in 0–120; invalid dates raise errors.",
        "- All other features, including numeric codes, are string categories. OrdinalEncoder is fitted only on each training fold; unseen categories map to -1.",
        "- Constant categorical and median age imputers are fitted inside each training pipeline; a fresh model is created per fold.",
        "- Institution separation, all four classes, and exactly one OOF prediction per row are checked.", "",
        "## Variables and exclusions", "",
        "A uses 43 features; B removes 16 institutional/geographic fields and uses 27.",
        "Duplicate institution name/program code fields are excluded in memory if present.", "",
        "B exclusions:", "", *[f"- `{column}`" for column in EXCLUDED_B], "",
        "Common leakage exclusions (18 total, including punt_global):", "",
        *[f"- `{column}`" for column in LEAKAGE_COLUMNS], "",
        "Scenario A predictors:", "", *[f"- `{column}`" for column in X.columns], "",
        "## Fold composition", "",
        "| Fold | Train rows | Test rows | Train institutions | Test institutions | Test n1/n2/n3/n4 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for number, (train, test) in enumerate(folds, 1):
        counts = y.iloc[test].value_counts().reindex(LABELS, fill_value=0)
        lines.append(f"| {number} | {len(train)} | {len(test)} | {groups.iloc[train].nunique()} | "
                     f"{groups.iloc[test].nunique()} | {' / '.join(map(str, counts))} |")

    results = {}
    scenarios = [("A", list(X.columns)), ("B", [c for c in X if c not in EXCLUDED_B])]
    for scenario, columns in scenarios:
        lines += ["", f"## Scenario {scenario}: {len(columns)} predictors", "",
                  "| Fold | Macro F1 | Balanced accuracy |", "|---|---:|---:|"]
        oof = np.zeros(len(y), dtype=int)
        fold_scores, details = [], []
        for number, (train, test) in enumerate(folds, 1):
            model = make_model(columns)
            model.fit(X.iloc[train][columns], y.iloc[train])
            predicted = model.predict(X.iloc[test][columns])
            oof[test] = predicted
            metrics = scores(y.iloc[test], predicted)
            fold_scores.append(metrics)
            lines.append(f"| {number} | {metrics[0]:.4f} | {metrics[1]:.4f} |")
            details += ["", f"### Fold {number}", "", *detailed_metrics(y.iloc[test], predicted)]
            print(f"{scenario} fold {number}: macro F1={metrics[0]:.4f}, balanced accuracy={metrics[1]:.4f}", flush=True)
        mean = np.mean(fold_scores, axis=0)
        std = np.std(fold_scores, axis=0, ddof=1)
        pooled = scores(y, oof)
        results[scenario] = pooled
        lines += [f"| Unweighted mean | {mean[0]:.4f} | {mean[1]:.4f} |",
                  f"| Sample standard deviation (ddof=1) | {std[0]:.4f} | {std[1]:.4f} |",
                  f"| Pooled OOF | {pooled[0]:.4f} | {pooled[1]:.4f} |", "",
                  "### Pooled OOF metrics", "", *detailed_metrics(y, oof), *details]
        print(f"{scenario} pooled OOF: macro F1={pooled[0]:.4f}, balanced accuracy={pooled[1]:.4f}", flush=True)
    delta = np.subtract(results["B"], results["A"])
    lines += ["", "## Interpretation and limitations", "",
              f"- B minus A pooled OOF: macro F1 {delta[0]:+.4f}; balanced accuracy {delta[1]:+.4f}.",
              "- B jointly ablates institution identity, institutional attributes, and explicit geography (including country/exterior). This is not an isolated feature effect; indirect proxies can remain.",
              "- Fold means weight folds equally; pooled OOF metrics are recomputed over all rows. Balanced accuracy averages class recall. Undefined per-class metrics use zero_division=0.",
              "- Fold standard deviation is not a confidence interval or significance test. Training sets overlap and GroupKFold does not stratify classes.",
              "- Unseen institution codes map to -1; this does not learn to extrapolate new identities. OrdinalEncoder imposes an artificial order on nominal categories.",
              "- The 0.465 macro F1 in 06 used random holdout and epoch dates. It is not a controlled comparison: splits, age representation, and unknown-category handling differ.",
              "- Prior preprocessing leakage remains: analysis 03 imputed modes/medians on the full dataset before these folds. Original missing-value masks are unavailable. Train-only pipelines cannot undo those imputations; fully leakage-free evaluation requires reconstructing pre-imputation data.",
              "- No causal claims, temporal validation, repeated seeds, or nested tuning.", ""]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written: {REPORT}", flush=True)


if __name__ == "__main__":
    main()

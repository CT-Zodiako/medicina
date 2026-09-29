"""Scenario B, leakage-free version: fold-local imputation instead of global.

Run after 02 (NOT after 03): .venv/bin/python scripts_2021_2024/12_modelo_final_sin_fuga.py
Writes docs_2021_2024/12_modelo_final_sin_fuga.md.

Analyses 03 and 09 impute mode/median statistics over the FULL dataset before
any train/test split exists — a preprocessing leakage the fold-local
ColumnTransformer in 09/10 could not undo, since the missing-value mask was
already gone by the time those scripts ran. This script fixes that: it
reads the raw CSV, reapplies only step 02's deterministic transform (score
reconstruction, level derivation, column drops, category normalization —
none of which uses cross-row statistics), keeps real NaNs, and fits every
mode/median/constant imputer **inside each GroupKFold training fold**.

The only global, pre-split operation here is dropping rows with a null or
corrupted birth date. That is a fixed per-row filter, not a statistic
derived from the data's distribution, so it introduces no leakage.
"""

import hashlib
import importlib
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, f1_score, precision_recall_fscore_support
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from common import (  # noqa: E402
    BINARY_COLUMNS, DATE_COLUMN, DUPLICATE_COLUMNS, LABELS, LEAKAGE_COLUMNS,
    RANDOM_STATE, RAW_DATA, REPORT_DIR, TARGET, read_csv,
)

step02 = importlib.import_module("02_tratamiento_datos")
step03 = importlib.import_module("03_imputacion_datos")

REPORT = REPORT_DIR / "12_modelo_final_sin_fuga.md"
GROUP = "inst_cod_institucion"
N_SPLITS = 5
REFERENCE_YEAR = 2024
BEST_PARAMS = {
    "forest__n_estimators": 600,
    "forest__min_samples_split": 5,
    "forest__min_samples_leaf": 1,
    "forest__max_features": "log2",
    "forest__max_depth": None,
}
# Same 16-field ablation as analyses 09 and 10.
EXCLUDED_B = (
    "inst_cod_institucion", "inst_origen", "inst_caracter_academico",
    "estu_prgm_codmunicipio", "estu_prgm_municipio", "estu_prgm_departamento",
    "estu_inst_codmunicipio", "estu_inst_municipio", "estu_inst_departamento",
    "estu_cod_mcpio_presentacion", "estu_mcpio_presentacion",
    "estu_cod_depto_presentacion", "estu_depto_presentacion",
    "estu_nacionalidad", "estu_pais_reside", "estu_exterior",
)
# Prior pipeline-leakage baseline: analysis 10, tuned scenario B, global imputation.
BASELINE_MACRO_F1 = 0.3787
BASELINE_BALANCED_ACCURACY = 0.3930


def load_preimputation_frame():
    """Rebuild scenario-02 output straight from raw data, keeping real NaNs."""
    raw = read_csv(RAW_DATA, dtype={"estu_semestrecursa": "string"})
    frame = step02.transform(raw)
    dates = frame[DATE_COLUMN].astype("string")
    missing = dates.isna()
    corrupt = dates.str.contains(step03.CORRUPT_DATE_PATTERN, regex=True, na=False)
    frame = frame.loc[~(missing | corrupt)].copy()
    pd.to_datetime(frame[DATE_COLUMN], format="%d/%m/%Y", errors="raise")
    return frame, int(missing.sum()), int(corrupt.sum())


def select_features(frame):
    """Exclude leakage/duplicate columns, mirroring common.load_features minus its no-NaN check."""
    excluded = {TARGET, *LEAKAGE_COLUMNS, *DUPLICATE_COLUMNS}
    columns = [c for c in frame.columns if c not in excluded]
    if len(columns) != 43:
        raise ValueError(f"Expected 43 scenario-A predictors, got {len(columns)}")
    return columns


def build_pipeline(columns):
    """Fold-local imputers by documented column role, then encode for the forest."""
    binary_cols = [c for c in columns if c in BINARY_COLUMNS]
    median_cols = [c for c in columns if c in step03.MEDIAN_COLUMNS and c != "edad"]
    nominal_cols = [c for c in columns if c in step03.NOMINAL_COLUMNS]
    other_cat_cols = [
        c for c in columns
        if c not in binary_cols and c not in median_cols and c not in nominal_cols and c != "edad"
    ]
    preprocessing = ColumnTransformer([
        ("age", SimpleImputer(strategy="median"), ["edad"]),
        ("binary", SimpleImputer(strategy="most_frequent"), binary_cols),
        ("ordinal_numeric", SimpleImputer(strategy="median"), median_cols),
        ("nominal", Pipeline([
            ("impute", SimpleImputer(strategy="constant", fill_value="Sin dato")),
            ("encode", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ]), nominal_cols),
        ("other_categorical", Pipeline([
            ("impute", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            ("encode", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ]), other_cat_cols),
    ])
    return Pipeline([
        ("preprocessing", preprocessing),
        ("forest", RandomForestClassifier(
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=1,
        )),
    ])


def scores(truth, predicted):
    return (
        f1_score(truth, predicted, labels=LABELS, average="macro", zero_division=0),
        balanced_accuracy_score(truth, predicted),
    )


def detailed_metrics(truth, predicted):
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predicted, labels=LABELS, zero_division=0,
    )
    lines = ["| Level | Precision | Recall | F1 | Support |", "|---|---:|---:|---:|---:|"]
    for index, label in enumerate(LABELS):
        lines.append(f"| {label} | {precision[index]:.4f} | {recall[index]:.4f} | "
                     f"{f1[index]:.4f} | {support[index]} |")
    matrix = confusion_matrix(truth, predicted, labels=LABELS)
    lines += ["", "Rows = actual level; columns = predicted level.", "",
              "| Actual / Predicted | 1 | 2 | 3 | 4 |", "|---|---:|---:|---:|---:|"]
    for label, row in zip(LABELS, matrix):
        lines.append(f"| {label} | " + " | ".join(map(str, row)) + " |")
    return lines


def main():
    frame, dropped_null, dropped_corrupt = load_preimputation_frame()
    columns_a = select_features(frame)
    target = frame[TARGET].astype("int64")
    groups = frame[GROUP].copy()

    working = frame[columns_a].copy()
    birth = pd.to_datetime(working.pop(DATE_COLUMN), format="%d/%m/%Y", errors="raise")
    working["edad"] = REFERENCE_YEAR - birth.dt.year
    if not working["edad"].between(0, 120).all():
        raise ValueError("Age outside 0-120 years; inspect data before modeling")
    for column in working.columns:
        if column != "edad" and not pd.api.types.is_numeric_dtype(working[column]):
            working[column] = working[column].where(working[column].isna(), working[column].astype("string"))

    columns_b = [c for c in working.columns if c not in EXCLUDED_B]

    folds = list(GroupKFold(n_splits=N_SPLITS).split(working[columns_b], target, groups))
    for train, test in folds:
        if not set(groups.iloc[train]).isdisjoint(set(groups.iloc[test])):
            raise ValueError("Institution leakage between training and test folds")

    lines = [
        "# Final scenario-B model — no preprocessing leakage", "",
        "Continuation of [11_conclusion_importancia_variables.md](11_conclusion_importancia_variables.md). "
        "Fixes the preprocessing-leakage caveat from analyses 09 and 10: mode/median/constant "
        "imputers are now fit only on each fold's training rows.", "",
        "## Reproducible protocol", "", "```bash",
        ".venv/bin/python scripts_2021_2024/12_modelo_final_sin_fuga.py", "```", "",
        "This script reads `dataset_medicina.csv` directly and reapplies analysis 02's "
        "deterministic transform; it does not read or write `dataset_medicina_procesado.csv`, "
        "and it does not run analysis 03's global imputation.", "",
        f"- Rows after dropping null/corrupted birth dates: {len(frame):,} "
        f"(dropped {dropped_null} null, {dropped_corrupt} corrupted — same fixed row filter as 03).",
        f"- Institutions: {groups.nunique()}.",
        f"- Environment: Python {platform.python_version()}, pandas {pd.__version__}, "
        f"NumPy {np.__version__}, scikit-learn {sklearn.__version__}.",
        f"- Raw CSV SHA-256: `{hashlib.sha256(RAW_DATA.read_bytes()).hexdigest()}`.",
        f"- GroupKFold: {N_SPLITS} folds, no shuffle, groups={GROUP}.",
        "- edad = 2024 - birth year, computed after dropping unusable dates (same as 09/10).",
        "- Binary columns: most-frequent (mode) imputed per training fold, matching analysis 03's rule.",
        "- Ordinal/continuous columns: median imputed per training fold, matching analysis 03's rule.",
        "- Nominal columns (`fami_ocupacionmadre`, `fami_ocupacionpadre`, `estu_tituloobtenidobachiller`): "
        "constant-filled with `\"Sin dato\"` per training fold, matching analysis 03's rule.",
        "- Remaining always-complete categorical columns: constant-filled as a safety net, then "
        "`OrdinalEncoder` fit only on the training fold; unseen categories map to -1.",
        f"- Forest hyperparameters: best parameters found in analysis 10 — {BEST_PARAMS}.",
        f"- Scenario B predictors: {len(columns_b)} (same 27-field exclusion as 09/10).",
        f"- Baseline for comparison: analysis 10 tuned scenario B, global imputation — "
        f"macro F1={BASELINE_MACRO_F1:.4f}, balanced accuracy={BASELINE_BALANCED_ACCURACY:.4f}.",
        "", "## Fold results", "", "| Fold | Macro F1 | Balanced accuracy |", "|---|---:|---:|",
    ]

    oof = np.empty(len(target), dtype=int)
    fold_scores = []
    details = []
    for number, (train, test) in enumerate(folds, 1):
        model = build_pipeline(columns_b)
        model.set_params(**BEST_PARAMS)
        model.fit(working.iloc[train][columns_b], target.iloc[train])
        predicted = model.predict(working.iloc[test][columns_b])
        oof[test] = predicted
        metrics = scores(target.iloc[test], predicted)
        fold_scores.append(metrics)
        lines.append(f"| {number} | {metrics[0]:.4f} | {metrics[1]:.4f} |")
        details += ["", f"### Fold {number}", "", *detailed_metrics(target.iloc[test], predicted)]
        print(f"Fold {number}: macro F1={metrics[0]:.4f}, balanced accuracy={metrics[1]:.4f}", flush=True)

    mean = np.mean(fold_scores, axis=0)
    std = np.std(fold_scores, axis=0, ddof=1)
    pooled = scores(target, oof)
    delta_f1 = pooled[0] - BASELINE_MACRO_F1
    delta_ba = pooled[1] - BASELINE_BALANCED_ACCURACY
    lines += [
        f"| Unweighted mean | {mean[0]:.4f} | {mean[1]:.4f} |",
        f"| Sample standard deviation (ddof=1) | {std[0]:.4f} | {std[1]:.4f} |",
        f"| Pooled OOF | {pooled[0]:.4f} | {pooled[1]:.4f} |",
        "", "## Comparison against the leaky baseline", "",
        "| Metric | Baseline (10, global imputation) | This run (fold-local) | Delta |",
        "|---|---:|---:|---:|",
        f"| Macro F1 | {BASELINE_MACRO_F1:.4f} | {pooled[0]:.4f} | {delta_f1:+.4f} |",
        f"| Balanced accuracy | {BASELINE_BALANCED_ACCURACY:.4f} | {pooled[1]:.4f} | {delta_ba:+.4f} |",
        "", "### Pooled OOF metrics", "", *detailed_metrics(target, oof), *details,
        "", "## Interpretation and limitations", "",
        "- If the delta above is small, it confirms the global-imputation leakage in 09/10 had "
        "little practical effect on this dataset (a handful of percent missing per column). It "
        "does not mean leakage is acceptable practice — it means this leakage was mild here.",
        "- Row-level date filtering remains a global step, applied before any split. It is a "
        "fixed, deterministic filter, not a distribution-derived statistic, so it does not leak "
        "test-fold information into training.",
        "- Hyperparameters are fixed to analysis 10's best parameters, not re-tuned inside this "
        "leakage-free protocol; a fully rigorous pipeline would re-run tuning with fold-local "
        "imputation from the start (nested cross-validation).",
        "- No causal claims, temporal validation, or repeated-seed stability checks.", "",
    ]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Pooled OOF: macro F1={pooled[0]:.4f} (delta {delta_f1:+.4f}), "
          f"balanced accuracy={pooled[1]:.4f} (delta {delta_ba:+.4f})")
    print(f"Report written: {REPORT}")


if __name__ == "__main__":
    main()

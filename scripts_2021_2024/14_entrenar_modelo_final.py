"""Train and persist the final scenario-B model on 100% of the data.

Run after 02 (NOT after 03): .venv/bin/python scripts_2021_2024/14_entrenar_modelo_final.py
Writes modelos_2021_2024/modelo_final_nivel_desempeno.joblib and
docs_2021_2024/14_entrenamiento_modelo_final.md.

This is the first production artifact of the project: a fitted pipeline
that can predict `nivel_desempeno` for a student who has NOT taken the
exam, because none of its 27 inputs are exam-derived (see 05-08 for the
leakage exclusions). Analyses 06-12 only validated architecture/generalization
via cross-validation and never persisted a reusable model; this script fits
on every available row using the same hyperparameters validated in 10/12.

Fitting the imputers/encoder on 100% of the data is correct here, not
leakage: there is no held-out set left to protect once this is the final
production artifact. Reported performance expectations should still come
from the out-of-fold metrics in 12, not from this script's training fit.
"""

import hashlib
import importlib
import json
import platform
import sys
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

from common import (  # noqa: E402
    BINARY_COLUMNS, DATE_COLUMN, DUPLICATE_COLUMNS, LABELS, LEAKAGE_COLUMNS,
    RANDOM_STATE, RAW_DATA, REPORT_DIR, ROOT, TARGET, read_csv,
)

step02 = importlib.import_module("02_tratamiento_datos")
step03 = importlib.import_module("03_imputacion_datos")

MODEL_DIR = ROOT / "modelos_2021_2024"
MODEL_PATH = MODEL_DIR / "modelo_final_nivel_desempeno.joblib"
METADATA_PATH = MODEL_DIR / "modelo_final_nivel_desempeno_metadata.json"
REPORT = REPORT_DIR / "14_entrenamiento_modelo_final.md"
GROUP = "inst_cod_institucion"
REFERENCE_YEAR = 2024
BEST_PARAMS = {
    "forest__n_estimators": 600,
    "forest__min_samples_split": 5,
    "forest__min_samples_leaf": 1,
    "forest__max_features": "log2",
    "forest__max_depth": None,
}
EXCLUDED_B = (
    "inst_cod_institucion", "inst_origen", "inst_caracter_academico",
    "estu_prgm_codmunicipio", "estu_prgm_municipio", "estu_prgm_departamento",
    "estu_inst_codmunicipio", "estu_inst_municipio", "estu_inst_departamento",
    "estu_cod_mcpio_presentacion", "estu_mcpio_presentacion",
    "estu_cod_depto_presentacion", "estu_depto_presentacion",
    "estu_nacionalidad", "estu_pais_reside", "estu_exterior",
)
# Out-of-fold performance from 12 (fold-local imputation, same hyperparameters).
# This is the honest expectation for new, unseen students — NOT a number from
# this script's own training fit, which would be optimistic.
VALIDATED_MACRO_F1 = 0.3786
VALIDATED_BALANCED_ACCURACY = 0.3924


def load_preimputation_frame():
    """Reapply analysis 02's deterministic transform straight from raw data."""
    raw = read_csv(RAW_DATA, dtype={"estu_semestrecursa": "string"})
    frame = step02.transform(raw)
    dates = frame[DATE_COLUMN].astype("string")
    missing = dates.isna()
    corrupt = dates.str.contains(step03.CORRUPT_DATE_PATTERN, regex=True, na=False)
    frame = frame.loc[~(missing | corrupt)].copy()
    pd.to_datetime(frame[DATE_COLUMN], format="%d/%m/%Y", errors="raise")
    return frame


def select_features(frame):
    excluded = {TARGET, *LEAKAGE_COLUMNS, *DUPLICATE_COLUMNS}
    columns = [c for c in frame.columns if c not in excluded]
    if len(columns) != 43:
        raise ValueError(f"Expected 43 scenario-A predictors, got {len(columns)}")
    return columns


def build_pipeline(columns):
    """Same column roles and imputer rules as analysis 12, fit on all rows here."""
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
    pipeline = Pipeline([
        ("preprocessing", preprocessing),
        ("forest", RandomForestClassifier(
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1,
        )),
    ])
    pipeline.set_params(**BEST_PARAMS)
    return pipeline, binary_cols, median_cols, nominal_cols, other_cat_cols


def main():
    frame = load_preimputation_frame()
    columns_a = select_features(frame)
    target = frame[TARGET].astype("int64")

    working = frame[columns_a].copy()
    birth = pd.to_datetime(working.pop(DATE_COLUMN), format="%d/%m/%Y", errors="raise")
    working["edad"] = REFERENCE_YEAR - birth.dt.year
    if not working["edad"].between(0, 120).all():
        raise ValueError("Age outside 0-120 years; inspect data before modeling")
    for column in working.columns:
        if column != "edad" and not pd.api.types.is_numeric_dtype(working[column]):
            working[column] = working[column].where(working[column].isna(), working[column].astype("string"))

    columns_b = [c for c in working.columns if c not in EXCLUDED_B]
    X = working[columns_b]

    model, binary_cols, median_cols, nominal_cols, other_cat_cols = build_pipeline(columns_b)
    model.fit(X, target)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    metadata = {
        "target": TARGET,
        "labels": list(LABELS),
        "level_ranges_punt_global": {
            "1": "0-129", "2": "130-156", "3": "157-189", "4": "190-300",
        },
        "reference_year_for_age": REFERENCE_YEAR,
        "feature_order": columns_b,
        "feature_roles": {
            "age_median_imputed": ["edad"],
            "binary_mode_imputed": binary_cols,
            "ordinal_numeric_median_imputed": median_cols,
            "nominal_text_constant_imputed": nominal_cols,
            "other_categorical_constant_imputed": other_cat_cols,
        },
        "hyperparameters": BEST_PARAMS,
        "random_state": RANDOM_STATE,
        "training_rows": int(len(target)),
        "training_class_distribution": target.value_counts().sort_index().to_dict(),
        "validated_out_of_fold_performance": {
            "source": "analysis 12 (fold-local imputation, institution-disjoint GroupKFold)",
            "macro_f1": VALIDATED_MACRO_F1,
            "balanced_accuracy": VALIDATED_BALANCED_ACCURACY,
        },
        "raw_csv_sha256": hashlib.sha256(RAW_DATA.read_bytes()).hexdigest(),
        "environment": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__,
            "joblib": joblib.__version__,
        },
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Final model training — scenario B, 100% of data", "",
        "Continuation of [13_explicacion_modelo_y_datos_faltantes.md](13_explicacion_modelo_y_datos_faltantes.md). "
        "Persists a reusable model for predicting `nivel_desempeno` for students who have not "
        "taken the exam, since none of its inputs are exam-derived.", "",
        "## Reproducible protocol", "", "```bash",
        ".venv/bin/python scripts_2021_2024/14_entrenar_modelo_final.py", "```", "",
        f"- Training rows: {len(target):,} (100% of the cleaned dataset, no holdout — this is the "
        "final artifact, not a generalization test).",
        f"- Class distribution: {target.value_counts().sort_index().to_dict()}.",
        f"- Predictors: {len(columns_b)} (scenario B — no institution or geography fields).",
        f"- Hyperparameters: best parameters found in analysis 10 — {BEST_PARAMS}.",
        f"- Model file: `{MODEL_PATH.relative_to(ROOT)}`.",
        f"- Metadata file: `{METADATA_PATH.relative_to(ROOT)}` (feature order, roles, validated performance).",
        "", "## Expected real-world performance", "",
        "This script's own training fit is **not** a valid performance estimate — it would be "
        "optimistic, since the model saw every row it was evaluated on. The honest expectation "
        "for new, unseen students comes from analysis 12's fold-local, institution-disjoint "
        "out-of-fold evaluation, using the same hyperparameters:", "",
        f"| Metric | Validated value |", "|---|---:|",
        f"| Macro F1 | {VALIDATED_MACRO_F1:.4f} |",
        f"| Balanced accuracy | {VALIDATED_BALANCED_ACCURACY:.4f} |", "",
        "See [13](13_explicacion_modelo_y_datos_faltantes.md) for what this means in plain terms: "
        "usable for population-level tendencies, not reliable for individual decisions.",
        "", "## Required inputs, in the exact order the model expects", "",
        "| # | Field | Imputation role if missing |", "|---:|---|---|",
    ]
    roles_by_column = {}
    for column in binary_cols:
        roles_by_column[column] = "mode (most frequent)"
    for column in median_cols:
        roles_by_column[column] = "median"
    for column in nominal_cols:
        roles_by_column[column] = "constant 'Sin dato'"
    for column in other_cat_cols:
        roles_by_column[column] = "constant '__MISSING__'"
    roles_by_column["edad"] = "median"
    for index, column in enumerate(columns_b, 1):
        lines.append(f"| {index} | `{column}` | {roles_by_column[column]} |")
    lines += [
        "", "## Limitations", "",
        "- This is a single fitted snapshot of `dataset_medicina.csv` as it exists today; "
        "retraining on updated data will change the artifact and should bump the metadata.",
        "- Imputation defaults above are learned from this training set's distribution "
        "(e.g. `estu_pagomatriculapadres` mode = 1). New inference inputs with real values "
        "should be provided directly rather than relying on these defaults, which exist only "
        "to keep the pipeline robust to incomplete inputs.",
        "- The model has not been used for individual decisions; see 13 for why.", "",
    ]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Trained on {len(target):,} rows, {len(columns_b)} predictors")
    print(f"Model written: {MODEL_PATH}")
    print(f"Metadata written: {METADATA_PATH}")
    print(f"Report written: {REPORT}")


if __name__ == "__main__":
    main()

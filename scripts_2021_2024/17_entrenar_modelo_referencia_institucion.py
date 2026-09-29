"""Train and persist scenario A (with institution) as a reference model.

Run after 02 (NOT after 03): .venv/bin/python scripts_2021_2024/17_entrenar_modelo_referencia_institucion.py
Writes modelos_2021_2024/modelo_referencia_con_institucion.joblib and
docs_2021_2024/17_modelo_referencia_institucion.md.

This is scenario A from analyses 09/10/12: all 43 predictors, including
inst_cod_institucion. It exists ONLY as a side-by-side reference against the
production model (scenario B, no institution) — analysis 09 already showed
it generalizes worse to institutions unseen in training (macro F1 0.27 vs
0.38). Do not treat this model as more accurate just because it fits
training data better; that is the exact memorization pattern documented in
04-12.
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
MODEL_PATH = MODEL_DIR / "modelo_referencia_con_institucion.joblib"
METADATA_PATH = MODEL_DIR / "modelo_referencia_con_institucion_metadata.json"
INSTITUTIONS_PATH = MODEL_DIR / "instituciones.json"
REPORT = REPORT_DIR / "17_modelo_referencia_institucion.md"
REFERENCE_YEAR = 2024
# Same hyperparameters validated for scenario B in 10/12; scenario A was not
# separately tuned, since 09 already showed it is not the candidate to ship.
FOREST_PARAMS = {
    "forest__n_estimators": 300,
    "forest__class_weight": "balanced",
}
# Out-of-fold performance from analysis 09, scenario A, default forest settings.
VALIDATED_MACRO_F1 = 0.2711
VALIDATED_BALANCED_ACCURACY = 0.3223


def load_preimputation_frame():
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
        ("forest", RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=-1)),
    ])
    pipeline.set_params(**FOREST_PARAMS)
    return pipeline, binary_cols, median_cols, nominal_cols, other_cat_cols


def main():
    raw = read_csv(RAW_DATA, dtype={"estu_semestrecursa": "string"})
    institutions = (
        raw[["inst_cod_institucion", "inst_nombre_institucion"]]
        .drop_duplicates()
        .sort_values("inst_nombre_institucion")
    )

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

    columns_full = list(working.columns)
    X = working[columns_full]

    model, binary_cols, median_cols, nominal_cols, other_cat_cols = build_pipeline(columns_full)
    model.fit(X, target)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    institutions.to_json(INSTITUTIONS_PATH, orient="records", force_ascii=False, indent=2)

    metadata = {
        "target": TARGET,
        "labels": list(LABELS),
        "reference_year_for_age": REFERENCE_YEAR,
        "feature_order": columns_full,
        "feature_roles": {
            "age_median_imputed": ["edad"],
            "binary_mode_imputed": binary_cols,
            "ordinal_numeric_median_imputed": median_cols,
            "nominal_text_constant_imputed": nominal_cols,
            "other_categorical_constant_imputed": other_cat_cols,
        },
        "hyperparameters": FOREST_PARAMS,
        "random_state": RANDOM_STATE,
        "training_rows": int(len(target)),
        "institutions_count": int(institutions.shape[0]),
        "validated_out_of_fold_performance": {
            "source": "analysis 09 (global imputation, institution-disjoint GroupKFold, scenario A)",
            "macro_f1": VALIDATED_MACRO_F1,
            "balanced_accuracy": VALIDATED_BALANCED_ACCURACY,
            "warning": "Worse unseen-institution generalization than scenario B (0.3786). "
                       "This model exists as a reference, not as the recommended predictor.",
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
        "# Reference model — scenario A, with institution", "",
        "Continuation of [16_interfaz_visual.md](16_interfaz_visual.md). Trains and persists "
        "scenario A (43 predictors, including `inst_cod_institucion`) purely as a side-by-side "
        "reference against the production model (scenario B, no institution).", "",
        "## Why this exists, and why it is NOT the recommended model", "",
        "Analysis [09](09_validacion_groupkfold.md) already measured this exact scenario on "
        "institution-disjoint folds: it generalizes worse to institutions never seen in "
        "training (macro F1 0.2711 vs. 0.3786 for scenario B). This model is kept only so the "
        "prediction tool can show, for the SAME student answers, how much the prediction shifts "
        "when institution identity is added — making the memorization risk visible rather than "
        "hidden.", "",
        "## Reproducible protocol", "", "```bash",
        ".venv/bin/python scripts_2021_2024/17_entrenar_modelo_referencia_institucion.py",
        "```", "",
        f"- Training rows: {len(target):,} (100% of the cleaned dataset, no holdout).",
        f"- Predictors: {len(columns_full)} (scenario A — includes `inst_cod_institucion`, "
        "`inst_origen`, `inst_caracter_academico`, and program/institution geography).",
        f"- Institutions in the dropdown list: {institutions.shape[0]}.",
        f"- Hyperparameters: {FOREST_PARAMS} (not separately tuned — see rationale above).",
        f"- Model file: `{MODEL_PATH.relative_to(ROOT)}`.",
        f"- Metadata file: `{METADATA_PATH.relative_to(ROOT)}`.",
        f"- Institution list file: `{INSTITUTIONS_PATH.relative_to(ROOT)}` "
        "(code + name, for populating a selector).",
        "", "## Expected real-world performance", "",
        "| Metric | Scenario A (this model) | Scenario B (production) |",
        "|---|---:|---:|",
        f"| Macro F1 | {VALIDATED_MACRO_F1:.4f} | 0.3786 |",
        f"| Balanced accuracy | {VALIDATED_BALANCED_ACCURACY:.4f} | 0.3924 |",
        "", "Both numbers come from out-of-fold, institution-disjoint validation — not from "
        "this script's own training fit, which would be optimistic for both scenarios.",
        "", "## Limitations", "",
        "- Predictions from this model for a NEW institution (not in the 55 seen during "
        "training) fall back to an 'unknown' category and should not be trusted more than "
        "scenario B's prediction for the same student.",
        "- This model is for comparison only; the dashboard and CLI should present it "
        "alongside scenario B, never alone.", "",
    ]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Trained on {len(target):,} rows, {len(columns_full)} predictors")
    print(f"Model written: {MODEL_PATH}")
    print(f"Institutions written: {INSTITUTIONS_PATH} ({institutions.shape[0]} rows)")
    print(f"Report written: {REPORT}")


if __name__ == "__main__":
    main()

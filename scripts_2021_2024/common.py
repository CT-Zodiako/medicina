"""Shared constants, CSV handling, and historical analysis 05–08 preprocessing.

Paths are relative to the repository, not the caller's working directory.
The holdout analyses deliberately retain the documented global imputation and
encoding protocol; they are exploratory reproduction, not leakage-free model
selection. Analysis 09 instead fits new encoders inside each training fold.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OrdinalEncoder

ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = ROOT / "dataset_medicina.csv"
PROCESSED_DATA = ROOT / "dataset_medicina_procesado.csv"
REPORT_DIR = ROOT / "docs_2021_2024"
CSV_SEPARATOR = ";"
CSV_ENCODING = "utf-8-sig"
TARGET = "nivel_desempeno"
DATE_COLUMN = "estu_fechanacimiento"
LABELS = (1, 2, 3, 4)
RANDOM_STATE = 42
TEST_SIZE = 0.2
EXPECTED_FEATURES = 43
DUPLICATE_COLUMNS = ("inst_nombre_institucion", "estu_snies_prgmacademico")
# Eighteen exclusions TOTAL: punt_global + 16 complete module fields + one score.
LEAKAGE_COLUMNS = (
    "mod_competen_ciudada_desem", "mod_competen_ciudada_pnal",
    "mod_competen_ciudada_pnbc", "mod_competen_ciudada_punt",
    "mod_comuni_escrita_desem", "mod_comuni_escrita_pnal",
    "mod_comuni_escrita_pnbc", "mod_comuni_escrita_punt",
    "mod_ingles_desem", "mod_ingles_pnal", "mod_ingles_pnbc", "mod_ingles_punt",
    "mod_lectura_critica_desem", "mod_lectura_critica_pnal",
    "mod_lectura_critica_pnbc", "mod_lectura_critica_punt",
    "mod_razona_cuantitat_punt", "punt_global",
)
BINARY_COLUMNS = (
    "fami_tieneconsolavideojuegos", "fami_tienemotocicleta",
    "fami_tienehornomicroogas", "fami_tieneautomovil", "fami_tienelavadora",
    "fami_tienecomputador", "fami_tieneserviciotv", "fami_tieneinternet",
    "estu_pagomatriculabeca", "estu_pagomatriculacredito",
    "estu_pagomatriculapropio", "estu_pagomatriculapadres",
)


def read_csv(path, **kwargs):
    """Read semicolon CSVs and consume the UTF-8 byte-order mark."""
    return pd.read_csv(path, sep=CSV_SEPARATOR, encoding=CSV_ENCODING, **kwargs)


def write_dataset(frame, path):
    """Preserve the input CSV dialect and do not serialize the DataFrame index."""
    frame.to_csv(path, sep=CSV_SEPARATOR, encoding=CSV_ENCODING, index=False)


def load_features(frame=None):
    """Exclude leakage and optional duplicates without rewriting the dataset."""
    if frame is None:
        frame = read_csv(PROCESSED_DATA)
    required = {TARGET, DATE_COLUMN, *LEAKAGE_COLUMNS}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    excluded = {TARGET, *LEAKAGE_COLUMNS, *DUPLICATE_COLUMNS}
    features = frame.loc[:, [column for column in frame if column not in excluded]].copy()
    if features.shape[1] != EXPECTED_FEATURES:
        raise ValueError(f"Expected {EXPECTED_FEATURES} predictors, got {features.shape[1]}")
    if any(column.startswith("mod_") for column in features):
        raise ValueError("Unexpected module-derived predictor; inspect leakage exclusions")
    target = pd.to_numeric(frame[TARGET], errors="raise")
    if target.isna().any() or set(target.unique()) != set(LABELS):
        raise ValueError("Expected complete target with levels 1–4")
    if features.isna().any().any():
        raise ValueError("Missing predictor values; run analysis 03 before modeling")
    return features, target.astype("int64")


def encode_features(features):
    """Encode all non-date columns as discrete categories, retaining column order.

    The date is converted explicitly to seconds since the Unix epoch. Using a
    timedelta avoids datetime storage-unit differences across pandas versions.
    Numeric ordinal/code columns also pass through OrdinalEncoder, as in 05.
    """
    encoded = pd.DataFrame(index=features.index, columns=features.columns, dtype=float)
    dates = pd.to_datetime(features[DATE_COLUMN], format="%d/%m/%Y", errors="raise")
    if dates.isna().any():
        raise ValueError("Missing birth dates; run analysis 03 first")
    encoded[DATE_COLUMN] = (dates - pd.Timestamp("1970-01-01")).dt.total_seconds()
    categorical = [column for column in features if column != DATE_COLUMN]
    encoder = OrdinalEncoder()
    encoded[categorical] = encoder.fit_transform(features[categorical])
    if not np.isfinite(encoded.to_numpy()).all():
        raise ValueError("Encoded predictors must be finite")
    return encoded


def fit_holdout_forest(n_estimators=300, max_depth=None):
    """Recreate the same stratified 80/20 holdout for analyses 06, 07, and 08."""
    features, target = load_features()
    encoded = encode_features(features)
    X_train, X_test, y_train, y_test = train_test_split(
        encoded, target, test_size=TEST_SIZE, stratify=target, random_state=RANDOM_STATE,
    )
    model = RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth, class_weight="balanced",
        random_state=RANDOM_STATE, n_jobs=-1,
    )
    model.fit(X_train, y_train)
    print(f"Predictors: {encoded.shape[1]}; train rows: {len(X_train)}; test rows: {len(X_test)}")
    return model, X_test, y_test


def print_metrics(model, features, target):
    """Print accuracy, macro F1, and per-class holdout metrics."""
    predicted = model.predict(features)
    print(f"Accuracy: {accuracy_score(target, predicted):.6f}")
    print(f"Macro F1: {f1_score(target, predicted, labels=LABELS, average='macro', zero_division=0):.6f}")
    print(classification_report(target, predicted, labels=LABELS, digits=4, zero_division=0))


def save_report(report, score_column, output):
    """Print and save an aggregate ranking, keeping original order for ties."""
    report = report.sort_values(score_column, ascending=False, kind="stable")
    output.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output, index=False, encoding=CSV_ENCODING)
    print(report.to_string(index=False))
    print(f"Report written: {output}")


def main():
    """Explain the helper's role without loading or modifying datasets."""
    print("Shared helpers only. Run the numbered scripts in order: 01, 02, 03, 05–09.")


if __name__ == "__main__":
    main()

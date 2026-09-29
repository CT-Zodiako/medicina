"""Apply documented full-dataset imputation and remove unusable birth dates.

Run after 02: .venv/bin/python scripts_2021_2024/03_imputacion_datos.py
Overwrites the processed CSV only. Full-dataset imputation intentionally
reproduces analysis 03; later holdout scores are not preprocessing-leakage-free.
"""

import pandas as pd

from common import BINARY_COLUMNS, DATE_COLUMN, PROCESSED_DATA, read_csv, write_dataset

MEDIAN_COLUMNS = (
    "fami_cuantoscompartebaño", "estu_horassemanatrabaja", "fami_estratovivienda",
    "fami_educacionmadre", "fami_educacionpadre", "estu_semestrecursa",
    "mod_comuni_escrita_desem", "estu_nse_individual", "mod_ingles_desem",
    "mod_ingles_punt", "mod_ingles_pnal", "mod_ingles_pnbc",
)
NOMINAL_COLUMNS = (
    "fami_ocupacionmadre", "fami_ocupacionpadre", "estu_tituloobtenidobachiller",
)
MISSING_CATEGORY = "Sin dato"
CORRUPT_DATE_PATTERN = r"#{3,}"


def impute(frame):
    """Calculate modes/medians before removing the four documented date rows."""
    frame = frame.copy()
    for column in (*BINARY_COLUMNS, *MEDIAN_COLUMNS):
        values = pd.to_numeric(frame[column], errors="raise")
        if values.notna().sum() == 0:
            raise ValueError(f"Cannot impute entirely missing column: {column}")
        value = values.mode().iloc[0] if column in BINARY_COLUMNS else values.median()
        print(f"{column}: fill={value:g}, missing={int(values.isna().sum())}")
        frame[column] = values.fillna(value)
    for column in NOMINAL_COLUMNS:
        print(f"{column}: fill={MISSING_CATEGORY}, missing={int(frame[column].isna().sum())}")
        frame[column] = frame[column].fillna(MISSING_CATEGORY)
    dates = frame[DATE_COLUMN].astype("string")
    missing = dates.isna()
    corrupt = dates.str.contains(CORRUPT_DATE_PATTERN, regex=True, na=False)
    print(f"Dropped null birth dates: {int(missing.sum())}")
    print(f"Dropped corrupted birth dates: {int(corrupt.sum())}")
    frame = frame.loc[~(missing | corrupt)].copy()
    # Reject other date problems rather than silently dropping extra records.
    pd.to_datetime(frame[DATE_COLUMN], format="%d/%m/%Y", errors="raise")
    remaining = frame.isna().sum()
    if remaining.any():
        raise ValueError(f"Unexpected remaining missing values:\n{remaining[remaining.gt(0)]}")
    return frame


def main():
    """Impute the working CSV and report aggregate changes."""
    result = impute(read_csv(PROCESSED_DATA))
    write_dataset(result, PROCESSED_DATA)
    print(f"Output shape: {result.shape}; missing cells: 0")
    print(f"Dataset written: {PROCESSED_DATA}")


if __name__ == "__main__":
    main()

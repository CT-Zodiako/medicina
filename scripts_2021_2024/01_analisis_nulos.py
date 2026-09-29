"""Report row counts and missing percentages by year for the current raw CSV.

Run: .venv/bin/python scripts_2021_2024/01_analisis_nulos.py
The report reflects the file as it exists now, not its historical null pattern.
"""

import pandas as pd

from common import RAW_DATA, REPORT_DIR, read_csv

YEARS = (2021, 2022, 2023, 2024)
OUTPUT = REPORT_DIR / "01_null_pct_by_year.csv"


def main():
    """Print aggregate coverage and save column-level missing percentages."""
    frame = read_csv(RAW_DATA)
    year = pd.to_numeric(frame["periodo"].astype(str).str[:4], errors="raise")
    if year.isna().any() or not year.isin(YEARS).all():
        raise ValueError("Expected complete periodo values for 2021–2024")
    counts = year.value_counts().reindex(YEARS, fill_value=0).rename("rows")
    counts.index.name = "year"
    report = pd.DataFrame({
        str(value): frame.loc[year.eq(value)].isna().mean().mul(100)
        for value in YEARS
    })
    report["global"] = frame.isna().mean().mul(100)
    report.index.name = "column"
    print(counts.to_string())
    print(report.round(2).to_string())
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report.to_csv(OUTPUT, encoding="utf-8-sig")
    print(f"Report written: {OUTPUT}")


if __name__ == "__main__":
    main()

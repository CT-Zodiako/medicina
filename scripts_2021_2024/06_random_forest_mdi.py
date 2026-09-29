"""Fit the documented balanced forest and report holdout metrics and MDI.

Run after 03: .venv/bin/python scripts_2021_2024/06_random_forest_mdi.py
Uses the same deterministic preprocessing, split, and forest as analysis 07.
"""

import pandas as pd

from common import REPORT_DIR, fit_holdout_forest, print_metrics, save_report

OUTPUT = REPORT_DIR / "06_random_forest_mdi_results.csv"
N_ESTIMATORS = 300


def main():
    """Print accuracy, macro F1 and per-class metrics; save the MDI ranking."""
    model, X_test, y_test = fit_holdout_forest(n_estimators=N_ESTIMATORS)
    print_metrics(model, X_test, y_test)
    report = pd.DataFrame({"feature": X_test.columns, "mdi": model.feature_importances_})
    save_report(report, "mdi", OUTPUT)


if __name__ == "__main__":
    main()

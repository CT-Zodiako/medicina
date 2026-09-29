"""Measure holdout permutation importance using macro F1 and 15 repeats.

Run after 03: .venv/bin/python scripts_2021_2024/07_permutation_importance.py
Rebuilds the same deterministic forest/split as 06, so no saved model is needed.
The forest is fitted once, never refitted during permutations.
"""

import pandas as pd
from sklearn.inspection import permutation_importance

from common import RANDOM_STATE, REPORT_DIR, fit_holdout_forest, print_metrics, save_report

OUTPUT = REPORT_DIR / "07_permutation_importance_results.csv"
N_ESTIMATORS = 300
N_REPEATS = 15
SCORING = "f1_macro"


def main():
    """Save mean and population standard deviation of holdout score drops."""
    model, X_test, y_test = fit_holdout_forest(n_estimators=N_ESTIMATORS)
    print_metrics(model, X_test, y_test)
    result = permutation_importance(
        model, X_test, y_test, scoring=SCORING, n_repeats=N_REPEATS,
        random_state=RANDOM_STATE, n_jobs=1,
    )
    report = pd.DataFrame({
        "feature": X_test.columns,
        "importance_mean": result.importances_mean,
        "importance_std": result.importances_std,
    })
    save_report(report, "importance_mean", OUTPUT)


if __name__ == "__main__":
    main()

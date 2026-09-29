"""Rank the documented 43 predictors using univariate mutual information.

Run after 03: .venv/bin/python scripts_2021_2024/05_mutual_information.py
Institution/program duplicates are excluded in memory, not from the CSV.
"""

import pandas as pd
from sklearn.feature_selection import mutual_info_classif

from common import DATE_COLUMN, RANDOM_STATE, REPORT_DIR, encode_features, load_features, save_report

OUTPUT = REPORT_DIR / "05_mutual_information_results.csv"
N_NEIGHBORS = 3


def main():
    """Treat only epoch birth dates as continuous; all other fields are discrete."""
    features, target = load_features()
    encoded = encode_features(features)
    information = mutual_info_classif(
        encoded, target,
        discrete_features=encoded.columns != DATE_COLUMN,
        n_neighbors=N_NEIGHBORS, random_state=RANDOM_STATE,
    )
    report = pd.DataFrame({"feature": encoded.columns, "mutual_information": information})
    save_report(report, "mutual_information", OUTPUT)


if __name__ == "__main__":
    main()

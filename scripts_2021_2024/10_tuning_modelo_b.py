"""Hyperparameter search for scenario B (no institution/geography features).

Run after 03: .venv/bin/python scripts_2021_2024/10_tuning_modelo_b.py
Writes docs_2021_2024/10_tuning_modelo_b.md. Uses the same institution-disjoint
GroupKFold protocol as analysis 09, scoring on macro F1. Only scenario B is
tuned here: scenario A already showed worse unseen-institution generalization
in 09 and is not a candidate for production tuning.
"""

import hashlib
import platform

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.model_selection import GroupKFold, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from common import (
    DATE_COLUMN, LABELS, PROCESSED_DATA, RANDOM_STATE, REPORT_DIR,
    load_features, read_csv,
)

REPORT = REPORT_DIR / "10_tuning_modelo_b.md"
GROUP = "inst_cod_institucion"
N_SPLITS = 5
N_ITER = 15
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
PARAM_DISTRIBUTIONS = {
    "forest__n_estimators": [200, 300, 400, 600],
    "forest__max_depth": [None, 8, 12, 16, 24],
    "forest__min_samples_leaf": [1, 2, 5, 10, 20],
    "forest__min_samples_split": [2, 5, 10, 20],
    "forest__max_features": ["sqrt", "log2", 0.3, 0.5],
}
# Baseline from analysis 09, scenario B, default RandomForestClassifier settings.
BASELINE_MACRO_F1 = 0.3721
BASELINE_BALANCED_ACCURACY = 0.3759


def build_pipeline(columns):
    """Fresh train-only preprocessing plus a balanced forest, same shape as 09."""
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
            class_weight="balanced", random_state=RANDOM_STATE, n_jobs=1,
        )),
    ])


def main():
    """Search scenario-B hyperparameters under institution-disjoint folds."""
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
    columns_b = [c for c in X.columns if c not in EXCLUDED_B]
    for column in columns_b:
        if column != "edad":
            X[column] = X[column].map(lambda value: str(value) if pd.notna(value) else np.nan)

    folds = list(GroupKFold(n_splits=N_SPLITS).split(X[columns_b], y, groups))

    search = RandomizedSearchCV(
        estimator=build_pipeline(columns_b),
        param_distributions=PARAM_DISTRIBUTIONS,
        n_iter=N_ITER,
        scoring="f1_macro",
        cv=folds,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        refit=True,
    )
    search.fit(X[columns_b], y)

    oof = np.empty(len(y), dtype=int)
    for train, test in folds:
        model = build_pipeline(columns_b)
        model.set_params(**search.best_params_)
        model.fit(X.iloc[train][columns_b], y.iloc[train])
        oof[test] = model.predict(X.iloc[test][columns_b])
    tuned_macro_f1 = f1_score(y, oof, labels=LABELS, average="macro", zero_division=0)
    tuned_balanced_accuracy = balanced_accuracy_score(y, oof)

    cv_results = pd.DataFrame(search.cv_results_)
    ranked = cv_results.sort_values("rank_test_score")[
        ["rank_test_score", "mean_test_score", "std_test_score", "params"]
    ]

    lines = [
        "# Hyperparameter tuning — scenario B", "",
        "Continuation of [09_validacion_groupkfold.md](09_validacion_groupkfold.md). "
        "Tunes only scenario B (no institution/geography features), which showed "
        "better unseen-institution generalization in 09.", "",
        "## Reproducible protocol", "", "```bash",
        ".venv/bin/python scripts_2021_2024/10_tuning_modelo_b.py", "```", "",
        f"- Input: {len(frame):,} rows, {len(frame.columns)} columns, {groups.nunique()} institutions.",
        f"- CSV SHA-256: `{hashlib.sha256(PROCESSED_DATA.read_bytes()).hexdigest()}`.",
        f"- Environment: Python {platform.python_version()}, pandas {pd.__version__}, "
        f"NumPy {np.__version__}, scikit-learn {sklearn.__version__}.",
        f"- Same 5 institution-disjoint GroupKFold folds as analysis 09 (groups={GROUP}), "
        f"regenerated identically here (same split call, same random state is not applicable "
        "to GroupKFold, which has no shuffle).",
        f"- Scenario B predictors: {len(columns_b)} (excludes institution identity, "
        "institutional attributes, and explicit geography — see 09 for the exact list).",
        f"- Search: RandomizedSearchCV, n_iter={N_ITER}, scoring='f1_macro', "
        f"random_state={RANDOM_STATE}, refit=True.",
        "- Preprocessing (median age imputation, constant-fill + OrdinalEncoder for the "
        "rest) is refit inside each training fold via the same Pipeline used in 09.",
        f"- Baseline for comparison: analysis 09 scenario B pooled OOF, default forest "
        f"settings — macro F1={BASELINE_MACRO_F1:.4f}, balanced accuracy={BASELINE_BALANCED_ACCURACY:.4f}.",
        "", "## Best parameters found", "",
        "| Parameter | Value |", "|---|---|",
    ]
    for key, value in search.best_params_.items():
        lines.append(f"| `{key}` | {value} |")
    delta_f1 = tuned_macro_f1 - BASELINE_MACRO_F1
    delta_ba = tuned_balanced_accuracy - BASELINE_BALANCED_ACCURACY
    lines += [
        "", "## Tuned pooled out-of-fold performance", "",
        "| Metric | Baseline (09, defaults) | Tuned | Delta |",
        "|---|---:|---:|---:|",
        f"| Macro F1 | {BASELINE_MACRO_F1:.4f} | {tuned_macro_f1:.4f} | {delta_f1:+.4f} |",
        f"| Balanced accuracy | {BASELINE_BALANCED_ACCURACY:.4f} | {tuned_balanced_accuracy:.4f} | {delta_ba:+.4f} |",
        "", "## Full search results (ranked by mean CV macro F1)", "",
        "| Rank | Mean F1 macro | Std | Params |", "|---:|---:|---:|---|",
    ]
    for _, row in ranked.iterrows():
        lines.append(f"| {int(row['rank_test_score'])} | {row['mean_test_score']:.4f} | "
                     f"{row['std_test_score']:.4f} | {row['params']} |")
    lines += [
        "", "## Interpretation and limitations", "",
        "- The search optimizes mean macro F1 across the same 5 institution-disjoint "
        "folds used in 09; the reported tuned score is the pooled out-of-fold score "
        "using the single best parameter set across all folds, not five independently "
        "tuned models.",
        "- This is a bounded random search over a fixed grid (n_iter="
        f"{N_ITER}), not an exhaustive grid search; a different budget or search space "
        "could find different parameters.",
        "- The same prior-imputation leakage caveat from 09 applies: 03 imputed the "
        "full dataset before these folds existed.",
        "- No nested cross-validation was used to estimate generalization of the tuning "
        "process itself; the reported tuned metric may be mildly optimistic relative to "
        "a fully nested protocol.",
        "",
    ]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Best params: {search.best_params_}")
    print(f"Tuned pooled OOF macro F1: {tuned_macro_f1:.4f} (baseline {BASELINE_MACRO_F1:.4f}, "
          f"delta {delta_f1:+.4f})")
    print(f"Tuned pooled OOF balanced accuracy: {tuned_balanced_accuracy:.4f} "
          f"(baseline {BASELINE_BALANCED_ACCURACY:.4f}, delta {delta_ba:+.4f})")
    print(f"Report written: {REPORT}")


if __name__ == "__main__":
    main()

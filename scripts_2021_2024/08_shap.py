"""Run bounded multiclass SHAP and summarize the documented top 15 features.

Run after 03: .venv/bin/python scripts_2021_2024/08_shap.py
Fits all 43 predictors, as documented in 08; only the summary is restricted
to the 15 highest positive permutation importances published in 07.
"""

import numpy as np
import pandas as pd
import shap

from common import RANDOM_STATE, REPORT_DIR, fit_holdout_forest, print_metrics, save_report

OUTPUT = REPORT_DIR / "08_shap_summary.csv"
N_ESTIMATORS = 100
MAX_DEPTH = 18
SAMPLE_SIZE = 250
TOP_FEATURES = (
    "inst_cod_institucion", "estu_fechanacimiento", "inst_origen",
    "estu_horassemanatrabaja", "fami_estratovivienda", "estu_prgm_codmunicipio",
    "estu_prgm_departamento", "estu_prgm_municipio", "inst_caracter_academico",
    "periodo", "fami_educacionpadre", "estu_pagomatriculabeca",
    "estu_semestrecursa", "fami_ocupacionpadre", "estu_inst_departamento",
)


def main():
    """Save mean absolute SHAP by class and its class-averaged overall value."""
    model, X_test, y_test = fit_holdout_forest(
        n_estimators=N_ESTIMATORS, max_depth=MAX_DEPTH,
    )
    print_metrics(model, X_test, y_test)
    if len(X_test) < SAMPLE_SIZE:
        raise ValueError(f"Need at least {SAMPLE_SIZE} held-out records")
    sample = X_test.sample(n=SAMPLE_SIZE, random_state=RANDOM_STATE)
    explainer = shap.TreeExplainer(model, feature_perturbation="tree_path_dependent")
    values = explainer.shap_values(sample)
    # SHAP <0.45 returned one array per class; newer releases return a 3-D array.
    values = np.stack(values, axis=-1) if isinstance(values, list) else np.asarray(values)
    expected_shape = (SAMPLE_SIZE, X_test.shape[1], len(model.classes_))
    if values.shape != expected_shape:
        raise ValueError(f"Unexpected SHAP shape {values.shape}; expected {expected_shape}")
    summary = pd.DataFrame(
        np.abs(values).mean(axis=0), index=X_test.columns,
        columns=[f"nivel_{int(label)}" for label in model.classes_],
    ).loc[list(TOP_FEATURES)]
    summary["overall"] = summary.mean(axis=1)
    summary.index.name = "feature"
    save_report(summary.reset_index(), "overall", OUTPUT)


if __name__ == "__main__":
    main()

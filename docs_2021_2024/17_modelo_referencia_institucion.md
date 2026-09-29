# Reference model — scenario A, with institution

Continuation of [16_interfaz_visual.md](16_interfaz_visual.md). Trains and persists scenario A (43 predictors, including `inst_cod_institucion`) purely as a side-by-side reference against the production model (scenario B, no institution).

## Why this exists, and why it is NOT the recommended model

Analysis [09](09_validacion_groupkfold.md) already measured this exact scenario on institution-disjoint folds: it generalizes worse to institutions never seen in training (macro F1 0.2711 vs. 0.3786 for scenario B). This model is kept only so the prediction tool can show, for the SAME student answers, how much the prediction shifts when institution identity is added — making the memorization risk visible rather than hidden.

## Reproducible protocol

```bash
.venv/bin/python scripts_2021_2024/17_entrenar_modelo_referencia_institucion.py
```

- Training rows: 30,738 (100% of the cleaned dataset, no holdout).
- Predictors: 43 (scenario A — includes `inst_cod_institucion`, `inst_origen`, `inst_caracter_academico`, and program/institution geography).
- Institutions in the dropdown list: 55.
- Hyperparameters: {'forest__n_estimators': 300, 'forest__class_weight': 'balanced'} (not separately tuned — see rationale above).
- Model file: `modelos_2021_2024/modelo_referencia_con_institucion.joblib`.
- Metadata file: `modelos_2021_2024/modelo_referencia_con_institucion_metadata.json`.
- Institution list file: `modelos_2021_2024/instituciones.json` (code + name, for populating a selector).

## Expected real-world performance

| Metric | Scenario A (this model) | Scenario B (production) |
|---|---:|---:|
| Macro F1 | 0.2711 | 0.3786 |
| Balanced accuracy | 0.3223 | 0.3924 |

Both numbers come from out-of-fold, institution-disjoint validation — not from this script's own training fit, which would be optimistic for both scenarios.

## Limitations

- Predictions from this model for a NEW institution (not in the 55 seen during training) fall back to an 'unknown' category and should not be trusted more than scenario B's prediction for the same student.
- This model is for comparison only; the dashboard and CLI should present it alongside scenario B, never alone.

# Final model training — scenario B, 100% of data

Continuation of [13_explicacion_modelo_y_datos_faltantes.md](13_explicacion_modelo_y_datos_faltantes.md). Persists a reusable model for predicting `nivel_desempeno` for students who have not taken the exam, since none of its inputs are exam-derived.

## Reproducible protocol

```bash
.venv/bin/python scripts_2021_2024/14_entrenar_modelo_final.py
```

- Training rows: 30,738 (100% of the cleaned dataset, no holdout — this is the final artifact, not a generalization test).
- Class distribution: {1: 2607, 2: 8204, 3: 15160, 4: 4767}.
- Predictors: 27 (scenario B — no institution or geography fields).
- Hyperparameters: best parameters found in analysis 10 — {'forest__n_estimators': 600, 'forest__min_samples_split': 5, 'forest__min_samples_leaf': 1, 'forest__max_features': 'log2', 'forest__max_depth': None}.
- Model file: `modelos_2021_2024/modelo_final_nivel_desempeno.joblib`.
- Metadata file: `modelos_2021_2024/modelo_final_nivel_desempeno_metadata.json` (feature order, roles, validated performance).

## Expected real-world performance

This script's own training fit is **not** a valid performance estimate — it would be optimistic, since the model saw every row it was evaluated on. The honest expectation for new, unseen students comes from analysis 12's fold-local, institution-disjoint out-of-fold evaluation, using the same hyperparameters:

| Metric | Validated value |
|---|---:|
| Macro F1 | 0.3786 |
| Balanced accuracy | 0.3924 |

See [13](13_explicacion_modelo_y_datos_faltantes.md) for what this means in plain terms: usable for population-level tendencies, not reliable for individual decisions.

## Required inputs, in the exact order the model expects

| # | Field | Imputation role if missing |
|---:|---|---|
| 1 | `periodo` | constant '__MISSING__' |
| 2 | `estu_tipodocumento` | constant '__MISSING__' |
| 3 | `estu_agregado` | constant '__MISSING__' |
| 4 | `estu_genero` | constant '__MISSING__' |
| 5 | `estu_horassemanatrabaja` | median |
| 6 | `estu_nse_individual` | median |
| 7 | `estu_pagomatriculabeca` | mode (most frequent) |
| 8 | `estu_pagomatriculacredito` | mode (most frequent) |
| 9 | `estu_pagomatriculapadres` | mode (most frequent) |
| 10 | `estu_pagomatriculapropio` | mode (most frequent) |
| 11 | `estu_semestrecursa` | median |
| 12 | `estu_tituloobtenidobachiller` | constant 'Sin dato' |
| 13 | `fami_cuantoscompartebaño` | median |
| 14 | `fami_educacionmadre` | median |
| 15 | `fami_educacionpadre` | median |
| 16 | `fami_estratovivienda` | median |
| 17 | `fami_ocupacionmadre` | constant 'Sin dato' |
| 18 | `fami_ocupacionpadre` | constant 'Sin dato' |
| 19 | `fami_tieneautomovil` | mode (most frequent) |
| 20 | `fami_tienecomputador` | mode (most frequent) |
| 21 | `fami_tieneconsolavideojuegos` | mode (most frequent) |
| 22 | `fami_tienehornomicroogas` | mode (most frequent) |
| 23 | `fami_tieneinternet` | mode (most frequent) |
| 24 | `fami_tienelavadora` | mode (most frequent) |
| 25 | `fami_tienemotocicleta` | mode (most frequent) |
| 26 | `fami_tieneserviciotv` | mode (most frequent) |
| 27 | `edad` | median |

## Limitations

- This is a single fitted snapshot of `dataset_medicina.csv` as it exists today; retraining on updated data will change the artifact and should bump the metadata.
- Imputation defaults above are learned from this training set's distribution (e.g. `estu_pagomatriculapadres` mode = 1). New inference inputs with real values should be provided directly rather than relying on these defaults, which exist only to keep the pipeline robust to incomplete inputs.
- The model has not been used for individual decisions; see 13 for why.

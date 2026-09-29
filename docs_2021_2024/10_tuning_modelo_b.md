# Hyperparameter tuning — scenario B

Continuation of [09_validacion_groupkfold.md](09_validacion_groupkfold.md). Tunes only scenario B (no institution/geography features), which showed better unseen-institution generalization in 09.

## Reproducible protocol

```bash
.venv/bin/python scripts_2021_2024/10_tuning_modelo_b.py
```

- Input: 30,738 rows, 64 columns, 55 institutions.
- CSV SHA-256: `ebd5724d52a36b8fc14d974691080571ad363aae2e14d8bbde72903d3c2d0684`.
- Environment: Python 3.14.7, pandas 3.0.5, NumPy 2.5.3, scikit-learn 1.9.1.
- Same 5 institution-disjoint GroupKFold folds as analysis 09 (groups=inst_cod_institucion), regenerated identically here (same split call, same random state is not applicable to GroupKFold, which has no shuffle).
- Scenario B predictors: 27 (excludes institution identity, institutional attributes, and explicit geography — see 09 for the exact list).
- Search: RandomizedSearchCV, n_iter=15, scoring='f1_macro', random_state=42, refit=True.
- Preprocessing (median age imputation, constant-fill + OrdinalEncoder for the rest) is refit inside each training fold via the same Pipeline used in 09.
- Baseline for comparison: analysis 09 scenario B pooled OOF, default forest settings — macro F1=0.3721, balanced accuracy=0.3759.

## Best parameters found

| Parameter | Value |
|---|---|
| `forest__n_estimators` | 600 |
| `forest__min_samples_split` | 5 |
| `forest__min_samples_leaf` | 1 |
| `forest__max_features` | log2 |
| `forest__max_depth` | None |

## Tuned pooled out-of-fold performance

| Metric | Baseline (09, defaults) | Tuned | Delta |
|---|---:|---:|---:|
| Macro F1 | 0.3721 | 0.3787 | +0.0066 |
| Balanced accuracy | 0.3759 | 0.3930 | +0.0171 |

## Full search results (ranked by mean CV macro F1)

| Rank | Mean F1 macro | Std | Params |
|---:|---:|---:|---|
| 1 | 0.3765 | 0.0092 | {'forest__n_estimators': 600, 'forest__min_samples_split': 5, 'forest__min_samples_leaf': 1, 'forest__max_features': 'log2', 'forest__max_depth': None} |
| 2 | 0.3752 | 0.0075 | {'forest__n_estimators': 600, 'forest__min_samples_split': 2, 'forest__min_samples_leaf': 2, 'forest__max_features': 0.3, 'forest__max_depth': 24} |
| 3 | 0.3723 | 0.0058 | {'forest__n_estimators': 400, 'forest__min_samples_split': 5, 'forest__min_samples_leaf': 1, 'forest__max_features': 0.3, 'forest__max_depth': 16} |
| 4 | 0.3699 | 0.0056 | {'forest__n_estimators': 200, 'forest__min_samples_split': 5, 'forest__min_samples_leaf': 1, 'forest__max_features': 'log2', 'forest__max_depth': 16} |
| 5 | 0.3687 | 0.0056 | {'forest__n_estimators': 600, 'forest__min_samples_split': 2, 'forest__min_samples_leaf': 1, 'forest__max_features': 0.3, 'forest__max_depth': 16} |
| 6 | 0.3665 | 0.0078 | {'forest__n_estimators': 400, 'forest__min_samples_split': 10, 'forest__min_samples_leaf': 1, 'forest__max_features': 0.3, 'forest__max_depth': 16} |
| 7 | 0.3640 | 0.0052 | {'forest__n_estimators': 400, 'forest__min_samples_split': 10, 'forest__min_samples_leaf': 5, 'forest__max_features': 0.3, 'forest__max_depth': 24} |
| 8 | 0.3632 | 0.0085 | {'forest__n_estimators': 400, 'forest__min_samples_split': 20, 'forest__min_samples_leaf': 1, 'forest__max_features': 'sqrt', 'forest__max_depth': 24} |
| 9 | 0.3617 | 0.0048 | {'forest__n_estimators': 400, 'forest__min_samples_split': 5, 'forest__min_samples_leaf': 5, 'forest__max_features': 0.5, 'forest__max_depth': 16} |
| 10 | 0.3585 | 0.0061 | {'forest__n_estimators': 300, 'forest__min_samples_split': 10, 'forest__min_samples_leaf': 5, 'forest__max_features': 'log2', 'forest__max_depth': None} |
| 11 | 0.3582 | 0.0081 | {'forest__n_estimators': 200, 'forest__min_samples_split': 5, 'forest__min_samples_leaf': 5, 'forest__max_features': 'log2', 'forest__max_depth': 24} |
| 12 | 0.3414 | 0.0110 | {'forest__n_estimators': 600, 'forest__min_samples_split': 5, 'forest__min_samples_leaf': 10, 'forest__max_features': 'log2', 'forest__max_depth': 16} |
| 13 | 0.3360 | 0.0082 | {'forest__n_estimators': 200, 'forest__min_samples_split': 20, 'forest__min_samples_leaf': 10, 'forest__max_features': 0.3, 'forest__max_depth': 12} |
| 14 | 0.3118 | 0.0105 | {'forest__n_estimators': 400, 'forest__min_samples_split': 10, 'forest__min_samples_leaf': 1, 'forest__max_features': 'sqrt', 'forest__max_depth': 8} |
| 15 | 0.3078 | 0.0096 | {'forest__n_estimators': 400, 'forest__min_samples_split': 2, 'forest__min_samples_leaf': 20, 'forest__max_features': 'log2', 'forest__max_depth': 8} |

## Interpretation and limitations

- The search optimizes mean macro F1 across the same 5 institution-disjoint folds used in 09; the reported tuned score is the pooled out-of-fold score using the single best parameter set across all folds, not five independently tuned models.
- This is a bounded random search over a fixed grid (n_iter=15), not an exhaustive grid search; a different budget or search space could find different parameters.
- The same prior-imputation leakage caveat from 09 applies: 03 imputed the full dataset before these folds existed.
- No nested cross-validation was used to estimate generalization of the tuning process itself; the reported tuned metric may be mildly optimistic relative to a fully nested protocol.

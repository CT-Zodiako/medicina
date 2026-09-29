# Final scenario-B model — no preprocessing leakage

Continuation of [11_conclusion_importancia_variables.md](11_conclusion_importancia_variables.md). Fixes the preprocessing-leakage caveat from analyses 09 and 10: mode/median/constant imputers are now fit only on each fold's training rows.

## Reproducible protocol

```bash
.venv/bin/python scripts_2021_2024/12_modelo_final_sin_fuga.py
```

This script reads `dataset_medicina.csv` directly and reapplies analysis 02's deterministic transform; it does not read or write `dataset_medicina_procesado.csv`, and it does not run analysis 03's global imputation.

- Rows after dropping null/corrupted birth dates: 30,738 (dropped 2 null, 2 corrupted — same fixed row filter as 03).
- Institutions: 55.
- Environment: Python 3.14.7, pandas 3.0.5, NumPy 2.5.3, scikit-learn 1.9.1.
- Raw CSV SHA-256: `63feb36895735a73e7b2ff03a110db394b0796d06f06b72b3b005906da635eaa`.
- GroupKFold: 5 folds, no shuffle, groups=inst_cod_institucion.
- edad = 2024 - birth year, computed after dropping unusable dates (same as 09/10).
- Binary columns: most-frequent (mode) imputed per training fold, matching analysis 03's rule.
- Ordinal/continuous columns: median imputed per training fold, matching analysis 03's rule.
- Nominal columns (`fami_ocupacionmadre`, `fami_ocupacionpadre`, `estu_tituloobtenidobachiller`): constant-filled with `"Sin dato"` per training fold, matching analysis 03's rule.
- Remaining always-complete categorical columns: constant-filled as a safety net, then `OrdinalEncoder` fit only on the training fold; unseen categories map to -1.
- Forest hyperparameters: best parameters found in analysis 10 — {'forest__n_estimators': 600, 'forest__min_samples_split': 5, 'forest__min_samples_leaf': 1, 'forest__max_features': 'log2', 'forest__max_depth': None}.
- Scenario B predictors: 27 (same 27-field exclusion as 09/10).
- Baseline for comparison: analysis 10 tuned scenario B, global imputation — macro F1=0.3787, balanced accuracy=0.3930.

## Fold results

| Fold | Macro F1 | Balanced accuracy |
|---|---:|---:|
| 1 | 0.3677 | 0.3734 |
| 2 | 0.3902 | 0.4143 |
| 3 | 0.3767 | 0.3866 |
| 4 | 0.3758 | 0.3941 |
| 5 | 0.3719 | 0.3891 |
| Unweighted mean | 0.3765 | 0.3915 |
| Sample standard deviation (ddof=1) | 0.0085 | 0.0149 |
| Pooled OOF | 0.3786 | 0.3924 |

## Comparison against the leaky baseline

| Metric | Baseline (10, global imputation) | This run (fold-local) | Delta |
|---|---:|---:|---:|
| Macro F1 | 0.3787 | 0.3786 | -0.0001 |
| Balanced accuracy | 0.3930 | 0.3924 | -0.0006 |

### Pooled OOF metrics

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.2211 | 0.1772 | 0.1967 | 2607 |
| 2 | 0.3900 | 0.4844 | 0.4321 | 8204 |
| 3 | 0.5557 | 0.4356 | 0.4884 | 15160 |
| 4 | 0.3426 | 0.4724 | 0.3971 | 4767 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 462 | 1335 | 669 | 141 |
| 2 | 772 | 3974 | 2738 | 720 |
| 3 | 741 | 4354 | 6604 | 3461 |
| 4 | 115 | 527 | 1873 | 2252 |

### Fold 1

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.2401 | 0.1923 | 0.2136 | 598 |
| 2 | 0.3822 | 0.5365 | 0.4464 | 1741 |
| 3 | 0.5299 | 0.4174 | 0.4670 | 2844 |
| 4 | 0.3403 | 0.3475 | 0.3439 | 938 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 115 | 324 | 131 | 28 |
| 2 | 170 | 934 | 506 | 131 |
| 3 | 162 | 1022 | 1187 | 473 |
| 4 | 32 | 164 | 416 | 326 |

### Fold 2

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.3144 | 0.1768 | 0.2263 | 594 |
| 2 | 0.4107 | 0.4900 | 0.4469 | 1798 |
| 3 | 0.5589 | 0.4406 | 0.4928 | 3016 |
| 4 | 0.3081 | 0.5499 | 0.3949 | 702 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 105 | 302 | 153 | 34 |
| 2 | 113 | 881 | 647 | 157 |
| 3 | 108 | 903 | 1329 | 676 |
| 4 | 8 | 59 | 249 | 386 |

### Fold 3

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.1945 | 0.1762 | 0.1849 | 522 |
| 2 | 0.4100 | 0.4576 | 0.4325 | 1617 |
| 3 | 0.5411 | 0.4532 | 0.4933 | 2961 |
| 4 | 0.3480 | 0.4593 | 0.3960 | 1069 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 92 | 265 | 143 | 22 |
| 2 | 183 | 740 | 549 | 145 |
| 3 | 165 | 701 | 1342 | 753 |
| 4 | 33 | 99 | 446 | 491 |

### Fold 4

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.1855 | 0.1715 | 0.1783 | 478 |
| 2 | 0.3973 | 0.4955 | 0.4410 | 1760 |
| 3 | 0.5655 | 0.4262 | 0.4861 | 3090 |
| 4 | 0.3380 | 0.4834 | 0.3978 | 842 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 82 | 253 | 121 | 22 |
| 2 | 186 | 872 | 563 | 139 |
| 3 | 157 | 980 | 1317 | 636 |
| 4 | 17 | 90 | 328 | 407 |

### Fold 5

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.1878 | 0.1639 | 0.1750 | 415 |
| 2 | 0.3417 | 0.4247 | 0.3787 | 1288 |
| 3 | 0.5816 | 0.4398 | 0.5009 | 3249 |
| 4 | 0.3673 | 0.5280 | 0.4332 | 1216 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 68 | 191 | 121 | 35 |
| 2 | 120 | 547 | 473 | 148 |
| 3 | 149 | 748 | 1429 | 923 |
| 4 | 25 | 115 | 434 | 642 |

## Interpretation and limitations

- If the delta above is small, it confirms the global-imputation leakage in 09/10 had little practical effect on this dataset (a handful of percent missing per column). It does not mean leakage is acceptable practice — it means this leakage was mild here.
- Row-level date filtering remains a global step, applied before any split. It is a fixed, deterministic filter, not a distribution-derived statistic, so it does not leak test-fold information into training.
- Hyperparameters are fixed to analysis 10's best parameters, not re-tuned inside this leakage-free protocol; a fully rigorous pipeline would re-run tuning with fold-local imputation from the start (nested cross-validation).
- No causal claims, temporal validation, or repeated-seed stability checks.

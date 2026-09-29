# Unseen-institution validation — GroupKFold

Continuation of [08_shap.md](08_shap.md). This tests institutional, not temporal, generalization.

## Reproducible protocol

```bash
.venv/bin/python scripts_2021_2024/09_validacion_groupkfold.py
```

- Input: 30,738 rows, 64 columns, 55 institutions; no rows removed.
- CSV SHA-256: `ebd5724d52a36b8fc14d974691080571ad363aae2e14d8bbde72903d3c2d0684`.
- Environment: Python 3.14.7, pandas 3.0.5, NumPy 2.5.3, scikit-learn 1.9.1.
- Target: nivel_desempeno (1–4). GroupKFold: 5 folds, no shuffle, groups=inst_cod_institucion; identical folds for A/B.
- Random forest: 300 trees, class_weight='balanced', random_state=42, n_jobs=-1; other defaults unchanged.
- edad = 2024 - birth year; approximate age at the end of 2024, not age at examination. Replaces the birth date.
- Dates use day/month/year and ages must fall in 0–120; invalid dates raise errors.
- All other features, including numeric codes, are string categories. OrdinalEncoder is fitted only on each training fold; unseen categories map to -1.
- Constant categorical and median age imputers are fitted inside each training pipeline; a fresh model is created per fold.
- Institution separation, all four classes, and exactly one OOF prediction per row are checked.

## Variables and exclusions

A uses 43 features; B removes 16 institutional/geographic fields and uses 27.
Duplicate institution name/program code fields are excluded in memory if present.

B exclusions:

- `inst_cod_institucion`
- `inst_origen`
- `inst_caracter_academico`
- `estu_prgm_codmunicipio`
- `estu_prgm_municipio`
- `estu_prgm_departamento`
- `estu_inst_codmunicipio`
- `estu_inst_municipio`
- `estu_inst_departamento`
- `estu_cod_mcpio_presentacion`
- `estu_mcpio_presentacion`
- `estu_cod_depto_presentacion`
- `estu_depto_presentacion`
- `estu_nacionalidad`
- `estu_pais_reside`
- `estu_exterior`

Common leakage exclusions (18 total, including punt_global):

- `mod_competen_ciudada_desem`
- `mod_competen_ciudada_pnal`
- `mod_competen_ciudada_pnbc`
- `mod_competen_ciudada_punt`
- `mod_comuni_escrita_desem`
- `mod_comuni_escrita_pnal`
- `mod_comuni_escrita_pnbc`
- `mod_comuni_escrita_punt`
- `mod_ingles_desem`
- `mod_ingles_pnal`
- `mod_ingles_pnbc`
- `mod_ingles_punt`
- `mod_lectura_critica_desem`
- `mod_lectura_critica_pnal`
- `mod_lectura_critica_pnbc`
- `mod_lectura_critica_punt`
- `mod_razona_cuantitat_punt`
- `punt_global`

Scenario A predictors:

- `periodo`
- `estu_tipodocumento`
- `estu_nacionalidad`
- `estu_agregado`
- `estu_cod_depto_presentacion`
- `estu_cod_mcpio_presentacion`
- `estu_depto_presentacion`
- `estu_exterior`
- `estu_genero`
- `estu_horassemanatrabaja`
- `estu_inst_codmunicipio`
- `estu_inst_departamento`
- `estu_inst_municipio`
- `estu_mcpio_presentacion`
- `estu_nse_individual`
- `estu_pagomatriculabeca`
- `estu_pagomatriculacredito`
- `estu_pagomatriculapadres`
- `estu_pagomatriculapropio`
- `estu_pais_reside`
- `estu_prgm_codmunicipio`
- `estu_prgm_departamento`
- `estu_prgm_municipio`
- `estu_semestrecursa`
- `estu_tituloobtenidobachiller`
- `fami_cuantoscompartebaño`
- `fami_educacionmadre`
- `fami_educacionpadre`
- `fami_estratovivienda`
- `fami_ocupacionmadre`
- `fami_ocupacionpadre`
- `fami_tieneautomovil`
- `fami_tienecomputador`
- `fami_tieneconsolavideojuegos`
- `fami_tienehornomicroogas`
- `fami_tieneinternet`
- `fami_tienelavadora`
- `fami_tienemotocicleta`
- `fami_tieneserviciotv`
- `inst_caracter_academico`
- `inst_cod_institucion`
- `inst_origen`
- `edad`

## Fold composition

| Fold | Train rows | Test rows | Train institutions | Test institutions | Test n1/n2/n3/n4 |
|---|---:|---:|---:|---:|---|
| 1 | 24617 | 6121 | 45 | 10 | 598 / 1741 / 2844 / 938 |
| 2 | 24628 | 6110 | 43 | 12 | 594 / 1798 / 3016 / 702 |
| 3 | 24569 | 6169 | 44 | 11 | 522 / 1617 / 2961 / 1069 |
| 4 | 24568 | 6170 | 44 | 11 | 478 / 1760 / 3090 / 842 |
| 5 | 24570 | 6168 | 44 | 11 | 415 / 1288 / 3249 / 1216 |

## Scenario A: 43 predictors

| Fold | Macro F1 | Balanced accuracy |
|---|---:|---:|
| 1 | 0.3319 | 0.3427 |
| 2 | 0.2600 | 0.3621 |
| 3 | 0.2203 | 0.2790 |
| 4 | 0.2423 | 0.2934 |
| 5 | 0.2755 | 0.3339 |
| Unweighted mean | 0.2660 | 0.3222 |
| Sample standard deviation (ddof=1) | 0.0422 | 0.0348 |
| Pooled OOF | 0.2711 | 0.3223 |

### Pooled OOF metrics

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.3699 | 0.0207 | 0.0392 | 2607 |
| 2 | 0.4641 | 0.0772 | 0.1323 | 8204 |
| 3 | 0.4742 | 0.6049 | 0.5316 | 15160 |
| 4 | 0.2826 | 0.5863 | 0.3814 | 4767 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 54 | 292 | 2001 | 260 |
| 2 | 63 | 633 | 6216 | 1292 |
| 3 | 27 | 419 | 9170 | 5544 |
| 4 | 2 | 20 | 1950 | 2795 |

### Fold 1

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.4167 | 0.0418 | 0.0760 | 598 |
| 2 | 0.4755 | 0.1953 | 0.2769 | 1741 |
| 3 | 0.4926 | 0.7757 | 0.6026 | 2844 |
| 4 | 0.3871 | 0.3582 | 0.3721 | 938 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 25 | 145 | 408 | 20 |
| 2 | 25 | 340 | 1272 | 104 |
| 3 | 9 | 221 | 2206 | 408 |
| 4 | 1 | 9 | 592 | 336 |

### Fold 2

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.4444 | 0.0202 | 0.0386 | 594 |
| 2 | 0.4459 | 0.0367 | 0.0678 | 1798 |
| 3 | 0.4518 | 0.5952 | 0.5137 | 3016 |
| 4 | 0.2849 | 0.7963 | 0.4197 | 702 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 12 | 29 | 514 | 39 |
| 2 | 11 | 66 | 1521 | 200 |
| 3 | 4 | 53 | 1795 | 1164 |
| 4 | 0 | 0 | 143 | 559 |

### Fold 3

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.2222 | 0.0077 | 0.0148 | 522 |
| 2 | 0.5185 | 0.0260 | 0.0495 | 1617 |
| 3 | 0.4414 | 0.5427 | 0.4868 | 2961 |
| 4 | 0.2375 | 0.5398 | 0.3299 | 1069 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 4 | 21 | 398 | 99 |
| 2 | 9 | 42 | 1145 | 421 |
| 3 | 5 | 17 | 1607 | 1332 |
| 4 | 0 | 1 | 491 | 577 |

### Fold 4

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.1538 | 0.0042 | 0.0081 | 478 |
| 2 | 0.4498 | 0.0636 | 0.1115 | 1760 |
| 3 | 0.4757 | 0.6427 | 0.5467 | 3090 |
| 4 | 0.2250 | 0.4632 | 0.3029 | 842 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 2 | 50 | 382 | 44 |
| 2 | 4 | 112 | 1364 | 280 |
| 3 | 7 | 78 | 1986 | 1019 |
| 4 | 0 | 9 | 443 | 390 |

### Fold 5

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.3929 | 0.0265 | 0.0497 | 415 |
| 2 | 0.4269 | 0.0567 | 0.1001 | 1288 |
| 3 | 0.5134 | 0.4851 | 0.4988 | 3249 |
| 4 | 0.3218 | 0.7673 | 0.4535 | 1216 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 11 | 47 | 299 | 58 |
| 2 | 14 | 73 | 914 | 287 |
| 3 | 2 | 50 | 1576 | 1621 |
| 4 | 1 | 1 | 281 | 933 |

## Scenario B: 27 predictors

| Fold | Macro F1 | Balanced accuracy |
|---|---:|---:|
| 1 | 0.3638 | 0.3634 |
| 2 | 0.3786 | 0.3911 |
| 3 | 0.3644 | 0.3658 |
| 4 | 0.3737 | 0.3793 |
| 5 | 0.3707 | 0.3764 |
| Unweighted mean | 0.3703 | 0.3752 |
| Sample standard deviation (ddof=1) | 0.0063 | 0.0112 |
| Pooled OOF | 0.3721 | 0.3759 |

### Pooled OOF metrics

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.2284 | 0.1158 | 0.1537 | 2607 |
| 2 | 0.3921 | 0.4798 | 0.4316 | 8204 |
| 3 | 0.5504 | 0.5068 | 0.5277 | 15160 |
| 4 | 0.3528 | 0.4011 | 0.3754 | 4767 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 302 | 1351 | 840 | 114 |
| 2 | 493 | 3936 | 3196 | 579 |
| 3 | 451 | 4212 | 7683 | 2814 |
| 4 | 76 | 538 | 2241 | 1912 |

### Fold 1

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.2544 | 0.1221 | 0.1650 | 598 |
| 2 | 0.3884 | 0.5325 | 0.4491 | 1741 |
| 3 | 0.5351 | 0.4986 | 0.5162 | 2844 |
| 4 | 0.3538 | 0.3006 | 0.3251 | 938 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 73 | 332 | 173 | 20 |
| 2 | 111 | 927 | 587 | 116 |
| 3 | 84 | 963 | 1418 | 379 |
| 4 | 19 | 165 | 472 | 282 |

### Fold 2

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.3057 | 0.1178 | 0.1701 | 594 |
| 2 | 0.4088 | 0.4739 | 0.4389 | 1798 |
| 3 | 0.5523 | 0.5056 | 0.5280 | 3016 |
| 4 | 0.3166 | 0.4672 | 0.3774 | 702 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 70 | 306 | 194 | 24 |
| 2 | 77 | 852 | 733 | 136 |
| 3 | 76 | 867 | 1525 | 548 |
| 4 | 6 | 59 | 309 | 328 |

### Fold 3

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.2014 | 0.1130 | 0.1448 | 522 |
| 2 | 0.4057 | 0.4496 | 0.4265 | 1617 |
| 3 | 0.5250 | 0.5144 | 0.5196 | 2961 |
| 4 | 0.3491 | 0.3863 | 0.3668 | 1069 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 59 | 263 | 181 | 19 |
| 2 | 105 | 727 | 667 | 118 |
| 3 | 108 | 697 | 1523 | 633 |
| 4 | 21 | 105 | 530 | 413 |

### Fold 4

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.1834 | 0.1109 | 0.1382 | 478 |
| 2 | 0.4066 | 0.4972 | 0.4473 | 1760 |
| 3 | 0.5647 | 0.5042 | 0.5327 | 3090 |
| 4 | 0.3515 | 0.4050 | 0.3764 | 842 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 53 | 260 | 147 | 18 |
| 2 | 123 | 875 | 660 | 102 |
| 3 | 97 | 926 | 1558 | 509 |
| 4 | 16 | 91 | 394 | 341 |

### Fold 5

| Level | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| 1 | 0.2098 | 0.1133 | 0.1471 | 415 |
| 2 | 0.3422 | 0.4309 | 0.3814 | 1288 |
| 3 | 0.5742 | 0.5106 | 0.5406 | 3249 |
| 4 | 0.3824 | 0.4507 | 0.4137 | 1216 |

Rows = actual level; columns = predicted level.

| Actual / Predicted | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| 1 | 47 | 190 | 145 | 33 |
| 2 | 77 | 555 | 549 | 107 |
| 3 | 86 | 759 | 1659 | 745 |
| 4 | 14 | 118 | 536 | 548 |

## Interpretation and limitations

- B minus A pooled OOF: macro F1 +0.1010; balanced accuracy +0.0536.
- B jointly ablates institution identity, institutional attributes, and explicit geography (including country/exterior). This is not an isolated feature effect; indirect proxies can remain.
- Fold means weight folds equally; pooled OOF metrics are recomputed over all rows. Balanced accuracy averages class recall. Undefined per-class metrics use zero_division=0.
- Fold standard deviation is not a confidence interval or significance test. Training sets overlap and GroupKFold does not stratify classes.
- Unseen institution codes map to -1; this does not learn to extrapolate new identities. OrdinalEncoder imposes an artificial order on nominal categories.
- The 0.465 macro F1 in 06 used random holdout and epoch dates. It is not a controlled comparison: splits, age representation, and unknown-category handling differ.
- Prior preprocessing leakage remains: analysis 03 imputed modes/medians on the full dataset before these folds. Original missing-value masks are unavailable. Train-only pipelines cannot undo those imputations; fully leakage-free evaluation requires reconstructing pre-imputation data.
- No causal claims, temporal validation, repeated seeds, or nested tuning.

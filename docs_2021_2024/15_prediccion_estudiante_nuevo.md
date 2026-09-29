# Predicting a student who has not taken the exam

Continuation of [14_entrenamiento_modelo_final.md](14_entrenamiento_modelo_final.md).
Documents the inference script that turns human-readable answers into a
`nivel_desempeno` prediction using the persisted model.

## Reproducible usage

```bash
.venv/bin/python scripts_2021_2024/15_predecir_estudiante.py modelos_2021_2024/ejemplo_estudiante.json
```

The script:

1. Loads `modelos_2021_2024/modelo_final_nivel_desempeno.joblib` and its metadata.
2. Converts human-readable answers (`"Si"`/`"No"`, `"Estrato 3"`, `"Menos de 10 horas"`,
   etc. — the same vocabulary as the original survey, reusing the exact
   mapping dictionaries from analysis 02) into the encoded values the model
   was trained on.
3. Computes `edad` from `estu_fechanacimiento` if `edad` is not given directly.
4. Predicts the level and prints the probability of each of the 4 classes.
5. Warns when the top two classes are within 0.15 of each other, since that
   signals the prediction is not confidently separating two adjacent levels.

Any field left out of the input JSON falls back to the fitted pipeline's
imputation default (mode/median/`"Sin dato"`, recorded in the metadata file)
— not to a value invented by this script.

## Worked example

Input: [`modelos_2021_2024/ejemplo_estudiante.json`](../modelos_2021_2024/ejemplo_estudiante.json),
a synthetic student profile (not a real record).

Output:

```
Predicted nivel_desempeno: 1
Class probabilities:
  nivel 1: 0.3685
  nivel 3: 0.2376
  nivel 2: 0.2070
  nivel 4: 0.1869

Warning: top two classes are close in probability; see doc 13 for why
this model's confidence is limited for individual decisions.
```

## Why this example matters

The predicted class (nivel 1) only carries **37% probability** — barely
ahead of nivel 3 at 24%. This is not a bug; it is the honest behavior of a
model whose out-of-fold macro F1 is 0.38 (see
[12](12_modelo_final_sin_fuga.md)). The script surfaces this explicitly
instead of hiding it behind a single confident-looking label.

## Input contract

All 27 fields listed in
[14_entrenamiento_modelo_final.md](14_entrenamiento_modelo_final.md#required-inputs-in-the-exact-order-the-model-expects)
are accepted as JSON keys, using these value conventions:

| Field type | Example fields | Accepted values |
|---|---|---|
| Binary | `fami_tieneinternet`, `estu_pagomatriculabeca` | `"Si"` / `"No"` |
| Ordinal (text label) | `fami_estratovivienda`, `estu_horassemanatrabaja`, `fami_educacionmadre`, `estu_semestrecursa`, `fami_cuantoscompartebaño` | Exact original survey labels, e.g. `"Estrato 3"`, `"Menos de 10 horas"` |
| Ordinal (already numeric) | `estu_nse_individual` | Integer 1-4 |
| Nominal (free text) | `fami_ocupacionmadre`, `fami_ocupacionpadre`, `estu_tituloobtenidobachiller` | Any of the categories seen in training; unrecognized text maps to an "unknown" code, not an error |
| Other categorical | `periodo`, `estu_tipodocumento`, `estu_agregado`, `estu_genero` | Original raw values, e.g. `"F"`/`"M"`, `"CC"` |
| Age | `estu_fechanacimiento` (or `edad` directly) | `"DD/MM/AAAA"` or an integer age |

## Limitations

- This is a single example, not a validation run. Real accuracy expectations
  come from analysis 12's out-of-fold metrics, not from this one prediction.
- Unrecognized nominal/categorical values do not raise an error; they are
  encoded as -1 (unknown) by `OrdinalEncoder`, which may reduce prediction
  quality silently. Malformed binary or ordinal-label values do raise an
  error, since those have a small, fixed vocabulary worth enforcing strictly.
- As already stated in [13](13_explicacion_modelo_y_datos_faltantes.md), this
  model should not be used for individual decisions about a real student.

# Permutation Importance — `nivel_desempeno`

Paso 3 de la secuencia definida en
[`04_importancia_variables_conceptos.md`](04_importancia_variables_conceptos.md).
Mide, sobre el conjunto de **test** (que el modelo no vio), cuánto empeora
el F1 macro cuando se mezclan aleatoriamente los valores de cada variable.
Esta es la respuesta honesta a "¿esta variable ayuda a predecir en datos
nuevos?", a diferencia de MI (univariada, sin modelo) y MDI (medida sobre
entrenamiento, sesgada por cardinalidad).

## Configuración

- Mismo Random Forest de [`06_random_forest_mdi.md`](06_random_forest_mdi.md)
  (`n_estimators=300`, `class_weight='balanced'`), sin reentrenar.
- Medido sobre `X_test`/`y_test` (20% del dataset, no visto en entrenamiento).
- **Métrica:** F1 macro (no accuracy) — necesario por el desbalance de
  clases: con accuracy plano, una variable puede parecer poco importante
  solo porque el modelo igual acierta prediciendo la clase mayoritaria
  (nivel 3) todo el tiempo.
- `n_repeats=15`, `random_state=42` — cada variable se permuta 15 veces y se
  promedia, para que el resultado no dependa de una sola mezcla al azar.

## Ranking completo (43 variables)

| # | Variable | Importancia (↓ F1 macro) | Desvío |
|---:|---|---:|---:|
| 1 | `inst_cod_institucion` | 0.0765 | 0.0047 |
| 2 | `estu_fechanacimiento` | 0.0359 | 0.0026 |
| 3 | `inst_origen` | 0.0220 | 0.0043 |
| 4 | `estu_horassemanatrabaja` | 0.0113 | 0.0035 |
| 5 | `fami_estratovivienda` | 0.0112 | 0.0023 |
| 6 | `estu_prgm_codmunicipio` | 0.0091 | 0.0027 |
| 7 | `estu_prgm_departamento` | 0.0070 | 0.0022 |
| 8 | `estu_prgm_municipio` | 0.0068 | 0.0022 |
| 9 | `inst_caracter_academico` | 0.0060 | 0.0015 |
| 10 | `periodo` | 0.0051 | 0.0021 |
| 11 | `fami_educacionpadre` | 0.0045 | 0.0026 |
| 12 | `estu_pagomatriculabeca` | 0.0043 | 0.0022 |
| 13 | `estu_semestrecursa` | 0.0043 | 0.0020 |
| 14 | `fami_ocupacionpadre` | 0.0040 | 0.0023 |
| 15 | `estu_inst_departamento` | 0.0039 | 0.0019 |
| 16 | `estu_cod_depto_presentacion` | 0.0037 | 0.0011 |
| 17 | `fami_educacionmadre` | 0.0036 | 0.0030 |
| 18 | `estu_genero` | 0.0034 | 0.0019 |
| 19 | `estu_inst_municipio` | 0.0031 | 0.0024 |
| 20 | `fami_cuantoscompartebaño` | 0.0027 | 0.0026 |
| 21 | `fami_tieneinternet` | 0.0019 | 0.0008 |
| 22 | `estu_pagomatriculapropio` | 0.0017 | 0.0009 |
| 23 | `fami_tieneconsolavideojuegos` | 0.0015 | 0.0018 |
| 24 | `estu_depto_presentacion` | 0.0015 | 0.0018 |
| 25 | `fami_tienelavadora` | 0.0015 | 0.0010 |
| 26 | `estu_inst_codmunicipio` | 0.0011 | 0.0024 |
| 27 | `estu_mcpio_presentacion` | 0.0008 | 0.0029 |
| 28 | `fami_ocupacionmadre` | 0.0006 | 0.0023 |
| 29 | `estu_nse_individual` | 0.0004 | 0.0021 |
| 30 | `estu_cod_mcpio_presentacion` | 0.0003 | 0.0018 |
| 31 | `estu_agregado` | 0.0002 | 0.0003 |
| 32 | `fami_tienehornomicroogas` | 0.0001 | 0.0024 |
| 33 | `estu_tipodocumento` | 0.0001 | 0.0002 |
| 34 | `estu_exterior` | -0.0000 | 0.0002 |
| 35 | `estu_nacionalidad` | -0.0001 | 0.0001 |
| 36 | `estu_pais_reside` | -0.0002 | 0.0001 |
| 37 | `fami_tienemotocicleta` | -0.0004 | 0.0013 |
| 38 | `fami_tieneserviciotv` | -0.0005 | 0.0014 |
| 39 | `estu_tituloobtenidobachiller` | -0.0006 | 0.0015 |
| 40 | `fami_tienecomputador` | -0.0006 | 0.0006 |
| 41 | `estu_pagomatriculapadres` | -0.0007 | 0.0013 |
| 42 | `estu_pagomatriculacredito` | -0.0011 | 0.0023 |
| 43 | `fami_tieneautomovil` | -0.0019 | 0.0018 |

Valores negativos o ≈0 significan que mezclar esa variable al azar no
empeoró el modelo (dentro del ruido) la variable no está aportando nada
que el modelo realmente use.

## Lo que esto confirma o descarta de los pasos anteriores

- **`inst_cod_institucion` es señal real, no memorización pura.** Sigue
  siendo, por lejos, la variable más importante (0.0765) incluso midiendo
  sobre datos no vistos. Ojo: esto no dice si generaliza a instituciones
  *nunca vistas* en el entrenamiento (eso requeriría `GroupKFold` por
  institución, como se hizo en el proyecto anterior para `PUNT_GLOBAL`) —
  solo confirma que dentro de las instituciones que el modelo sí conoce, la
  variable aporta información real.
- **`estu_fechanacimiento` se sostiene como #2**, igual que en MDI. No era
  puro sesgo de cardinalidad — la edad/fecha de nacimiento sí tiene señal
  real sobre el nivel de desempeño.
- **`fami_ocupacionmadre` y `fami_ocupacionpadre` se desploman**: en MDI
  estaban en el puesto #3 y #4 (0.055, 0.055); acá caen al puesto #28 y #14
  con importancia casi nula (0.0006, 0.0040). Confirma la sospecha del paso
  anterior: su alto MDI era **sesgo de cardinalidad** (12 categorías cada
  una), no señal real.
- **`inst_origen`** (si la institución es oficial o privada) emerge con
  fuerza real (#3, 0.022) — no se destacaba tanto en MI ni MDI, pero acá
  muestra que sí importa de verdad.
- **`fami_estratovivienda` y `estu_horassemanatrabaja` se confirman** como
  señal real (top 5 en los tres métodos: MI, MDI y permutation importance) —
  son las variables socioeconómicas más consistentemente relevantes.
- **La mayoría de las variables de bienes del hogar** (`fami_tienecomputador`,
  `fami_tieneautomovil`, etc.) y trámites de matrícula
  (`estu_pagomatriculacredito/padres`) quedan con importancia ≈0 o negativa
  — el modelo no las necesita.

## Siguiente paso

SHAP (paso 4) sobre las variables que sí mostraron señal real acá, para ver
**cómo** cada una mueve la predicción (ej. si estrato alto empuja a nivel 4,
o si el efecto de la institución varía según su origen oficial/privado).

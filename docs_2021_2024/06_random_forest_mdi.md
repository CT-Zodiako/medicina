# Random Forest — Importancia por MDI (`nivel_desempeno`)

Paso 2 de la secuencia definida en
[`04_importancia_variables_conceptos.md`](04_importancia_variables_conceptos.md).
Se entrena un Random Forest y se mira su importancia por impureza (MDI/Gini)
**no como conclusión final**, sino como punto de comparación contra
Mutual Information (paso 1) y contra permutation importance (paso 3, aún
pendiente).

## Configuración

- **Variables:** las mismas 43 de
  [`05_mutual_information.md`](05_mutual_information.md) (excluye
  `punt_global` y los 18 puntajes/derivados de módulo por leakage).
- **Modelo:** `RandomForestClassifier(n_estimators=300, class_weight='balanced', random_state=42)`.
  `class_weight='balanced'` porque las clases están desbalanceadas (nivel 3
  ≈ 49% de los datos, ver `nivel_desempeno` en
  [`02_tratamiento_datos.md`](02_tratamiento_datos.md)).
- **Split:** 80/20 train/test, estratificado por `nivel_desempeno`.
- **Codificación:** igual que en MI — `OrdinalEncoder` para categóricas,
  `estu_fechanacimiento` como epoch continuo.

## Desempeño del modelo (para contexto, no es el foco de este paso)

| Métrica | Valor |
|---|---:|
| Accuracy | 0.530 |
| F1 macro | 0.465 |

| Nivel | Precision | Recall | F1 |
|---|---:|---:|---:|
| 1 | 0.25 | 0.17 | 0.21 |
| 2 | 0.46 | 0.61 | 0.52 |
| 3 | 0.65 | 0.51 | 0.58 |
| 4 | 0.49 | 0.64 | 0.56 |

El nivel 1 (el más raro, 8.5% de los datos) es el peor predicho — esperable
con este desbalance y sin ningún ajuste fino todavía. No se optimiza el
modelo en este paso; el objetivo acá es solo el ranking de importancia.

## Ranking completo por MDI (43 variables)

| # | Variable | MDI |
|---:|---|---:|
| 1 | `estu_fechanacimiento` | 0.1084 |
| 2 | `inst_cod_institucion` | 0.0799 |
| 3 | `fami_ocupacionmadre` | 0.0556 |
| 4 | `fami_ocupacionpadre` | 0.0548 |
| 5 | `fami_educacionpadre` | 0.0476 |
| 6 | `fami_educacionmadre` | 0.0463 |
| 7 | `fami_estratovivienda` | 0.0461 |
| 8 | `periodo` | 0.0410 |
| 9 | `fami_cuantoscompartebaño` | 0.0399 |
| 10 | `estu_horassemanatrabaja` | 0.0382 |
| 11 | `inst_origen` | 0.0288 |
| 12 | `estu_semestrecursa` | 0.0250 |
| 13 | `estu_nse_individual` | 0.0228 |
| 14 | `estu_prgm_municipio` | 0.0201 |
| 15 | `estu_genero` | 0.0199 |
| 16 | `estu_prgm_codmunicipio` | 0.0186 |
| 17 | `estu_pagomatriculacredito` | 0.0182 |
| 18 | `estu_mcpio_presentacion` | 0.0179 |
| 19 | `estu_prgm_departamento` | 0.0175 |
| 20 | `estu_cod_mcpio_presentacion` | 0.0166 |
| 21 | `fami_tieneautomovil` | 0.0162 |
| 22 | `estu_pagomatriculapadres` | 0.0161 |
| 23 | `fami_tienemotocicleta` | 0.0160 |
| 24 | `estu_tituloobtenidobachiller` | 0.0151 |
| 25 | `fami_tieneconsolavideojuegos` | 0.0151 |
| 26 | `inst_caracter_academico` | 0.0150 |
| 27 | `estu_depto_presentacion` | 0.0150 |
| 28 | `estu_pagomatriculabeca` | 0.0147 |
| 29 | `fami_tienehornomicroogas` | 0.0143 |
| 30 | `estu_cod_depto_presentacion` | 0.0142 |
| 31 | `estu_inst_municipio` | 0.0137 |
| 32 | `estu_inst_codmunicipio` | 0.0136 |
| 33 | `estu_inst_departamento` | 0.0129 |
| 34 | `fami_tieneserviciotv` | 0.0118 |
| 35 | `estu_pagomatriculapropio` | 0.0112 |
| 36 | `fami_tienelavadora` | 0.0079 |
| 37 | `fami_tienecomputador` | 0.0056 |
| 38 | `fami_tieneinternet` | 0.0055 |
| 39 | `estu_exterior` | 0.0009 |
| 40 | `estu_tipodocumento` | 0.0009 |
| 41 | `estu_agregado` | 0.0007 |
| 42 | `estu_nacionalidad` | 0.0004 |
| 43 | `estu_pais_reside` | 0.0004 |

## Comparación con Mutual Information — el sesgo de MDI en acción

| Variable | Puesto en MI | Puesto en MDI | Lectura |
|---|---:|---:|---|
| `estu_fechanacimiento` | #18 | **#1** | 4.644 valores únicos (fecha exacta de nacimiento). El árbol tiene muchísimos puntos de corte posibles y la "usa" mucho más, sin que MI viera esa señal como fuerte. Es el sesgo de cardinalidad descrito en `04_importancia_variables_conceptos.md`. |
| `fami_ocupacionmadre` / `fami_ocupacionpadre` | #27 / #23 | **#3 / #4** | 12 categorías cada una, sin orden. Mismo patrón: más categorías → más splits posibles → más "importancia" aparente. |
| `inst_cod_institucion` | **#1** (dominante, 0.21) | #2 (0.08, ya no domina tanto) | Sigue relevante en ambos rankings, pero deja de ser la variable aplastantemente más importante. Sigue pendiente confirmar con permutation importance si es señal real o memorización. |
| `fami_estratovivienda`, `fami_educacionmadre/padre`, `estu_horassemanatrabaja` | Top 20 en ambos | Top 10 en ambos | Estas se sostienen en los dos métodos — son las candidatas más creíbles a señal real hasta ahora, porque no dependen de un sesgo de cardinalidad para aparecer arriba. |

## Conclusión de este paso

Ni MI ni MDI solos alcanzan: MI subestimó `estu_fechanacimiento` y las
ocupaciones (relaciones menos "limpias" para su estimador), y MDI las
sobreestimó por su cardinalidad. Las variables que se mantienen relevantes
en **ambos** métodos (`fami_estratovivienda`, educación de los padres,
`estu_horassemanatrabaja`, `inst_cod_institucion`) son las que más confianza
inspiran por ahora — pero la palabra final la tiene permutation importance
(paso 3), que mide el efecto real sobre un conjunto que el modelo no vio.

## Siguiente paso

Correr permutation importance sobre el modelo ya entrenado, medido en el set
de test con F1 macro, para separar señal real de sesgo de cardinalidad y de
memorización.

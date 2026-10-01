# Mutual Information — `nivel_desempeno`

Primer paso de la secuencia definida en
[`04_importancia_variables_conceptos.md`](04_importancia_variables_conceptos.md):
ranking rápido univariado sobre las variables candidatas, usando
`sklearn.feature_selection.mutual_info_classif`.

## Qué se corrió y qué no

- **Target:** `nivel_desempeno` (1-4).
- **Variables excluidas por composición matemática del target** (17):
  `punt_global` y los 16 puntajes/derivados de módulo (`mod_*_punt`,
  `mod_*_desem`, `mod_*_pnal`, `mod_*_pnbc`). Se excluyen porque
  **componen matemáticamente** `punt_global` → `nivel_desempeno`
  (`punt_global = round(mean(5 puntajes de módulo))`, ver
  [`02_tratamiento_datos.md`](02_tratamiento_datos.md)). Medir MI contra ellos
  solo confirmaría la fórmula, no aportaría nada sobre qué factores
  demográficos/socioeconómicos/institucionales se asocian al desempeño.
- **Variables eliminadas del dataset por ser el mismo dato repetido** (2):
  `inst_nombre_institucion` y `estu_snies_prgmacademico`. En la primera
  corrida de este análisis, el top 3 del ranking fue
  `estu_snies_prgmacademico` (0.2128), `inst_nombre_institucion` (0.2078) e
  `inst_cod_institucion` (0.2078) — las tres apuntando a lo mismo:
  - `inst_nombre_institucion` e `inst_cod_institucion` tuvieron **exactamente
    la misma MI** porque son el nombre y el código de la misma institución;
    es un solo dato codificado dos veces.
  - `estu_snies_prgmacademico` es el código del programa académico dentro de
    esa institución — está altísimamente correlacionado con cuál institución
    es, así que aporta la misma señal que las dos anteriores.

  No tiene sentido conservar 3 columnas que son variantes del mismo dato: se
  **eliminaron del dataset** `inst_nombre_institucion` y
  `estu_snies_prgmacademico`, y se conservó `inst_cod_institucion` como
  representante único (código, más compacto que el nombre en texto). El
  dataset pasó de 64 a 62 columnas.

- **Cuenta exacta de la exclusión por leakage:** son **18** columnas, no 17
  — `punt_global` más los 4 estadísticos (`_punt`, `_desem`, `_pnal`, `_pnbc`)
  de cada uno de los 4 módulos completos (competencias ciudadanas,
  comunicación escrita, inglés, lectura crítica = 4×4 = 16), más el puntaje
  suelto de razonamiento cuantitativo (`mod_razona_cuantitat_punt`, que solo
  conserva el `_punt` porque sus variantes `_pnal`/`_pnbc` ya se habían
  eliminado antes por nulos estructurales, ver
  [`01_dataset_medicina_nulos.md`](01_dataset_medicina_nulos.md)). Total:
  1 + 16 + 1 = 18.

- **Cuenta de columnas usadas:** 62 columnas totales del dataset procesado
  − 1 (`nivel_desempeno`, es el target, no una feature) − 18 (leakage) =
  **43 variables incluidas** en esta corrida.
- **Preprocesamiento:** `estu_fechanacimiento` se convirtió a epoch (segundos)
  y se trató como continua; el resto de variables (categóricas y ordinales ya
  codificadas como número) se codificaron con `OrdinalEncoder` y se marcaron
  como discretas (`discrete_features`) para el estimador de MI.

## Ranking completo (43 variables)

| # | Variable | Mutual Information |
|---:|---|---:|
| 1 | `inst_cod_institucion` | 0.2078 |
| 2 | `estu_prgm_codmunicipio` | 0.0790 |
| 3 | `estu_prgm_municipio` | 0.0790 |
| 4 | `estu_prgm_departamento` | 0.0682 |
| 5 | `estu_inst_codmunicipio` | 0.0583 |
| 6 | `estu_inst_municipio` | 0.0583 |
| 7 | `inst_origen` | 0.0561 |
| 8 | `estu_inst_departamento` | 0.0517 |
| 9 | `estu_cod_mcpio_presentacion` | 0.0420 |
| 10 | `estu_mcpio_presentacion` | 0.0420 |
| 11 | `fami_estratovivienda` | 0.0386 |
| 12 | `estu_depto_presentacion` | 0.0342 |
| 13 | `estu_cod_depto_presentacion` | 0.0342 |
| 14 | `inst_caracter_academico` | 0.0245 |
| 15 | `estu_pagomatriculacredito` | 0.0242 |
| 16 | `estu_horassemanatrabaja` | 0.0225 |
| 17 | `fami_educacionpadre` | 0.0210 |
| 18 | `estu_fechanacimiento` | 0.0198 |
| 19 | `fami_educacionmadre` | 0.0179 |
| 20 | `fami_tienehornomicroogas` | 0.0143 |
| 21 | `fami_cuantoscompartebaño` | 0.0139 |
| 22 | `estu_pagomatriculabeca` | 0.0133 |
| 23 | `fami_ocupacionpadre` | 0.0097 |
| 24 | `periodo` | 0.0091 |
| 25 | `fami_tieneconsolavideojuegos` | 0.0084 |
| 26 | `fami_tienemotocicleta` | 0.0078 |
| 27 | `fami_ocupacionmadre` | 0.0077 |
| 28 | `estu_nse_individual` | 0.0076 |
| 29 | `fami_tieneautomovil` | 0.0066 |
| 30 | `fami_tieneinternet` | 0.0062 |
| 31 | `fami_tienelavadora` | 0.0056 |
| 32 | `fami_tienecomputador` | 0.0048 |
| 33 | `estu_tituloobtenidobachiller` | 0.0044 |
| 34 | `estu_genero` | 0.0034 |
| 35 | `estu_semestrecursa` | 0.0028 |
| 36 | `estu_pagomatriculapropio` | 0.0027 |
| 37 | `estu_exterior` | 0.0021 |
| 38 | `estu_pagomatriculapadres` | 0.0020 |
| 39 | `estu_pais_reside` | 0.0011 |
| 40 | `estu_nacionalidad` | 0.0011 |
| 41 | `estu_tipodocumento` | 0.0009 |
| 42 | `fami_tieneserviciotv` | 0.0007 |
| 43 | `estu_agregado` | 0.0000 |

Los valores no cambiaron respecto a la corrida anterior con las 45 variables
(cada MI se calcula de forma independiente por columna) — lo único que
cambió es que ya no aparece la señal institucional duplicada tres veces en
el top.

## Lectura de los resultados (con la salvedad del punto 1 de
`04_importancia_variables_conceptos.md`)

- `inst_cod_institucion` sigue siendo, por lejos, la variable con más MI
  (0.2078) — 2.6 veces más que la siguiente. Es una **señal de alerta**: un identificador de alta cardinalidad
  puede dominar el ranking sin que necesariamente generalice a instituciones nuevas — la MI no distingue
  todavía entre "señal real del tipo de institución" y "memorización del
  identificador puntual". Esto se valida más adelante con permutation
  importance (paso 3 de la secuencia).
- Debajo de ese identificador, las variables con más señal genuina son
  geográficas (municipio/departamento de programa e institución) y
  socioeconómicas (`fami_estratovivienda`, `estu_pagomatriculacredito`,
  `estu_horassemanatrabaja`, educación de los padres).
- Las variables de bienes del hogar (`fami_tiene*`) y demográficas
  (`estu_genero`, `estu_nacionalidad`, `estu_pais_reside`) quedan con MI muy
  baja (<0.01) — no significa que no importen nada, pero el filtro univariado
  no las destaca.

## Siguiente paso

Entrenar Random Forest/Gradient Boosting (paso 2) y comparar su importancia
por MDI contra este ranking, antes de correr permutation importance (paso 3)
para separar la señal institucional real de la memorización.

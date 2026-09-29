# `dataset_medicina.csv` — Plan de imputación de nulos

Este documento define la estrategia de imputación para las 27 columnas que
quedaron con nulos después del recorte de columnas
(`01_dataset_medicina_nulos.md`) y la normalización a número
(`02_tratamiento_datos.md`). **Todavía no se ejecuta** — es el plan a confirmar
antes de aplicar.

## % de nulos actual (después de normalizar Si/No y ordinales)

| Columna | % nulo |
|---|---:|
| `fami_tieneconsolavideojuegos` | 15.65 |
| `fami_cuantoscompartebaño` | 14.39 |
| `fami_tienemotocicleta` | 5.61 |
| `fami_educacionpadre` | 5.60 |
| `fami_tienehornomicroogas` | 4.99 |
| `fami_tieneautomovil` | 4.80 |
| `mod_comuni_escrita_desem` | 4.68 |
| `estu_nse_individual` | 4.50 |
| `fami_tienelavadora` | 4.50 |
| `fami_tienecomputador` | 4.43 |
| `estu_horassemanatrabaja` | 3.94 |
| `fami_estratovivienda` | 3.92 |
| `fami_educacionmadre` | 3.66 |
| `fami_tieneserviciotv` | 3.57 |
| `fami_tieneinternet` | 3.50 |
| `estu_pagomatriculabeca` | 1.34 |
| `estu_pagomatriculapropio` | 1.33 |
| `estu_pagomatriculacredito` | 1.33 |
| `estu_pagomatriculapadres` | 1.31 |
| `estu_tituloobtenidobachiller` | 1.30 |
| `estu_semestrecursa` | 1.30 |
| `fami_ocupacionmadre` | 1.21 |
| `fami_ocupacionpadre` | 1.20 |
| `mod_ingles_punt` | 0.02 |
| `mod_ingles_desem` | 0.02 |
| `mod_ingles_pnal` | 0.02 |
| `mod_ingles_pnbc` | 0.02 |
| `estu_fechanacimiento` | 0.01 |

`fami_educacionmadre`/`fami_educacionpadre` subieron su % respecto al
original porque `No sabe`/`No Aplica` se mapearon a `NaN` en el paso anterior
(no encajan en la escala ordinal).

## Estrategia por grupo

### 1. Binarias `0`/`1` (Si/No) → moda

Con nulos entre 1.3% y 15.65%, y solo dos valores posibles, imputar con el
valor más frecuente (moda) de cada columna es lo razonable: no hay una
escala que distorsionar y la clase mayoritaria domina fuertemente en casi
todas.

Columnas: `fami_tieneconsolavideojuegos`, `fami_tienemotocicleta`,
`fami_tienehornomicroogas`, `fami_tieneautomovil`, `fami_tienelavadora`,
`fami_tienecomputador`, `fami_tieneserviciotv`, `fami_tieneinternet`,
`estu_pagomatriculabeca`, `estu_pagomatriculacredito`,
`estu_pagomatriculapropio`, `estu_pagomatriculapadres`.

### 2. Ordinales numéricas → mediana

La mediana preserva la escala ordinal sin inventar una categoría que no
existe (a diferencia de la media, que podría caer en un decimal sin sentido
como "estrato 3.4"). Es además robusta a valores extremos.

Columnas: `fami_cuantoscompartebaño`, `estu_horassemanatrabaja`,
`fami_estratovivienda`, `fami_educacionmadre`, `fami_educacionpadre`,
`estu_semestrecursa`, `mod_comuni_escrita_desem`, `estu_nse_individual`,
`mod_ingles_desem`.

### 3. Cuantitativas continuas → mediana

Solo ~5-6 filas nulas en cada una (0.02%). Se imputa con la mediana por
consistencia con el grupo anterior; el impacto es marginal por el volumen.

Columnas: `mod_ingles_punt`, `mod_ingles_pnal`, `mod_ingles_pnbc`.

### 4. Nominales multi-categoría (sin orden) → categoría explícita `"Sin dato"`

Estas variables no tienen un orden natural entre sus valores (ocupación,
tipo de bachillerato), así que imputar con la moda forzaría una mayoría
arbitraria sobre datos que en realidad no se respondieron. Se crea una
categoría nueva y explícita en vez de adivinar.

Columnas: `fami_ocupacionmadre`, `fami_ocupacionpadre`,
`estu_tituloobtenidobachiller`.

### 5. `estu_fechanacimiento` → eliminar filas

Solo 2-3 filas nulas (0.01%). Inventar una fecha de nacimiento no tiene
sentido; se eliminan esas filas puntuales en vez de imputar.

## ✅ Ejecutado

Se corrió sobre `dataset_medicina_procesado.csv` (copia de trabajo). Resultado
exacto, columna por columna:

### Binarias → moda

| Columna | Valor usado | Filas imputadas |
|---|---:|---:|
| `fami_tieneconsolavideojuegos` | 0 | 4.810 |
| `fami_tienemotocicleta` | 0 | 1.726 |
| `fami_tienehornomicroogas` | 1 | 1.534 |
| `fami_tieneautomovil` | 1 | 1.476 |
| `fami_tienelavadora` | 1 | 1.382 |
| `fami_tienecomputador` | 1 | 1.363 |
| `fami_tieneserviciotv` | 1 | 1.097 |
| `fami_tieneinternet` | 1 | 1.077 |
| `estu_pagomatriculabeca` | 0 | 411 |
| `estu_pagomatriculacredito` | 0 | 409 |
| `estu_pagomatriculapropio` | 0 | 409 |
| `estu_pagomatriculapadres` | 1 | 403 |

### Ordinales numéricas → mediana

| Columna | Valor usado | Filas imputadas |
|---|---:|---:|
| `fami_cuantoscompartebaño` | 2 | 4.423 |
| `estu_horassemanatrabaja` | 1 | 1.212 |
| `fami_estratovivienda` | 3 | 1.205 |
| `fami_educacionmadre` | 8 | 1.124 |
| `fami_educacionpadre` | 8 | 1.723 |
| `estu_semestrecursa` | 11 | 401 |
| `mod_comuni_escrita_desem` | 3 | 1.439 |
| `estu_nse_individual` | 4 | 1.382 |
| `mod_ingles_desem` | 3 | 5 |

### Cuantitativas continuas → mediana

| Columna | Valor usado | Filas imputadas |
|---|---:|---:|
| `mod_ingles_punt` | 181 | 5 |
| `mod_ingles_pnal` | 79 | 5 |
| `mod_ingles_pnbc` | 51 | 5 |

### Nominales sin orden → categoría `"Sin dato"`

| Columna | Valor usado | Filas imputadas |
|---|---|---:|
| `fami_ocupacionmadre` | `Sin dato` | 371 |
| `fami_ocupacionpadre` | `Sin dato` | 370 |
| `estu_tituloobtenidobachiller` | `Sin dato` | 401 |

### `estu_fechanacimiento` → filas eliminadas

2 filas eliminadas por nulo (0.01% del dataset).

**Ajuste posterior:** al preparar `estu_fechanacimiento` para Mutual
Information se detectaron 2 filas adicionales con el valor corrupto
`"###...#"` (artefacto de exportación de Excel por desbordamiento de columna,
no un nulo real, por eso no aparecía en el conteo de nulos). Se eliminaron
igual que las anteriores.

## Resultado final

- **0 nulos** en las 64 columnas.
- Shape final: **30.738 filas × 64 columnas** (2 filas sin fecha de
  nacimiento + 2 filas con fecha corrupta).
- Archivo de trabajo: `dataset_medicina_procesado.csv`.

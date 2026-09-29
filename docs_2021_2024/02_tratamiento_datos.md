# `dataset_medicina.csv` — Tratamiento de datos aplicado

Este documento registra, en orden, las transformaciones ya ejecutadas sobre
`dataset_medicina.csv`. El análisis de nulos y columnas a eliminar (aún no
aplicado) está en
[`01_dataset_medicina_nulos.md`](01_dataset_medicina_nulos.md).

## 1. Reconstrucción de `punt_global`

**Problema:** `punt_global` (variable objetivo) era estructuralmente nula al
100% en 2022 y 2023 (15.065 filas), porque ICFES no publicó ese campo para
esos dos periodos en este dataset.

**Solución:** `punt_global` es el promedio simple de los 5 puntajes de
módulo, redondeado al entero. Fórmula:

```
punt_global = round( mean(
    mod_competen_ciudada_punt,
    mod_comuni_escrita_punt,
    mod_ingles_punt,
    mod_lectura_critica_punt,
    mod_razona_cuantitat_punt
) )
```

**Validación:** se aplicó la fórmula sobre las 15.677 filas de 2021/2024
donde `punt_global` ya existía, y coincidió de forma exacta en el 100% de
los casos (0 diferencias) contra el valor real.

**Resultado:** se recalculó `punt_global` para las 15.065 filas nulas de
2022/2023. `punt_global` quedó completo al 100% en las 30.742 filas.

## 2. Creación de `nivel_desempeno`

**Objetivo:** derivar el nivel de desempeño oficial (1 a 4) a partir de
`punt_global`, según los rangos de corte:

| Nivel | Rango de `punt_global` |
|---|---|
| 1 | 0 – 129 |
| 2 | 130 – 156 |
| 3 | 157 – 189 |
| 4 | 190 – 300 |

**Resultado (distribución sobre las 30.742 filas):**

| Nivel | Filas | % |
|---|---:|---:|
| 1 | 2.608 | 8.5% |
| 2 | 8.206 | 26.7% |
| 3 | 15.161 | 49.3% |
| 4 | 4.767 | 15.5% |

**Nota para el modelado:** hay desbalance de clases marcado (nivel 3 casi la
mitad de los datos, nivel 1 apenas 8.5%). Habrá que manejarlo en la etapa de
entrenamiento (estratificación, `class_weight`, o técnicas de balanceo) —
no se corrige en esta etapa de tratamiento de datos.

## 3. Lista de columnas a eliminar (pendiente de ejecutar)

Antes de aplicar el recorte, esta es la lista definitiva de columnas que se
van a quitar y por qué. El detalle completo con las tablas de % de nulos por
año está en `01_dataset_medicina_nulos.md`; acá queda el checklist consolidado
para ejecutar el paso.

### Estructurales (huecos por cambio de esquema entre años)

| # | Columna | Por qué se quita |
|---|---|---|
| 1 | `estu_otrocole_termino` | 100% nula en 2023, >83% nula en el resto. |
| 2 | `estu_valormatriculauniversidad` | Solo poblada en 2021; 100% nula en 2022-2024. |
| 3 | `estu_comocapacitoexamensb11` | Solo poblada en 2021; 100% nula en 2022-2024. |
| 4 | `estu_estadocivil` | Cobertura errática entre años (97%/0.2%/70%/100% nula). No comparable. |
| 5 | `estu_cod_cole_mcpio_termino` | 100% nula en 2023 y 2024. |
| 6 | `estu_cole_termino` | 100% nula en 2023 y 2024; redundante con la anterior. |
| 7 | `percentil_global` | 100% nula en 2022; es una transformación derivada de `punt_global`, ya no aporta nada. |
| 8 | `mod_razona_cuantitativo_pnal` | 100% nula en 2022; el puntaje bruto del módulo ya está completo. |
| 9 | `mod_razona_cuantitativo_pnbc` | 100% nula en 2022; mismo motivo que la anterior. |
| 10 | `estu_tipodocumentosb11` | 100% nula en 2024; redundante con `estu_tipodocumento` (completa). |
| 11 | `estu_areareside` | 100% nula en 2024. |
| 12 | `estu_cod_reside_depto` | 100% nula en 2024; redundante con ubicación de la institución/programa. |
| 13 | `estu_cod_reside_mcpio` | 100% nula en 2024; redundante con ubicación de la institución/programa. |
| 14 | `estu_depto_reside` | 100% nula en 2024; redundante con ubicación de la institución/programa. |
| 15 | `estu_mcpio_reside` | 100% nula en 2024; redundante con ubicación de la institución/programa. |

### Comunes con altísimo % de nulos

| # | Columna | Por qué se quita |
|---|---|---|
| 16 | `estu_etnia` | 92.76% nula, no imputable con criterio. |
| 17 | `estu_tieneetnia` | 44.16% nula; bandera acompañante de `estu_etnia`, mismo patrón de no-respuesta. |
| 18 | `estu_cursoiesexterna` | 83.74% nula (pregunta de rama condicional, no respondida por la mayoría). |
| 19 | `estu_simulacrotipoicfes` | 83.74% nula, mismo patrón que la anterior. |
| 20 | `estu_actividadrefuerzoareas` | 83.74% nula, mismo patrón. |
| 21 | `estu_actividadrefuerzogeneric` | 83.74% nula, mismo patrón. |
| 22 | `estu_cursodocentesies` | 83.74% nula, mismo patrón. |
| 23 | `estu_cursoiesapoyoexterno` | 83.74% nula, mismo patrón. |

### Dato inválido/anómalo

| # | Columna | Por qué se quita |
|---|---|---|
| 24 | `estu_inse_individual` | Contiene números tipo documento (ej. `63320267`), no un índice socioeconómico válido; además confirmado que el mismo valor se repite en el mismo periodo con género distinto, así que ni siquiera sirve como identificador. Se conserva `estu_nse_individual` (escala limpia 1-4) en su lugar. |

### Varianza cero (dataset ya filtrado a Medicina)

| # | Columna | Valor único |
|---|---|---|
| 25 | `estu_prgm_academico` | `MEDICINA` |
| 26 | `estu_nucleo_pregrado` | `MEDICINA` |
| 27 | `estu_nivel_prgm_academico` | `UNIVERSITARIO` |
| 28 | `estu_metodo_prgm` | `PRESENCIAL` |
| 29 | `estu_privado_libertad` | `N` |

### Metadato redundante

| # | Columna | Por qué se quita |
|---|---|---|
| 30 | `Source.Name` | Nombre del archivo de origen; ya representado por `periodo`. |

**Total: 30 columnas eliminadas.** ✅ Ejecutado. El dataset pasó de 94 a 64
columnas.

## 4. Nulos restantes tras el recorte (dataset de 64 columnas)

Con las 30 columnas ya eliminadas, esto es lo que queda por resolver antes de
modelar: 27 columnas todavía tienen nulos (todos bajos/moderados, ya no hay
huecos estructurales del 100%), y las otras 37 quedan completas al 100%.

| Columna | % nulo |
|---|---:|
| `fami_tieneconsolavideojuegos` | 15.65 |
| `fami_cuantoscompartebaño` | 14.39 |
| `fami_tienemotocicleta` | 5.61 |
| `fami_tienehornomicroogas` | 4.99 |
| `fami_tieneautomovil` | 4.80 |
| `mod_comuni_escrita_desem` | 4.68 |
| `estu_nse_individual` | 4.50 |
| `fami_tienelavadora` | 4.50 |
| `fami_tienecomputador` | 4.43 |
| `estu_horassemanatrabaja` | 3.94 |
| `fami_estratovivienda` | 3.92 |
| `fami_tieneserviciotv` | 3.57 |
| `fami_tieneinternet` | 3.50 |
| `fami_educacionmadre` | 3.01 |
| `fami_educacionpadre` | 2.89 |
| `estu_pagomatriculabeca` | 1.34 |
| `estu_pagomatriculacredito` | 1.33 |
| `estu_pagomatriculapropio` | 1.33 |
| `estu_pagomatriculapadres` | 1.31 |
| `estu_semestrecursa` | 1.30 |
| `estu_tituloobtenidobachiller` | 1.30 |
| `fami_ocupacionmadre` | 1.21 |
| `fami_ocupacionpadre` | 1.20 |
| `mod_ingles_desem` | 0.02 |
| `mod_ingles_pnal` | 0.02 |
| `mod_ingles_pnbc` | 0.02 |
| `mod_ingles_punt` | 0.02 |
| `estu_fechanacimiento` | 0.01 |

Las 36 columnas restantes (identificadores de institución/programa, puntajes
de módulo, `punt_global`, `nivel_desempeno`, etc.) están completas al 100%.

## 5. Tipo de dato de las 27 columnas con nulos (antes de imputar)

### Cuantitativas (numéricas continuas/discretas)

| Columna | Valores encontrados |
|---|---|
| `mod_ingles_punt` | Puntaje del módulo de inglés, entero, rango observado ~105-227. |
| `mod_ingles_pnal` | Percentil nacional del módulo de inglés, entero 0-100. |
| `mod_ingles_pnbc` | Percentil por núcleo/grupo del módulo de inglés, entero 0-99. |

### Cualitativas ordinales codificadas como número

Son categorías con orden, aunque el dato viene guardado como `float`:

| Columna | Valores encontrados |
|---|---|
| `mod_comuni_escrita_desem` | Nivel de desempeño del módulo de comunicación escrita: `1.0, 2.0, 3.0, 4.0` (análogo a `nivel_desempeno`, pero solo para ese módulo). |
| `estu_nse_individual` | Nivel socioeconómico individual: `1.0, 2.0, 3.0, 4.0`. |

### Cualitativas ordinales (texto)

| Columna | Valores encontrados |
|---|---|
| `mod_ingles_desem` | Nivel CEFR: `A1, A2, B1, B2` (orden creciente de dominio del idioma). |
| `fami_cuantoscompartebaño` | `NINGUNA, 1, 2, 3 o 4, 5 o 6, MAS DE 6`. |
| `estu_horassemanatrabaja` | `0, Menos de 10 horas, Entre 11 y 20 horas, Entre 21 y 30 horas, Más de 30 horas`. |
| `fami_estratovivienda` | `Sin Estrato, Estrato 1, Estrato 2, Estrato 3, Estrato 4, Estrato 5, Estrato 6`. |
| `fami_educacionmadre` | 12 categorías: desde `Ninguno` hasta `Postgrado`, pasando por primaria/secundaria/técnica/profesional, incompleta y completa. |
| `fami_educacionpadre` | Mismas 12 categorías que `fami_educacionmadre`. |
| `estu_semestrecursa` | Semestre que cursa, guardado como texto: `01`...`11`, `12 o más`. |

### Cualitativas nominales (binarias Si/No)

| Columna | Valores encontrados |
|---|---|
| `fami_tieneconsolavideojuegos` | `Si, No` |
| `fami_tienemotocicleta` | `Si, No` |
| `fami_tienehornomicroogas` | `Si, No` |
| `fami_tieneautomovil` | `Si, No` |
| `fami_tienelavadora` | `Si, No` |
| `fami_tienecomputador` | `Si, No` |
| `fami_tieneserviciotv` | `Si, No` |
| `fami_tieneinternet` | `Si, No` |
| `estu_pagomatriculabeca` | `Si, No` |
| `estu_pagomatriculacredito` | `Si, No` |
| `estu_pagomatriculapropio` | `Si, No` |
| `estu_pagomatriculapadres` | `Si, No` |

### Cualitativas nominales (multi-categoría, sin orden natural)

| Columna | Valores encontrados |
|---|---|
| `estu_tituloobtenidobachiller` | `Bachiller académico, Bachiller técnico, Bachiller pedagógico o normalista`. |
| `fami_ocupacionmadre` | 12 categorías: `Hogar, Pensionado, Empresario, Trabajador por cuenta propia, Empleado de nivel técnico/auxiliar/directivo, Profesional independiente`, etc. |
| `fami_ocupacionpadre` | Mismas 12 categorías que `fami_ocupacionmadre`. |

### Fecha (no encaja en cuanti/cualitativa directamente)

| Columna | Valores encontrados |
|---|---|
| `estu_fechanacimiento` | Fecha de nacimiento en texto `D/M/AAAA` (ej. `1/11/1995`), 4.644 valores únicos. Candidata a transformarse en edad (cuantitativa) más adelante, no se imputa como fecha directamente. |

## 6. Normalización de columnas Si/No y ordinales de texto a número

Se convirtieron a valores numéricos las columnas binarias (`Si/No`) y las
ordinales de texto, para que puedan usarse en el modelo sin one-hot. Las
nominales sin orden (`fami_ocupacionmadre/padre`, `estu_tituloobtenidobachiller`)
**no** se tocaron en este paso.

### Binarias `Si`/`No` → `1`/`0`

Aplicado igual en las 12 columnas: `fami_tieneconsolavideojuegos`,
`fami_tienemotocicleta`, `fami_tienehornomicroogas`, `fami_tieneautomovil`,
`fami_tienelavadora`, `fami_tienecomputador`, `fami_tieneserviciotv`,
`fami_tieneinternet`, `estu_pagomatriculabeca`, `estu_pagomatriculacredito`,
`estu_pagomatriculapropio`, `estu_pagomatriculapadres`.

| Valor original | Valor nuevo |
|---|---|
| `Si` | `1` |
| `No` | `0` |

### `mod_ingles_desem` (nivel CEFR)

| Valor original | Valor nuevo |
|---|---|
| `A1` | `1` |
| `A2` | `2` |
| `B1` | `3` |
| `B2` | `4` |

### `fami_cuantoscompartebaño`

| Valor original | Valor nuevo |
|---|---|
| `NINGUNA` | `0` |
| `1` | `1` |
| `2` | `2` |
| `3 o 4` | `3` |
| `5 o 6` | `4` |
| `MAS DE 6` | `5` |

### `estu_horassemanatrabaja`

| Valor original | Valor nuevo |
|---|---|
| `0` | `0` |
| `Menos de 10 horas` | `1` |
| `Entre 11 y 20 horas` | `2` |
| `Entre 21 y 30 horas` | `3` |
| `Más de 30 horas` | `4` |

### `fami_estratovivienda`

| Valor original | Valor nuevo |
|---|---|
| `Sin Estrato` | `0` |
| `Estrato 1` | `1` |
| `Estrato 2` | `2` |
| `Estrato 3` | `3` |
| `Estrato 4` | `4` |
| `Estrato 5` | `5` |
| `Estrato 6` | `6` |

### `fami_educacionmadre` y `fami_educacionpadre` (mismo mapeo para ambas)

| Valor original | Valor nuevo |
|---|---|
| `Ninguno` | `0` |
| `Primaria incompleta` | `1` |
| `Primaria completa` | `2` |
| `Secundaria (Bachillerato) incompleta` | `3` |
| `Secundaria (Bachillerato) completa` | `4` |
| `Técnica o tecnológica incompleta` | `5` |
| `Técnica o tecnológica completa` | `6` |
| `Educación profesional incompleta` | `7` |
| `Educación profesional completa` | `8` |
| `Postgrado` | `9` |
| `No sabe` | `NaN` (no encaja en la escala; se trata como nulo, a imputar en el próximo paso) |
| `No Aplica` | `NaN` (mismo motivo) |

**Efecto secundario:** al mapear `No sabe`/`No Aplica` a `NaN`, el % de nulos
de `fami_educacionmadre` y `fami_educacionpadre` sube de ~3% a un valor mayor
(1.124 nulos en `fami_educacionmadre` tras el mapeo). Esto es intencional: son
respuestas válidas pero sin un nivel educativo asignable en la escala.

### `estu_semestrecursa`

| Valor original | Valor nuevo |
|---|---|
| `02`...`11` | `2`...`11` (mismo número, sin ceros a la izquierda) |
| `12 o más` | `12` |

## Estado actual del dataset

- `punt_global`: 100% completo.
- `nivel_desempeno`: nueva columna, 100% completa (derivada de `punt_global`,
  que ya no tiene nulos).
- Pendiente: aplicar el recorte de columnas descrito en
  `01_dataset_medicina_nulos.md` y la imputación de las columnas comunes con
  nulos bajos/moderados que se decidió conservar.

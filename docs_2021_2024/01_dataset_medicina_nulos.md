# `dataset_medicina.csv` — Cobertura por año y porcentaje de nulos

## Resumen del dataset

- **Filas totales:** 30.742
- **Columnas:** 93 (+ `Source.Name`, que identifica el archivo origen)
- **Periodos (`periodo` → año):**

| Año  | Filas |
|------|------:|
| 2021 | 6.745 |
| 2022 | 7.089 |
| 2023 | 7.976 |
| 2024 | 8.932 |


## ✅ `punt_global` reconstruido

**Actualización:** ya se resolvió. `punt_global` es el promedio simple de los 5
puntajes de módulo, redondeado al entero:

```
punt_global = round( mean(
    mod_competen_ciudada_punt,
    mod_comuni_escrita_punt,
    mod_ingles_punt,
    mod_lectura_critica_punt,
    mod_razona_cuantitat_punt
) )
```

Verificado contra las 15.677 filas de 2021/2024 donde `punt_global` ya existía:
**match exacto en el 100% de los casos** (0 diferencias). Se aplicó la misma
fórmula para reconstruir las 15.065 filas nulas de 2022/2023 y se sobrescribió
`dataset_medicina.csv`. `punt_global` queda ahora completo al 100% en las
30.742 filas.

## Hallazgo original (ya resuelto, se deja como referencia histórica)

`punt_global` (la variable objetivo para derivar el nivel de desempeño) es
**estructural, no aleatoria**: 0% nulo en 2021 y 2024, pero **100% nulo en
2022 y 2023**. No es que falte el dato ICFES no publicó ese campo para esos
dos años en este dataset.

1. Se recalcula `punt_global` a partir de los puntajes de módulo
   (`mod_*_punt`), que sí están completos en 2022 y solo con nulos
   marginales en 2023, replicando la fórmula oficial de ICFES, o

## Columnas estructurales (nulas al 100% en ≥1 año)

| Columna | 2021 | 2022 | 2023 | 2024 | Global |
|---|---:|---:|---:|---:|---:|
| estu_otrocole_termino | 84.83 | 86.63 | 100.00 | 83.04 | 88.66 |
| estu_valormatriculauniversidad | 3.87 | 100.00 | 100.00 | 100.00 | 78.91 |
| estu_comocapacitoexamensb11 | 0.62 | 100.00 | 100.00 | 100.00 | 78.20 |
| estu_estadocivil | 97.05 | 0.20 | 70.41 | 100.00 | 68.66 |
| estu_cod_cole_mcpio_termino | 24.57 | 25.24 | 100.00 | 100.00 | 66.21 |
| estu_cole_termino | 24.57 | 25.24 | 100.00 | 100.00 | 66.21 |
| ~~punt_global~~ (resuelto) | 0.00 | ~~100.00~~ | ~~100.00~~ | 0.00 | ~~49.00~~ → 0.00 |
| estu_tipodocumentosb11 | 2.05 | 2.37 | 3.13 | 100.00 | 30.86 |
| estu_areareside | 0.62 | 0.93 | 1.94 | 100.00 | 29.91 |
| estu_cod_reside_depto | 0.00 | 0.04 | 0.00 | 100.00 | 29.06 |
| estu_cod_reside_mcpio | 0.00 | 0.04 | 0.00 | 100.00 | 29.06 |
| estu_depto_reside | 0.00 | 0.04 | 0.00 | 100.00 | 29.06 |
| estu_mcpio_reside | 0.00 | 0.04 | 0.00 | 100.00 | 29.06 |
| percentil_global | 0.01 | 100.00 | 0.04 | 0.01 | 23.08 |
| mod_razona_cuantitativo_pnal | 0.00 | 100.00 | 0.00 | 0.00 | 23.06 |
| mod_razona_cuantitativo_pnbc | 0.00 | 100.00 | 0.00 | 0.00 | 23.06 |

## Columnas comunes a los 4 años (con su % de nulos)

Ordenadas de mayor a menor % global de nulos. Las que tienen 0.00 en las
cuatro columnas están completas.

| Columna | 2021 | 2022 | 2023 | 2024 | Global |
|---|---:|---:|---:|---:|---:|
| estu_etnia | 92.51 | 92.19 | 94.03 | 92.25 | 92.76 |
| estu_cursoiesexterna | 81.42 | 83.40 | 86.89 | 82.95 | 83.74 |
| estu_simulacrotipoicfes | 81.42 | 83.40 | 86.89 | 82.94 | 83.74 |
| estu_actividadrefuerzoareas | 81.42 | 83.40 | 86.89 | 82.94 | 83.74 |
| estu_actividadrefuerzogeneric | 81.42 | 83.40 | 86.89 | 82.94 | 83.74 |
| estu_cursodocentesies | 81.42 | 83.40 | 86.89 | 82.94 | 83.74 |
| estu_cursoiesapoyoexterno | 81.42 | 83.40 | 86.89 | 82.94 | 83.74 |
| estu_tieneetnia | 0.03 | 0.21 | 66.68 | 92.25 | 44.16 |
| fami_tieneconsolavideojuegos | 7.32 | 7.28 | 3.31 | 39.59 | 15.65 |
| fami_cuantoscompartebaño | 3.83 | 5.67 | 3.11 | 39.35 | 14.39 |
| fami_tienemotocicleta | 7.61 | 6.90 | 3.01 | 5.42 | 5.61 |
| fami_tienehornomicroogas | 7.41 | 5.87 | 3.00 | 4.24 | 4.99 |
| fami_tieneautomovil | 7.44 | 6.21 | 2.93 | 3.36 | 4.80 |
| mod_comuni_escrita_desem | 1.68 | 8.08 | 3.90 | 4.95 | 4.68 |
| estu_nse_individual | 3.81 | 5.74 | 4.04 | 4.43 | 4.50 |
| estu_inse_individual | 3.81 | 5.74 | 4.04 | 4.43 | 4.50 |
| fami_tienelavadora | 7.09 | 5.39 | 2.87 | 3.28 | 4.50 |
| fami_tienecomputador | 6.75 | 5.30 | 2.93 | 3.34 | 4.43 |
| estu_horassemanatrabaja | 3.45 | 6.11 | 3.01 | 3.43 | 3.94 |
| fami_estratovivienda | 3.20 | 4.92 | 3.64 | 3.92 | 3.92 |
| fami_tieneserviciotv | 3.35 | 5.08 | 2.82 | 3.20 | 3.57 |
| fami_tieneinternet | 3.25 | 5.01 | 2.78 | 3.15 | 3.50 |
| fami_educacionmadre | 2.18 | 4.26 | 2.53 | 3.07 | 3.01 |
| fami_educacionpadre | 1.94 | 4.08 | 2.48 | 3.03 | 2.89 |
| estu_pagomatriculabeca | 0.70 | 1.03 | 2.08 | 1.40 | 1.34 |
| estu_pagomatriculacredito | 0.70 | 1.03 | 2.07 | 1.39 | 1.33 |
| estu_pagomatriculapropio | 0.70 | 1.04 | 2.07 | 1.38 | 1.33 |
| estu_pagomatriculapadres | 0.68 | 1.00 | 2.07 | 1.35 | 1.31 |
| estu_tituloobtenidobachiller | 0.68 | 1.00 | 2.06 | 1.34 | 1.30 |
| estu_semestrecursa | 0.68 | 1.00 | 2.06 | 1.34 | 1.30 |
| fami_ocupacionmadre | 0.62 | 0.93 | 1.94 | 1.21 | 1.21 |
| fami_ocupacionpadre | 0.62 | 0.93 | 1.94 | 1.20 | 1.20 |
| mod_ingles_desem | 0.01 | 0.00 | 0.04 | 0.01 | 0.02 |
| mod_ingles_pnbc | 0.01 | 0.00 | 0.04 | 0.01 | 0.02 |
| mod_ingles_pnal | 0.01 | 0.00 | 0.04 | 0.01 | 0.02 |
| mod_ingles_punt | 0.01 | 0.00 | 0.04 | 0.01 | 0.02 |
| estu_fechanacimiento | 0.00 | 0.01 | 0.00 | 0.01 | 0.01 |

Las **39 columnas restantes** (identificadores de estudiante/institución/
programa, puntajes de módulo `mod_competen_ciudada_*`, `mod_lectura_critica_*`,
`mod_comuni_escrita_punt/pnal/pnbc`, `mod_razona_cuantitat_punt`, `periodo`,
`estu_genero`, `estu_tipodocumento`, etc.) están **completas al 100%** en los
4 años — 0.00% de nulos en todos los casos.

## Columnas a eliminar, con justificación

### 1. Resuelto — ya no se elimina

| Columna | Estado |
|---|---|
| `punt_global` | Reconstruido al 100% (ver sección arriba). No se elimina ninguna fila por este motivo. |

### 2. Estructurales — huecos por cambio de esquema entre años (se eliminan)

| Columna | % nulo global | Justificación |
|---|---:|---|
| `estu_otrocole_termino` | 88.66 | 100% nula en 2023 y >83% en el resto; campo casi vacío en todos los años, sin valor predictivo utilizable. |
| `estu_valormatriculauniversidad` | 78.91 | Solo existe en 2021 (3.87% nulo); 100% nula en 2022-2024. No se puede usar de forma consistente entre años. |
| `estu_comocapacitoexamensb11` | 78.20 | Igual que la anterior: solo poblada en 2021, 100% nula el resto. |
| `estu_estadocivil` | 68.66 | Cobertura errática entre años (97% nula en 2021, 0.2% en 2022, 70% en 2023, 100% en 2024). No es una variable confiable ni comparable año a año. |
 | `estu_cod_cole_mcpio_termino`, `estu_cole_termino` | 66.21 | 100% nulas en 2023 y 2024 (la mitad del dataset). Además son redundantes con otras variables geográficas del colegio de origen. |
| `percentil_global` | 23.08 | 100% nula en 2022; y es una transformación derivada de `punt_global` (percentil del mismo puntaje), por lo que no aporta información nueva una vez resuelto el puntaje global. |
| `mod_razona_cuantitativo_pnal`, `mod_razona_cuantitativo_pnbc` | 23.06 | 100% nulas en 2022. Son el percentil nacional/por-núcleo del módulo de razonamiento cuantitativo; el puntaje bruto (`mod_razona_cuantitat_punt`) sí está completo y es la señal que realmente se necesita. |
| `estu_tipodocumentosb11` | 30.86 | 100% nula en 2024. Es redundante con `estu_tipodocumento` (completa, 0% nula, y con la misma información — tipo de documento). |
| `estu_areareside`, `estu_cod_reside_depto`, `estu_cod_reside_mcpio`, `estu_depto_reside`, `estu_mcpio_reside` | ~29.06-29.91 | Las cinco quedan 100% nulas en 2024 (el año con más filas). Son redundantes con la ubicación de la institución/programa (`estu_prgm_departamento`, `estu_prgm_municipio`, `estu_inst_departamento`, `estu_inst_municipio`), que sí están completas en los 4 años. |

### 3. Comunes de muy alto % de nulos (se eliminan)

| Columna | % nulo global | Justificación |
|---|---:|---|
| `estu_etnia` | 92.76 | Más de 9 de cada 10 registros sin dato; no alcanza para una señal útil ni para imputar con criterio. |
| `estu_tieneetnia` | 44.16 | Bandera acompañante de `estu_etnia`, con el mismo patrón de no-respuesta; se elimina junto con ella. |
| `estu_cursoiesexterna`, `estu_simulacrotipoicfes`, `estu_actividadrefuerzoareas`, `estu_actividadrefuerzogeneric`, `estu_cursodocentesies`, `estu_cursoiesapoyoexterno` | 83.74 (las 6) | Comparten exactamente el mismo % de nulos por año, lo que indica que son preguntas condicionadas a una respuesta previa (rama del cuestionario) que la mayoría no contestó. Con >80% de vacíos no son recuperables ni imputables con confianza. |

### 4. Columnas con datos inválidos o anómalos (se eliminan)

| Columna | Problema detectado | Justificación |
|---|---|---|
| `estu_inse_individual` | Sus valores (ej. `63320267`, `54052525`, `41356342`) no corresponden a un índice socioeconómico (que debería ser una escala acotada tipo 0-100); parecen números de documento u otro identificador filtrado por error. | Se elimina por ser un dato corrupto/mal etiquetado. Se conserva `estu_nse_individual` (escala limpia 1-4, nivel socioeconómico categórico) como reemplazo. |

### 5. Columnas sin variación (varianza cero — se eliminan)

El dataset ya viene filtrado a un solo programa (Medicina), por lo que estas columnas tienen un único valor en las 30.742 filas y no aportan nada a un modelo:

| Columna | Valor único |
|---|---|
| `estu_prgm_academico` | `MEDICINA` |
| `estu_nucleo_pregrado` | `MEDICINA` |
| `estu_nivel_prgm_academico` | `UNIVERSITARIO` |
| `estu_metodo_prgm` | `PRESENCIAL` |
| `estu_privado_libertad` | `N` |

### 6. Metadato redundante (se elimina)

| Columna | Justificación |
|---|---|
| `Source.Name` | Nombre del archivo de origen; ya está representado por `periodo` (que identifica el año/semestre) y no aporta información adicional. |

## Resumen del recorte

- **Se eliminan ~30 columnas**: 9 estructurales, 8 comunes de alto % de nulos, 1 dato anómalo, 5 de varianza cero y 1 metadato redundante.
- **`punt_global` queda pendiente** hasta resolver si se reconstruye para 2022-2023 o se limita el análisis a 2021+2024.
- El resto de columnas comunes con nulos bajos-moderados (`fami_*`, `estu_nse_individual`, `estu_horassemanatrabaja`, etc.) se conservan para imputar en el siguiente paso.

## Siguiente paso

Con este recorte definido, el siguiente paso es resolver `punt_global` y luego
imputar las columnas conservadas que aún tienen nulos (bajo/moderado %).


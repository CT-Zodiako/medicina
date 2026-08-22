# Dataset final para ML — Predicción de PUNT_GLOBAL

Fuente: `ESTU_MEDICINA_3_MODULOS.xlsx` (23.134 filas, 80 columnas)

## Target

- **PUNT_GLOBAL** (numérico, 0-278) — variable a predecir. Problema de regresión.

## Columnas excluidas por fuga de datos (data leakage)

Componentes matemáticos del puntaje global o resultados del mismo examen — dejarlas hace que el modelo "prediga" con otro resultado del test, no con factores explicativos:

| Columna | Motivo |
|---|---|
| MOD_LECTURA_CRITICA_PUNT | Componente directo de PUNT_GLOBAL |
| MOD_RAZONA_CUANTITAT_PUNT | Componente directo de PUNT_GLOBAL |
| MOD_COMUNI_ESCRITA_PUNT | Componente directo de PUNT_GLOBAL |
| MOD_COMPETEN_CIUDADA_PUNT | Componente directo de PUNT_GLOBAL |
| MOD_INGLES_PUNT | Componente directo de PUNT_GLOBAL |
| MOD_*_DESEM, MOD_*_PNAL, MOD_*_PNBC | Nivel de desempeño / percentiles derivados de los puntajes por módulo |
| PERCENTIL_GLOBAL | Derivado directo de PUNT_GLOBAL |
| Puntaje_Atencion_en_Salud | Otro resultado del mismo examen, misma habilidad del estudiante |
| Puntaje_Fundamentacion_Diagnostico_Tratamiento | Otro resultado del mismo examen, misma habilidad del estudiante |
| Puntaje_Promocion_Salud_Prevencion | Otro resultado del mismo examen, misma habilidad del estudiante |

## Columnas excluidas por nulos >80%

| Columna | % nulo |
|---|---:|
| ESTU_ACTIVIDADREFUERZOAREAS | 82.1% |
| ESTU_ACTIVIDADREFUERZOGENERIC | 82.1% |
| ESTU_CURSODOCENTESIES | 82.1% |
| ESTU_CURSOIESAPOYOEXTERNO | 82.1% |
| ESTU_CURSOIESEXTERNA | 82.1% |
| ESTU_SIMULACROTIPOICFES | 82.1% |

## Columnas excluidas por no aportar varianza (un solo valor único)

`ESTU_ESTUDIANTE`, `ESTU_EXTERIOR`, `ESTU_METODO_PRGM`, `ESTU_NIVEL_PRGM_ACADEMICO`, `ESTU_NUCLEO_PREGRADO`, `ESTU_PRGM_ACADEMICO`, `ESTU_PRIVADO_LIBERTAD`

## Columnas excluidas por ser identificador o redundantes

| Columna | Motivo |
|---|---|
| ESTU_CONSECUTIVO | ID único del estudiante — se mantiene como índice, no como feature |
| ESTU_FECHANACIMIENTO | Se transforma en `EDAD` (feature derivada), no se usa cruda |
| ESTU_NSE_INDIVIDUAL | Redundante con `ESTU_INSE_INDIVIDUAL` (misma variable, versión categórica) |
| INST_COD_INSTITUCION | Redundante con `INST_NOMBRE_INSTITUCION` (mismo dato en código) |
| ESTU_SNIES_PRGMACADEMICO | Redundante — combinación institución+programa+sede ya cubierta por `INST_NOMBRE_INSTITUCION` |
| ESTU_COD_DEPTO_PRESENTACION, ESTU_COD_MCPIO_PRESENTACION | Redundante con sus versiones de texto (`ESTU_DEPTO_PRESENTACION`, `ESTU_MCPIO_PRESENTACION`) |
| ESTU_INST_CODMUNICIPIO | Redundante con `ESTU_INST_MUNICIPIO` |
| ESTU_PRGM_CODMUNICIPIO | Redundante con `ESTU_PRGM_MUNICIPIO` |
| ESTU_PRGM_DEPARTAMENTO, ESTU_PRGM_MUNICIPIO | Redundante — como es presencial, coincide con `ESTU_INST_DEPARTAMENTO`/`ESTU_INST_MUNICIPIO` |
| ESTU_DEPTO_PRESENTACION, ESTU_MCPIO_PRESENTACION | Redundante — lugar de presentación del examen coincide con la sede de la institución |

## Columnas finales del dataset (features)

### Numéricas (imputar con mediana si aplica)

| Columna | % nulo | Imputación |
|---|---:|---|
| ESTU_INSE_INDIVIDUAL | 4.3% | Mediana |
| ESTU_EDAD (derivada de ESTU_FECHANACIMIENTO) | 0% | — |

### Categóricas sin nulos (usar directo)

| Columna |
|---|
| INST_NOMBRE_INSTITUCION |
| INST_CARACTER_ACADEMICO |
| INST_ORIGEN |
| ESTU_GENERO |
| ESTU_SEMESTRECURSA |
| PERIODO |
| ESTU_INST_DEPARTAMENTO |
| ESTU_INST_MUNICIPIO |

### Categóricas/binarias con nulos ~4-5% (imputar con moda o categoría "Sin dato")

| Columna | % nulo |
|---|---:|
| FAMI_ESTRATOVIVIENDA | 5.3% |
| FAMI_EDUCACIONMADRE | 4.1% |
| FAMI_EDUCACIONPADRE | 3.9% |
| FAMI_CUANTOSCOMPARTEBAÑO | 4.8% |
| FAMI_TIENEAUTOMOVIL | 4.8% |
| FAMI_TIENECOMPUTADOR | 4.7% |
| FAMI_TIENECONSOLAVIDEOJUEGOS | 5.3% |
| FAMI_TIENEHORNOMICROOGAS | 4.8% |
| FAMI_TIENEINTERNET | 4.4% |
| FAMI_TIENELAVADORA | 4.6% |
| FAMI_TIENEMOTOCICLETA | 5.0% |
| FAMI_TIENESERVICIOTV | 4.5% |
| ESTU_HORASSEMANATRABAJA | 5.0% |

### Categóricas/binarias con nulos <1% (imputar con moda)

| Columna | % nulo |
|---|---:|
| ESTU_PAGOMATRICULABECA | 0.5% |
| ESTU_PAGOMATRICULACREDITO | 0.5% |
| ESTU_PAGOMATRICULAPADRES | 0.5% |
| ESTU_PAGOMATRICULAPROPIO | 0.5% |

## Resumen

- Filas: 23.134
- Columnas originales: 80
- Columnas descartadas: ~58 (fuga de datos, nulos >80%, sin varianza, redundantes/IDs)
- Columnas finales (features + target): ~24

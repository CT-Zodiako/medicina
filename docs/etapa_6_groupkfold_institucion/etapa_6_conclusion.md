# Etapa 6 — GroupKFold por institución: ¿el modelo generaliza a instituciones nuevas?

## 1. Qué se hizo y por qué

`docs/conclusiones/conclusion_final.md` señala como limitación que "se requiere validación cruzada
y, preferiblemente, evaluación temporal o por institución". La etapa_5 ya introdujo validación
cruzada (KFold, k=5), pero de forma aleatoria: la misma institución podía aparecer simultáneamente
en entrenamiento y validación dentro de un mismo fold, dejando abierta la duda de si el modelo
generaliza a datos nuevos o simplemente memoriza patrones propios de cada institución.

Esta etapa 6 entrena el mismo Random Forest de referencia (mismo feature set completo de
`etapa_3_random_forest_shap`, incluyendo `INST_NOMBRE_INSTITUCION`, `INST_CARACTER_ACADEMICO`,
`INST_ORIGEN`, `ESTU_INST_DEPARTAMENTO`, `ESTU_INST_MUNICIPIO`, mismos hiperparámetros
`n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0`) usando `GroupKFold(n_splits=5)`
con `groups=INST_NOMBRE_INSTITUCION`. Esto garantiza que en cada fold las instituciones del conjunto
de validación **nunca** aparecieron en el conjunto de entrenamiento de ese fold (verificado en el
script con un `assert` de no solapamiento). El dataset tiene 55 instituciones únicas, ninguna nulls
y ninguna representa más del ~7% de las filas, por lo que el reparto en 5 grupos de validación
(10 a 12 instituciones cada uno) es razonable.

## 2. Comparación de R² entre etapas

| Etapa | Esquema de validación | ¿Incluye institución? | R² |
|---|---|---|---|
| Etapa 3 | Split único 80/20 (instituciones compartidas entre train y test) | Sí | 0.374 |
| Etapa 5 | KFold aleatorio, k=5 (instituciones compartidas dentro de cada fold) | No | 0.186 ± 0.011 |
| Etapa 6 | GroupKFold, k=5 (instituciones de validación nunca vistas en entrenamiento) | Sí | **0.1199 ± 0.1459** |

Detalle por fold (etapa 6): R² = 0.159, 0.013, 0.250, 0.252, -0.074 (10 a 12 instituciones nuevas
por fold). La dispersión entre folds es muy alta (std ≈ 0.146, mayor que la propia media), incluido
un fold con R² negativo.

## 3. Interpretación

El R² de etapa 6 (0.12 ± 0.15) es notablemente más bajo que el de etapa_3 (0.374) — una caída de
≈0.25 puntos — y, de hecho, también queda por debajo del de etapa_5 (0.186 ± 0.011), que ni
siquiera usa variables de institución. Esto es evidencia bastante clara de que el modelo de
etapa_3 **memorizaba patrones específicos de las instituciones vistas** (vía one-hot de
`INST_NOMBRE_INSTITUCION` y variables correlacionadas) en lugar de aprender una relación
generalizable entre las variables socioeconómicas/académicas y `PUNT_GLOBAL`. Cuando se le exige
predecir sobre instituciones nunca vistas, ese "atajo" deja de funcionar y el desempeño se degrada
más allá incluso de lo que se pierde al remover la institución por completo (etapa_5). La alta
varianza entre folds (algunos con R² ~0.25, otro negativo) refuerza esto: el modelo es inestable
ante instituciones nuevas, lo que sugiere que gran parte de la señal capturada por institución no
es transferible.

## 4. Variables más importantes y estabilidad entre folds

Top variables por importancia media (ver `feature_importance_groupkfold.csv` completo):

| Variable | Importancia media | Std | Std/media |
|---|---|---|---|
| `INST_ORIGEN_NO OFICIAL - CORPORACIÓN` | 0.243 | 0.077 | 32% |
| `INST_NOMBRE_INSTITUCION_UNIVERSIDAD DE LOS ANDES-...` | 0.103 | 0.075 | 73% |
| `INST_CARACTER_ACADEMICO_INSTITUCIÓN UNIVERSITARIA` | 0.092 | 0.020 | 21% |
| `INST_CARACTER_ACADEMICO_UNIVERSIDAD` | 0.089 | 0.019 | 21% |
| `EDAD` | 0.088 | 0.003 | 4% |
| `INST_NOMBRE_INSTITUCION_UNIVERSIDAD ICESI-CALI` | 0.064 | 0.036 | 56% |
| `ESTU_INSE_INDIVIDUAL` | 0.044 | 0.006 | 15% |

Las variables ligadas a instituciones individuales concretas (`UNIVERSIDAD DE LOS ANDES`,
`UNIVERSIDAD ICESI`, etc.) tienen una importancia relativa muy inestable entre folds (std/media
entre 55% y 75%): esto es esperable, ya que una institución solo puede tener importancia distinta
de cero en los folds donde aparece en entrenamiento, y su peso depende de cuántas de sus filas caen
ahí. En cambio, `EDAD`, `INST_CARACTER_ACADEMICO_*` y `ESTU_INSE_INDIVIDUAL` son mucho más estables
(std/media entre 4% y 21%), lo que indica que son señales realmente generalizables, no artefactos
de memorización institucional.

## 5. Conclusión

GroupKFold confirma la sospecha planteada en `conclusion_final.md`: el R²=0.374 de etapa_3 dependía
en buena parte de haber visto la institución del estudiante durante el entrenamiento, y esa señal
no se transfiere a instituciones nuevas (R² cae a 0.12 ± 0.15, con alta varianza entre folds). Para
un uso predictivo honesto —estimar el desempeño de estudiantes de instituciones que el modelo no
ha visto— conviene apoyarse en variables individuales/socioeconómicas estables como `EDAD`,
`ESTU_INSE_INDIVIDUAL` y el carácter académico de la institución, más que en el nombre puntual de
la institución.

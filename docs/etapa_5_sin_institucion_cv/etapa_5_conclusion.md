# Etapa 5 — Random Forest sin institución, con validación cruzada

## Qué se hizo y por qué

El informe consolidado (`docs/conclusiones/conclusion_final.md`, sección
"Limitaciones") señala dos problemas del análisis original:

1. **`INST_NOMBRE_INSTITUCION`** (y columnas asociadas de carácter académico,
   origen y ubicación institucional) es un proxy de alta cardinalidad que
   empaqueta ubicación geográfica, selección de alumnado y recursos, y domina
   las importancias en todos los análisis previos (mutual information, árbol
   de decisión, Random Forest + SHAP).
2. Las métricas e importancias del Random Forest se calcularon con un **único
   `train_test_split`**, sin evidencia de qué tan estables son.

Esta etapa ataca ambas a la vez: se reentrena el mismo Random Forest del
script de referencia (`docs/etapa_3_random_forest_shap/random_forest_shap_analysis.py`,
mismos hiperparámetros: `n_estimators=300, max_depth=8, min_samples_leaf=20`),
pero (a) **sin** `INST_NOMBRE_INSTITUCION`, `INST_CARACTER_ACADEMICO`,
`INST_ORIGEN`, `ESTU_INST_DEPARTAMENTO` ni `ESTU_INST_MUNICIPIO`, y (b) con
**K-Fold (k=5, shuffle, random_state=0)** en vez de un solo split, reportando
media ± desvío estándar de métricas e importancias entre folds.

Script: `docs/etapa_5_sin_institucion_cv/random_forest_sin_institucion_cv.py`.

## Métricas: comparación contra el script original

El script original no guarda el R² en un CSV, solo lo imprime en consola. Para
poder comparar se reejecutó ese mismo código (sin modificar nada del archivo
ni de sus outputs guardados en `docs/etapa_3_random_forest_shap/`) desde una copia
temporal fuera del repo, usando el mismo split y los mismos hiperparámetros.
El número obtenido es real, no estimado:

| | Con institución (script original, split único) | Sin institución (Etapa 5, CV k=5) |
|---|---:|---:|
| R² | 0.3742 | 0.1862 ± 0.0107 |
| MAE | 14.77 | 17.21 ± 0.18 |
| RMSE | 19.56 | 22.30 ± 0.23 |

Quitar institución **reduce el R² de ~0.37 a ~0.19** (se pierde más de la
mitad del poder explicativo del modelo) y empeora MAE y RMSE de forma
consistente. Esto confirma cuantitativamente que la variable institucional
dominaba el modelo: gran parte de lo que el Random Forest "explicaba" no
venía de factores individuales o familiares del estudiante, sino de en qué
institución rindió la prueba.

## Variables más importantes sin institución

Top del ranking agregado (`feature_importance_cv.csv`, importancia media
entre los 5 folds):

1. `EDAD` (0.150)
2. `ESTU_HORASSEMANATRABAJA_0` — no trabaja (0.103)
3. `ESTU_INSE_INDIVIDUAL` — índice socioeconómico individual (0.101)
4. `ESTU_PAGOMATRICULACREDITO_No` / `_Si` — pagó matrícula con crédito (0.077 / 0.073)
5. `ESTU_PAGOMATRICULABECA_Si` / `_No` — pagó matrícula con beca (0.044 / 0.042)
6. `FAMI_ESTRATOVIVIENDA_Estrato 6` (0.040)
7. `FAMI_EDUCACIONPADRE_Postgrado` (0.034)

Sin institución, el modelo se apoya en variables socioeconómicas y
demográficas del estudiante (edad, si trabaja, INSE individual, forma de pago
de la matrícula, estrato, educación de los padres) en vez de en un proxy
institucional.

## Estabilidad de las importancias entre folds

El desvío estándar de la importancia media es pequeño en relación a la media
para las variables top (p. ej. `EDAD`: 0.150 ± 0.010; `ESTU_INSE_INDIVIDUAL`:
0.101 ± 0.010; `ESTU_HORASSEMANATRABAJA_0`: 0.103 ± 0.009), es decir, un
coeficiente de variación de ~7-10%. El orden del top 5-6 se mantiene estable
entre folds; más abajo en el ranking (estrato, tenencia de electrodomésticos)
el std relativo crece un poco pero sin invertir el orden general. Las
métricas agregadas (R² con std de solo 0.011 sobre una media de 0.186)
también muestran baja variabilidad entre folds.

## Conclusión

La institución no es una variable más: es, con diferencia, el factor con
mayor poder predictivo del puntaje global, y su remoción reduce el R² a menos
de la mitad. El resto de las variables (socioeconómicas, demográficas y de
financiamiento del estudio) explica una porción real pero modesta de la
varianza del puntaje (R² ≈ 0.19), y esa porción es razonablemente estable
entre folds. Esto es consistente con la lectura del informe original: la
institución actúa como proxy agregado de ubicación, selección de alumnado y
recursos, y buena parte de la "explicación" del modelo con institución
incluida probablemente refleja esas diferencias entre instituciones más que
factores individuales del estudiante.

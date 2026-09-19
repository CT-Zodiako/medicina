# Random Forest + SHAP

Modelo más robusto que el árbol único, más su explicación con SHAP.

## ¿Cómo funciona Random Forest?

Un Random Forest entrena **muchos árboles de decisión distintos** (acá 300) y promedia sus predicciones. La diversidad entre árboles viene de dos trucos:

1. **Bagging**: cada árbol se entrena con una muestra aleatoria (con reemplazo) de las filas — no todos ven los mismos estudiantes.
2. **Feature bagging**: en cada corte, el árbol solo puede elegir entre un subconjunto aleatorio de columnas, no todas.

Un árbol individual tiene mucha varianza (como vimos: sin podar, memoriza y da R² negativo). Al promediar cientos de árboles distintos que cometen errores en direcciones diferentes, esos errores se cancelan parcialmente y el promedio generaliza mejor. Es la técnica de **reducir varianza sin perder tanto sesgo** como perdía el árbol podado a `max_depth=4`.

## ¿Cómo funciona SHAP?

SHAP (SHapley Additive exPlanations) responde una pregunta distinta a "feature importance": no dice qué variable es importante en general, dice **cuánto empujó cada variable la predicción de un estudiante en particular**, arriba o abajo del promedio.

Viene de teoría de juegos (valores de Shapley): imaginá que las variables son "jugadores" que colaboran para llegar a la predicción final. SHAP reparte el crédito de la predicción entre cada variable de forma matemáticamente justa, probando qué pasaría si esa variable no estuviera presente, en todas las combinaciones posibles con las demás. Para árboles (`TreeExplainer`), existe un atajo exacto y rápido que no necesita probar todas las combinaciones fuerza bruta.

**Ventaja clave frente a `feature_importances_`**: el valor de SHAP está en las **mismas unidades que el target** (puntos de `PUNT_GLOBAL`), no es un número abstracto entre 0 y 1. Por ejemplo, acá `EDAD` tiene un impacto promedio absoluto de **2.76 puntos** — literal, en promedio la edad del estudiante mueve la predicción ±2.76 puntos sobre el puntaje global.

## Resultados

| Modelo | R² | MAE |
|---|---:|---:|
| Árbol sin podar | -0.24 | 21.08 |
| Árbol podado (depth=4) | 0.29 | 15.84 |
| **Random Forest (300 árboles)** | **0.37** | **14.77** |

Mejora real sobre el árbol único, pero sigue sin ser un modelo fuerte (R²=0.37 significa que ~63% de la varianza del puntaje sigue sin explicarse con estas variables — lógico, factores como preparación individual, salud, o cuánto estudió el día del examen no están en el dataset).

**Ranking SHAP confirma el patrón de las 3 técnicas anteriores**: `INST_ORIGEN` (si es corporación no oficial) es la variable con más impacto (8.35 puntos promedio), seguida de `EDAD`, `INST_CARACTER_ACADEMICO` e `ESTU_INSE_INDIVIDUAL`. La institución sigue siendo, con las 4 técnicas (MI, árbol, Random Forest, SHAP), el factor dominante.

## Archivos

- `random_forest_shap_analysis.py` — entrena el modelo y calcula SHAP sobre una muestra de 2.000 estudiantes del set de test.
- `rf_feature_importance.csv` — importancia clásica (reducción de varianza) del Random Forest.
- `shap_ranking.csv` — impacto promedio absoluto en puntos, por variable.
- `shap_summary_plot.png` — gráfico beeswarm: cada punto es un estudiante, el color indica si el valor de la variable era alto o bajo, la posición horizontal indica el impacto en la predicción.

Corre desde la raíz del proyecto (lee `ESTU_MEDICINA_3_MODULOS.xlsx` con ruta relativa).

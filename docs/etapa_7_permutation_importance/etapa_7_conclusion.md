# Etapa 7 — Permutation importance agrupada vs. MDI/Gini: ¿institución sigue dominando?

## 1. Qué se hizo y por qué

La importancia MDI/Gini que reporta `RandomForestRegressor.feature_importances_` (usada en
etapa_3 y etapa_6) tiene un sesgo estadístico conocido: sobreestima variables categóricas de alta
cardinalidad, porque el algoritmo de construcción de árboles tiene más oportunidades de encontrar
un split que reduzca impureza cuando una variable tiene muchos niveles posibles — aunque ese split
no generalice fuera de muestra. En este proyecto, `INST_NOMBRE_INSTITUCION` se expande a 55
columnas dummy vía one-hot encoding, la variable de mayor cardinalidad del feature set con margen.

Para probar esta hipótesis se replicó exactamente el pipeline de etapa_6 (mismo dataset, mismo
feature set con institución, mismo `GroupKFold(n_splits=5)` agrupado por
`INST_NOMBRE_INSTITUCION`, mismos hiperparámetros del Random Forest) y, en cada uno de los 5
folds, se calcularon dos métricas por variable ORIGINAL (agregando las columnas dummy de cada
categórica):

- **MDI agregada**: suma de las importancias Gini de todas las columnas dummy de esa variable.
- **Permutation importance agrupada**: en el fold de validación, se permutan a la vez (con la
  misma permutación de filas) todas las columnas dummy de una variable categórica —o la columna
  individual si es numérica— y se mide la caída de R² respecto al modelo sin permutar
  (`n_repeats=5` por variable y fold). Al permutar todas las dummies de una variable juntas se
  preserva la estructura one-hot válida, pero se rompe la asociación de esa variable con el
  target y con el resto de las variables. A diferencia de MDI (que se mide sobre los splits de
  entrenamiento), la permutación se mide sobre datos de validación held-out, con instituciones
  nunca vistas en entrenamiento — el mismo esquema riguroso de etapa_6.

## 2. Tabla comparativa (variables con mayor cambio o mayor importancia)

| variable | mdi_rank | permutation_rank | mdi_mean | permutation_mean |
|---|---|---|---|---|
| INST_ORIGEN | 2 | **1** | 0.2544 | 0.2634 |
| INST_CARACTER_ACADEMICO | 3 | **2** | 0.1818 | 0.1344 |
| EDAD | 4 | 3 | 0.0882 | 0.0616 |
| ESTU_INSE_INDIVIDUAL | 5 | 4 | 0.0435 | 0.0138 |
| ESTU_HORASSEMANATRABAJA | 9 | 5 | 0.0095 | 0.0048 |
| FAMI_TIENEHORNOMICROOGAS | 8 | 6 | 0.0156 | 0.0041 |
| FAMI_TIENECONSOLAVIDEOJUEGOS | 13 | 7 | 0.0057 | 0.0024 |
| ESTU_GENERO | 16 | 10 | 0.0036 | 0.0009 |
| **INST_NOMBRE_INSTITUCION** | **1** | **24** | **0.2952** | **≈0.0000** |
| ESTU_INST_MUNICIPIO | 6 | 27 (último) | 0.0292 | -0.0323 |
| ESTU_INST_DEPARTAMENTO | 7 | 26 | 0.0286 | -0.0317 |

Tabla completa (27 variables originales) en
`docs/etapa_7_permutation_importance/permutation_vs_mdi_importance.csv`.

## 3. Institución: ¿señal real o artefacto de MDI?

El resultado es contundente y no es ambiguo: **`INST_NOMBRE_INSTITUCION` cae de la posición #1 en
MDI (0.2952, la variable "más importante" del modelo) a la posición #24 de 27 en permutation
importance, con una caída de R² promedio de prácticamente cero (-4.4e-17, indistinguible de
ruido numérico)**. Es decir, romper aleatoriamente la identidad de la institución en el conjunto
de validación no cambia el poder predictivo del modelo en absoluto.

Esto tiene una explicación mecánica que refuerza — no contradice — la conclusión de etapa_6: como
`GroupKFold` garantiza que las instituciones de validación nunca aparecieron en entrenamiento, las
columnas dummy de esas instituciones son siempre 0 durante el entrenamiento de ese fold (nunca
toman valor 1), así que el Random Forest jamás pudo aprender un split útil sobre ellas para el
fold de validación correspondiente. La importancia MDI alta (0.2952) se genera enteramente sobre
splits sacados de las instituciones de ENTRENAMIENTO — es decir, mide memorización de instituciones
específicas, exactamente lo que etapa_6 ya sospechaba con la caída de R² frente a instituciones no
vistas. La permutación en validación expone esa memorización como no transferible: la variable
"institución específica" no aporta nada al generalizar.

En cambio, **`INST_ORIGEN` e `INST_CARACTER_ACADEMICO`** — variables de institución pero de baja
cardinalidad (unas pocas categorías: tipo de sector/carácter académico, no el nombre puntual) que
sí se comparten entre instituciones de entrenamiento y validación — **no solo mantienen su
importancia, sino que SUBEN de ranking y terminan siendo la #1 y #2 bajo permutación**
(0.2634 y 0.1344 respectivamente). La conclusión no es "institución no importa": es que el
**tipo/origen de institución es señal real y generalizable**, mientras que la **identidad
puntual de la institución es un artefacto de memorización que MDI infla por su alta cardinalidad**.

El mismo patrón de colapso aparece en `ESTU_INST_MUNICIPIO` y `ESTU_INST_DEPARTAMENTO`
(variables geográficas correlacionadas con la institución, también de cardinalidad relativamente
alta): pasan de los puestos 6 y 7 en MDI a los últimos dos puestos (26 y 27) en permutación, con
importancia promedio NEGATIVA (-0.0317 y -0.0323) — permutarlas mejora ligeramente el R² en
promedio, señal de que MDI las sobrevalora casi tanto como al nombre de institución.

## 4. Variables de baja cardinalidad: suben de ranking

Consistente con la hipótesis, varias variables de baja cardinalidad o numéricas suben de posición
al pasar de MDI a permutación: `EDAD` (4→3), `ESTU_INSE_INDIVIDUAL` (5→4), `ESTU_GENERO` (16→10),
`ESTU_HORASSEMANATRABAJA` (9→5), `FAMI_TIENEHORNOMICROOGAS` (8→6), `FAMI_TIENECONSOLAVIDEOJUEGOS`
(13→7), `ESTU_PAGOMATRICULABECA` (17→9), entre otras — la mayoría de las 27 variables originales
suben de puesto, porque MDI les resta importancia relativa a favor de las categóricas de alta
cardinalidad.

## 5. Implicación para las conclusiones generales del proyecto

El hallazgo de etapa_6 (el modelo con institución generaliza mal a instituciones nuevas) queda
confirmado y precisado por etapa_7: no es que "institución" en general sea ruido, sino que la
**identidad puntual de la institución** (y sus proxies geográficos directos, municipio/departamento
de la institución) es memorización pura y no debe usarse como variable predictiva confiable fuera
de la muestra de entrenamiento. El **tipo de institución** (`INST_CARACTER_ACADEMICO`,
`INST_ORIGEN`) sí captura señal socioeconómica/académica genuina y generalizable, y junto con
`EDAD` e `ESTU_INSE_INDIVIDUAL` debería ser el foco de cualquier modelo o conclusión que busque
generalizar a instituciones no observadas.

# Qué variables se asocian con `PUNT_GLOBAL` — Saber Pro Medicina

## Resumen ejecutivo

El resultado más consistente de los análisis es que las variables de **institución** concentran la mayor parte de la señal disponible para asociar el `PUNT_GLOBAL`: nombre de la institución, origen y carácter académico aparecen en los primeros lugares de Mutual Information, árbol de decisión, Random Forest y SHAP. Sin embargo, esos tres componentes institucionales no pesan igual bajo una medición robusta de generalización: como muestra la sección "Validación de robustez" más abajo, la señal que realmente se transfiere a instituciones nuevas es el **tipo de institución** (`INST_ORIGEN`, `INST_CARACTER_ACADEMICO`), mientras que la importancia del **nombre puntual** de la institución (`INST_NOMBRE_INSTITUCION`) resulta ser en gran medida memorización de las instituciones vistas en entrenamiento, sin poder predictivo transferible. La edad y los indicadores socioeconómicos (`FAMI_ESTRATOVIVIENDA`, `ESTU_INSE_INDIVIDUAL` y educación de los padres) muestran una asociación secundaria. Género y la mayoría de bienes del hogar aportan poca señal individual.

Esto describe **asociaciones predictivas**, no efectos causales. La institución puede representar conjuntamente selección de estudiantes, contexto geográfico, recursos, currículo y otros factores no observados; los modelos no permiten separar esos mecanismos.

El mejor desempeño observado (Random Forest, R²≈0.37) proviene de un único split 80/20 en el que las mismas instituciones pueden aparecer tanto en entrenamiento como en prueba. Al validar con `GroupKFold` agrupando por institución —de modo que las instituciones de validación nunca fueron vistas en entrenamiento— ese R² cae a **0.12 ± 0.15**. Esto es evidencia de que buena parte del desempeño original reflejaba memorización de instituciones específicas del set de entrenamiento, más que una generalización genuina a instituciones nuevas. A nivel de variable individual, permutation importance agrupada lo confirma de forma directa: `INST_NOMBRE_INSTITUCION` cae del puesto #1 al #24 de 27 al medir su aporte real en validación (caída de R² ≈0), mientras que `INST_ORIGEN` e `INST_CARACTER_ACADEMICO` se mantienen —y suben— como las dos variables más importantes bajo este método más robusto. El detalle está en la sección "Validación de robustez" más abajo.

## Datos y metodología

- Fuente: resultados ICFES Saber Pro de Medicina, períodos 2019–2024.
- Archivo original: `ESTU_MEDICINA_3_MODULOS.xlsx`, 43.563 registros.
- Muestra analizada: 23.134 estudiantes con las tres especialidades y puntaje registrado.
- Objetivo: `PUNT_GLOBAL`, problema de regresión.
- Preprocesamiento: `EDAD` se deriva de `ESTU_FECHANACIMIENTO`; numéricas imputadas con mediana y categóricas con moda. Las categóricas se codifican ordinalmente para MI y one-hot para árboles.
- Evaluación: partición aleatoria única 80/20 (`random_state=0`).

Se aplicaron Mutual Information (señal univariada no lineal), árbol podado (interpretabilidad), Random Forest (importancia por reducción de varianza) y SHAP (impacto medio absoluto en puntos). PCA/UMAP se usaron únicamente como apoyo visual.

## Grupos de variables incluidos

1. **Institución y geografía:** `INST_NOMBRE_INSTITUCION`, `INST_ORIGEN`, `INST_CARACTER_ACADEMICO`, departamento y municipio de la institución.
2. **Socioeconomía familiar:** estrato, educación de madre/padre, personas que comparten baño y tenencia de bienes.
3. **Estudiante:** edad, género, semestre cursado, horas trabajadas y forma de pago de matrícula.
4. **Contexto:** `PERIODO` e `ESTU_INSE_INDIVIDUAL`.

## Exclusiones y fuga de información

Se excluyeron identificadores, columnas constantes o casi vacías, redundancias y variables de resultado o del mismo examen. En particular, `PUNT_GLOBAL` se construye a partir de módulos generales; por tanto, sus puntajes, percentiles, niveles de desempeño y módulos componentes no deben usarse como predictores. También se excluyeron los tres módulos específicos de Medicina por medir el mismo desempeño del examen.

La validación sobre las 78 columnas originales confirma el criterio: `PERCENTIL_GLOBAL` tiene MI **3.2623**, mientras que la primera variable legítima, `INST_NOMBRE_INSTITUCION`, tiene **0.2508**. Los módulos generales tienen MI aproximadamente entre **0.23 y 0.51**. Incluirlos produciría una evaluación artificialmente optimista.

## Resultados por método

### Mutual Information

MI mide reducción de incertidumbre, en nats, y no es un porcentaje de varianza explicada. Ranking completo de las variables finales:

| Variable | MI |
|---|---:|
| `INST_NOMBRE_INSTITUCION` | 0.2549 |
| `INST_ORIGEN` | 0.0594 |
| `ESTU_INST_MUNICIPIO` | 0.0581 |
| `ESTU_INST_DEPARTAMENTO` | 0.0516 |
| `FAMI_ESTRATOVIVIENDA` | 0.0392 |
| `INST_CARACTER_ACADEMICO` | 0.0300 |
| `EDAD` | 0.0246 |
| `FAMI_EDUCACIONPADRE` | 0.0239 |
| `FAMI_EDUCACIONMADRE` | 0.0230 |
| `ESTU_PAGOMATRICULACREDITO` | 0.0226 |
| `ESTU_INSE_INDIVIDUAL` | 0.0225 |
| `ESTU_HORASSEMANATRABAJA` | 0.0210 |
| `FAMI_CUANTOSCOMPARTEBAÑO` | 0.0207 |
| `FAMI_TIENEHORNOMICROOGAS` | 0.0190 |
| `ESTU_PAGOMATRICULABECA` | 0.0189 |
| `FAMI_TIENEAUTOMOVIL` | 0.0140 |
| `FAMI_TIENECONSOLAVIDEOJUEGOS` | 0.0124 |
| `FAMI_TIENEMOTOCICLETA` | 0.0115 |
| `ESTU_SEMESTRECURSA` | 0.0112 |
| `FAMI_TIENELAVADORA` | 0.0088 |
| `FAMI_TIENECOMPUTADOR` | 0.0067 |
| `PERIODO` | 0.0056 |
| `ESTU_PAGOMATRICULAPROPIO` | 0.0049 |
| `FAMI_TIENEINTERNET` | 0.0046 |
| `ESTU_PAGOMATRICULAPADRES` | 0.0038 |
| `ESTU_GENERO` | 0.0029 |
| `FAMI_TIENESERVICIOTV` | 0.0027 |

La institución está muy por encima del resto; a partir de aproximadamente 0.01 la señal individual es débil y debe interpretarse con cautela.

### Árbol de decisión

El árbol podado (`max_depth=4`, `min_samples_leaf=50`) obtiene **R²=0.2877**, **MAE=15.84** y **RMSE=20.86**. El árbol sin podar obtiene R²=-0.2373 por sobreajuste (17.443 hojas).

| Variable/categoría | Importancia |
|---|---:|
| `INST_ORIGEN` = NO OFICIAL - CORPORACIÓN | 0.3223 |
| `INST_CARACTER_ACADEMICO` = INSTITUCIÓN UNIVERSITARIA | 0.2409 |
| Institución = Universidad de los Andes | 0.1685 |
| `EDAD` | 0.0918 |
| Institución = Universidad Icesi | 0.0836 |
| Institución = Universidad de Boyacá | 0.0366 |
| Fundación Universitaria de Ciencias de la Salud | 0.0261 |
| Fundación Universitaria Sanitas | 0.0150 |
| `ESTU_INSE_INDIVIDUAL` | 0.0131 |

Estas importancias son reducción de varianza en cortes one-hot, no efectos marginales causales.

### Random Forest

El bosque usa 300 árboles, profundidad máxima 8 y mínimo 20 observaciones por hoja. En el split único alcanza **R²=0.37**, **MAE=14.77** y es el mejor desempeño observado, aunque deja cerca del 63% de la variación fuera del modelo. Esta cifra se obtiene con un único split en el que las instituciones se comparten entre entrenamiento y prueba; la sección "Validación de robustez" muestra que el R² cae a ~0.12 cuando se valida contra instituciones nunca vistas.

| Variable/categoría | Importancia |
|---|---:|
| `INST_ORIGEN` = NO OFICIAL - CORPORACIÓN | 0.2489 |
| Institución = Universidad de los Andes | 0.1310 |
| `INST_CARACTER_ACADEMICO` = INSTITUCIÓN UNIVERSITARIA | 0.0963 |
| `EDAD` | 0.0960 |
| `INST_CARACTER_ACADEMICO` = UNIVERSIDAD | 0.0912 |
| Institución = Universidad Icesi | 0.0647 |
| `ESTU_INSE_INDIVIDUAL` | 0.0511 |
| Universidad de Boyacá | 0.0298 |
| UNAB | 0.0201 |
| Fundación Universitaria de Ciencias de la Salud | 0.0199 |

### SHAP: interpretación en puntos

SHAP reparte la predicción del bosque entre sus variables. Los valores siguientes son el impacto absoluto promedio en una muestra de 2.000 estudiantes del test: indican cuánto cambia típicamente la predicción, sin indicar por sí solos si el cambio es positivo o negativo.

| Variable/categoría | Impacto medio absoluto (puntos) |
|---|---:|
| `INST_ORIGEN` = NO OFICIAL - CORPORACIÓN | 8.35 |
| `EDAD` | 2.76 |
| `INST_CARACTER_ACADEMICO` = INSTITUCIÓN UNIVERSITARIA | 2.32 |
| `INST_CARACTER_ACADEMICO` = UNIVERSIDAD | 2.19 |
| Universidad de los Andes | 1.27 |
| `ESTU_INSE_INDIVIDUAL` | 1.22 |
| Universidad Icesi | 0.80 |
| Universidad de Boyacá | 0.57 |
| UNAB | 0.48 |
| Fundación Universitaria de Ciencias de la Salud | 0.44 |

Un impacto absoluto de 8.35 no significa que todas las corporaciones obtengan 8.35 puntos menos o más: es un promedio de magnitudes, condicionado por el modelo y la distribución observada.

## Síntesis entre métodos

La señal estable es institucional: nombre, origen y carácter académico dominan los rankings de los cuatro métodos anteriores. Sin embargo, esa aparente equivalencia entre los tres componentes institucionales no sobrevive a una medición más robusta de generalización — ver la sección "Validación de robustez" (etapa 7): el nombre puntual de la institución resulta ser memorización, mientras que origen y carácter académico (tipo de institución) son la señal institucional que realmente se transfiere a instituciones nuevas. Edad aparece consistentemente en los modelos de árboles y SHAP; estrato, INSE y educación familiar aparecen con menor magnitud; género, período y varios bienes presentan señal baja. MI aporta una lectura univariada, mientras que los árboles capturan interacciones y SHAP traduce la importancia del bosque a puntos de predicción. PCA/UMAP muestran aproximadamente 55 agrupaciones institucionales, pero no agregan una variable explicativa independiente.

## Validación de robustez: institución sin variable propia y generalización a instituciones nuevas

Las limitaciones "un único split" y "codificación institucional" señaladas más abajo se atacaron empíricamente con dos análisis adicionales que reentrenan el mismo Random Forest de referencia (`n_estimators=300, max_depth=8, min_samples_leaf=20`) bajo dos esquemas distintos.

### Etapa 5 — Random Forest sin institución, con validación cruzada

Se removieron `INST_NOMBRE_INSTITUCION`, `INST_CARACTER_ACADEMICO`, `INST_ORIGEN`, `ESTU_INST_DEPARTAMENTO` y `ESTU_INST_MUNICIPIO`, y se evaluó con K-Fold (k=5, shuffle, `random_state=0`) en vez de un único split, reportando media ± desvío estándar entre folds:

| Métrica | Valor |
|---|---:|
| R² | 0.186 ± 0.011 |
| MAE | 17.21 ± 0.18 |
| RMSE | 22.30 ± 0.23 |

Quitar institución reduce el R² de ~0.37 a ~0.19: se pierde más de la mitad del poder explicativo del modelo. Las variables que quedan al frente son socioeconómicas y demográficas: `EDAD` (0.150), no trabajar horas/semana (`ESTU_HORASSEMANATRABAJA_0`, 0.103), `ESTU_INSE_INDIVIDUAL` (0.101), forma de pago de matrícula con crédito o beca (0.04-0.08), estrato 6 (0.040) y padre con posgrado (0.034). Estas importancias son estables entre folds (coeficiente de variación de ~7-10% en el top de la lista), y la propia dispersión de R² entre folds es baja (std=0.011 sobre una media de 0.186).

### Etapa 6 — GroupKFold agrupando por institución

Se entrenó el mismo Random Forest con el set completo de variables (incluida institución), pero con `GroupKFold(n_splits=5)` agrupando por `INST_NOMBRE_INSTITUCION`, de modo que las instituciones del conjunto de validación de cada fold nunca aparecen en su conjunto de entrenamiento (55 instituciones únicas, ninguna representa más del ~7% de las filas):

| Métrica | Valor |
|---|---:|
| R² | 0.120 ± 0.146 |
| MAE | 17.59 ± 1.07 |
| RMSE | 22.78 ± 1.53 |

El R² por fold (0.159, 0.013, 0.250, 0.252, -0.074) tiene una dispersión muy alta —el desvío estándar (0.146) es casi tan grande como la media—, incluido un fold con R² negativo. Las variables ligadas a una institución puntual (p. ej. "Universidad de los Andes": std/media ≈73%; "Universidad Icesi": ≈56%) son muy inestables entre folds, mientras que `EDAD` (std/media ≈4%) y, en menor medida, `ESTU_INSE_INDIVIDUAL` (≈15%) y `INST_CARACTER_ACADEMICO_*` (≈21%) se mantienen mucho más estables.

### Comparación de R² entre esquemas de validación

| Etapa | Esquema de validación | ¿Incluye institución? | R² |
|---|---|---|---:|
| Etapa 3 | Split único 80/20 (instituciones compartidas entre train y test) | Sí | 0.374 |
| Etapa 5 | KFold aleatorio, k=5 (instituciones compartidas dentro de cada fold) | No | 0.186 ± 0.011 |
| Etapa 6 | GroupKFold, k=5 (instituciones de validación nunca vistas en entrenamiento) | Sí | 0.120 ± 0.146 |

### Interpretación: memorización institucional, no solo señal institucional

El R² de etapa 6 (0.12 ± 0.15) no solo es muy inferior al de etapa 3 (0.374): también queda por debajo del de etapa 5 (0.186 ± 0.011), que ni siquiera usa variables de institución. Esto es evidencia de que el modelo de etapa 3 memorizaba patrones específicos de las instituciones vistas en entrenamiento (vía el one-hot de `INST_NOMBRE_INSTITUCION` y variables correlacionadas), en lugar de aprender una relación generalizable entre las variables socioeconómicas/académicas y `PUNT_GLOBAL`. Al exigirle predecir sobre instituciones nunca vistas, ese atajo deja de funcionar y el desempeño se degrada más allá incluso de lo que se pierde al remover la institución por completo.

Esto matiza —no invalida— el hallazgo central del informe: la institución sigue siendo la señal dominante y el resto de variables explica una porción real pero modesta de la varianza (R²≈0.19 sin institución, estable entre folds). Lo que cambia es la lectura del R²=0.37 original: parte de esa cifra reflejaba el diseño de validación (split único, sin agrupar por institución) más que capacidad predictiva genuina sobre instituciones nuevas. La sección siguiente (etapa 7) precisa este punto a nivel de variable individual: distingue qué parte de la señal institucional es memorización del nombre puntual y cuál es tipo de institución realmente generalizable.

### Etapa 7 — Permutation importance agrupada vs. MDI/Gini: nombre vs. tipo de institución

La importancia MDI/Gini que usan etapa 3 y etapa 6 tiene un sesgo estadístico conocido: sobreestima variables categóricas de alta cardinalidad, porque el algoritmo de construcción de árboles tiene más oportunidades de encontrar un split que reduzca impureza cuantas más categorías tenga la variable, aunque ese split no generalice fuera de muestra. `INST_NOMBRE_INSTITUCION` se expande a 55 columnas dummy vía one-hot, la variable de mayor cardinalidad del feature set con margen.

Para probar esta hipótesis se replicó el mismo pipeline y esquema `GroupKFold(n_splits=5)` de etapa 6, y en cada fold se calcularon dos métricas por variable ORIGINAL (agregando las columnas dummy de cada categórica): la **MDI agregada** (suma de importancias Gini de las dummies) y la **permutation importance agrupada** (se permutan a la vez todas las dummies de una variable —o la columna individual si es numérica— en el fold de validación, y se mide la caída de R² respecto al modelo sin permutar, `n_repeats=5`). A diferencia de MDI, que se mide sobre los splits de entrenamiento, la permutación se mide sobre datos de validación con instituciones nunca vistas en entrenamiento — el mismo esquema riguroso de etapa 6.

| Variable | Rank MDI | Rank permutación | MDI media | Permutación media |
|---|---:|---:|---:|---:|
| `INST_ORIGEN` | 2 | **1** | 0.2544 | 0.2634 |
| `INST_CARACTER_ACADEMICO` | 3 | **2** | 0.1818 | 0.1344 |
| `EDAD` | 4 | 3 | 0.0882 | 0.0616 |
| `ESTU_INSE_INDIVIDUAL` | 5 | 4 | 0.0435 | 0.0138 |
| **`INST_NOMBRE_INSTITUCION`** | **1** | **24 de 27** | **0.2952** | **≈0.0000** |
| `ESTU_INST_DEPARTAMENTO` | 7 | 26 | 0.0286 | -0.0317 |
| `ESTU_INST_MUNICIPIO` | 6 | 27 (último) | 0.0292 | -0.0323 |

Tabla completa (27 variables originales) en `docs/etapa_7_permutation_importance/permutation_vs_mdi_importance.csv`.

El resultado es contundente y no es ambiguo: `INST_NOMBRE_INSTITUCION` —la variable "más importante" del modelo según MDI (0.2952, puesto #1)— cae al puesto #24 de 27 en permutation importance, con una caída de R² promedio de prácticamente cero (indistinguible de ruido numérico). Romper aleatoriamente la identidad de la institución en el conjunto de validación no cambia el poder predictivo del modelo en absoluto: la importancia MDI alta se genera enteramente sobre splits de instituciones de *entrenamiento*, que por diseño de `GroupKFold` nunca coinciden con las de validación — exactamente la memorización que etapa 6 ya hacía sospechar con la caída de R² frente a instituciones no vistas. `ESTU_INST_MUNICIPIO` y `ESTU_INST_DEPARTAMENTO` (proxies geográficos de institución, también de cardinalidad relativamente alta) muestran el mismo colapso, con importancia por permutación **negativa** (ranks #26 y #27): permutarlas mejora ligeramente el R² en promedio, señal de que MDI las sobrevaloraba casi tanto como al nombre de institución.

En cambio, `INST_ORIGEN` e `INST_CARACTER_ACADEMICO` —variables de institución pero de baja cardinalidad (unas pocas categorías de tipo de sector/carácter académico, no el nombre puntual), compartidas entre instituciones de entrenamiento y validación— no solo mantienen su importancia sino que **suben** de ranking y terminan siendo la #1 y #2 bajo permutación (#2→#1 y #3→#2). `EDAD` y `ESTU_INSE_INDIVIDUAL` se mantienen estables en el top (ranks #3-4 en ambos métodos).

La conclusión que deja etapa 7 no es "institución no importa": es que el **tipo/origen de institución es señal real y generalizable**, mientras que la **identidad puntual de la institución es un artefacto de memorización que MDI infla por su alta cardinalidad** y que no debe usarse como variable predictiva confiable fuera de la muestra de instituciones vistas en entrenamiento.

## Limitaciones

- **Asociación no es causalidad:** no se puede atribuir el puntaje a una institución o característica particular.
- **Codificación institucional:** el nombre de institución es una categoría de alta cardinalidad y puede empaquetar ubicación, selección, composición del alumnado y recursos. *Abordado empíricamente* en "Validación de robustez": al remover la institución (etapa 5, CV k=5) el R² cae de 0.374 a 0.186±0.011, cuantificando cuánto de la señal original dependía de esa variable. El punto conceptual —que sigue siendo una categoría que empaqueta varios factores— permanece válido.
- **Un único split:** R², MAE, RMSE e importancias pueden variar; se requiere validación cruzada y, preferiblemente, evaluación temporal o por institución. *Abordado empíricamente* en "Validación de robustez": la etapa 5 agrega K-Fold (k=5) y la etapa 6 agrega `GroupKFold` por institución, mostrando que el R²=0.374 del split único cae a 0.120±0.146 cuando las instituciones de validación nunca fueron vistas en entrenamiento — evidencia de memorización institucional, no solo de varianza entre splits.
- **Nombre de institución no es señal transferible:** no puede sostenerse que el nombre puntual de una institución (`INST_NOMBRE_INSTITUCION`) tenga poder predictivo transferible a instituciones nuevas. *Abordado empíricamente* en "Validación de robustez" (etapa 7): la permutation importance agrupada por variable muestra que el nombre cae del puesto #1 en MDI (0.2952) al puesto #24 de 27 con una caída de R² prácticamente nula, mientras que el origen y el carácter académico de la institución (tipo de institución) se mantienen —y suben— como las variables más importantes bajo este método más robusto.
- **Variables omitidas:** preparación, horas de estudio, salud, trayectoria escolar y condiciones del examen no están disponibles.
- **Importancias no equivalen a significancia estadística:** no se presentan intervalos de confianza ni pruebas de estabilidad.
- **PCA/UMAP son exploratorios:** sus clusters dependen de la codificación one-hot y de parámetros de visualización.

## Reproducibilidad y artefactos

Desde la raíz del repositorio, las técnicas se ejecutan con los scripts documentados en cada carpeta. El informe se genera con:

```bash
python docs/conclusiones/generar_pdf.py
```

El generador lee los rankings CSV existentes y produce el PDF en `docs/conclusiones/Analisis_Completo_Saber_Pro_Medicina.pdf` (y una copia con nombre descriptivo `Analisis_Variables_Puntaje_Global.pdf`). Fuentes principales: `docs/etapa_1_mutual_information/mutual_info_ranking_24.csv`, `mutual_info_ranking_78.csv`, `docs/etapa_2_decision_tree/feature_importance.csv`, `docs/etapa_3_random_forest_shap/rf_feature_importance.csv`, `shap_ranking.csv`, los scripts `*_analysis.py`, `tree_rules.txt` y las visualizaciones PCA/UMAP/SHAP. La validación de robustez usa además `docs/etapa_5_sin_institucion_cv/random_forest_sin_institucion_cv.py`, `metrics_cv.csv` y `feature_importance_cv.csv`; `docs/etapa_6_groupkfold_institucion/random_forest_groupkfold_institucion.py`, `metrics_groupkfold.csv` y `feature_importance_groupkfold.csv`; y `docs/etapa_7_permutation_importance/random_forest_permutation_importance.py` con `permutation_vs_mdi_importance.csv`.

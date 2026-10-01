# Fundamentación metodológica — Random Forest y escenarios A/B

Documento de soporte que justifica, con la evidencia producida en el propio
pipeline 2021–2024, tres decisiones de diseño:

1. Por qué se siguió la progresión MI → Random Forest + MDI → permutation
   importance → SHAP.
2. Por qué se eligió Random Forest y qué aportó el ajuste de hiperparámetros.
3. Por qué se compararon dos escenarios (A y B) y por qué el modelo final es el B.

Cada afirmación remite al archivo de `docs_2021_2024/` o `scripts_2021_2024/`
que la respalda.

---

## 0. Objetivo del proyecto

| Pipeline | Carpeta | Variable objetivo | Tipo de problema |
|---|---|---|---|
| 2021–2024 | `docs_2021_2024/` (pasos 01–19) | `nivel_desempeno` (niveles 1–4) | Clasificación multiclase |

**Pregunta central:** ¿qué variables del estudiante y de su contexto se asocian
con el desempeño en Saber Pro Medicina, y cuánto de ese desempeño se puede
anticipar **antes** de que el estudiante presente el examen?

De ese objetivo se derivan dos restricciones que condicionan todo el diseño:

- **Sin variables del propio examen.** Se excluyen 18 columnas de *leakage*
  (`punt_global` y los puntajes/desempeños de cada módulo), porque no existen
  antes del examen y harían trivial la predicción
  (`scripts_2021_2024/common.py:31-32`; `punt_global` es la fuente de
  `nivel_desempeno`, ver `02_tratamiento_datos.md`).
- **Generalización honesta.** Un modelo útil debe funcionar con estudiantes e
  instituciones que no estuvieron en el entrenamiento, no solo con los ya vistos.

---

## 1. Progresión de técnicas de importancia (pasos 04 a 08)

Fuente: `04_importancia_variables_conceptos.md`, que define el plan de cuatro
capas y su orden. Cada técnica resuelve una limitación de la anterior:

| Paso | Técnica | Qué agrega | Limitación que deja |
|---|---|---|---|
| 05 | Mutual Information | Filtro univariado rápido sobre las 43 variables candidatas, sin modelo y válido para variables mixtas | No ve interacciones ni redundancia; no dice si el modelo puede usar la señal |
| 06 | Random Forest + MDI | Modelo base con primera intuición de importancia | MDI se sesga hacia alta cardinalidad y se mide sobre entrenamiento |
| 07 | Permutation importance | Importancia medida sobre test, con F1 macro | Un solo número global por variable, sin dirección ni interacciones |
| 08 | SHAP | Contribución por clase y por predicción | Explica el modelo, no prueba generalización ni causalidad |

### 1.1 MI como primer filtro (05)

MI es rápida, funciona con variables categóricas, ordinales y continuas sin
transformarlas más, y ordena las candidatas antes de invertir en modelos
pesados (`04_importancia_variables_conceptos.md`, sección 1). Su resultado ya
mostró el riesgo central del dataset: `inst_cod_institucion` quedó con MI 0.2078,
2.6 veces la siguiente, sin que MI pueda distinguir señal real de memorización
del identificador (`05_mutual_information.md`).

### 1.2 Random Forest + MDI (06)

Se entrena el bosque base y se mira MDI **solo como punto de comparación**, no
como conclusión (`06_random_forest_mdi.md`). En holdout aleatorio 80/20
estratificado, el modelo alcanzó accuracy 0.530 y F1 macro 0.465. La comparación
con MI reveló el sesgo de cardinalidad: `estu_fechanacimiento` (4.644 valores
únicos) pasó del puesto #18 en MI al #1 en MDI, y las ocupaciones de los padres
(12 categorías) del #27/#23 al #3/#4.

### 1.3 Permutation importance (07)

Mide cuánto cae el F1 macro en test al mezclar cada variable; se usa F1 macro y
no accuracy porque el nivel 3 concentra ≈49 % de los datos
(`07_permutation_importance.md`, `04_importancia_variables_conceptos.md`). Dio
la respuesta que MDI no podía dar:

- `fami_ocupacionmadre` y `fami_ocupacionpadre` se desplomaron (de #3/#4 en MDI
  a #28/#14), lo que confirmó que su MDI alto era sesgo de cardinalidad.
- `inst_cod_institucion` siguió primera (0.0765), seguida por
  `estu_fechanacimiento` (0.0359) e `inst_origen` (0.0220).
- `fami_estratovivienda` y `estu_horassemanatrabaja` se sostuvieron en el top 5
  de los tres métodos.

Límite documentado: esta medición usa un holdout aleatorio, por lo que no dice
si la institución generaliza a instituciones **nunca vistas**; eso requería
`GroupKFold` por institución (paso 09).

### 1.4 SHAP (08)

SHAP se aplica al final, sobre un conjunto acotado de variables, por ser la
técnica más costosa (`04_importancia_variables_conceptos.md`, sección 4). Aporta
la contribución por clase (`nivel_1` a `nivel_4`): `inst_cod_institucion`
dominó, sobre todo para el nivel 4, y `inst_origen`, `estu_fechanacimiento`,
`estu_horassemanatrabaja` y `fami_estratovivienda` aparecieron entre las
siguientes (`08_shap.md`). Su propio límite: explica el modelo, no demuestra que
la señal institucional generalice (`08_shap.md`, sección Limitaciones).

**Resultado de la progresión:** las cuatro técnicas coincidían en que la
institución era la señal dominante, y ninguna podía responder si esa señal era
transferible. Esa pregunta pendiente justifica el experimento de la sección 3.

---

## 2. Random Forest y ajuste de hiperparámetros

### 2.1 Por qué Random Forest

Fuentes: `04_importancia_variables_conceptos.md`, `06_random_forest_mdi.md`,
`scripts_2021_2024/06_random_forest_mdi.py`.

- **Datos mixtos.** El dataset tiene variables numéricas, ordinales, binarias y
  nominales (`04_importancia_variables_conceptos.md`); en 06 se codifican con
  `OrdinalEncoder` (categóricas) y fecha como valor continuo, sin necesidad de
  más transformaciones.
- **Desbalance de clases.** El nivel 3 concentra ≈49 % de los datos y el nivel 1
  solo 8.5 %; se usa `class_weight='balanced'` (`06_random_forest_mdi.md`).
- **Compatibilidad con las cuatro técnicas.** El bosque permite MDI (06),
  permutation importance (07) y `TreeExplainer` de SHAP (08), lo que mantiene
  el mismo modelo a lo largo de toda la secuencia.
- **Interacciones.** El modelo basado en árboles puede dividir sobre
  combinaciones de variables, algo que MI univariada no ve
  (`04_importancia_variables_conceptos.md`, secciones 1 y 4).

Alcance: en 2021–2024 no se comparó Random Forest contra otros algoritmos; la
elección se apoya en las características de los datos, no en un benchmark.

### 2.2 Ajuste de hiperparámetros (paso 10)

Fuente: `10_tuning_modelo_b.md`, `scripts_2021_2024/10_tuning_modelo_b.py:43-49`.

- **Modelo ajustado:** Random Forest clasificador del **escenario B**.
- **Método:** `RandomizedSearchCV`, 15 combinaciones, métrica macro F1, usando
  los mismos 5 folds `GroupKFold` por institución del paso 09.

| Hiperparámetro | Valores probados | Ganador |
|---|---|---|
| `n_estimators` | 200, 300, 400, 600 | 600 |
| `max_depth` | None, 8, 12, 16, 24 | None |
| `min_samples_leaf` | 1, 2, 5, 10, 20 | 1 |
| `min_samples_split` | 2, 5, 10, 20 | 5 |
| `max_features` | sqrt, log2, 0.3, 0.5 | log2 |

| Métrica | Por defecto | Ajustado | Delta |
|---|---:|---:|---:|
| Macro F1 | 0.3721 | 0.3787 | +0.0066 |
| Balanced accuracy | 0.3759 | 0.3930 | +0.0171 |

Qué aporta este resultado:

1. **Mejora medida y documentada**, sobre todo en balanced accuracy (mejor
   reconocimiento de las clases minoritarias).
2. **El techo está en los datos, no en el modelo:** las 15 combinaciones
   quedaron entre 0.31 y 0.38 de macro F1 (`10_tuning_modelo_b.md`, tabla de
   resultados completos).
3. **Los bosques más restringidos rindieron peor:** las configuraciones con
   `max_depth=8` (y `min_samples_leaf` de 20) quedaron últimas (≈0.31), mientras
   que la ganadora usa árboles sin límite de profundidad y hojas de un
   estudiante.
4. **Configuración defendible** para el modelo final
   (`scripts_2021_2024/12_modelo_final_sin_fuga.py:52`).

Límite documentado: no se usó validación cruzada anidada, por lo que la métrica
ajustada puede ser levemente optimista (`10_tuning_modelo_b.md`).

---

## 3. Escenarios A y B (paso 09)

Fuentes: `09_validacion_groupkfold.md`,
`scripts_2021_2024/09_validacion_groupkfold.py:34-41`,
`11_conclusion_importancia_variables.md`.

### 3.1 Qué es cada escenario

Ambos escenarios usan **las mismas 30.738 filas y los mismos folds**. Solo
cambian las **columnas** que ve el modelo:

| Grupo de columnas | Cantidad | Escenario A | Escenario B |
|---|---:|:---:|:---:|
| Objetivo (`nivel_desempeno`) | 1 | — | — |
| *Leakage* (resultados del examen) | 18 | excluidas | excluidas |
| Duplicadas (`inst_nombre_institucion`, `estu_snies_prgmacademico`) | 2 | excluidas | excluidas |
| Institución y geografía | 16 | **incluidas** | excluidas |
| Estudiante, familia y contexto socioeconómico | 27 | incluidas | incluidas |
| **Total de predictores** | | **43** | **27** |

Las 16 columnas que diferencian a A de B son: `inst_cod_institucion`,
`inst_origen`, `inst_caracter_academico`, municipio/departamento del programa,
de la institución y del lugar de presentación, `estu_nacionalidad`,
`estu_pais_reside` y `estu_exterior` (lista completa en
`09_validacion_groupkfold.md`).

### 3.2 Por qué hacer dos escenarios

La pregunta pendiente de la sección 1 solo se responde con un experimento
controlado:

- **Misma data, mismos folds, mismo modelo** (300 árboles,
  `class_weight='balanced'`).
- **Una sola diferencia:** presencia o ausencia de las 16 columnas
  institucionales/geográficas (diseño de ablación). El propio paso 09 advierte
  que es una ablación conjunta, no el efecto aislado de una variable.

### 3.3 Por qué validar con GroupKFold por institución

En una partición aleatoria, estudiantes de la misma universidad quedan a la vez
en entrenamiento y en prueba, por lo que el modelo puede "reconocer" la
institución. `GroupKFold` con `groups=inst_cod_institucion` (5 folds, sin
shuffle) garantiza que cada fold se evalúe sobre **instituciones nunca vistas
en entrenamiento**, que es el caso de uso real: predecir para cualquier
estudiante, de cualquier institución (`09_validacion_groupkfold.md`).

### 3.4 Resultado

| Escenario | Predictores | Macro F1 (OOF) | Balanced accuracy (OOF) |
|---|---:|---:|---:|
| A — con institución/geografía | 43 | 0.2711 | 0.3223 |
| **B — sin institución/geografía** | **27** | **0.3721** | **0.3759** |

El escenario B generaliza mejor a instituciones no vistas (+0.1010 de macro F1
y +0.0536 de balanced accuracy; `09_validacion_groupkfold.md`). Como referencia
adicional, el mismo tipo de modelo con institución alcanzó macro F1 = 0.465 con
una partición aleatoria (`06_random_forest_mdi.md`), aunque esa comparación no
es controlada: difieren la partición, la representación de la edad y el manejo
de categorías desconocidas (`09_validacion_groupkfold.md`, sección
Interpretation and limitations). La caída de ≈0.47 a 0.27 al pasar a
instituciones no vistas es consistente con memorización, no una prueba de ella.

Mecanismo documentado: los códigos de institución no vistos se codifican como
desconocido (−1) y el modelo no aprende a extrapolar identidades nuevas
(`09_validacion_groupkfold.md`).

### 3.5 Por qué el modelo final es B

1. **Mejor generalización medida** (0.37 frente a 0.27 de macro F1).
2. **Coherencia con el caso de uso:** debe servir para estudiantes de
   cualquier institución, incluidas las que no están en los datos.
3. **Robusto a la fuga de preprocesamiento:** en el paso 12 se reajustó la
   imputación dentro de cada fold; el resultado prácticamente no cambió
   (macro F1 0.3787 → 0.3786; balanced accuracy 0.3930 → 0.3924), por lo que el
   desempeño de B no dependía de esa fuga (`12_modelo_final_sin_fuga.md`).
4. **Reentrenamiento final con el 100 % de los datos** (30.738 filas) con los
   hiperparámetros del paso 10. No es una prueba de generalización, porque esa
   ya se hizo en 09, 10 y 12; es el artefacto que se usa para predecir
   (`14_entrenamiento_modelo_final.md`).

### 3.6 Por qué se conserva A como referencia

El escenario A se entrenó y se persistió solo como **modelo de referencia**
(pasos 17 y 18), para mostrar lado a lado cómo cambia la predicción cuando se
conoce la institución. No se ajustaron sus hiperparámetros (300 árboles,
`class_weight='balanced'`), porque el paso 09 ya lo había descartado como
candidato (`17_modelo_referencia_institucion.md`). La comparación que decide
entre A y B es la del paso 09, donde ambos usaron exactamente la misma
configuración. El paso 18 muestra con un estudiante de ejemplo que ambos
modelos pueden discrepar (nivel 1 con 37 % frente a nivel 3 con 46 %), y por eso
el modelo B sigue siendo el que se debe considerar
(`18_comparacion_con_sin_institucion.md`).

---

## 4. Limitaciones y puntos abiertos

- **Asociación, no causalidad.** Estrato, educación de los padres, trabajo y
  forma de pago se mueven juntos; el modelo detecta contextos, no causas
  (`08_shap.md`, `11_conclusion_importancia_variables.md`).
- **Desempeño absoluto modesto.** Un macro F1 ≈ 0.38 en 4 clases confirma que
  la mayor parte de la variación depende de factores ausentes del dataset
  (historial académico previo, tipo de colegio; ver
  `13_explicacion_modelo_y_datos_faltantes.md`).
- **Exclusión completa de lo institucional en B.** El escenario B excluye
  también `inst_origen` e `inst_caracter_academico`. Sin embargo, `inst_origen`
  (oficial o privada) fue la tercera variable en permutation importance
  (0.0220, `07_permutation_importance.md`) y SHAP la describe como una señal más
  general que el código puntual de institución (`08_shap.md`). Un escenario
  intermedio (B + tipo de institución), validado con `GroupKFold`, queda
  pendiente como mejora: permitiría medir si esa señal es transferible a
  instituciones nuevas.
- **A no fue ajustado.** No altera la conclusión (la diferencia es de 0.10 y el
  ajuste aportó solo +0.0066 a B), pero la comparación final entre modelos
  persistidos no es simétrica.
- **Validación institucional, no temporal.** No se evaluó entrenar con años
  anteriores y predecir años posteriores (`09_validacion_groupkfold.md`).
- **Fuga residual de imputación en 09 y 10.** El paso 03 imputó el dataset
  completo antes de los folds; el paso 12 la corrige para B
  (`09_validacion_groupkfold.md`, `12_modelo_final_sin_fuga.md`).
- **Sin comparación con otros algoritmos.** No se evaluó, por ejemplo, un modelo
  más simple como regresión logística ordinal
  (`11_conclusion_importancia_variables.md`).

---

## 5. Resumen

| Decisión | Fundamento | Evidencia |
|---|---|---|
| MI como primer filtro (05) | Rápida, válida con variables mixtas, ordena las candidatas | `inst_cod_institucion` con MI 0.2078, 2.6 veces la siguiente |
| Random Forest + MDI (06) | Modelo base para toda la secuencia; MDI solo como comparación | F1 macro 0.465 en holdout aleatorio; sesgo de cardinalidad en fecha de nacimiento y ocupaciones |
| Permutation importance (07) | Mide sobre test y con F1 macro | Ocupaciones de los padres caen a #28/#14; institución sigue primera (0.0765) |
| SHAP (08) | Contribución por clase y por predicción | Institución dominante, sobre todo en nivel 4; no prueba generalización |
| Random Forest como modelo | Datos mixtos, clases desbalanceadas (`class_weight='balanced'`), compatible con MDI/permutation/SHAP | Pasos 04 y 06; sin benchmark contra otros algoritmos |
| Ajuste de hiperparámetros solo en B | B es el candidato elegido en 09 | +0.0066 macro F1; el techo está en los datos |
| Comparar escenarios A y B | Ablación controlada para distinguir señal transferible de memorización | Mismas filas, folds y modelo; solo cambian 16 columnas |
| GroupKFold por institución | Simula el caso real: instituciones nuevas | Macro F1 0.2711 (A) frente a 0.3721 (B) con instituciones no vistas |
| Modelo final = B, 100 % de los datos | Mejor generalización y coherencia con el uso | Macro F1 0.3786 y balanced accuracy 0.3924 con imputación por fold (paso 12) |

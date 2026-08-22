# Árbol de Decisión

Modelo base interpretable para predecir `PUNT_GLOBAL` a partir de las ~24 columnas finales (`docs/dataset/dataset_final_ml.md`).

## ¿Cómo funciona?

Un árbol de decisión de regresión predice el target dividiendo los datos en grupos cada vez más chicos mediante preguntas binarias sobre las features (ej. "¿es Universidad de los Andes? sí/no"). En cada nodo:

1. Prueba todos los posibles cortes de todas las variables.
2. Elige el corte que **más reduce la varianza** del `PUNT_GLOBAL` dentro de cada grupo resultante (el grupo queda más "homogéneo" en puntaje).
3. Repite el proceso dentro de cada grupo, de forma recursiva, hasta llegar a una hoja.
4. La predicción final para un estudiante nuevo es el **promedio de `PUNT_GLOBAL`** de todos los estudiantes de entrenamiento que cayeron en esa misma hoja.

**El riesgo central es el overfitting**: si no se limita la profundidad, el árbol sigue cortando hasta casi memorizar cada fila individual (como pasó acá: 17.443 hojas para ~18.500 filas de entrenamiento → R² negativo en datos nuevos). Por eso se usan dos frenos:
- `max_depth`: cuántos niveles de preguntas puede hacer como máximo.
- `min_samples_leaf`: cuántos estudiantes como mínimo tiene que haber en un grupo final para aceptarlo como hoja (evita hojas de 1-2 estudiantes que son ruido, no patrón).

**Feature importance** se calcula sumando, para cada variable, cuánta reducción de varianza total aportó en todos los cortes donde se usó — por eso una variable que aparece en el primer corte (como el tipo de institución) casi siempre domina el ranking: afecta a todos los estudiantes, no a un subgrupo.

Ventaja frente a Mutual Information: el árbol muestra **combinaciones** de variables (ej. "si es institución universitaria Y no oficial, el puntaje baja"), mientras que MI evalúa cada variable de forma aislada.

- `decision_tree_analysis.py` — entrena dos árboles para comparar:
  - **Sin podar**: referencia de overfitting. R² = -0.24 (peor que predecir la media) con 17.443 hojas — memoriza el set de entrenamiento.
  - **Podado** (`max_depth=4`, `min_samples_leaf=50`): R² = 0.29, MAE = 15.84. Generaliza, se usa para interpretar.
- `feature_importance.csv` — importancia de cada variable (one-hot) en el árbol podado.
- `tree_rules.txt` — reglas de corte legibles (`export_text`).

## Hallazgo principal

El primer corte del árbol es por tipo de institución (`INST_ORIGEN`, `INST_CARACTER_ACADEMICO`), consistente con el resultado de Mutual Information: la institución es, por lejos, el factor más explicativo del puntaje global.

Corre desde la raíz del proyecto (lee `ESTU_MEDICINA_3_MODULOS.xlsx` con ruta relativa).

# Mutual Information

Ranking de importancia de variables contra `PUNT_GLOBAL` usando Mutual Information (`sklearn.feature_selection.mutual_info_regression`).

## ¿Cómo funciona?

Mutual Information (MI) mide cuánta **incertidumbre sobre el target se reduce** al conocer el valor de una variable, sin asumir que la relación es lineal — a diferencia de la correlación de Pearson, que solo detecta relaciones en forma de línea recta.

- Si una variable no aporta nada para adivinar `PUNT_GLOBAL`, su MI es ≈ 0 (independencia).
- Cuanto más alta la MI, más se reduce la incertidumbre al conocer esa variable — sin importar si la relación es lineal, en forma de U, categórica, etc.
- Se mide en **nats** (logaritmo natural), no tiene techo fijo como un porcentaje o un R². Por eso no se interpreta como "explica el X%", sino de forma **relativa**: una variable con MI=0.25 aporta ~10 veces más información que una con MI=0.025.
- Internamente usa un estimador de vecinos más cercanos (KSG) que no necesita discretizar ni asumir una distribución — funciona igual de bien mezclando variables numéricas y categóricas, que es el caso de este dataset.
- Valores muy pequeños (< 0.01) no son "señal débil real", son ruido estadístico del estimador — se tratan como cero.

Ventaja principal para este análisis: al no asumir linealidad, detecta relaciones que una correlación se perdería, y funciona sin necesitar imputar de una forma especial más allá de rellenar nulos antes de calcular.

- `mutual_info_analysis.py` — corre MI solo sobre las ~24 columnas finales seleccionadas en `docs/dataset/dataset_final_ml.md` (sin fuga de datos, sin columnas vacías/redundantes). Genera `mutual_info_ranking_24.csv`.
- `mutual_info_full_80.py` — corre MI sobre las 78 columnas originales (excluye solo `ESTU_CONSECUTIVO` por ser ID único). Se usa para validar con números el filtro aplicado en el dataset final. Genera `mutual_info_ranking_78.csv`.

Ambos scripts esperan correrse desde la raíz del proyecto (leen `ESTU_MEDICINA_3_MODULOS.xlsx` con ruta relativa).

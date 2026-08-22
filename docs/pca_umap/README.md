# PCA + UMAP

Técnicas de reducción de dimensionalidad, exploratorias — no explican causalidad, ayudan a **visualizar** estructura.

## ¿Cómo funciona PCA?

PCA (Análisis de Componentes Principales) busca **nuevos ejes** (combinaciones lineales de las columnas originales) ordenados de mayor a menor varianza explicada. El primer eje (PC1) es la dirección donde los datos varían más; PC2 es la siguiente dirección de mayor varianza que además es perpendicular a PC1, y así sucesivamente. Es una técnica **lineal**: solo encuentra combinaciones tipo `a*col1 + b*col2 + ...`, no relaciones curvas.

## ¿Cómo funciona UMAP?

UMAP construye un grafo de vecinos más cercanos en el espacio original (alta dimensión) y después busca una proyección en 2D que preserve esa vecindad lo mejor posible — si dos estudiantes son "parecidos" en las ~140 columnas (tras one-hot), UMAP intenta ponerlos cerca en el mapa 2D. A diferencia de PCA, **no es lineal**, puede capturar clusters con formas arbitrarias.

## Resultado y por qué es limitado acá

Ambas técnicas trabajan sobre distancias/varianza en el espacio numérico. Este dataset tiene solo 2 columnas realmente numéricas (`ESTU_INSE_INDIVIDUAL`, `EDAD`); el resto son ~140 columnas binarias de one-hot (institución, estrato, etc.). Eso genera dos problemas visibles en los resultados:

- **PCA**: PC1 explica solo 4.3% de la varianza (`pca_explained_variance.csv`), y hacen falta 10 componentes para pasar de 22%. El scatter (`pca_scatter_puntaje.png`) muestra "rayas" — artefacto típico de PCA sobre variables binarias — sin gradiente de color limpio por `PUNT_GLOBAL`.
- **UMAP** (`umap_scatter_puntaje.png`, `umap_scatter_caracter.png`): se forman ~55 clusters bien separados, uno por institución — porque la distancia euclidiana en one-hot está dominada por "¿es la misma universidad?". Cada cluster es casi monocromático en carácter académico y en puntaje, pero esto es la **misma información que ya teníamos** de Mutual Information/SHAP (institución domina), no un hallazgo nuevo.

## Conclusión

Con este dataset, PCA/UMAP sirven para **confirmar visualmente** que la institución es el eje dominante, pero no para descubrir estructura nueva — el problema real es que el dataset es mayormente categórico con muy pocas variables continuas, así que las técnicas basadas en distancia/varianza tienen poco con qué trabajar. Mutual Information + SHAP siguen siendo las herramientas más informativas para este caso.

## Archivos

- `pca_umap_analysis.py`
- `pca_explained_variance.csv`
- `pca_scatter_puntaje.png`
- `umap_scatter_puntaje.png`
- `umap_scatter_caracter.png`

Corre desde la raíz del proyecto (lee `ESTU_MEDICINA_3_MODULOS.xlsx` con ruta relativa).

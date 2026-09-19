# Saber Pro Medicina — Variables asociadas con `PUNT_GLOBAL`

Análisis exploratorio de machine learning sobre los resultados de Saber Pro
(ICFES, Colombia) para estudiantes de Medicina, con el objetivo de identificar
qué variables se asocian con el puntaje global (`PUNT_GLOBAL`) y qué tan
confiable es esa señal cuando se valida correctamente.

## Resultado principal

El hallazgo inicial (la institución domina todos los rankings de importancia)
resultó estar inflado por memorización: el nombre puntual de una institución
no generaliza a instituciones nuevas, pero el **tipo** de institución sí. El
modelo final recomendado combina esa señal real con variables demográficas y
socioeconómicas, validado con instituciones nunca vistas (`GroupKFold`):
**R² ≈ 0.23**, frente al R² = 0.37 original (inflado) y a los ~0.12-0.19 que
resultan de descartar la institución sin más o de validarla sin corregir el
sesgo de memorización.

El detalle completo está en el informe consolidado:
[`docs/conclusiones/conclusion_final.md`](docs/conclusiones/conclusion_final.md)
(también disponible como PDF en esa misma carpeta).

## Cómo reproducir los análisis

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Cada etapa se ejecuta desde la raíz del repositorio, por ejemplo:

```bash
python docs/etapa_3_random_forest_shap/random_forest_shap_analysis.py
```

Los scripts leen `ESTU_MEDICINA_3_MODULOS.xlsx` (en la raíz) y escriben sus
resultados (CSVs, gráficos) dentro de su propia carpeta de etapa. El informe
consolidado se regenera con:

```bash
python docs/conclusiones/generar_pdf.py
```

## Estructura del proyecto

| Carpeta | Contenido |
|---|---|
| `docs/dataset/` | Documentación del dataset y las variables disponibles |
| `docs/etapa_1_mutual_information/` | Ranking de variables por Mutual Information |
| `docs/etapa_2_decision_tree/` | Árbol de decisión interpretable |
| `docs/etapa_3_random_forest_shap/` | Random Forest + SHAP (feature set completo, split único) |
| `docs/etapa_4_pca_umap/` | PCA/UMAP exploratorio (feature set completo) |
| `docs/etapa_5_sin_institucion_cv/` | Random Forest sin variables de institución, con validación cruzada |
| `docs/etapa_6_groupkfold_institucion/` | Random Forest con institución, validado con `GroupKFold` por institución (instituciones no vistas) |
| `docs/etapa_7_permutation_importance/` | Permutation importance vs. MDI/Gini — separa memorización de señal real |
| `docs/etapa_8_modelo_final_honesto/` | **Modelo final recomendado**: señal institucional real + validación honesta |
| `docs/etapa_9_pca_umap_sin_institucion/` | PCA/UMAP sin institución — confirma que los clusters de la etapa 4 eran identidad institucional |
| `docs/conclusiones/` | Informe consolidado (Markdown + PDF) y su generador |

Cada carpeta de etapa tiene su propio script de análisis, sus artefactos
(CSVs, gráficos) y, a partir de la etapa 5, un archivo `etapa_N_conclusion.md`
con el detalle de esa validación puntual.

## Limitaciones

Los análisis muestran asociación, no causalidad, y el dataset no incluye
variables como preparación para el examen, horas de estudio o trayectoria
escolar previa. El detalle completo de limitaciones está en la sección
correspondiente de `docs/conclusiones/conclusion_final.md`.

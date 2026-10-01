# Saber Pro Medicina 2021–2024 — Variables asociadas con `nivel_desempeno`

Análisis y modelo de clasificación sobre los resultados de Saber Pro (ICFES,
Colombia) de estudiantes de Medicina, periodos 2021–2024. El objetivo es
identificar qué variables del estudiante y de su contexto se asocian con el
nivel de desempeño (`nivel_desempeno`, niveles 1–4, derivado de `punt_global`)
y qué tan bien se puede predecir ese nivel **antes** de que el estudiante
presente el examen, validando con instituciones que el modelo nunca vio en el
entrenamiento.

## Resultado principal

El modelo recomendado es el **escenario B**: Random Forest con 27 predictores
demográficos y socioeconómicos, sin institución ni geografía, validado con
`GroupKFold` por institución (5 folds, 55 instituciones, 30.738 filas), con la
imputación ajustada dentro de cada fold
([paso 12](docs_2021_2024/12_modelo_final_sin_fuga.md)):

| Escenario | Predictores | Macro F1 (OOF) | Balanced accuracy (OOF) |
|---|---:|---:|---:|
| **B — sin institución/geografía (modelo final)** | 27 | **0.3786** | **0.3924** |
| A — con institución/geografía (referencia) | 43 | 0.2711 | 0.3223 |

Los valores de B provienen del paso 12 y los de A del paso
[17](docs_2021_2024/17_modelo_referencia_institucion.md) (medidos en el paso
[09](docs_2021_2024/09_validacion_groupkfold.md)). Con instituciones nuevas, la
institución deja de ayudar: el modelo B generaliza mejor que el A. Las
variables socioeconómicas más consistentes son estrato, horas de trabajo
semanal, educación de los padres, forma de pago de matrícula y semestre que
cursa ([paso 11](docs_2021_2024/11_conclusion_importancia_variables.md)).

`punt_global` se reconstruye en el paso 02 y es la fuente de
`nivel_desempeno`; se excluye de los predictores (junto con los demás
resultados del examen, 18 columnas en total) para evitar fuga de información.

## Cómo reproducir

Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ejecutar los scripts de `scripts_2021_2024/` en orden numérico. Los pasos 04,
11, 13, 16 y 18 son solo documentación (no tienen script propio).

```bash
python scripts_2021_2024/01_analisis_nulos.py
python scripts_2021_2024/02_tratamiento_datos.py      # escribe dataset_medicina_procesado.csv
python scripts_2021_2024/03_imputacion_datos.py
python scripts_2021_2024/05_mutual_information.py
python scripts_2021_2024/06_random_forest_mdi.py
python scripts_2021_2024/07_permutation_importance.py
python scripts_2021_2024/08_shap.py
python scripts_2021_2024/09_validacion_groupkfold.py
python scripts_2021_2024/10_tuning_modelo_b.py
python scripts_2021_2024/12_modelo_final_sin_fuga.py
python scripts_2021_2024/14_entrenar_modelo_final.py   # guarda el modelo B en modelos_2021_2024/
python scripts_2021_2024/17_entrenar_modelo_referencia_institucion.py
```

Los pasos 02 y 03 generan `dataset_medicina_procesado.csv` a partir de
`dataset_medicina.csv`; los pasos 05–10 lo leen. Los pasos 12, 14 y 17 leen
directamente el CSV crudo.

### Predicción de un estudiante nuevo

```bash
python scripts_2021_2024/15_predecir_estudiante.py modelos_2021_2024/ejemplo_estudiante.json
```

Imprime el nivel predicho de los dos modelos (B y A) y la probabilidad de cada
clase ([paso 15](docs_2021_2024/15_prediccion_estudiante_nuevo.md) y
[paso 18](docs_2021_2024/18_comparacion_con_sin_institucion.md)).

### API y dashboard

El dashboard (Next.js) consume una API local FastAPI. Se ejecutan en dos
terminales, desde la raíz del repositorio
([paso 16](docs_2021_2024/16_interfaz_visual.md)):

```bash
# Terminal 1 — API de predicción
uvicorn api_2021_2024.main:app --port 8001

# Terminal 2 — dashboard (Node >= 20.9)
cd dashboard
npm install
npm run dev
```

Abrir `http://localhost:3000`. Si la API no está activa, el formulario muestra
un error 503 explícito.

## Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `dataset_medicina.csv` | Datos crudos 2021–2024 (30.742 filas) |
| `dataset_medicina_procesado.csv` | Datos tratados e imputados (pasos 02 y 03) |
| `scripts_2021_2024/` | Scripts numerados por paso, más `common.py` y `prediccion_core.py` (lógica compartida de predicción) |
| `docs_2021_2024/` | Documentación de cada paso (01–19) y sus reportes en CSV/log |
| `modelos_2021_2024/` | Modelos persistidos (B y A), metadatos, lista de instituciones y estudiante de ejemplo |
| `api_2021_2024/` | API FastAPI de predicción (`main.py`) |
| `dashboard/` | Interfaz web Next.js con el formulario de predicción |

## Pasos

| Paso | Documento | Tema |
|---|---|---|
| 01 | [01_dataset_medicina_nulos.md](docs_2021_2024/01_dataset_medicina_nulos.md) | Cobertura por año y porcentaje de nulos |
| 02 | [02_tratamiento_datos.md](docs_2021_2024/02_tratamiento_datos.md) | Reconstrucción de `punt_global` y creación de `nivel_desempeno` |
| 03 | [03_imputacion_datos.md](docs_2021_2024/03_imputacion_datos.md) | Plan de imputación de nulos |
| 04 | [04_importancia_variables_conceptos.md](docs_2021_2024/04_importancia_variables_conceptos.md) | Conceptos y orden de las técnicas de importancia (solo doc) |
| 05 | [05_mutual_information.md](docs_2021_2024/05_mutual_information.md) | Mutual Information |
| 06 | [06_random_forest_mdi.md](docs_2021_2024/06_random_forest_mdi.md) | Random Forest e importancia MDI |
| 07 | [07_permutation_importance.md](docs_2021_2024/07_permutation_importance.md) | Permutation importance |
| 08 | [08_shap.md](docs_2021_2024/08_shap.md) | SHAP |
| 09 | [09_validacion_groupkfold.md](docs_2021_2024/09_validacion_groupkfold.md) | Validación con instituciones no vistas (escenarios A y B) |
| 10 | [10_tuning_modelo_b.md](docs_2021_2024/10_tuning_modelo_b.md) | Ajuste de hiperparámetros del modelo B |
| 11 | [11_conclusion_importancia_variables.md](docs_2021_2024/11_conclusion_importancia_variables.md) | Conclusión sobre importancia de variables (solo doc) |
| 12 | [12_modelo_final_sin_fuga.md](docs_2021_2024/12_modelo_final_sin_fuga.md) | Modelo B con imputación dentro de cada fold |
| 13 | [13_explicacion_modelo_y_datos_faltantes.md](docs_2021_2024/13_explicacion_modelo_y_datos_faltantes.md) | Explicación en lenguaje simple y datos que faltan (solo doc) |
| 14 | [14_entrenamiento_modelo_final.md](docs_2021_2024/14_entrenamiento_modelo_final.md) | Entrenamiento final con el 100 % de los datos |
| 15 | [15_prediccion_estudiante_nuevo.md](docs_2021_2024/15_prediccion_estudiante_nuevo.md) | Predicción para un estudiante nuevo (CLI) |
| 16 | [16_interfaz_visual.md](docs_2021_2024/16_interfaz_visual.md) | API y dashboard (solo doc; código en `api_2021_2024/` y `dashboard/`) |
| 17 | [17_modelo_referencia_institucion.md](docs_2021_2024/17_modelo_referencia_institucion.md) | Modelo de referencia A, con institución |
| 18 | [18_comparacion_con_sin_institucion.md](docs_2021_2024/18_comparacion_con_sin_institucion.md) | Comparación lado a lado (cambios en CLI, API y dashboard; solo doc) |
| 19 | [19_fundamentacion_modelos_y_escenarios.md](docs_2021_2024/19_fundamentacion_modelos_y_escenarios.md) | Fundamentación de la metodología y los escenarios |

## Limitaciones

- **Asociación, no causalidad.** El modelo detecta contextos que se mueven
  juntos con el desempeño, no efectos atribuibles a una variable.
- **Techo de desempeño modesto.** Un macro F1 ≈ 0.38 en 4 clases está por
  encima del azar, pero no es confiable para decisiones sobre un estudiante
  individual; el ajuste de hiperparámetros solo aportó +0.0066 de macro F1
  (pasos 10 y 13). La palanca es contar con variables nuevas (historial
  académico previo, tipo de colegio), no cambiar el modelo.
- **Validación institucional, no temporal.** Se probó con instituciones no
  vistas; no se evaluó entrenar con años anteriores y predecir posteriores
  (paso 09).
- **Fuga de preprocesamiento en el CSV procesado.** Los pasos 09 y 10 parten de
  una imputación global (paso 03); el paso 12 la corrige dentro de cada fold y
  el resultado casi no cambia (0.3787 → 0.3786).
- La API y el dashboard son un entorno de desarrollo local, sin autenticación
  (paso 16).

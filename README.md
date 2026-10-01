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

## Requisitos

Verificado en una copia limpia del repositorio (`git clone`) sobre macOS 26.6.2
(Apple Silicon, arm64):

| Herramienta | Versión probada | Notas |
|---|---|---|
| Python | 3.14.7 | `requirements.txt` fija versiones exactas probadas con 3.14.7 |
| Node.js | 24.19.0 | `dashboard/package.json` exige `>=20.9.0` (solo para el dashboard) |
| npm | 12.0.2 | El dashboard trae `package-lock.json` |
| Espacio en disco | ~1,4 GB solo para modelos | Los dos modelos `.joblib` pesan 769 MB y 590 MB |

Los comandos usan `python`/`pip` dentro del entorno virtual y `.venv/bin/...`
para que funcionen igual con el entorno activado o sin activar. En Windows la
ruta del entorno es `.venv\Scripts\` (no probado).

## Inicio rápido: solo quiero usar la predicción

Los modelos (`modelos_2021_2024/*.joblib`) **no están en git** (`.gitignore`);
hay que generarlos una vez. Con los datos ya incluidos en el repo toma menos de
10 s en total (paso 14: 5 s, paso 17: 3 s en la prueba).

```bash
git clone https://github.com/CT-Zodiako/medicina.git medicina && cd medicina
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1. Generar los dos modelos
python scripts_2021_2024/14_entrenar_modelo_final.py
python scripts_2021_2024/17_entrenar_modelo_referencia_institucion.py

# 2. Terminal 1 (raíz del repo): API en el puerto 8001
.venv/bin/uvicorn api_2021_2024.main:app --port 8001

# 3. Terminal 2: dashboard en el puerto 3000
cd dashboard && npm ci && npm run dev
```

Abrir `http://localhost:3000`. Sin los archivos `.joblib`, la CLI y la API
fallan (ver [Problemas frecuentes](#problemas-frecuentes)).

## Cómo reproducir todo el pipeline

### 1. Clonar e instalar

```bash
git clone https://github.com/CT-Zodiako/medicina.git medicina && cd medicina
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt      # ~20 s
```

### 2. Ejecutar los scripts en orden

Desde la raíz del repositorio. Los pasos 04, 11, 13, 16, 18 y 19 son solo
documentación (no tienen script). Duraciones medidas en la prueba de
reproducción (Apple Silicon, ejecución secuencial):

| Paso | Comando | Lee | Escribe | Duración |
|---|---|---|---|---|
| 01 | `python scripts_2021_2024/01_analisis_nulos.py` | `dataset_medicina.csv` | `docs_2021_2024/01_null_pct_by_year.csv` | ~36 s |
| 02 | `python scripts_2021_2024/02_tratamiento_datos.py` | `dataset_medicina.csv` | `dataset_medicina_procesado.csv` | ~1 s |
| 03 | `python scripts_2021_2024/03_imputacion_datos.py` | `dataset_medicina_procesado.csv` | `dataset_medicina_procesado.csv` (sobrescribe) | ~1 s |
| 05 | `python scripts_2021_2024/05_mutual_information.py` | procesado | `docs_2021_2024/05_mutual_information_results.csv` | ~1 s |
| 06 | `python scripts_2021_2024/06_random_forest_mdi.py` | procesado | `docs_2021_2024/06_random_forest_mdi_results.csv` | ~2 s |
| 07 | `python scripts_2021_2024/07_permutation_importance.py` | procesado | `docs_2021_2024/07_permutation_importance_results.csv` | ~52 s |
| 08 | `python scripts_2021_2024/08_shap.py` | procesado | `docs_2021_2024/08_shap_summary.csv` | ~41 s |
| 09 | `python scripts_2021_2024/09_validacion_groupkfold.py` | procesado | `docs_2021_2024/09_validacion_groupkfold.md` | ~12 s |
| 10 | `python scripts_2021_2024/10_tuning_modelo_b.py` | procesado | `docs_2021_2024/10_tuning_modelo_b.md` | ~190 s |
| 12 | `python scripts_2021_2024/12_modelo_final_sin_fuga.py` | `dataset_medicina.csv` | `docs_2021_2024/12_modelo_final_sin_fuga.md` | ~35 s |
| 14 | `python scripts_2021_2024/14_entrenar_modelo_final.py` | `dataset_medicina.csv` | `modelos_2021_2024/modelo_final_nivel_desempeno.joblib` y `_metadata.json`, `docs_2021_2024/14_entrenamiento_modelo_final.md` | ~5 s |
| 17 | `python scripts_2021_2024/17_entrenar_modelo_referencia_institucion.py` | `dataset_medicina.csv` | `modelos_2021_2024/modelo_referencia_con_institucion.joblib` y `_metadata.json`, `instituciones.json`, `docs_2021_2024/17_modelo_referencia_institucion.md` | ~3 s |

Tiempo total: unos 6 minutos (el paso 10, búsqueda de hiperparámetros, es el
más largo).

Orden y dependencias:

- 02 debe correr antes que 03, y ambos antes de 05–10, porque estos leen
  `dataset_medicina_procesado.csv`. El repo ya incluye una versión generada de
  ese archivo, así que re-ejecutar 02 y 03 es opcional.
- Los pasos 12, 14 y 17 leen el CSV crudo directamente y no dependen de 02–10.
- Los scripts resuelven las rutas respecto al repositorio (`common.py`), pero
  se recomienda ejecutarlos desde la raíz.

Los pasos 14 y 17 son los únicos que **deben** ejecutarse antes de usar la CLI,
la API o el dashboard.

### Reproducibilidad verificada

En la copia limpia se ejecutaron los 12 scripts anteriores. Después de la
corrida, `git status` no mostró ningún archivo modificado: el CSV procesado, los
CSV de resultados y los informes `.md` regenerados son idénticos byte a byte a
los versionados. Los números clave coinciden con los de este documento (por
ejemplo, el paso 10 reportó macro F1 0.3787 y el paso 14 reportó macro F1 OOF
0.3786, balanced accuracy 0.3924).

Los archivos `docs_2021_2024/10_tuning_modelo_b.log` y
`docs_2021_2024/12_modelo_final_sin_fuga.log` son la salida de consola de esos
scripts guardada a mano; los scripts no los escriben.

## Uso

### CLI: predecir un estudiante

Requiere los modelos de los pasos 14 y 17.

```bash
python scripts_2021_2024/15_predecir_estudiante.py modelos_2021_2024/ejemplo_estudiante.json
```

Imprime el nivel predicho y la probabilidad de cada clase para el modelo de
producción (B) y el de referencia (A) ([paso
15](docs_2021_2024/15_prediccion_estudiante_nuevo.md) y [paso
18](docs_2021_2024/18_comparacion_con_sin_institucion.md)). Con el ejemplo
incluido, la salida observada fue: modelo B nivel 1 (probabilidad 0.3685) y
modelo A nivel 3 (0.4533); el script avisa que los dos modelos discrepan y que
debe preferirse B. Los campos ausentes del JSON se imputan con los valores
ajustados del entrenamiento.

### API (FastAPI, puerto 8001)

Desde la raíz del repositorio:

```bash
.venv/bin/uvicorn api_2021_2024.main:app --port 8001   # añadir --reload en desarrollo
```

| Endpoint | Descripción |
|---|---|
| `GET /metadata` | Contrato de entrada (orden de campos, roles) de ambos modelos |
| `GET /instituciones` | Lista de código y nombre de institución del modelo A |
| `POST /predict` | Predicción de ambos modelos (`produccion_sin_institucion` y `referencia_con_institucion`) |
| `GET /docs` | Documentación interactiva (Swagger) generada por FastAPI |

```bash
curl -X POST http://127.0.0.1:8001/predict \
  -H 'Content-Type: application/json' \
  -d @modelos_2021_2024/ejemplo_estudiante.json
```

Respuesta observada (HTTP 200, recortada): `produccion_sin_institucion` con
`predicted_level: 1`, `probabilities` por nivel, `low_confidence: true` y
`validated_performance` (macro F1 0.3786); `referencia_con_institucion` con
`predicted_level: 3`. Un valor inválido (por ejemplo
`{"fami_estratovivienda": "Estrato 99"}`) devuelve HTTP 422 con la lista de
valores permitidos. No existe un endpoint `/health`. La API no tiene
autenticación y solo permite CORS desde `http://localhost:3000` y
`http://127.0.0.1:3000`.

### Dashboard (Next.js, puerto 3000)

Necesita la API corriendo. Se ejecutan dos procesos, cada uno en su terminal
([paso 16](docs_2021_2024/16_interfaz_visual.md)):

```bash
# Terminal 1 (raíz del repo)
.venv/bin/uvicorn api_2021_2024.main:app --port 8001

# Terminal 2
cd dashboard
npm ci                # primera vez (usa package-lock.json)
npm run dev           # desarrollo: http://localhost:3000
```

Build de producción (verificado: compila sin errores en ~9 s):

```bash
npm run build && npm run start      # sirve en http://localhost:3000
```

El navegador nunca habla con Python: las rutas `dashboard/src/app/api/predict`
(`GET` = metadata, `POST` = predicción) y `dashboard/src/app/api/instituciones`
hacen de proxy hacia la API.

| Variable | Por defecto | Uso |
|---|---|---|
| `PREDICTION_API_URL` | `http://127.0.0.1:8001` | URL base de la API FastAPI; cambiarla si la API corre en otro host o puerto (no hay archivos `.env` de ejemplo) |

Verificado con ambos procesos activos: `GET /` devuelve 200 y
`POST http://localhost:3000/api/predict` con el JSON de ejemplo devuelve la
misma predicción que la API directa. Con la API detenida, el formulario muestra
un error 503 explícito. Si cambia el puerto del dashboard, hay que actualizar
`allow_origins` en `api_2021_2024/main.py`.

## Problemas frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `FileNotFoundError: ... modelo_final_nivel_desempeno.joblib` al usar la CLI; `POST /predict` devuelve `500 Internal Server Error` | Los `.joblib` no están en git | Ejecutar los pasos 14 y 17 |
| `ModuleNotFoundError: No module named 'api_2021_2024'` al lanzar `uvicorn` | Se ejecutó fuera de la raíz del repo | Lanzar `uvicorn api_2021_2024.main:app --port 8001` desde la raíz |
| `ModuleNotFoundError: No module named 'joblib'` (o `pandas`, `fastapi`) | Se usó el `python3` del sistema en vez del entorno virtual | `source .venv/bin/activate && pip install -r requirements.txt`, o usar `.venv/bin/python` |
| El formulario muestra 503 / "¿está corriendo uvicorn?" | La API no está activa en `PREDICTION_API_URL` | Iniciar la API en el puerto 8001 o ajustar `PREDICTION_API_URL` |
| HTTP 404 en `/health` | La API no define ese endpoint | Probar con `GET /instituciones` o `GET /docs` |
| HTTP 422 en `/predict` | Un valor no coincide con las categorías esperadas | Usar los textos exactos de `modelos_2021_2024/ejemplo_estudiante.json` o el detalle del error |
| `npm ci` muestra `install-scripts ... unrs-resolver ... blocked` | Aviso de npm 12 sobre scripts de instalación | Es solo un aviso; `npm run build` funciona sin aprobarlo |
| El puerto 3000 u 8001 ya está ocupado por otro proceso (en la prueba, otro servidor local usaba el 3000) | Conflicto de puertos | Detener el otro proceso, o usar otro puerto y actualizar `PREDICTION_API_URL` (API) y `allow_origins` en `api_2021_2024/main.py` (dashboard); no probado con puertos alternativos |

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

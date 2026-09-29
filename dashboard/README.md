# Dashboard — Predicción de nivel de desempeño

App Next.js (App Router + TypeScript) con un único formulario: predice el
nivel de desempeño (1-4) de un estudiante de Medicina que aún no presentó el
examen Saber Pro, usando el modelo entrenado en
`modelos_2021_2024/modelo_final_nivel_desempeno.joblib`.

## Desarrollo

Necesita la API de predicción corriendo en paralelo (backend Python, no
Node). Desde la raíz del repo:

```bash
# Terminal 1
.venv/bin/uvicorn api_2021_2024.main:app --port 8001

# Terminal 2
cd dashboard
npm install
npm run dev
```

Abre `http://localhost:3000`.

## Build de producción

```bash
npm run build
npm start
```

## Cómo se conecta con el modelo

`src/app/api/predict/route.ts` es un Route Handler que hace de proxy hacia
`http://127.0.0.1:8001/predict` (la API FastAPI). El navegador nunca le habla
directo a Python. Ver
`docs_2021_2024/16_interfaz_visual.md` en la raíz del repo para la
arquitectura completa y las limitaciones del modelo.

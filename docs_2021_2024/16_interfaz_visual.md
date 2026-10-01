# Visual interface — predicting a new student from the dashboard

Continuation of [15_prediccion_estudiante_nuevo.md](15_prediccion_estudiante_nuevo.md).
Adds a form to the existing Next.js dashboard, backed by a small local
FastAPI service that wraps the same `prediccion_core` module the CLI uses.

## Architecture

```
Browser (localhost:3000)
  └─ dashboard/src/app/page.tsx                   (form UI, route `/`)
       └─ POST /api/predict (Next.js Route Handler, same origin)
            └─ proxies to → http://127.0.0.1:8001/predict (FastAPI)
                 └─ scripts_2021_2024/prediccion_core.py
                      └─ modelos_2021_2024/modelo_final_nivel_desempeno.joblib
```

The browser never talks to Python directly — the Next.js route handler
proxies the request server-side, so there is no CORS exposure beyond the
FastAPI service's own `localhost:3000` allow-list (defense in depth, not
strictly required given the proxy).

`scripts_2021_2024/prediccion_core.py` is now the single source of truth for
answer conversion and prediction; both the CLI
(`15_predecir_estudiante.py`) and the API (`api_2021_2024/main.py`) import it,
so they cannot silently diverge.

## Running it locally

Two processes, from the repository root:

```bash
# Terminal 1 — prediction API
.venv/bin/uvicorn api_2021_2024.main:app --port 8001

# Terminal 2 — dashboard
cd dashboard && npm run dev
```

Then open `http://localhost:3000`.

If the API is not running, the Next.js route handler returns a 503 with an
explicit message telling the user to start it — the form does not fail
silently or show a misleading result.

## What the form does and does not do

- Every field is optional. Fields left as "Sin dato" are filled by the
  model's fitted imputation defaults (mode/median/`"Sin dato"`), the same
  ones documented in [14](14_entrenamiento_modelo_final.md), not by a value
  invented in the browser.
- Select options use the exact original survey vocabulary (`"Estrato 3"`,
  `"Menos de 10 horas"`, etc.), reusing the category lists from analysis 02
  and the actual training data (`fami_ocupacionmadre/padre`,
  `estu_tituloobtenidobachiller`).
- The result shows a probability bar per level, not just the predicted
  class, and surfaces the same low-confidence warning as the CLI when the
  top two classes are within 0.15 of each other.
- The validated out-of-fold performance (macro F1 ≈ 0.38, balanced accuracy
  ≈ 0.39) is shown alongside every prediction, so the tool cannot be used
  without seeing its own honesty disclaimer.

## Verification performed

- `npm run build` in `dashboard/` completed successfully; `/prediccion` (since moved to `/`, see `dashboard/src/app/page.tsx`) and
  `/api/predict` both appear in the route manifest.
- `npm run dev` + `uvicorn api_2021_2024.main:app --port 8001` running
  together: `GET /prediccion` returned 200, and `POST /api/predict` with a
  partial answer set returned a valid prediction with the expected
  `missing_fields` list and `low_confidence` flag.
- The CLI (`15_predecir_estudiante.py`) was re-run after the refactor into
  `prediccion_core.py` and produced the exact same output as before, on the
  same example student.

## Limitations

- This is a local development setup, not a deployed service: the FastAPI
  app has no authentication and assumes a trusted local network (`localhost`
  CORS allow-list only).
- The form does not validate ordinal/nominal values beyond what the browser
  `<select>` already constrains — since options are hardcoded from the
  known training vocabulary, this should not diverge in practice, but it is
  not enforced by a shared schema between frontend and backend.
- As with every prior document in this series: not for individual
  decisions. See [13](13_explicacion_modelo_y_datos_faltantes.md).

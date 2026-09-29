# Side-by-side comparison — with vs. without institution

Continuation of [17_modelo_referencia_institucion.md](17_modelo_referencia_institucion.md).
Wires the reference model (scenario A, with institution) into the same CLI
and dashboard used for the production model, so both predictions are shown
for the exact same student answers.

## What changed

- `scripts_2021_2024/prediccion_core.py` gained `predict_with_reference()`,
  which runs both persisted models on one answer set and returns
  `{"produccion_sin_institucion": ..., "referencia_con_institucion": ...}`.
- `scripts_2021_2024/15_predecir_estudiante.py` now always prints both
  results, plus a note when they disagree.
- `api_2021_2024/main.py` exposes `/instituciones` (the 55 code+name pairs
  scenario A was trained on) and `POST /predict` now returns both models'
  results under the same two keys.
- `dashboard`: a new `/api/instituciones` route proxies the institution
  list; `PrediccionForm.tsx` adds an institution selector (used only by the
  reference model) and renders two result cards stacked in the results
  column, with a red callout when the two models disagree.

## Worked example

Same synthetic student as
[`modelos_2021_2024/ejemplo_estudiante.json`](../modelos_2021_2024/ejemplo_estudiante.json),
run with and without an explicit institution:

| | Production (no institution) | Reference (with institution) |
|---|---|---|
| Predicted level | 1 (37%) | 3 (46%) |
| Low confidence? | Yes (top two within 15pp) | No |
| Validated macro F1 | 0.3786 | 0.2711 |

The two models disagree on this student. This is not a bug to fix — it is
the exact risk documented since [09](09_validacion_groupkfold.md): the
institution model looks more confident, but that confidence is partly
borrowed from memorizing which institutions tend toward which level, not
from a stronger read on this particular student. When no institution is
given, the reference model silently falls back to the most common
institution in training, which alone can swing the prediction — that is
why the production model (no institution) is still the one to trust.

## Reproducible usage

```bash
# CLI — always shows both
.venv/bin/python scripts_2021_2024/15_predecir_estudiante.py modelos_2021_2024/ejemplo_estudiante.json

# API
.venv/bin/uvicorn api_2021_2024.main:app --port 8001
curl -s http://127.0.0.1:8001/instituciones | head -c 200
curl -s -X POST http://127.0.0.1:8001/predict -H "Content-Type: application/json" \
  -d '{"fami_estratovivienda": "Estrato 3", "inst_cod_institucion": 1714}'
```

## Limitations

- Adding `inst_cod_institucion` for an institution NOT among the 55 seen in
  training encodes to "unknown" (-1) and should not be trusted more than the
  production model's prediction for the same student.
- This comparison is descriptive, not causal: a disagreement between models
  says the institution changes the prediction, not that the institution
  causes a different real outcome for this student.
- As with every model in this series: not for individual decisions. See
  [13](13_explicacion_modelo_y_datos_faltantes.md).

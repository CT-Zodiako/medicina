"""Local prediction API for the Next.js dashboard.

Run: .venv/bin/uvicorn api_2021_2024.main:app --reload --port 8001
(from the repository root, so `scripts_2021_2024` resolves as a sibling package).

Exposes POST /predict, backed by the same persisted model and answer
conversion logic as the CLI (scripts_2021_2024/15_predecir_estudiante.py).
Always returns both the production model (scenario B, no institution) and
the reference model (scenario A, with institution) for the same answers, so
callers see the institution's effect on this one student rather than only
the abstract validation numbers. This is a local development helper, not a
hardened public API: it has no authentication and is meant to run on
localhost alongside `next dev`.
"""

import sys
from pathlib import Path
from typing import Optional, Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts_2021_2024"))

from prediccion_core import (  # noqa: E402
    InvalidAnswerError, load_institutions, load_metadata, load_reference_metadata,
    predict_with_reference,
)

app = FastAPI(title="Predicción nivel_desempeno — Saber Pro Medicina")

# Local-only dashboard; `next dev` runs on 3000 by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)


class StudentAnswers(BaseModel):
    """Loose schema: every field is optional, matching the CLI's contract
    where missing fields fall back to the pipeline's imputation defaults.
    Values are typed loosely (str | int | None) because ordinal fields
    accept either the original text label or its already-mapped number.
    `inst_cod_institucion` is only used by the reference model (scenario A).
    """

    model_config = ConfigDict(extra="allow")

    periodo: Optional[str] = None
    estu_tipodocumento: Optional[str] = None
    estu_agregado: Optional[str] = None
    estu_genero: Optional[str] = None
    estu_fechanacimiento: Optional[str] = None
    edad: Optional[int] = None
    estu_horassemanatrabaja: Optional[Union[str, int]] = None
    estu_nse_individual: Optional[int] = None
    estu_pagomatriculabeca: Optional[str] = None
    estu_pagomatriculacredito: Optional[str] = None
    estu_pagomatriculapadres: Optional[str] = None
    estu_pagomatriculapropio: Optional[str] = None
    estu_semestrecursa: Optional[Union[str, int]] = None
    estu_tituloobtenidobachiller: Optional[str] = None
    fami_cuantoscompartebaño: Optional[Union[str, int]] = None
    fami_educacionmadre: Optional[Union[str, int]] = None
    fami_educacionpadre: Optional[Union[str, int]] = None
    fami_estratovivienda: Optional[Union[str, int]] = None
    fami_ocupacionmadre: Optional[str] = None
    fami_ocupacionpadre: Optional[str] = None
    fami_tieneautomovil: Optional[str] = None
    fami_tienecomputador: Optional[str] = None
    fami_tieneconsolavideojuegos: Optional[str] = None
    fami_tienehornomicroogas: Optional[str] = None
    fami_tieneinternet: Optional[str] = None
    fami_tienelavadora: Optional[str] = None
    fami_tienemotocicleta: Optional[str] = None
    fami_tieneserviciotv: Optional[str] = None
    inst_cod_institucion: Optional[Union[str, int]] = None


@app.get("/metadata")
def get_metadata():
    """Expose the input contract (field order, roles) for the frontend form."""
    return {
        "produccion_sin_institucion": load_metadata(),
        "referencia_con_institucion": load_reference_metadata(),
    }


@app.get("/instituciones")
def get_institutions():
    """Institution code + name list scenario A was trained on, for a selector."""
    return load_institutions()


@app.post("/predict")
def post_predict(answers: StudentAnswers):
    try:
        return predict_with_reference(answers.model_dump())
    except InvalidAnswerError as error:
        raise HTTPException(status_code=422, detail=str(error))

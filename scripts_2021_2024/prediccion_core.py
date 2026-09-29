"""Shared inference logic for predicting `nivel_desempeno` on a new student.

Used by both the CLI (15_predecir_estudiante.py) and the FastAPI service
(api_2021_2024/main.py), so the two entry points can never disagree on how
a human-readable answer is converted into the value the model expects.
"""

import importlib
import json
import sys
from pathlib import Path

import joblib
import pandas as pd

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from common import ROOT  # noqa: E402

step02 = importlib.import_module("02_tratamiento_datos")

MODEL_DIR = ROOT / "modelos_2021_2024"
MODEL_PATH = MODEL_DIR / "modelo_final_nivel_desempeno.joblib"
METADATA_PATH = MODEL_DIR / "modelo_final_nivel_desempeno_metadata.json"
REFERENCE_MODEL_PATH = MODEL_DIR / "modelo_referencia_con_institucion.joblib"
REFERENCE_METADATA_PATH = MODEL_DIR / "modelo_referencia_con_institucion_metadata.json"
INSTITUTIONS_PATH = MODEL_DIR / "instituciones.json"
REFERENCE_YEAR = 2024
SI_NO_MAP = {"Si": 1, "No": 0}
# Same ordinal vocabulary as analysis 02, minus mod_ingles_desem (exam-derived,
# excluded as leakage and never part of scenario B).
TEXT_ORDINAL_MAPS = {
    key: value for key, value in step02.ORDINAL_MAPS.items() if key != "mod_ingles_desem"
}

_model = None
_metadata = None
_reference_model = None
_reference_metadata = None
_institutions = None


class InvalidAnswerError(ValueError):
    """A provided field value does not match its documented vocabulary."""


def load_metadata():
    global _metadata
    if _metadata is None:
        _metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return _metadata


def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def load_reference_metadata():
    global _reference_metadata
    if _reference_metadata is None:
        _reference_metadata = json.loads(REFERENCE_METADATA_PATH.read_text(encoding="utf-8"))
    return _reference_metadata


def load_reference_model():
    global _reference_model
    if _reference_model is None:
        _reference_model = joblib.load(REFERENCE_MODEL_PATH)
    return _reference_model


def load_institutions():
    """Return the code+name list scenario A was trained on, for a selector."""
    global _institutions
    if _institutions is None:
        _institutions = json.loads(INSTITUTIONS_PATH.read_text(encoding="utf-8"))
    return _institutions


def convert_field(column, raw_value, binary_cols):
    """Convert one human-readable answer into the value the pipeline expects."""
    if raw_value is None:
        return None
    if column in binary_cols:
        if raw_value in SI_NO_MAP:
            return SI_NO_MAP[raw_value]
        if raw_value in (0, 1, "0", "1"):
            return int(raw_value)
        raise InvalidAnswerError(f"{column}: expected 'Si'/'No', got {raw_value!r}")
    if column in TEXT_ORDINAL_MAPS:
        mapping = TEXT_ORDINAL_MAPS[column]
        if raw_value in mapping:
            return mapping[raw_value]
        if raw_value in mapping.values():
            return raw_value
        raise InvalidAnswerError(
            f"{column}: unrecognized value {raw_value!r}; expected one of {sorted(mapping)}"
        )
    return raw_value


def build_row(answers, metadata):
    """Assemble a single-row DataFrame in the exact column order the model expects."""
    feature_order = metadata["feature_order"]
    binary_cols = set(metadata["feature_roles"]["binary_mode_imputed"])
    row = {}
    if "edad" in feature_order:
        if answers.get("edad") is not None:
            row["edad"] = answers["edad"]
        elif answers.get("estu_fechanacimiento"):
            birth = pd.to_datetime(answers["estu_fechanacimiento"], format="%d/%m/%Y")
            row["edad"] = REFERENCE_YEAR - birth.year
        else:
            row["edad"] = None
    for column in feature_order:
        if column == "edad":
            continue
        row[column] = convert_field(column, answers.get(column), binary_cols)
    return pd.DataFrame([row], columns=feature_order)


def _run(model, metadata, answers):
    row = build_row(answers, metadata)
    predicted = model.predict(row)[0]
    probabilities = model.predict_proba(row)[0]
    classes = model.named_steps["forest"].classes_
    ranked = sorted(zip(classes, probabilities), key=lambda item: -item[1])

    missing = [c for c in metadata["feature_order"] if row[c].iloc[0] is None]
    top_two_gap = ranked[0][1] - ranked[1][1] if len(ranked) > 1 else 1.0

    return {
        "predicted_level": int(predicted),
        "probabilities": {int(level): float(probability) for level, probability in ranked},
        "missing_fields": missing,
        "low_confidence": bool(top_two_gap < 0.15),
        "validated_performance": metadata["validated_out_of_fold_performance"],
    }


def predict(answers):
    """Run one prediction and return a JSON-serializable result dict.

    Raises InvalidAnswerError if a provided value does not match its
    documented vocabulary. Missing fields are left as None and resolved by
    the pipeline's fitted imputation defaults.
    """
    return _run(load_model(), load_metadata(), answers)


def predict_with_reference(answers):
    """Run scenario B (production) and scenario A (with institution) side by
    side on the exact same answers, so the institution's effect on this one
    student is visible instead of only known in the abstract.

    `answers['inst_cod_institucion']` is optional for scenario B (ignored)
    and used only by scenario A; if omitted, scenario A falls back to its
    fitted imputation default (the most frequent institution).
    """
    production = predict(answers)
    reference = _run(load_reference_model(), load_reference_metadata(), answers)
    return {"produccion_sin_institucion": production, "referencia_con_institucion": reference}

"""Reconstruct scores, derive levels, drop 30 fields, and normalize categories.

Run: .venv/bin/python scripts_2021_2024/02_tratamiento_datos.py
Writes dataset_medicina_procesado.csv; never changes the raw CSV. This stage
intentionally preserves missing values, including No sabe / No Aplica. The
current raw snapshot already lacks the 30 dropped columns; both original and
previously treated snapshots are supported without applying mappings twice.
"""

import numpy as np
import pandas as pd

from common import BINARY_COLUMNS, PROCESSED_DATA, RAW_DATA, read_csv, write_dataset

MODULE_SCORES = (
    "mod_competen_ciudada_punt", "mod_comuni_escrita_punt", "mod_ingles_punt",
    "mod_lectura_critica_punt", "mod_razona_cuantitat_punt",
)
DROP_COLUMNS = (
    "estu_otrocole_termino", "estu_valormatriculauniversidad",
    "estu_comocapacitoexamensb11", "estu_estadocivil",
    "estu_cod_cole_mcpio_termino", "estu_cole_termino", "percentil_global",
    "mod_razona_cuantitativo_pnal", "mod_razona_cuantitativo_pnbc",
    "estu_tipodocumentosb11", "estu_areareside", "estu_cod_reside_depto",
    "estu_cod_reside_mcpio", "estu_depto_reside", "estu_mcpio_reside",
    "estu_etnia", "estu_tieneetnia", "estu_cursoiesexterna",
    "estu_simulacrotipoicfes", "estu_actividadrefuerzoareas",
    "estu_actividadrefuerzogeneric", "estu_cursodocentesies",
    "estu_cursoiesapoyoexterno", "estu_inse_individual", "estu_prgm_academico",
    "estu_nucleo_pregrado", "estu_nivel_prgm_academico", "estu_metodo_prgm",
    "estu_privado_libertad", "Source.Name",
)
EDUCATION_MAP = {
    "Ninguno": 0, "Primaria incompleta": 1, "Primaria completa": 2,
    "Secundaria (Bachillerato) incompleta": 3,
    "Secundaria (Bachillerato) completa": 4,
    "Técnica o tecnológica incompleta": 5,
    "Técnica o tecnológica completa": 6,
    "Educación profesional incompleta": 7,
    "Educación profesional completa": 8, "Postgrado": 9,
    "No sabe": np.nan, "No Aplica": np.nan,
}
ORDINAL_MAPS = {
    "mod_ingles_desem": {"A1": 1, "A2": 2, "B1": 3, "B2": 4},
    "fami_cuantoscompartebaño": {
        "NINGUNA": 0, "1": 1, "2": 2, "3 o 4": 3, "5 o 6": 4, "MAS DE 6": 5,
    },
    "estu_horassemanatrabaja": {
        "0": 0, "Menos de 10 horas": 1, "Entre 11 y 20 horas": 2,
        "Entre 21 y 30 horas": 3, "Más de 30 horas": 4,
    },
    "fami_estratovivienda": {
        "Sin Estrato": 0, **{f"Estrato {value}": value for value in range(1, 7)},
    },
    "fami_educacionmadre": EDUCATION_MAP,
    "fami_educacionpadre": EDUCATION_MAP,
    "estu_semestrecursa": {
        **{f"{value:02d}": value for value in range(1, 12)}, "12 o más": 12,
    },
}
LEVEL_BINS = (-1, 129, 156, 189, 300)
LEVELS = (1, 2, 3, 4)


def map_categories(series, mapping):
    """Map original labels or retain valid codes from an already-treated CSV."""
    numeric = pd.to_numeric(series, errors="coerce")
    valid_codes = {value for value in mapping.values() if pd.notna(value)}
    already_encoded = numeric.isin(valid_codes)
    original_label = series.isin(mapping)
    unknown = series.notna() & ~(original_label | already_encoded)
    if unknown.any():
        raise ValueError(f"{series.name}: {int(unknown.sum())} undocumented values")
    # Original text labels take precedence, including intentional null mappings.
    mapped = series.map(mapping)
    return mapped.where(original_label | ~already_encoded, numeric)


def transform(frame):
    """Apply only the transformations documented in analysis 02."""
    frame = frame.copy()
    scores = frame.loc[:, list(MODULE_SCORES)].apply(pd.to_numeric, errors="raise")
    global_score = pd.to_numeric(frame["punt_global"], errors="raise")
    # pandas mean skips missing module scores, matching the documented formula.
    frame["punt_global"] = global_score.fillna(scores.mean(axis=1).round())
    score = frame["punt_global"]
    if score.isna().any() or not score.between(0, 300).all() or score.mod(1).ne(0).any():
        raise ValueError("Global scores must be complete integers between 0 and 300")
    frame["nivel_desempeno"] = pd.cut(
        score, bins=LEVEL_BINS, labels=LEVELS,
    ).astype("int64")
    # The supplied raw snapshot may already have undergone this exact recrop.
    frame = frame.drop(columns=[column for column in DROP_COLUMNS if column in frame])
    for column in BINARY_COLUMNS:
        frame[column] = map_categories(frame[column], {"Si": 1, "No": 0})
    for column, mapping in ORDINAL_MAPS.items():
        frame[column] = map_categories(frame[column], mapping)
    return frame


def main():
    """Rebuild the processed CSV without imputing any missing values."""
    # Preserve leading zeros in semester labels for the exact documented mapping.
    frame = read_csv(RAW_DATA, dtype={"estu_semestrecursa": "string"})
    missing_scores = int(frame["punt_global"].isna().sum())
    result = transform(frame)
    write_dataset(result, PROCESSED_DATA)
    print(f"Reconstructed global scores: {missing_scores}")
    dropped = sum(column in frame for column in DROP_COLUMNS)
    print(f"Dropped columns: {dropped}; already absent: {len(DROP_COLUMNS) - dropped}")
    print(f"Output shape: {result.shape}")
    print(result["nivel_desempeno"].value_counts().sort_index().to_string())
    print(f"Remaining missing cells: {int(result.isna().sum().sum())}")
    print(f"Dataset written: {PROCESSED_DATA}")


if __name__ == "__main__":
    main()

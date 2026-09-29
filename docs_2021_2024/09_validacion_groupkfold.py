"""Validate unseen-institution performance; write only the sibling Markdown report.

Run from repository root: .venv/bin/python docs_2021_2024/09_validacion_groupkfold.py
"""

from pathlib import Path
import hashlib
import platform

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dataset_medicina_procesado.csv"
REPORT = Path(__file__).with_suffix(".md")
TARGET = "nivel_desempeno"
GROUP = "inst_cod_institucion"
LABELS = [1, 2, 3, 4]
# Broad ablation: institutional attributes and all explicit geographic fields,
# including presentation location and country-level student information.
EXCLUDED_B = [
    "inst_cod_institucion", "inst_origen", "inst_caracter_academico",
    "estu_prgm_codmunicipio", "estu_prgm_municipio", "estu_prgm_departamento",
    "estu_inst_codmunicipio", "estu_inst_municipio", "estu_inst_departamento",
    "estu_cod_mcpio_presentacion", "estu_mcpio_presentacion",
    "estu_cod_depto_presentacion", "estu_depto_presentacion",
    "estu_nacionalidad", "estu_pais_reside", "estu_exterior",
]


def make_model(columns):
    """Create fresh preprocessing and forest for each training fold."""
    categorical = [column for column in columns if column != "edad"]
    preprocessing = ColumnTransformer([
        ("age", SimpleImputer(strategy="median"), ["edad"]),
        ("categories", Pipeline([
            ("impute", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            ("encode", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ]), categorical),
    ])
    return Pipeline([
        ("preprocessing", preprocessing),
        ("forest", RandomForestClassifier(
            n_estimators=300, class_weight="balanced", random_state=42, n_jobs=-1,
        )),
    ])


def scores(truth, predicted):
    return (
        f1_score(truth, predicted, labels=LABELS, average="macro", zero_division=0),
        balanced_accuracy_score(truth, predicted),
    )


def detailed_metrics(truth, predicted):
    precision, recall, f1, support = precision_recall_fscore_support(
        truth, predicted, labels=LABELS, zero_division=0,
    )
    lines = ["| Nivel | Precision | Recall | F1 | Soporte |",
             "|---|---:|---:|---:|---:|"]
    for index, label in enumerate(LABELS):
        lines.append(f"| {label} | {precision[index]:.4f} | {recall[index]:.4f} | "
                     f"{f1[index]:.4f} | {support[index]} |")
    matrix = confusion_matrix(truth, predicted, labels=LABELS)
    assert matrix.sum() == len(truth)
    lines += ["", "Matriz: filas = nivel real; columnas = predicción (1, 2, 3, 4).", "",
              "| Real / Predicho | 1 | 2 | 3 | 4 |", "|---|---:|---:|---:|---:|"]
    for label, row in zip(LABELS, matrix):
        lines.append(f"| {label} | " + " | ".join(map(str, row)) + " |")
    return lines


def main():
    frame = pd.read_csv(DATA, sep=None, engine="python")
    if frame.shape != (30738, 62):
        raise ValueError(f"Unexpected dataset shape: {frame.shape}")
    leakage = [column for column in frame if column == "punt_global" or column.startswith("mod_")]
    features = [column for column in frame if column not in [TARGET, *leakage]]
    if len(leakage) != 18 or len(features) != 43:
        raise ValueError("Expected 18 leakage columns and 43 predictors")
    if not set(EXCLUDED_B).issubset(features):
        raise ValueError("Missing expected ablation fields")
    y = pd.to_numeric(frame[TARGET], errors="raise")
    if y.isna().any() or set(y.unique()) != set(LABELS):
        raise ValueError("Expected complete target with levels 1–4")
    if frame[GROUP].isna().any():
        raise ValueError("Missing institution groups")
    groups = frame[GROUP]
    X = frame[features].copy()
    # Analysis 02 documents day/month/year; do not infer ambiguous dates.
    birth = pd.to_datetime(X.pop("estu_fechanacimiento"), format="%d/%m/%Y", errors="coerce")
    if birth.isna().any():
        raise ValueError(f"Missing/invalid day/month/year birth dates: {birth.isna().sum()}")
    X["edad"] = 2024 - birth.dt.year
    if not X["edad"].between(0, 120).all():
        raise ValueError("Age outside 0–120 years; inspect data before modeling")
    # Converting scalar category types learns nothing from held-out observations.
    # Numeric-coded categories remain categorical, following analysis 05.
    for column in X.columns.drop("edad"):
        X[column] = X[column].map(lambda value: str(value) if pd.notna(value) else np.nan)
    folds = list(GroupKFold(n_splits=5).split(X, y, groups))
    seen = np.zeros(len(y), dtype=int)
    for train, test in folds:
        assert set(groups.iloc[train]).isdisjoint(set(groups.iloc[test]))
        assert set(y.iloc[train]) == set(LABELS)
        assert set(y.iloc[test]) == set(LABELS)
        seen[test] += 1
    assert np.all(seen == 1)

    lines = [
        "# Validación por instituciones no vistas — GroupKFold", "",
        "Continuación de [08_shap.md](08_shap.md). Se evalúa generalización a instituciones "
        "completas fuera del entrenamiento, no causalidad ni generalización temporal.", "",
        "## Protocolo reproducible", "",
        "```bash", ".venv/bin/python docs_2021_2024/09_validacion_groupkfold.py", "```", "",
        f"- Dataset: {len(frame):,} filas, {len(frame.columns)} columnas, {groups.nunique()} instituciones; sin eliminar filas.",
        f"- SHA-256 del CSV: `{hashlib.sha256(DATA.read_bytes()).hexdigest()}`.",
        f"- Entorno: Python {platform.python_version()}, pandas {pd.__version__}, "
        f"NumPy {np.__version__}, scikit-learn {sklearn.__version__}.",
        "- Target: `nivel_desempeno`, niveles 1–4. Cinco folds `GroupKFold`, "
        "sin shuffle, agrupados por `inst_cod_institucion`; mismos folds para A y B.",
        "- Bosque: 300 árboles, `class_weight='balanced'`, `random_state=42`, "
        "`n_jobs=-1`; restantes parámetros por defecto (sin límite de profundidad). Sin ajuste de hiperparámetros.",
        "- `edad = 2024 - año(estu_fechanacimiento)`: edad aproximada al cierre de 2024, "
        "no edad exacta al examen. Sustituye la fecha, no suma una variable. "
        "Se valida formato día/mes/año (documentado en 02) y rango 0–120; no se recortan edades ni se eliminan registros.",
        "- Todas las demás variables, incluso códigos numéricos, usan `OrdinalEncoder` "
        "ajustado solamente al train de cada fold; categorías desconocidas → -1. "
        "Imputación categórica constante e imputación mediana de edad dentro del pipeline "
        "(las fechas de esta corrida deben estar completas). Modelo nuevo por fold; los pesos de clase se calculan en train.",
        "- Se comprueba separación de instituciones, presencia de las cuatro clases y "
        "una única predicción fuera de muestra (OOF) por fila. No se imprimen registros individuales.",
        "", "## Variables y exclusiones", "",
        "A conserva las 43 variables de 05–08, con la fecha sustituida por `edad`, "
        "incluido el código de institución. B elimina 16 variables y conserva 27.", "",
        "B es una ablación amplia: elimina el identificador, los atributos institucionales "
        "(`inst_origen`, `inst_caracter_academico`, aunque no sean identificadores únicos), "
        "la geografía del programa/institución y la de presentación como posibles proxies. "
        "También elimina nacionalidad, país de residencia y exterior por ser geografía explícita. "
        "Se retienen `periodo` y atributos individuales/familiares; pueden persistir proxies "
        "indirectos. No se afirma haber eliminado toda señal institucional.", "",
        "Exclusión exacta de B:", "",
        *[f"- `{column}`" for column in EXCLUDED_B], "",
        "Exclusión común por leakage (18 columnas en total, no 18 más `punt_global`):", "",
        *[f"- `{column}`" for column in leakage], "",
        "Predictoras de A (B usa esta lista menos la exclusión anterior):", "",
        *[f"- `{column}`" for column in X.columns], "",
        "## Composición de folds", "",
        "| Fold | Train filas | Test filas | Train instituciones | Test instituciones | Test n1/n2/n3/n4 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for number, (train, test) in enumerate(folds, 1):
        counts = y.iloc[test].value_counts().reindex(LABELS, fill_value=0)
        lines.append(f"| {number} | {len(train)} | {len(test)} | {groups.iloc[train].nunique()} | "
                     f"{groups.iloc[test].nunique()} | {' / '.join(map(str, counts))} |")

    results = {}
    for scenario, columns in [("A", list(X.columns)), ("B", [c for c in X if c not in EXCLUDED_B])]:
        lines += ["", f"## Escenario {scenario}: {len(columns)} predictores", ""]
        oof = np.zeros(len(y), dtype=int)
        fold_scores = []
        details = []
        lines += ["| Fold | F1 macro | Balanced accuracy |", "|---|---:|---:|"]
        for number, (train, test) in enumerate(folds, 1):
            model = make_model(columns)
            model.fit(X.iloc[train][columns], y.iloc[train])
            predicted = model.predict(X.iloc[test][columns])
            oof[test] = predicted
            metrics = scores(y.iloc[test], predicted)
            fold_scores.append(metrics)
            lines.append(f"| {number} | {metrics[0]:.4f} | {metrics[1]:.4f} |")
            details += ["", f"### Fold {number}", "", *detailed_metrics(y.iloc[test], predicted)]
            print(f"{scenario} fold {number}: macro F1={metrics[0]:.4f}, balanced accuracy={metrics[1]:.4f}", flush=True)
        mean = np.mean(fold_scores, axis=0)
        std = np.std(fold_scores, axis=0, ddof=1)
        pooled = scores(y, oof)
        results[scenario] = pooled
        lines += [f"| Media no ponderada | {mean[0]:.4f} | {mean[1]:.4f} |",
                  f"| Desvío muestral (ddof=1) | {std[0]:.4f} | {std[1]:.4f} |",
                  f"| OOF agrupado | {pooled[0]:.4f} | {pooled[1]:.4f} |", "",
                  "### Métricas OOF agrupadas", "", *detailed_metrics(y, oof), *details]

    delta = np.subtract(results["B"], results["A"])
    lines += ["", "## Lectura y limitaciones", "",
              f"- Diferencia B − A en OOF: F1 macro {delta[0]:+.4f}; balanced accuracy {delta[1]:+.4f}. "
              "La diferencia corresponde a una ablación conjunta, no al efecto aislado de una variable.",
              "- La media de folds pondera cada fold igual; OOF reúne todas las predicciones "
              "y recalcula métricas. Las matrices OOF suman las matrices de folds. "
              "Balanced accuracy es el promedio de recall por clase, no accuracy general. "
              "Las métricas sin predicciones positivas se fijan en cero (`zero_division=0`).",
              "- El desvío entre cinco folds describe variación, no un intervalo de confianza "
              "ni una prueba de significancia; los entrenamientos se solapan y GroupKFold no estratifica clases.",
              "- En A todos los códigos de institución del test son desconocidos y se codifican "
              "como -1. Esto evita filtración pero no aprende a extrapolar identidades nuevas; "
              "el código puede inducir particiones arbitrarias en train. OrdinalEncoder también "
              "impone un orden artificial en las demás categorías nominales.",
              "- El F1 macro 0.465 publicado en 06 corresponde a un holdout aleatorio y fecha "
              "en epoch. No es una comparación controlada con esta corrida: cambian el split, "
              "la representación de edad y el tratamiento de categorías desconocidas. "
              "Una caída no prueba por sí sola memorización ni causalidad.",
              "- **Limitación de fuga previa:** [03_imputacion_datos.md](03_imputacion_datos.md) "
              "documenta imputaciones por moda/mediana realizadas sobre el dataset completo antes "
              "de estos folds. El CSV solicitado ya contiene esos valores y no conserva máscaras "
              "de nulos originales. El pipeline ajusta todas las transformaciones nuevas solamente "
              "en train, pero no puede revertir esa imputación global: esta evaluación no es "
              "completamente libre de fuga de preprocesamiento de extremo a extremo. Para garantizarlo "
              "se necesita reconstruir el dataset previo a imputación y repetir los folds; "
              "no se modificó el CSV ni se usó otro dataset en este paso.",
              "- No hay validación temporal, repetición de semillas ni tuning anidado.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written: {REPORT.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()

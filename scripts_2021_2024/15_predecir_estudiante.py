"""Predict `nivel_desempeno` for one student who has not taken the exam.

Usage:
    .venv/bin/python scripts_2021_2024/15_predecir_estudiante.py path/to/estudiante.json

Thin CLI wrapper around prediccion_core, the same module the FastAPI service
in api_2021_2024/main.py uses. Always prints both models side by side: the
production model (scenario B, no institution) and the reference model
(scenario A, with institution), so the institution's effect on this one
student's prediction is visible rather than only known in the abstract.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prediccion_core import InvalidAnswerError, predict_with_reference  # noqa: E402


def print_result(title, result):
    print(f"\n=== {title} ===")
    print(f"Predicted nivel_desempeno: {result['predicted_level']}")
    print("Class probabilities:")
    for level, probability in result["probabilities"].items():
        print(f"  nivel {level}: {probability:.4f}")
    if result["missing_fields"]:
        print(f"Fields not provided (used fitted imputation defaults): {result['missing_fields']}")
    if result["low_confidence"]:
        print("Warning: top two classes are close in probability; this model's confidence "
              "is limited for individual decisions.")
    perf = result["validated_performance"]
    print(f"Validated out-of-fold: macro F1={perf['macro_f1']:.4f}, "
          f"balanced accuracy={perf['balanced_accuracy']:.4f}")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} path/to/estudiante.json", file=sys.stderr)
        raise SystemExit(2)
    input_path = Path(sys.argv[1])
    answers = json.loads(input_path.read_text(encoding="utf-8"))

    try:
        comparison = predict_with_reference(answers)
    except InvalidAnswerError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        raise SystemExit(1)

    print_result("Production (scenario B, no institution)",
                 comparison["produccion_sin_institucion"])
    print_result("Reference (scenario A, with institution)",
                 comparison["referencia_con_institucion"])

    production_level = comparison["produccion_sin_institucion"]["predicted_level"]
    reference_level = comparison["referencia_con_institucion"]["predicted_level"]
    if production_level != reference_level:
        print(f"\nNote: the two models disagree ({production_level} vs. {reference_level}). "
              "Scenario A's institution signal partly reflects memorization (see doc 09); "
              "treat the production model's prediction as the default.")


if __name__ == "__main__":
    main()

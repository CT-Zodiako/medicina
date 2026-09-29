# Conclusión — importancia de variables sobre `nivel_desempeno`

Cierre de la secuencia 04–10. Resume qué se hizo, qué se descartó y qué
queda como respuesta honesta a la pregunta original: **qué variables se
asocian con el nivel de desempeño (1–4) en Saber Pro Medicina 2021–2024**.

## Secuencia completa

| Paso | Técnica | Qué aportó |
|---|---|---|
| [04](04_importancia_variables_conceptos.md) | Conceptos | Por qué ninguna técnica sola alcanza; plan de 4 capas |
| [05](05_mutual_information.md) | Mutual Information | Filtro univariado inicial; detectó dominancia institucional |
| [06](06_random_forest_mdi.md) | Random Forest + MDI | Reveló el sesgo de cardinalidad (fecha de nacimiento, ocupación de los padres) |
| [07](07_permutation_importance.md) | Permutation Importance | Descartó la ocupación de los padres como señal real; confirmó institución y fecha |
| [08](08_shap.md) | SHAP | Confirmó dirección/consistencia de la señal en las 4 clases |
| [09](09_validacion_groupkfold.md) | GroupKFold por institución | Probó generalización a instituciones nunca vistas: A (con institución) vs. B (sin institución) |
| [10](10_tuning_modelo_b.md) | Tuning de hiperparámetros | Confirmó que el techo del modelo B no está en los hiperparámetros |

## Resultado final de generalización (paso 09)

| Escenario | Predictores | Macro F1 (OOF) | Balanced accuracy (OOF) |
|---|---:|---:|---:|
| A — con institución/geografía | 43 | 0.2711 | 0.3223 |
| **B — sin institución/geografía** | 27 | **0.3721** | **0.3759** |

El modelo **B generaliza mejor** a instituciones que nunca vio en
entrenamiento. El modelo A, aunque tenía más señal aparente en MI/MDI/SHAP,
estaba aprovechando en parte la identidad de la institución — información
que no existe para una institución nueva.

## Resultado del tuning (paso 10)

| Métrica | Defaults (B) | Ajustado (B) | Delta |
|---|---:|---:|---:|
| Macro F1 | 0.3721 | 0.3787 | +0.0066 |
| Balanced accuracy | 0.3759 | 0.3930 | +0.0171 |

La mejora por hiperparámetros es marginal. **El límite no está en el
modelo, está en las variables disponibles.**

## Variables que se sostienen como señal real (modelo B)

De la secuencia 05–08, estas son las que se mantuvieron relevantes en más
de una técnica, dentro del conjunto sin institución/geografía:

- `estu_horassemanatrabaja` (horas de trabajo semanal)
- `fami_estratovivienda` (estrato)
- `fami_educacionpadre` / `fami_educacionmadre` (educación de los padres)
- `estu_pagomatriculabeca` (forma de pago de matrícula)
- `estu_semestrecursa` (semestre que cursa)

## Variables descartadas como señal real (memorización o cardinalidad)

- `fami_ocupacionmadre` / `fami_ocupacionpadre`: alta importancia en MDI
  (12 categorías cada una), casi nula en permutation importance.
- `estu_snies_prgmacademico`, `inst_nombre_institucion`: mismo dato que
  `inst_cod_institucion`, eliminadas del dataset por redundancia.
- La mayoría de bienes del hogar (`fami_tienecomputador`, `fami_tieneautomovil`,
  etc.) y trámites de matrícula (`estu_pagomatriculacredito/padres`):
  importancia ≈0 o negativa en las tres técnicas de validación.

## Conclusión honesta

1. **La institución (código, origen, tipo) es la señal predictiva más
   fuerte del dataset**, pero no generaliza bien a instituciones nuevas —
   es en parte memorización, replicando el mismo patrón que ya se había
   encontrado en el proyecto anterior con `PUNT_GLOBAL`.
2. **Sin institución, el modelo generaliza mejor** (F1 macro 0.37 vs. 0.27),
   aunque su techo de desempeño absoluto es modesto: predecir 4 niveles de
   desempeño con estas variables demográficas/socioeconómicas es un
   problema difícil, no resuelto por tuning.
3. Las variables socioeconómicas más consistentes son **estrato, horas de
   trabajo semanal, educación de los padres, forma de pago de matrícula y
   semestre que cursa**.
4. Esto es **asociación, no causalidad** — el mismo límite que ya se había
   documentado en el proyecto anterior aplica acá.

## Qué falta si se quiere seguir esta línea

- Reconstruir el pipeline de imputación **dentro** de cada fold de
  `GroupKFold` (hoy la imputación del paso 03 es global, ver limitación
  documentada en 09), para una validación 100% libre de fuga de
  preprocesamiento.
- Evaluar si un modelo más simple (regresión logística ordinal) captura la
  misma señal con mayor interpretabilidad, dado que `nivel_desempeno` es
  ordinal y no puramente nominal.
- Si se necesita mejor desempeño absoluto, la palanca no es el modelo: es
  conseguir variables nuevas (ej. preparación previa, tipo de colegio,
  trayectoria académica) que este dataset no tiene.

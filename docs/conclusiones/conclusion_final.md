# Conclusión final — Qué explica el PUNT_GLOBAL en Medicina

Síntesis de las 5 técnicas aplicadas sobre `ESTU_MEDICINA_3_MODULOS.xlsx` (23.134 estudiantes, target = `PUNT_GLOBAL`).

## Resumen ejecutivo

**La institución donde estudia el estudiante es, con diferencia, el factor más determinante del puntaje global.** Le siguen, muy por detrás, el carácter académico de la institución (Universidad vs Institución Universitaria), la edad del estudiante y el nivel socioeconómico del hogar (estrato, educación de los padres, índice INSE). Variables individuales como género o posesión de electrodomésticos casi no aportan señal por sí solas.

Ninguna de las 5 técnicas contradijo a las otras — todas señalan el mismo orden de importancia, lo cual da confianza en el resultado.

## Tabla comparativa por técnica

| Técnica | Qué mide | Variable #1 | Variable #2 | Variable #3 |
|---|---|---|---|---|
| Mutual Information (24 cols finales) | Reducción de incertidumbre, sin asumir linealidad | `INST_NOMBRE_INSTITUCION` (0.255) | `INST_ORIGEN` (0.059) | `ESTU_INST_MUNICIPIO` (0.058) |
| Mutual Information (78 cols, validación) | Igual, sobre dataset completo con fuga de datos incluida | `PERCENTIL_GLOBAL` (fuga, 3.26) | Módulos componentes de PUNT_GLOBAL (fuga, 0.10-0.51) | `INST_NOMBRE_INSTITUCION` (0.251, primera no-fuga) |
| Árbol de decisión (podado, R²=0.29) | Reducción de varianza en cada corte | `INST_ORIGEN` no oficial (0.322) | `INST_CARACTER_ACADEMICO` (0.241) | Instituciones específicas (Andes, Icesi) |
| Random Forest (R²=0.37) | Reducción de varianza promediada en 300 árboles | `INST_ORIGEN` no oficial (0.249) | `INST_NOMBRE_INSTITUCION` Andes (0.131) | `INST_CARACTER_ACADEMICO` / `EDAD` (~0.09-0.10) |
| SHAP sobre Random Forest | Impacto real en puntos sobre la predicción | `INST_ORIGEN` no oficial (8.35 puntos) | `EDAD` (2.76 puntos) | `INST_CARACTER_ACADEMICO` (~2.2-2.3 puntos) |
| PCA / UMAP | Estructura visual en espacio reducido | Confirma clusters por institución (55 grupos separados) — no aporta variable nueva | — | — |

## Qué SÍ explica el puntaje (en orden)

1. **Institución** (`INST_NOMBRE_INSTITUCION`, `INST_ORIGEN`, `INST_CARACTER_ACADEMICO`) — selectividad de admisión, calidad docente y nivel del grupo de estudiantes quedan empaquetados acá. Es, sin comparación, el factor dominante en las 5 técnicas.
2. **Edad** (`EDAD`) — señal moderada y consistente en árbol, Random Forest y SHAP.
3. **Nivel socioeconómico del hogar** — `FAMI_ESTRATOVIVIENDA`, `ESTU_INSE_INDIVIDUAL`, educación de padre y madre. Señal real pero bastante menor que institución.
4. **Cómo pagó la matrícula** (crédito, beca, propio, padres) — señal débil pero presente.

## Qué NO explica el puntaje

- Género, posesión individual de bienes (auto, lavadora, TV, consola, internet, microondas) — señal casi nula de forma individual. El estrato agregado captura mejor ese efecto que cada bien por separado.
- Nacionalidad, país de residencia, tipo de documento, período de presentación.

## Limitaciones importantes

- **El modelo explica poco en términos absolutos**: el mejor modelo (Random Forest) llega a R² = 0.37 — deja **63% de la varianza sin explicar**. Esto es esperable: factores como preparación individual, salud del estudiante el día del examen, o cuánto estudió, no están en este dataset y probablemente pesan más que cualquier variable disponible.
- **PCA/UMAP aportaron poco**: el dataset es mayormente categórico (solo 2 columnas numéricas de ~24), lo que limita técnicas basadas en varianza/distancia euclidiana. Confirmaron visualmente el hallazgo de institución, pero no revelaron estructura nueva.
- **Fuga de datos evitada correctamente**: se confirmó con números (MI sobre las 78 columnas) que los componentes del puntaje global (lectura crítica, razonamiento cuantitativo, etc.) y los módulos específicos tenían mutual information altísima — quedaron excluidos del dataset final desde el principio.

## Recomendación para seguir

Si el objetivo es mejorar el poder predictivo (subir el R²=0.37), el siguiente paso natural sería:
- Probar Gradient Boosting (XGBoost/LightGBM) con soporte nativo de categóricas de alta cardinalidad (evita el one-hot de 55 columnas de institución).
- Validación cruzada (k-fold) en vez de un solo split 80/20, para tener una estimación más confiable del R².
- Si el objetivo es equidad educativa más que predicción pura, el hallazgo ya es suficientemente claro: el estrato/institución explican más el resultado que el esfuerzo o mérito individual medible en este dataset.

## Técnicas usadas y dónde están

| Carpeta | Contenido |
|---|---|
| `docs/dataset/` | Definición del dataset final, columnas excluidas, nulos |
| `docs/mutual_information/` | Ranking de MI (24 cols y 78 cols de validación) |
| `docs/decision_tree/` | Árbol interpretable, comparación podado vs sin podar |
| `docs/random_forest_shap/` | Modelo con mejor R², explicación SHAP por estudiante |
| `docs/pca_umap/` | Visualización 2D, confirmación del hallazgo de institución |

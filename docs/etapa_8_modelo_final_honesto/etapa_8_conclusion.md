# Etapa 8 — Modelo final honesto

## Qué se hizo y por qué

Las etapas 5, 6 y 7 identificaron dos problemas independientes en el modelo de referencia (etapa 3):

1. **Sobreajuste institucional (memorización).** `INST_NOMBRE_INSTITUCION`, `ESTU_INST_DEPARTAMENTO` y `ESTU_INST_MUNICIPIO` son proxies de alta cardinalidad: el modelo los usa para "recordar" el desempeño histórico de cada institución puntual en lugar de aprender un patrón generalizable. La etapa 6 lo demostró al validar con `GroupKFold` agrupando por institución (instituciones nunca vistas en validación): el R² cayó de 0.374 a 0.120, con una varianza altísima entre folds (±0.146).
2. **Descarte total de la señal institucional.** La etapa 5 eliminó las 5 variables institucionales de una vez, incluyendo dos que la etapa 7 (permutation importance vs. MDI) confirmó como señal real y transferible: `INST_ORIGEN` (oficial/no oficial) y `INST_CARACTER_ACADEMICO` (universidad/institución universitaria/etc.). Al quitarlas junto con las que sí eran memorización, la etapa 5 fue innecesariamente conservadora.

Este modelo final combina lo mejor de ambos diagnósticos: conserva `INST_ORIGEN` e `INST_CARACTER_ACADEMICO` como features (señal real, según etapa 7), descarta explícitamente `INST_NOMBRE_INSTITUCION`, `ESTU_INST_DEPARTAMENTO` y `ESTU_INST_MUNICIPIO` (memorización, según etapa 6 y etapa 7), y se sigue validando con `GroupKFold(n_splits=5)` agrupando por `INST_NOMBRE_INSTITUCION` — esa columna define los folds pero nunca entra como feature del modelo — para seguir midiendo generalización genuina a instituciones nunca vistas en entrenamiento.

## Comparación de R² entre etapas

| Etapa | Feature set institucional | Validación | R² |
|---|---|---|---|
| 3 | Las 5 variables institucionales (incluye memorización) | Split único 80/20 (instituciones compartidas train/test) | 0.374 |
| 5 | Ninguna variable institucional | KFold aleatorio k=5 | 0.186 ± 0.011 |
| 6 | Las 5 variables institucionales (incluye memorización) | GroupKFold k=5 (instituciones nunca vistas) | 0.120 ± 0.146 |
| **8** | **Solo `INST_ORIGEN` + `INST_CARACTER_ACADEMICO`** | **GroupKFold k=5 (instituciones nunca vistas)** | **0.2287 ± 0.0874** |

**Lectura:**
- Etapa 3 (0.374) está inflada por memorización institucional y por compartir instituciones entre train y test; no es una estimación honesta de generalización.
- Etapa 5 (0.186 ± 0.011) es la cota inferior conservadora: sin ninguna señal institucional, con la validación más estable (std bajo) pero descartando información real.
- Etapa 6 (0.120 ± 0.146) muestra lo que pasa al exigir generalización honesta sin depurar la señal institucional: el R² promedio cae por debajo incluso de etapa 5, y la varianza entre folds (±0.146) es enorme — evidencia de que el modelo dependía de memorizar instituciones específicas y se desestabiliza por completo cuando no las ha visto.
- **Etapa 8 (0.2287 ± 0.0874)** supera tanto a etapa 5 (+0.043) como a etapa 6 (+0.109) en su propia validación honesta por institución. Esto confirma que `INST_ORIGEN` e `INST_CARACTER_ACADEMICO` aportan poder predictivo real y transferible (no memorización), y que aislarlos de las 3 variables de memorización reduce sustancialmente la inestabilidad entre folds frente a etapa 6 (std de 0.087 vs. 0.146).

## Variables más importantes e estabilidad entre folds

Top variables por importancia MDI (media ± std entre los 5 folds):

1. `INST_ORIGEN_NO OFICIAL - CORPORACIÓN` — 0.2807 ± 0.0771 (la más importante, pero también la de mayor variabilidad relativa)
2. `EDAD` — 0.1190 ± 0.0021 (muy estable)
3. `INST_CARACTER_ACADEMICO_INSTITUCIÓN UNIVERSITARIA` — 0.1175 ± 0.0281
4. `INST_CARACTER_ACADEMICO_UNIVERSIDAD` — 0.1110 ± 0.0257
5. `ESTU_INSE_INDIVIDUAL` (índice socioeconómico) — 0.0855 ± 0.0197
6. `ESTU_HORASSEMANATRABAJA_0` (no trabaja) — 0.0277 ± 0.0059
7. `FAMI_ESTRATOVIVIENDA_Estrato 6` — 0.0196 ± 0.0104
8. `ESTU_PAGOMATRICULABECA_No` — 0.0191 ± 0.0064
9. `ESTU_PAGOMATRICULABECA_Si` — 0.0187 ± 0.0060
10. `FAMI_TIENEHORNOMICROOGAS_No` — 0.0144 ± 0.0076

Las 4 variables institucionales retenidas (`INST_ORIGEN_*`, `INST_CARACTER_ACADEMICO_*`) concentran juntas más del 50% de la importancia total, seguidas por `EDAD` y `ESTU_INSE_INDIVIDUAL` como principales predictores no institucionales. La estabilidad es razonable: las variables socioeconómicas/demográficas (`EDAD`, `ESTU_INSE_INDIVIDUAL`) tienen std bajo y consistente entre folds, mientras que las institucionales muestran más variabilidad (esperable, dado que cada fold excluye instituciones completas y por tanto cambia la composición de categorías de origen/carácter académico vistas en entrenamiento).

## Conclusión

Este es el modelo que el proyecto debería reportar como resultado principal si tuviera que dar un único número de desempeño honesto: **R² = 0.2287 ± 0.0874** bajo `GroupKFold` por institución. Es la única configuración que (a) mide generalización real a instituciones nunca vistas, evitando la inflación por memorización de etapa 3 y etapa 6, y (b) no descarta señal institucional legítima como hacía etapa 5, por lo que captura más poder predictivo real que las dos validaciones honestas anteriores.

Para producción o uso real se recomienda el feature set de esta etapa: variables socioeconómicas/demográficas del estudiante (`ESTU_INSE_INDIVIDUAL`, `EDAD`, `ESTU_GENERO`, etc.), variables familiares (`FAMI_*`), variables de matrícula/trabajo (`ESTU_PAGOMATRICULA*`, `ESTU_HORASSEMANATRABAJA`) y únicamente `INST_ORIGEN` + `INST_CARACTER_ACADEMICO` como señal institucional — nunca `INST_NOMBRE_INSTITUCION`, `ESTU_INST_DEPARTAMENTO` ni `ESTU_INST_MUNICIPIO`, que no generalizan a instituciones nuevas y solo inflarían artificialmente el desempeño aparente sobre datos históricos.

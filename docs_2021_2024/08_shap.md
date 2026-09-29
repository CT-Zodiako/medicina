# SHAP — explicación del modelo de `nivel_desempeno`

Paso 4 de la secuencia de importancia de variables. SHAP no solo entrega un
ranking: estima cuánto contribuye cada variable a cada clase (`nivel_1` a
`nivel_4`) en cada predicción.

## Configuración

- Target: `nivel_desempeno`.
- Se mantuvieron las 43 variables candidatas de los análisis anteriores.
- Se excluyeron `punt_global` y los 18 puntajes/derivados de módulo por fuga
  matemática del target.
- Se usaron las 15 variables con importancia positiva más alta según
  permutation importance para el resumen interpretativo.
- Modelo SHAP: Random Forest balanceado, 100 árboles, profundidad máxima 18.
- Muestra explicada: 250 registros del conjunto de test.
- Se usó `TreeExplainer` con `tree_path_dependent`.

La configuración es exploratoria y acotada para hacer viable el cálculo. Los
valores son comparables dentro de este análisis, pero no deben interpretarse
como causalidad.

## Importancia media absoluta por clase

Un valor más alto significa mayor contribución promedio — positiva o negativa
— a la predicción de esa clase. `overall` es el promedio entre las cuatro
clases.

| Variable | Nivel 1 | Nivel 2 | Nivel 3 | Nivel 4 | Global |
|---|---:|---:|---:|---:|---:|
| `inst_cod_institucion` | 0.0411 | 0.0553 | 0.0258 | **0.0864** | **0.0521** |
| `inst_origen` | 0.0278 | 0.0344 | 0.0177 | 0.0464 | 0.0316 |
| `estu_fechanacimiento` | 0.0369 | 0.0133 | 0.0268 | 0.0217 | 0.0247 |
| `inst_caracter_academico` | 0.0186 | 0.0181 | 0.0098 | 0.0279 | 0.0186 |
| `estu_horassemanatrabaja` | 0.0223 | 0.0141 | 0.0159 | 0.0211 | 0.0183 |
| `fami_estratovivienda` | 0.0153 | 0.0124 | 0.0092 | 0.0228 | 0.0149 |
| `estu_prgm_municipio` | 0.0158 | 0.0128 | 0.0105 | 0.0199 | 0.0148 |
| `estu_prgm_codmunicipio` | 0.0145 | 0.0084 | 0.0096 | 0.0167 | 0.0123 |
| `estu_prgm_departamento` | 0.0119 | 0.0085 | 0.0076 | 0.0156 | 0.0109 |
| `fami_educacionpadre` | 0.0073 | 0.0072 | 0.0066 | 0.0108 | 0.0080 |
| `estu_pagomatriculabeca` | 0.0065 | 0.0072 | 0.0037 | 0.0126 | 0.0075 |
| `estu_inst_departamento` | 0.0060 | 0.0049 | 0.0051 | 0.0080 | 0.0060 |
| `fami_ocupacionpadre` | 0.0075 | 0.0042 | 0.0059 | 0.0033 | 0.0052 |
| `periodo` | 0.0055 | 0.0043 | 0.0057 | 0.0047 | 0.0050 |
| `estu_semestrecursa` | 0.0037 | 0.0027 | 0.0038 | 0.0030 | 0.0033 |

## Interpretación

- `inst_cod_institucion` es la variable dominante, especialmente para
  distinguir el nivel 4. Esto coincide con permutation importance, pero no
  prueba causalidad ni garantiza generalización a instituciones nunca vistas.
- `inst_origen` (tipo de institución) mantiene una contribución alta,
  especialmente hacia el nivel 4. Es una señal más general que el código
  puntual de institución, aunque ambas pueden estar correlacionadas.
- `estu_fechanacimiento` tiene mayor contribución relativa en la clase 1 y
  también aparece entre las primeras globalmente. Para comunicarla mejor se
  recomienda convertirla en `edad` en vez de usar la fecha cruda.
- `fami_estratovivienda` y `estu_horassemanatrabaja` muestran contribuciones
  consistentes y son las variables socioeconómicas más relevantes junto con
  educación del padre.
- Las variables geográficas del programa/institución tienen contribuciones
  intermedias y pueden ser proxies de la institución, no necesariamente
  efectos independientes.

## Limitaciones

- SHAP explica el modelo; no demuestra que una variable cause el desempeño.
- Las variables institucionales y geográficas pueden memorizar diferencias
  entre instituciones. Para comprobar generalización real falta validar con
  `GroupKFold` dejando instituciones completas fuera del entrenamiento.
- El análisis usa una muestra de 250 registros y un bosque acotado de 100
  árboles; sirve para interpretar tendencias, no como estimación definitiva
  de producción.
- Los valores SHAP no indican por sí solos la dirección del efecto. Para
  afirmar que un valor alto "sube" o "baja" el nivel hace falta revisar los
  gráficos de dependencia o los valores SHAP firmados por clase.

## Conclusión de la secuencia

Las cuatro técnicas convergen en una conclusión prudente:

1. La institución es la señal predictiva más fuerte, pero requiere validación
   por instituciones no vistas.
2. El origen institucional, la edad, las horas de trabajo y el estrato son
   las señales no institucionales más consistentes.
3. MDI sobreestimó ocupaciones de los padres por cardinalidad; permutation
   importance y SHAP reducen esa importancia.
4. Las asociaciones encontradas no deben presentarse como causalidad.

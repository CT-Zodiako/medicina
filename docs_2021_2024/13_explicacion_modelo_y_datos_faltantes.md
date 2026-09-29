# Cómo funciona el modelo final y qué datos faltarían

Continuación de [12_modelo_final_sin_fuga.md](12_modelo_final_sin_fuga.md).
Explica en términos simples qué es el modelo, cómo se probó, qué tan bien
predice y qué información adicional se necesitaría para mejorar la
clasificación de `nivel_desempeno`.

## Qué construimos

Un **Random Forest** (600 árboles de decisión que votan entre sí) que mira
27 variables de un estudiante y predice en cuál de los 4 niveles de
desempeño va a caer — **sin usar la institución** donde estudia, porque esa
variable generalizaba peor a instituciones nuevas (ver
[09](09_validacion_groupkfold.md) y [11](11_conclusion_importancia_variables.md)).

## Cómo se probó

No se evaluó con un split aleatorio simple. Se usó **GroupKFold por
institución**: se separaron las 55 instituciones del dataset en 5 grupos,
y en cada vuelta se entrenó con 44 instituciones y se probó con las 11 que
el modelo **nunca vio**. Esto evita que el modelo memorice patrones de una
institución puntual en vez de aprender señal real.

## ¿Predice bien?

No muy bien, en términos honestos:

| Métrica | Valor |
|---|---:|
| Macro F1 | 0.3786 |
| Balanced accuracy | 0.3924 |

Para contexto: con 4 clases, adivinar al azar da ~0.25. El modelo mejora
sobre el azar, pero está lejos de ser confiable para decisiones sobre un
estudiante individual.

Por clase, el modelo:

- Predice razonablemente bien el **nivel 3** (el más común, ~49% de los
  estudiantes) y el **nivel 4**.
- Confunde mucho el **nivel 1** y el **nivel 2** entre sí — son los que
  peor distingue.

## Por qué no predice mejor

No es un problema del algoritmo: ya se probó ajuste de hiperparámetros
([10](10_tuning_modelo_b.md)) y la mejora fue de apenas +0.007 en F1 macro.
El límite está en **qué tipo de variables tenemos**: las 27 predictoras son
demográficas y socioeconómicas (estrato, horas de trabajo, educación de los
padres, forma de pago de matrícula, bienes del hogar). Esas variables
correlacionan con el desempeño, pero no son las que más pesan en un
resultado de examen académico.

## Qué le faltaría pedir a un estudiante para clasificarlo mejor

Lo que este dataset no tiene, y que probablemente aportaría más señal real
que las variables socioeconómicas actuales:

1. **Historial académico previo**
   - Resultado del examen Saber 11 (bachillerato).
   - Promedio acumulado en la carrera hasta el momento del examen.
   - Notas del colegio de origen.

2. **Preparación específica para el examen**
   - Si hizo simulacros de Saber Pro.
   - Si tomó cursos de preparación (propios o de la institución).
   - Horas dedicadas a estudiar para el examen.

3. **Tipo y calidad del colegio de origen**
   - Público o privado.
   - Si era un colegio de alto rendimiento reconocido.
   - (El dataset actual tenía esta información, pero con 66-88% de nulos —
     inutilizable, ver [01](01_dataset_medicina_nulos.md)).

4. **Compromiso y trayectoria académica en la carrera**
   - Porcentaje de asistencia a clases.
   - Si repitió semestres o materias.
   - Carga académica cursada (créditos o materias por semestre).

Estas cuatro categorías apuntan a "cómo le está yendo académicamente" al
estudiante, en vez de "de dónde viene" — y son las que más probablemente
mejorarían la capacidad de clasificación del modelo.

## Conclusión práctica

El modelo actual sirve para tener una **idea general de tendencias
poblacionales** (qué factores socioeconómicos se asocian con el desempeño),
pero no está en condiciones de usarse para clasificar o intervenir sobre un
estudiante individual. Para eso, el paso siguiente no es ajustar el modelo
— es conseguir datos académicos que hoy no existen en este dataset.

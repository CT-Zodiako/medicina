# Importancia de variables — conceptos y por qué aplicarlos en este proyecto

Objetivo del análisis: identificar qué variables influyen en `nivel_desempeno`
(1-4, derivado de `punt_global`). Está pensada para las características
concretas de este dataset: **clasificación multiclase, clases desbalanceadas
(nivel 3 ≈ 49% de los datos), variables mixtas (numéricas, ordinales,
binarias, nominales)**.

## 1. Mutual Information (MI)

**Qué mide:** cuánta incertidumbre sobre `nivel_desempeno` se reduce al
conocer el valor de una variable. A diferencia de una correlación de
Pearson, no asume que la relación sea lineal detecta cualquier tipo de
dependencia estadística, incluso no lineal.

**Qué hay que tener claro antes de usarla:**
- Es una medida **univariada**: mide cada variable contra el objetivo por
  separado, sin ver interacciones entre variables ni redundancia entre ellas.
  Dos variables muy correlacionadas entre sí (por ejemplo `fami_estratovivienda`
  y `fami_tienecomputador`) pueden aparecer ambas con MI alta, aunque en
  realidad estén aportando la misma señal.
- No dice nada sobre si el modelo **puede usar** esa señal de forma honesta
  (eso lo valida la permutation importance más adelante).

**Por qué la aplicamos acá:** es rapida de calcular, funciona igual de bien
con variables categóricas, ordinales y continuas sin necesidad de
transformarlas más, y sirve como **primer filtro rápido** antes de invertir
tiempo en modelos más pesados. Con 63 variables candidatas, tener un ranking
inicial ayuda a priorizar qué mirar primero.

## 2. Random Forest / Gradient Boosting — importancia por impureza (MDI/Gini)

**Qué mide:** cuánto reduce cada variable la impureza (Gini o entropía) en
los splits del árbol, acumulado sobre todos los árboles del bosque.

**Qué hay que tener claro antes de usarla — y por qué NO nos podemos quedar
solo acá:**
- **Está sesgada hacia variables de alta cardinalidad** (muchas categorías o
  valores continuos con muchos decimales): el árbol tiene más puntos de corte
  posibles para dividir, así que tiende a "usarla" más aunque no sea
  genuinamente más predictiva.
- **Se mide sobre los datos de entrenamiento**, así que puede reflejar
  memorización en vez de una señal que generaliza. Este es exactamente el
  problema que ya vivimos en el proyecto anterior (`docs/etapa_3` a
  `etapa_8`): la institución dominaba el ranking de importancia por MDI, pero
  esa señal no generalizaba a instituciones nuevas era memorización, no
  asociación real.

**Por qué la aplicamos acá (con esa salvedad):** sigue siendo útil para
entrenar el modelo base y tener una primera intuición, pero **nunca se usa
como conclusión final** de qué variable importa. Se usa como punto de
comparación contra la permutation importance (punto 3): si una variable tiene
MDI alto pero permutation importance baja, es señal de memorización.

## 3. Permutation Importance

**Qué mide:** cuánto empeora el desempeño del modelo (accuracy, F1) cuando
se mezclan aleatoriamente los valores de una variable, dejando todo lo demás
igual. Si el modelo empeora mucho, la variable era genuinamente necesaria;
si no cambia nada, no lo era.

**Qué hay que tener claro antes de usarla:**
- Hay que medirla **sobre un conjunto de validación/holdout**, nunca sobre el
  mismo set de entrenamiento — si no, hereda el mismo problema de
  memorización que el MDI.
- Es más costosa computacionalmente (hay que re-evaluar el modelo una vez
  por variable, varias repeticiones para estabilidad), pero es la que da la
  respuesta honesta.
- Con clases desbalanceadas, la métrica de desempeño que se usa para medir
  el "empeoramiento" importa: si se usa accuracy plano, una variable puede
  parecer poco importante solo porque el modelo igual acierta prediciendo
  "nivel 3" todo el tiempo. Por eso se mide con F1 macro o balanced accuracy,
  no accuracy simple.

**Por qué la aplicamos acá:** es la técnica que realmente responde "¿esta
variable ayuda a predecir el nivel de desempeño en datos que el modelo no
vio?" — que es la pregunta que nos importa. Dado que el proyecto anterior ya
demostró que sin esta validación se puede llegar a una conclusión inflada
(R² = 0.37 vs. 0.23 real), acá se aplica desde el principio y no como
corrección posterior.

## 4. SHAP (SHapley Additive exPlanations)

**Qué mide:** para cada predicción individual, cuánto aportó cada variable
al resultado final, con una base matemática (valores de Shapley de teoría de
juegos) que garantiza que las contribuciones se repartan de forma consistente
entre variables correlacionadas.

**Qué hay que tener claro antes de usarla:**
- A diferencia de MI y permutation importance (que dan un solo número
  global por variable), SHAP muestra **cómo y en qué dirección** afecta cada
  variable — por ejemplo, si un estrato alto empuja hacia nivel 4 o si el
  efecto es distinto según el rango de `fami_estratovivienda`.
- Detecta **interacciones**: el efecto de una variable puede depender del
  valor de otra (ej. el efecto de `estu_horassemanatrabaja` puede ser
  distinto según `fami_estratovivienda`).
- Es la más costosa computacionalmente de las cuatro; por eso se aplica al
  final, sobre el conjunto ya filtrado de variables relevantes, no sobre las
  63 originales.

**Por qué la aplicamos acá:** una vez que sabemos qué variables importan de
verdad (MI + permutation importance), SHAP nos permite explicar el modelo
final: no solo "qué variables importan" sino "cómo cada una mueve la
predicción hacia un nivel de desempeño u otro", que es clave para comunicar
resultados de forma honesta y no solo mostrar un ranking.

## Orden de aplicación y por qué

1. **MI** → filtro rápido inicial sobre las 63 variables candidatas.
2. **Random Forest/GBM + MDI** → entrenar el modelo base y tener una primera
   intuición (con la salvedad ya explicada).
3. **Permutation Importance** (sobre holdout, con F1 macro) → validar cuáles
   de esas variables importan de verdad y detectar memorización.
4. **SHAP** → sobre el modelo final, para explicar cómo actúa cada variable
   relevante y sus interacciones.

Esta secuencia replica, para el problema de clasificación (`nivel_desempeno`),
la misma disciplina de validación que ya se aplicó en el proyecto anterior
para el problema de regresión (`punt_global`), donde separar memorización de
señal real fue lo que cambió la conclusión final del análisis.

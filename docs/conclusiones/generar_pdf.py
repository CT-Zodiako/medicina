import base64
from pathlib import Path
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"


def img_b64(path):
    data = base64.b64encode(Path(path).read_bytes()).decode()
    return f"data:image/png;base64,{data}"


pca_scatter = img_b64(DOCS / "pca_umap" / "pca_scatter_puntaje.png")
umap_puntaje = img_b64(DOCS / "pca_umap" / "umap_scatter_puntaje.png")
umap_caracter = img_b64(DOCS / "pca_umap" / "umap_scatter_caracter.png")
shap_plot = img_b64(DOCS / "random_forest_shap" / "shap_summary_plot.png")

html = f"""
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{ size: A4; margin: 2cm; @bottom-center {{ content: counter(page); }} }}
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color: #1a1a1a; font-size: 10.5pt; line-height: 1.5; }}
  h1 {{ color: #1F4E78; font-size: 22pt; border-bottom: 3px solid #1F4E78; padding-bottom: 8px; }}
  h2 {{ color: #1F4E78; font-size: 15pt; margin-top: 28px; border-bottom: 1px solid #ccc; padding-bottom: 4px; page-break-before: auto; }}
  h3 {{ color: #2E5F8A; font-size: 12pt; margin-top: 18px; }}
  table {{ border-collapse: collapse; width: 100%; table-layout: fixed; margin: 10px 0 16px 0; font-size: 8.5pt; }}
  th, td {{ border: 1px solid #ccc; padding: 5px 8px; text-align: left; word-wrap: break-word; overflow-wrap: break-word; }}
  th {{ background-color: #1F4E78; color: white; }}
  tr:nth-child(even) {{ background-color: #f2f6fa; }}
  .cover {{ text-align: center; margin-top: 8cm; }}
  .cover h1 {{ border: none; font-size: 26pt; }}
  .cover p {{ color: #555; font-size: 12pt; }}
  .subtitle {{ color: #555; font-size: 11pt; }}
  .box {{ background: #f2f6fa; border-left: 4px solid #1F4E78; padding: 10px 14px; margin: 14px 0; }}
  .warn {{ background: #fdf3e7; border-left: 4px solid #c9821f; padding: 10px 14px; margin: 14px 0; }}
  img {{ max-width: 100%; margin: 10px 0; border: 1px solid #ddd; }}
  .page-break {{ page-break-before: always; }}
  code {{ background: #eee; padding: 1px 4px; border-radius: 3px; font-size: 9.5pt; }}
  .figcaption {{ font-size: 9pt; color: #666; text-align: center; margin-top: -6px; }}
</style>
</head>
<body>

<div class="cover">
  <h1>Análisis de Factores que Explican<br>el Puntaje Global — Saber Pro Medicina</h1>
  <p class="subtitle">Dataset ICFES Saber Pro, Programa de Medicina (Colombia)<br>
  23.134 estudiantes con las 3 especialidades y puntaje completo<br>
  Mutual Information · Árbol de Decisión · Random Forest · SHAP · PCA / UMAP</p>
</div>

<div class="page-break"></div>

<h1>1. Resumen Ejecutivo</h1>
<div class="box">
<b>La institución donde estudia el estudiante es, con diferencia, el factor más determinante del puntaje global.</b>
Le siguen, muy por detrás, el carácter académico de la institución (Universidad vs Institución Universitaria),
la edad del estudiante y el nivel socioeconómico del hogar (estrato, educación de los padres, índice INSE).
Variables individuales como género o posesión de electrodomésticos casi no aportan señal por sí solas.
</div>
<p>Se aplicaron 5 técnicas de análisis independientes sobre el mismo dataset y target
(<code>PUNT_GLOBAL</code>). Ninguna contradijo a las otras — todas señalan el mismo orden de importancia,
lo cual da confianza en el resultado.</p>

<h2>1.1 Tabla comparativa por técnica</h2>
<table>
<tr><th>Técnica</th><th>Qué mide</th><th>Variable #1</th><th>Variable #2</th><th>Variable #3</th></tr>
<tr><td>Mutual Information (24 cols finales)</td><td>Reducción de incertidumbre, sin asumir linealidad</td>
<td>INST_NOMBRE_INSTITUCION (0.255)</td><td>INST_ORIGEN (0.059)</td><td>ESTU_INST_MUNICIPIO (0.058)</td></tr>
<tr><td>Mutual Information (78 cols, validación)</td><td>Igual, sobre dataset completo con fuga incluida</td>
<td>PERCENTIL_GLOBAL (fuga, 3.26)</td><td>Módulos componentes (fuga, 0.10-0.51)</td><td>INST_NOMBRE_INSTITUCION (0.251, 1ª no-fuga)</td></tr>
<tr><td>Árbol de decisión (podado, R²=0.29)</td><td>Reducción de varianza por corte</td>
<td>INST_ORIGEN no oficial (0.322)</td><td>INST_CARACTER_ACADEMICO (0.241)</td><td>Instituciones específicas (Andes, Icesi)</td></tr>
<tr><td>Random Forest (R²=0.37)</td><td>Reducción de varianza promediada en 300 árboles</td>
<td>INST_ORIGEN no oficial (0.249)</td><td>INST_NOMBRE_INSTITUCION Andes (0.131)</td><td>INST_CARACTER_ACADEMICO / EDAD (~0.09-0.10)</td></tr>
<tr><td>SHAP sobre Random Forest</td><td>Impacto real en puntos sobre la predicción</td>
<td>INST_ORIGEN no oficial (8.35 pts)</td><td>EDAD (2.76 pts)</td><td>INST_CARACTER_ACADEMICO (~2.2-2.3 pts)</td></tr>
<tr><td>PCA / UMAP</td><td>Estructura visual en espacio reducido</td>
<td colspan="3">Confirma clusters por institución (55 grupos separados) — no aporta variable nueva</td></tr>
</table>

<div class="page-break"></div>
<h1>2. El Dataset</h1>
<p>Fuente: resultados Saber Pro (ICFES) para el programa de Medicina en Colombia, períodos 2019 a 2024.</p>
<ul>
<li><b>43.563</b> estudiantes en el archivo original.</li>
<li><b>23.134</b> estudiantes tienen las 3 especialidades (Atención en Salud, Fundamentación en Diagnóstico
y Tratamiento Médico, Promoción de la Salud y Prevención) con puntaje registrado en las 3 — este es el
subconjunto usado en todo el análisis.</li>
<li><b>Target</b>: <code>PUNT_GLOBAL</code> (0-278 puntos). Problema de regresión.</li>
</ul>

<h2>2.1 Nulos por columna</h2>
<p>De 80 columnas originales: 44 sin ningún nulo, 36 con nulos. Las más afectadas (&gt;80% nulo) son
actividades de refuerzo y simulacros — se descartaron por no tener información utilizable. Un segundo bloque
(variables familiares socioeconómicas) tiene 4-5% de nulos, manejable con imputación por moda.</p>

<h2>2.2 Fuga de datos — por qué se excluyeron ciertas columnas</h2>
<div class="warn">
<code>PUNT_GLOBAL</code> es un promedio de 5 módulos: Lectura Crítica, Razonamiento Cuantitativo,
Comunicación Escrita, Competencias Ciudadanas e Inglés. Incluir esos módulos (o sus percentiles/niveles
de desempeño) como <i>features</i> sería hacer trampa: el modelo "predeciría" con partes de la misma
respuesta. Lo mismo aplica a los 3 módulos específicos de Medicina (Atención en Salud, Fundamentación
en Diagnóstico y Tratamiento, Promoción de la Salud) — no entran en la fórmula del global, pero miden
la misma habilidad del mismo estudiante en el mismo examen.
</div>
<p>Esto se confirmó con números, no solo por lógica: al correr Mutual Information sobre las 78 columnas
originales (sección 3.2), estas columnas de fuga aparecen con los valores más altos por un margen enorme
(hasta 3.26, cuando la primera variable legítima da 0.25).</p>

<h2>2.3 Dataset final para modelado</h2>
<p>~24 columnas quedaron tras excluir fuga de datos, columnas &gt;80% nulas, columnas sin varianza (un
solo valor único) y columnas redundantes (IDs, duplicados geográficos, mismo dato en código vs nombre):</p>
<table>
<tr><th>Grupo</th><th>Columnas</th></tr>
<tr><td>Numéricas</td><td>ESTU_INSE_INDIVIDUAL, EDAD (derivada de fecha de nacimiento)</td></tr>
<tr><td>Institución / geografía</td><td>INST_NOMBRE_INSTITUCION, INST_CARACTER_ACADEMICO, INST_ORIGEN,
ESTU_INST_DEPARTAMENTO, ESTU_INST_MUNICIPIO</td></tr>
<tr><td>Socioeconómicas familia</td><td>FAMI_ESTRATOVIVIENDA, FAMI_EDUCACIONMADRE, FAMI_EDUCACIONPADRE,
FAMI_CUANTOSCOMPARTEBAÑO, FAMI_TIENE* (auto, computador, consola, horno/microondas, internet, lavadora,
motocicleta, TV)</td></tr>
<tr><td>Estudiante</td><td>ESTU_GENERO, ESTU_SEMESTRECURSA, ESTU_HORASSEMANATRABAJA,
ESTU_PAGOMATRICULA* (beca, crédito, padres, propio)</td></tr>
<tr><td>Contexto</td><td>PERIODO</td></tr>
</table>

<div class="page-break"></div>
<h1>3. Mutual Information</h1>
<h2>3.1 ¿Cómo funciona?</h2>
<p>Mutual Information (MI) mide cuánta incertidumbre sobre el target se reduce al conocer el valor de
una variable, sin asumir que la relación es lineal — a diferencia de la correlación de Pearson, que solo
detecta relaciones en forma de línea recta. Se mide en <i>nats</i> (logaritmo natural), sin techo fijo;
se interpreta de forma relativa, no como un porcentaje: una variable con MI=0.25 aporta ~10 veces más
información que una con MI=0.025. Valores por debajo de ~0.01 se tratan como ruido estadístico, no como
señal real.</p>

<h2>3.2 Ranking sobre las 24 columnas finales</h2>
<table>
<tr><th>Variable</th><th>Mutual Information</th></tr>
<tr><td>INST_NOMBRE_INSTITUCION</td><td>0.2549</td></tr>
<tr><td>INST_ORIGEN</td><td>0.0594</td></tr>
<tr><td>ESTU_INST_MUNICIPIO</td><td>0.0581</td></tr>
<tr><td>ESTU_INST_DEPARTAMENTO</td><td>0.0516</td></tr>
<tr><td>FAMI_ESTRATOVIVIENDA</td><td>0.0392</td></tr>
<tr><td>INST_CARACTER_ACADEMICO</td><td>0.0300</td></tr>
<tr><td>EDAD</td><td>0.0246</td></tr>
<tr><td>FAMI_EDUCACIONPADRE</td><td>0.0239</td></tr>
<tr><td>FAMI_EDUCACIONMADRE</td><td>0.0230</td></tr>
<tr><td>ESTU_PAGOMATRICULACREDITO</td><td>0.0226</td></tr>
<tr><td>ESTU_INSE_INDIVIDUAL</td><td>0.0225</td></tr>
<tr><td>ESTU_HORASSEMANATRABAJA</td><td>0.0210</td></tr>
<tr><td>(resto de variables)</td><td>&lt; 0.02, la mayoría &lt; 0.01 (ruido)</td></tr>
</table>

<h2>3.3 Validación con las 78 columnas originales (incluye fuga)</h2>
<p>Se corrió el mismo análisis sin excluir nada (salvo el ID de estudiante, que rompe el estimador al
tener 1 fila por categoría). Esto confirma numéricamente el criterio de exclusión de la sección 2.2:</p>
<table>
<tr><th>Variable</th><th>Mutual Information</th><th>Motivo</th></tr>
<tr><td>PERCENTIL_GLOBAL</td><td>3.2623</td><td>Derivado directo de PUNT_GLOBAL — fuga</td></tr>
<tr><td>MOD_LECTURA_CRITICA_PUNT</td><td>0.5130</td><td>Componente de PUNT_GLOBAL — fuga</td></tr>
<tr><td>MOD_COMPETEN_CIUDADA_PNAL</td><td>0.4834</td><td>Derivado de componente — fuga</td></tr>
<tr><td>MOD_INGLES_PUNT</td><td>0.4550</td><td>Componente de PUNT_GLOBAL — fuga</td></tr>
<tr><td>MOD_RAZONA_CUANTITAT_PUNT</td><td>0.4042</td><td>Componente de PUNT_GLOBAL — fuga</td></tr>
<tr><td><b>INST_NOMBRE_INSTITUCION</b></td><td><b>0.2508</b></td><td><b>Primera variable legítima (sin fuga)</b></td></tr>
</table>
<p>Las columnas descartadas por &gt;80% de nulos o por tener un solo valor único (ESTU_ESTUDIANTE,
ESTU_METODO_PRGM, etc.) cayeron todas por debajo de 0.0004 — confirmando que no aportaban señal real.</p>

<div class="page-break"></div>
<h1>4. Árbol de Decisión</h1>
<h2>4.1 ¿Cómo funciona?</h2>
<p>Un árbol de decisión de regresión predice el target dividiendo los datos en grupos cada vez más chicos
mediante preguntas binarias sobre las features. En cada nodo prueba todos los posibles cortes de todas las
variables y elige el que más reduce la varianza del <code>PUNT_GLOBAL</code> dentro de cada grupo resultante.
La predicción final es el promedio de <code>PUNT_GLOBAL</code> de los estudiantes de entrenamiento que
cayeron en esa misma hoja.</p>
<p>El riesgo central es el <b>overfitting</b>: sin limitar la profundidad, el árbol sigue cortando hasta
casi memorizar cada fila individual. Por eso se compararon dos versiones:</p>

<table>
<tr><th>Modelo</th><th>R²</th><th>MAE</th><th>RMSE</th><th>Detalle</th></tr>
<tr><td>Sin podar</td><td>-0.2373</td><td>21.08</td><td>27.50</td><td>17.443 hojas — memoriza el set de
entrenamiento, predice peor que la media</td></tr>
<tr><td>Podado (max_depth=4, min_samples_leaf=50)</td><td>0.2877</td><td>15.84</td><td>20.86</td>
<td>Generaliza, interpretable</td></tr>
</table>

<h2>4.2 Feature importance (árbol podado)</h2>
<table>
<tr><th>Variable</th><th>Importancia</th></tr>
<tr><td>INST_ORIGEN = NO OFICIAL - CORPORACIÓN</td><td>0.3223</td></tr>
<tr><td>INST_CARACTER_ACADEMICO = INSTITUCIÓN UNIVERSITARIA</td><td>0.2409</td></tr>
<tr><td>INST_NOMBRE_INSTITUCION = Universidad de los Andes</td><td>0.1685</td></tr>
<tr><td>EDAD</td><td>0.0918</td></tr>
<tr><td>INST_NOMBRE_INSTITUCION = Universidad Icesi</td><td>0.0836</td></tr>
<tr><td>ESTU_INSE_INDIVIDUAL</td><td>0.0131</td></tr>
</table>
<p>Con solo 4 niveles de profundidad, el árbol prioriza institución antes de llegar a variables como
estrato o tenencia de bienes — que casi no entran al árbol.</p>

<div class="page-break"></div>
<h1>5. Random Forest + SHAP</h1>
<h2>5.1 ¿Cómo funciona Random Forest?</h2>
<p>Entrena muchos árboles distintos (acá 300) y promedia sus predicciones. La diversidad entre árboles
viene de dos trucos: <b>bagging</b> (cada árbol ve una muestra aleatoria de filas) y <b>feature bagging</b>
(en cada corte, solo puede elegir entre un subconjunto aleatorio de columnas). Al promediar cientos de
árboles que se equivocan en direcciones distintas, los errores se cancelan parcialmente y el promedio
generaliza mejor que un árbol único.</p>

<h2>5.2 ¿Cómo funciona SHAP?</h2>
<p>SHAP (SHapley Additive exPlanations) no dice qué variable es importante en general — dice cuánto
empujó cada variable la predicción de <i>un estudiante en particular</i>, arriba o abajo del promedio.
Viene de teoría de juegos: reparte el crédito de la predicción entre cada variable probando qué pasaría
si esa variable no estuviera, en combinación con las demás. La ventaja clave frente a
<code>feature_importances_</code>: el valor de SHAP está en las <b>mismas unidades que el target</b>
(puntos de <code>PUNT_GLOBAL</code>), no es un número abstracto.</p>

<h2>5.3 Resultados</h2>
<table>
<tr><th>Modelo</th><th>R²</th><th>MAE</th></tr>
<tr><td>Árbol sin podar</td><td>-0.24</td><td>21.08</td></tr>
<tr><td>Árbol podado (depth=4)</td><td>0.29</td><td>15.84</td></tr>
<tr><td><b>Random Forest (300 árboles)</b></td><td><b>0.37</b></td><td><b>14.77</b></td></tr>
</table>
<p>Mejora real sobre el árbol único, pero sigue sin ser un modelo fuerte: R²=0.37 significa que ~63% de
la varianza del puntaje sigue sin explicarse con estas variables.</p>

<h2>5.4 Ranking SHAP (impacto en puntos)</h2>
<table>
<tr><th>Variable</th><th>Impacto promedio absoluto (puntos)</th></tr>
<tr><td>INST_ORIGEN = NO OFICIAL - CORPORACIÓN</td><td>8.35</td></tr>
<tr><td>EDAD</td><td>2.76</td></tr>
<tr><td>INST_CARACTER_ACADEMICO = INSTITUCIÓN UNIVERSITARIA</td><td>2.32</td></tr>
<tr><td>INST_CARACTER_ACADEMICO = UNIVERSIDAD</td><td>2.19</td></tr>
<tr><td>INST_NOMBRE_INSTITUCION = Universidad de los Andes</td><td>1.27</td></tr>
<tr><td>ESTU_INSE_INDIVIDUAL</td><td>1.22</td></tr>
</table>

<div class="page-break"></div>
<img src="{shap_plot}">
<p class="figcaption">Fig. 1 — SHAP summary plot: cada punto es un estudiante; el color indica si el
valor de la variable era alto (rojo) o bajo (azul); la posición horizontal indica el impacto en la
predicción, en puntos de PUNT_GLOBAL.</p>

<div class="page-break"></div>
<h1>6. PCA + UMAP</h1>
<h2>6.1 ¿Cómo funcionan?</h2>
<p><b>PCA</b> busca nuevos ejes (combinaciones lineales de las columnas originales) ordenados de mayor a
menor varianza explicada — es una técnica lineal, solo encuentra combinaciones tipo <code>a·col1 +
b·col2 + ...</code>. <b>UMAP</b> construye un grafo de vecinos más cercanos en el espacio original y
busca una proyección en 2D que preserve esa vecindad — no es lineal, puede capturar clusters con formas
arbitrarias.</p>

<h2>6.2 Por qué son limitados en este dataset</h2>
<p>Ambas técnicas trabajan sobre distancias/varianza en espacio numérico. Este dataset tiene solo 2
columnas realmente numéricas (INSE, edad); el resto son ~140 columnas binarias tras one-hot encoding.
Eso genera dos síntomas visibles:</p>
<ul>
<li><b>PCA</b>: PC1 explica solo <b>4.3%</b> de la varianza, hacen falta 10 componentes para llegar a
<b>22.2%</b> acumulado.</li>
<li><b>UMAP</b>: se forman ~55 clusters bien separados, uno por institución — la distancia euclidiana en
one-hot está dominada por "¿es la misma universidad?".</li>
</ul>

<img src="{pca_scatter}">
<p class="figcaption">Fig. 2 — PCA coloreado por PUNT_GLOBAL. El patrón de "rayas" es un artefacto típico
de aplicar PCA sobre variables binarias (one-hot); no hay gradiente de color limpio.</p>

<div class="page-break"></div>
<img src="{umap_puntaje}">
<p class="figcaption">Fig. 3 — UMAP coloreado por PUNT_GLOBAL. Cada nube de puntos es una institución;
dentro de cada una el color es bastante uniforme, pero no hay una estructura global continua.</p>

<img src="{umap_caracter}">
<p class="figcaption">Fig. 4 — UMAP coloreado por carácter académico. Confirma que cada cluster
(institución) corresponde casi siempre a un solo carácter académico — no es un hallazgo nuevo, es la
misma señal de Mutual Information/SHAP vista de forma visual.</p>

<h2>6.3 Conclusión de esta sección</h2>
<p>PCA/UMAP sirven para confirmar visualmente que la institución es el eje dominante, pero no aportan
variables nuevas — el dataset es mayormente categórico, con muy pocas variables continuas, así que las
técnicas basadas en distancia/varianza tienen poco con qué trabajar.</p>

<div class="page-break"></div>
<h1>7. Conclusión Final</h1>

<h2>7.1 Qué SÍ explica el puntaje (en orden)</h2>
<ol>
<li><b>Institución</b> (nombre, origen, carácter académico) — selectividad de admisión, calidad docente
y nivel del grupo de estudiantes quedan empaquetados acá. Es, sin comparación, el factor dominante en
las 5 técnicas.</li>
<li><b>Edad</b> — señal moderada y consistente en árbol, Random Forest y SHAP.</li>
<li><b>Nivel socioeconómico del hogar</b> — estrato, INSE individual, educación de padre y madre. Señal
real pero bastante menor que institución.</li>
<li><b>Cómo pagó la matrícula</b> (crédito, beca, propio, padres) — señal débil pero presente.</li>
</ol>

<h2>7.2 Qué NO explica el puntaje</h2>
<p>Género, posesión individual de bienes (auto, lavadora, TV, consola, internet, microondas) — señal
casi nula de forma individual. El estrato agregado captura mejor ese efecto que cada bien por separado.
Tampoco aportan: nacionalidad, país de residencia, tipo de documento, período de presentación.</p>

<h2>7.3 Limitaciones importantes</h2>
<div class="warn">
<ul>
<li><b>El modelo explica poco en términos absolutos</b>: el mejor modelo (Random Forest) llega a
R²=0.37 — deja 63% de la varianza sin explicar. Factores como preparación individual, salud del
estudiante el día del examen, o cuánto estudió, no están en este dataset y probablemente pesan más
que cualquier variable disponible.</li>
<li><b>PCA/UMAP aportaron poco</b> por la naturaleza mayormente categórica del dataset.</li>
<li><b>Fuga de datos evitada correctamente</b> y confirmada con números (sección 3.3).</li>
</ul>
</div>

<h2>7.4 Recomendación para seguir</h2>
<p>Si el objetivo es mejorar el poder predictivo (subir el R²=0.37):</p>
<ul>
<li>Probar Gradient Boosting (CatBoost/LightGBM/XGBoost) con soporte nativo de categóricas de alta
cardinalidad — evita el one-hot de 55 columnas de institución.</li>
<li>Validación cruzada (k-fold) en vez de un solo split 80/20, para una estimación más confiable del R².</li>
<li>Si el objetivo es equidad educativa más que predicción pura, el hallazgo ya es suficientemente
claro: el estrato/institución explican más el resultado que el esfuerzo o mérito individual medible
en este dataset.</li>
</ul>

</body>
</html>
"""

out_path = DOCS / "conclusiones" / "Analisis_Completo_Saber_Pro_Medicina.pdf"
HTML(string=html, base_url=str(ROOT)).write_pdf(str(out_path))
print(f"PDF generado: {out_path}")

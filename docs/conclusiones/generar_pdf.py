"""Genera el informe PDF formal a partir de conclusion_final.md y rankings CSV."""
import base64
import csv
import html
import subprocess
from pathlib import Path

try:
    from weasyprint import HTML
except (ModuleNotFoundError, OSError):  # permite usar el fallback de macOS
    HTML = None

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
OUT = DOCS / "conclusiones"


def read_ranking(path, value_name, limit=None, key_name=""):
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows = [(row.get(key_name, ""), float(row[value_name])) for row in rows]
    return rows if limit is None else rows[:limit]


def table(rows, headers, decimals=4):
    body = []
    for row in rows:
        cells = []
        for value in row:
            if isinstance(value, float):
                value = f"{value:.{decimals}f}"
            cells.append(f"<td>{html.escape(str(value))}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    head = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
    return f'<table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def image_data(path):
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


mi = read_ranking(DOCS / "etapa_1_mutual_information" / "mutual_info_ranking_24.csv", "mutual_info")
mi_leak = read_ranking(DOCS / "etapa_1_mutual_information" / "mutual_info_ranking_78.csv", "mutual_info", 20)
tree = read_ranking(DOCS / "etapa_2_decision_tree" / "feature_importance.csv", "importance")
rf = read_ranking(DOCS / "etapa_3_random_forest_shap" / "rf_feature_importance.csv", "importance")
shap = read_ranking(DOCS / "etapa_3_random_forest_shap" / "shap_ranking.csv", "mean_abs_shap")
cv_importance = read_ranking(
    DOCS / "etapa_5_sin_institucion_cv" / "feature_importance_cv.csv",
    "importance_mean", key_name="feature",
)
groupkfold_importance = read_ranking(
    DOCS / "etapa_6_groupkfold_institucion" / "feature_importance_groupkfold.csv",
    "importance_mean", key_name="feature",
)
with (DOCS / "etapa_7_permutation_importance" / "permutation_vs_mdi_importance.csv").open(
    encoding="utf-8", newline=""
) as handle:
    permutation_rows = list(csv.DictReader(handle))
permutation_by_variable = {row["variable"]: row for row in permutation_rows}

mi_html = table(mi, ["Variable", "MI"])
leak_html = table(mi_leak, ["Variable (validación 78 columnas)", "MI"])
tree_html = table(tree, ["Variable/categoría", "Importancia"])
rf_html = table(rf, ["Variable/categoría", "Importancia"])
shap_html = table(shap, ["Variable/categoría", "Impacto medio absoluto (puntos)"], 2)
cv_importance_html = table(cv_importance, ["Variable", "Importancia media (CV k=5, sin institución)"])
groupkfold_importance_html = table(groupkfold_importance, ["Variable", "Importancia media (GroupKFold k=5, con institución)"])
permutation_vs_mdi_order = [
    "INST_ORIGEN",
    "INST_CARACTER_ACADEMICO",
    "EDAD",
    "ESTU_INSE_INDIVIDUAL",
    "INST_NOMBRE_INSTITUCION",
    "ESTU_INST_DEPARTAMENTO",
    "ESTU_INST_MUNICIPIO",
]
permutation_vs_mdi_html = table(
    [
        [
            variable,
            permutation_by_variable[variable]["mdi_rank"],
            permutation_by_variable[variable]["permutation_rank"],
            float(permutation_by_variable[variable]["mdi_importance_mean"]),
            float(permutation_by_variable[variable]["permutation_importance_mean"]),
        ]
        for variable in permutation_vs_mdi_order
    ],
    ["Variable", "Rank MDI", "Rank permutación", "MDI media", "Permutación media"],
)
r2_comparison_html = table(
    [
        ["Etapa 3", "Split único 80/20 (instituciones compartidas train/test)", "Sí", "0.374"],
        ["Etapa 5", "KFold aleatorio, k=5 (instituciones compartidas dentro de cada fold)", "No", "0.186 ± 0.011"],
        ["Etapa 6", "GroupKFold, k=5 (instituciones de validación nunca vistas)", "Sí", "0.120 ± 0.146"],
    ],
    ["Etapa", "Esquema de validación", "¿Incluye institución?", "R²"],
)
shap_plot = image_data(DOCS / "etapa_3_random_forest_shap" / "shap_summary_plot.png")
pca_plot = image_data(DOCS / "etapa_4_pca_umap" / "pca_scatter_puntaje.png")
umap_plot = image_data(DOCS / "etapa_4_pca_umap" / "umap_scatter_puntaje.png")

html_doc = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><style>
@page {{ size:A4; margin:1.7cm 1.8cm 1.8cm; @bottom-center {{ content:"Página " counter(page); color:#64748b; font-size:8pt; }} }}
body {{ font-family:Arial,Helvetica,sans-serif; color:#172033; font-size:9.5pt; line-height:1.42; }}
h1 {{ color:#123b5d; font-size:21pt; border-bottom:3px solid #1d7196; padding-bottom:7px; margin:0 0 14px; }}
h2 {{ color:#164e70; font-size:14pt; border-bottom:1px solid #b8cbd7; padding-bottom:4px; margin-top:24px; }}
h3 {{ color:#246b86; font-size:11pt; margin-top:16px; }}
p {{ margin:7px 0; }} ul,ol {{ margin-top:5px; }}
table {{ border-collapse:collapse; width:100%; margin:9px 0 14px; font-size:7.5pt; page-break-inside:auto; }}
thead {{ display:table-header-group; }} tr {{ page-break-inside:avoid; }} th,td {{ border:1px solid #cbd5e1; padding:4px 5px; text-align:left; overflow-wrap:anywhere; }}
th {{ background:#164e70; color:white; }} tr:nth-child(even) td {{ background:#f3f7fa; }}
.cover {{ height:22cm; display:flex; flex-direction:column; justify-content:center; text-align:center; }}
.cover h1 {{ border:0; font-size:27pt; }} .cover .rule {{ width:80px; border-top:4px solid #e49b35; margin:20px auto; }}
.subtitle {{ color:#526579; font-size:12pt; }} .small {{ color:#64748b; font-size:8.5pt; }}
.box {{ background:#eef6fa; border-left:5px solid #1d7196; padding:10px 13px; margin:12px 0; }}
.warn {{ background:#fff6e8; border-left:5px solid #d28a20; padding:10px 13px; margin:12px 0; }}
.page-break {{ page-break-before:always; }} img {{ max-width:100%; max-height:16cm; display:block; margin:10px auto; border:1px solid #d8e0e7; }}
.caption {{ text-align:center; color:#64748b; font-size:8pt; }} code {{ font-family:monospace; background:#eef2f5; padding:1px 3px; }}
</style></head><body>
<section class="cover"><h1>Variables asociadas con<br><i>PUNT_GLOBAL</i></h1><div class="rule"></div><p class="subtitle">Informe técnico — Saber Pro Medicina (Colombia)</p><p>Mutual Information · Árbol de Decisión · Random Forest · SHAP · PCA/UMAP</p><p class="small">23.134 estudiantes · períodos 2019–2024 · versión generada desde artefactos reproducibles</p></section>

<h1>Resumen ejecutivo</h1>
<div class="box"><b>El tipo de institución es señal real y generalizable; el nombre puntual de la institución no lo es.</b> Nombre, origen y carácter académico ocupan los primeros lugares en todos los métodos predictivos, pero no pesan igual bajo una medición robusta de generalización: <code>INST_ORIGEN</code> e <code>INST_CARACTER_ACADEMICO</code> (tipo de institución) se mantienen como las variables más importantes al medir permutation importance agrupada, mientras que <code>INST_NOMBRE_INSTITUCION</code> cae del puesto #1 (MDI) al #24 de 27, con caída de R² prácticamente nula — evidencia de memorización, no de señal transferible (ver sección 6). Edad e indicadores socioeconómicos aportan señal secundaria; género y muchos bienes del hogar tienen asociación baja. El mejor modelo, Random Forest, alcanza R²=0.37 en un único split 80/20 — pero al validar con <code>GroupKFold</code> agrupando por institución (instituciones de validación nunca vistas en entrenamiento) ese R² cae a 0.12 ± 0.15, evidencia adicional de memorización institucional.</div>
<p>El hallazgo es predictivo y asociativo: no demuestra que una institución cause un puntaje. El mejor modelo, Random Forest, alcanza R²=0.37 en un único split 80/20, por lo que gran parte de la variación permanece sin explicar. Esa cifra comparte instituciones entre entrenamiento y prueba; bajo validación cruzada agrupada por institución (<code>GroupKFold</code>) el R² cae a ~0.12, y si se remueve la institución por completo (K-Fold sin institución) el R² es ~0.19. El tipo de institución (origen, carácter académico) sigue siendo la señal más asociada y generalizable al puntaje; en cambio, buena parte del desempeño original de 0.37 —y de la importancia del nombre puntual de la institución— reflejaba patrones específicos de las instituciones vistas en entrenamiento, no una capacidad de generalización a instituciones nuevas.</p>
{table([["Mutual Information", "Institución (0.2549)", "MI univariada; sin techo fijo"], ["Árbol podado", "Origen institucional (0.3223)", "R²=0.2877; MAE=15.84"], ["Random Forest", "Origen institucional (0.2489)", "R²=0.37; MAE=14.77"], ["SHAP", "Origen institucional (8.35 puntos)", "Impacto absoluto medio"], ["PCA / UMAP", "Clusters institucionales", "Confirmación visual"]], ["Método", "Señal principal", "Lectura"])}

<h1>1. Datos, variables y metodología</h1>
<p>La fuente es el archivo ICFES Saber Pro de Medicina, con 43.563 registros originales. Se analizaron 23.134 estudiantes con las tres especialidades y puntaje completo. El objetivo es <code>PUNT_GLOBAL</code>, tratado como regresión. La edad se deriva de la fecha de nacimiento; se imputan numéricas con mediana y categóricas con moda.</p>
<h2>Grupos de variables</h2>
<ul><li><b>Institución/geografía:</b> nombre, origen, carácter académico, departamento y municipio.</li><li><b>Socioeconomía:</b> estrato, educación de madre/padre, baño e indicadores de bienes.</li><li><b>Estudiante:</b> edad, género, semestre, horas de trabajo y pago de matrícula.</li><li><b>Contexto:</b> período e índice INSE.</li></ul>
<p>MI usa codificación ordinal y `mutual_info_regression`; los árboles usan one-hot. La evaluación de árbol y bosque utiliza <code>train_test_split(test_size=0.2, random_state=0)</code>. SHAP se calcula con TreeExplainer sobre una muestra de hasta 2.000 estudiantes del test.</p>
<h2>Fuga de información y exclusiones</h2>
<div class="warn"><b>No se usan variables de resultado.</b> Se excluyen los componentes, percentiles y niveles de desempeño del examen, además de los tres módulos específicos de Medicina. Son resultados del mismo examen o derivados de <code>PUNT_GLOBAL</code> y producirían fuga.</div>
<p>La comprobación sobre las 78 columnas originales coloca <code>PERCENTIL_GLOBAL</code> en MI=3.2623 y los módulos generales aproximadamente entre 0.23 y 0.51; la primera variable legítima es la institución (MI=0.2508). También se eliminaron IDs, columnas constantes/casi vacías y redundancias.</p>

<div class="page-break"></div><h1>2. Rankings completos</h1>
<h2>2.1 Mutual Information — variables finales</h2>
<p>MI mide reducción de incertidumbre en nats. No es porcentaje de varianza explicada ni prueba causal. El CSV fuente contiene el ranking completo.</p>{mi_html}
<h2>2.2 Validación de fuga — 20 mayores MI de las 78 columnas</h2>{leak_html}

<div class="page-break"></div><h1>3. Árbol de decisión</h1>
<p>El modelo interpretado es un árbol podado (<code>max_depth=4</code>, <code>min_samples_leaf=50</code>): R²=0.2877, MAE=15.84 y RMSE=20.86. El árbol sin podar alcanza R²=-0.2373 por sobreajuste y tiene 17.443 hojas.</p>
<p>La importancia suma la reducción de varianza de los cortes one-hot; no equivale a un efecto individual.</p>{tree_html}

<div class="page-break"></div><h1>4. Random Forest y SHAP</h1>
<p>El bosque promedia 300 árboles (<code>max_depth=8</code>, <code>min_samples_leaf=20</code>), reduciendo la varianza del árbol individual. Resultados del split: R²=0.37, MAE=14.77. El ranking completo de importancia clásica es:</p>{rf_html}
<h2>SHAP: impacto en puntos</h2>
<p>SHAP explica la predicción del bosque en unidades de <code>PUNT_GLOBAL</code>. Los valores son magnitudes absolutas promedio: no indican dirección por sí solos. Por ejemplo, 8.35 puntos para origen institucional no significa que cada caso cambie exactamente esa cantidad.</p>{shap_html}
{('<img src="' + shap_plot + '"><p class="caption">SHAP summary plot: distribución de impactos por estudiante.</p>') if shap_plot else ''}

<div class="page-break"></div><h1>5. Síntesis y lectura sustantiva</h1>
<h2>Patrón común</h2><p>Los cuatro métodos cuantitativos coinciden en la centralidad de la institución. Sin embargo, esa aparente equivalencia entre nombre, origen y carácter académico no sobrevive a una medición más robusta de generalización — ver sección 6.4 (etapa 7): el nombre puntual resulta ser memorización, mientras que origen y carácter académico (tipo de institución) son la señal institucional que realmente se transfiere a instituciones nuevas. La edad aparece de manera estable en árbol, bosque y SHAP; estrato, INSE y educación familiar tienen una asociación menor; género, período y la mayoría de bienes del hogar tienen señal baja. PCA/UMAP forman aproximadamente 55 agrupaciones institucionales y confirman visualmente el patrón, pero no descubren una variable nueva.</p>
<h2>Qué no debe concluirse</h2><ul><li>No puede afirmarse que cambiar de institución cause un cambio concreto de puntaje.</li><li>Una importancia alta puede reflejar confusión entre selección, ubicación, recursos y composición del alumnado.</li><li>Las importancias no son coeficientes ni significancia estadística.</li><li>No puede sostenerse que el nombre puntual de una institución (<code>INST_NOMBRE_INSTITUCION</code>) tenga poder predictivo transferible a instituciones nuevas: bajo permutation importance agrupada (sección 6.4) cae del puesto #1 en MDI al #24 de 27, con caída de R² prácticamente nula.</li></ul>
<h2>Limitaciones</h2><ul><li>Asociación no implica causalidad.</li><li>El nombre de institución es categórico y de alta cardinalidad. <i>Abordado empíricamente</i> en la sección 6: al remover la institución (etapa 5, CV k=5) el R² cae de 0.374 a 0.186±0.011.</li><li>Un solo split limita la incertidumbre de las métricas y rankings. <i>Abordado empíricamente</i> en la sección 6: K-Fold (etapa 5) y GroupKFold por institución (etapa 6) muestran que el R²=0.374 del split único cae a 0.120±0.146 al validar contra instituciones nunca vistas.</li><li>El nombre de institución no es señal transferible. <i>Abordado empíricamente</i> en la sección 6.4 (etapa 7): la permutation importance agrupada muestra que el nombre cae del puesto #1 (MDI=0.2952) al #24 de 27 con caída de R² ≈0, mientras que origen y carácter académico institucional se mantienen —y suben— como las variables más importantes.</li><li>Faltan preparación, horas de estudio, salud y trayectoria escolar.</li><li>PCA/UMAP dependen de one-hot y de parámetros de visualización.</li></ul>

<div class="page-break"></div><h1>6. Validación de robustez: institución sin variable propia y generalización a instituciones nuevas</h1>
<p>Las dos limitaciones anteriores —codificación institucional y un único split— se atacaron empíricamente reentrenando el mismo Random Forest de referencia (<code>n_estimators=300, max_depth=8, min_samples_leaf=20</code>) bajo dos esquemas adicionales.</p>
<h2>6.1 Etapa 5 — sin variables de institución, con K-Fold (k=5)</h2>
<p>Se removieron <code>INST_NOMBRE_INSTITUCION</code>, <code>INST_CARACTER_ACADEMICO</code>, <code>INST_ORIGEN</code>, <code>ESTU_INST_DEPARTAMENTO</code> y <code>ESTU_INST_MUNICIPIO</code>, evaluando con K-Fold (k=5, shuffle, <code>random_state=0</code>): R²=0.186±0.011, MAE=17.21±0.18, RMSE=22.30±0.23. Quitar institución reduce el R² de ~0.37 a ~0.19: se pierde más de la mitad del poder explicativo del modelo. Las variables más importantes pasan a ser socioeconómicas y demográficas (edad, horas de trabajo, INSE individual, forma de pago de matrícula, estrato, educación de los padres), con importancias estables entre folds (coeficiente de variación ~7-10% en el top de la lista).</p>{cv_importance_html}
<h2>6.2 Etapa 6 — con institución, GroupKFold por institución (k=5)</h2>
<p>Se entrenó el mismo modelo con el set completo de variables (incluida institución), usando <code>GroupKFold(n_splits=5)</code> agrupado por <code>INST_NOMBRE_INSTITUCION</code>, de modo que las instituciones de validación de cada fold nunca aparecen en su entrenamiento (55 instituciones únicas, ninguna supera ~7% de las filas): R²=0.120±0.146, MAE=17.59±1.07, RMSE=22.78±1.53. El R² por fold (0.159, 0.013, 0.250, 0.252, -0.074) tiene una dispersión muy alta, con un fold negativo. Las variables ligadas a una institución puntual (p. ej. Universidad de los Andes: std/media ≈73%; Universidad Icesi: ≈56%) son muy inestables entre folds, mientras que <code>EDAD</code> (≈4%), <code>ESTU_INSE_INDIVIDUAL</code> (≈15%) y <code>INST_CARACTER_ACADEMICO_*</code> (≈21%) se mantienen más estables.</p>{groupkfold_importance_html}
<h2>6.3 Comparación de R² entre esquemas de validación</h2>{r2_comparison_html}
<p>El R² de etapa 6 (0.12±0.15) no solo es muy inferior al de etapa 3 (0.374): también queda por debajo del de etapa 5 (0.186±0.011), que ni siquiera usa variables de institución. Esto es evidencia de que el modelo de etapa 3 memorizaba patrones específicos de las instituciones vistas en entrenamiento, en lugar de aprender una relación generalizable entre las variables socioeconómicas/académicas y <code>PUNT_GLOBAL</code>. Esto matiza —no invalida— el hallazgo central: la institución sigue siendo la señal dominante, pero parte del R²=0.37 original reflejaba el diseño de validación (split único, sin agrupar por institución) más que capacidad predictiva genuina sobre instituciones nuevas. La sección 6.4 (etapa 7) precisa este punto a nivel de variable individual.</p>
<h2>6.4 Etapa 7 — Permutation importance agrupada vs. MDI/Gini: nombre vs. tipo de institución</h2>
<p>La importancia MDI/Gini (etapas 3 y 6) sobreestima variables categóricas de alta cardinalidad, porque el algoritmo de construcción de árboles tiene más oportunidades de encontrar un split que reduzca impureza cuantas más categorías tenga la variable, aunque ese split no generalice fuera de muestra. <code>INST_NOMBRE_INSTITUCION</code> se expande a 55 columnas dummy, la de mayor cardinalidad del feature set con margen. Para probarlo, se replicó el mismo <code>GroupKFold(n_splits=5)</code> de etapa 6 y se calculó, por variable original (agregando sus columnas dummy), tanto la MDI agregada como la <b>permutation importance agrupada</b>: en cada fold de validación se permutan a la vez todas las dummies de una variable y se mide la caída de R² respecto al modelo sin permutar (<code>n_repeats=5</code>). A diferencia de MDI, la permutación se mide en validación, con instituciones nunca vistas en entrenamiento.</p>
{permutation_vs_mdi_html}
<p>El resultado es contundente: <code>INST_NOMBRE_INSTITUCION</code> —la variable "más importante" según MDI (0.2952, puesto #1)— cae al puesto #24 de 27 en permutation importance, con caída de R² prácticamente cero (ruido numérico): romper la identidad de la institución en validación no cambia el poder predictivo del modelo, porque la importancia MDI se generaba sobre splits de instituciones de <i>entrenamiento</i> que <code>GroupKFold</code> nunca comparte con las de validación. <code>ESTU_INST_MUNICIPIO</code> y <code>ESTU_INST_DEPARTAMENTO</code> (proxies geográficos de institución) colapsan igual, con importancia por permutación <b>negativa</b> (ranks #26-27). En cambio, <code>INST_ORIGEN</code> e <code>INST_CARACTER_ACADEMICO</code> —de baja cardinalidad, compartidas entre instituciones de entrenamiento y validación— <b>suben</b> de ranking (#2→#1 y #3→#2) y quedan como las dos variables más importantes bajo este método más robusto; <code>EDAD</code> y <code>ESTU_INSE_INDIVIDUAL</code> se mantienen estables en el top. La conclusión no es "institución no importa": es que el <b>tipo/origen de institución es señal real y generalizable</b>, mientras que la <b>identidad puntual de la institución es un artefacto de memorización que MDI infla por su alta cardinalidad</b>.</p>

<div class="page-break"></div><h1>7. Reproducibilidad y referencias</h1>
<p>Para regenerar el informe desde la raíz:</p><p><code>python docs/conclusiones/generar_pdf.py</code></p>
<p>El generador lee automáticamente estos artefactos:</p><ul><li><code>docs/etapa_1_mutual_information/mutual_info_ranking_24.csv</code> y <code>mutual_info_ranking_78.csv</code></li><li><code>docs/etapa_2_decision_tree/feature_importance.csv</code> y <code>tree_rules.txt</code></li><li><code>docs/etapa_3_random_forest_shap/rf_feature_importance.csv</code>, <code>shap_ranking.csv</code> y <code>shap_summary_plot.png</code></li><li><code>docs/etapa_4_pca_umap/</code> para visualizaciones exploratorias</li><li><code>docs/etapa_5_sin_institucion_cv/random_forest_sin_institucion_cv.py</code>, <code>metrics_cv.csv</code> y <code>feature_importance_cv.csv</code></li><li><code>docs/etapa_6_groupkfold_institucion/random_forest_groupkfold_institucion.py</code>, <code>metrics_groupkfold.csv</code> y <code>feature_importance_groupkfold.csv</code></li><li><code>docs/etapa_7_permutation_importance/random_forest_permutation_importance.py</code> y <code>permutation_vs_mdi_importance.csv</code></li><li>Scripts fuente <code>*_analysis.py</code> y sus README en cada carpeta</li></ul>
<p>Los análisis se ejecutan con sus scripts documentados desde la raíz y leen <code>ESTU_MEDICINA_3_MODULOS.xlsx</code>. Este informe no modifica datos ni lógica de modelos; presenta los resultados ya calculados.</p>
<div class="box"><b>Conclusión:</b> dentro de las variables observadas, las características institucionales son las más asociadas con <code>PUNT_GLOBAL</code>, pero su poder predictivo aparente (R²=0.37) estaba parcialmente inflado por compartir instituciones entre entrenamiento y prueba: bajo <code>GroupKFold</code> por institución el R² cae a 0.12±0.15. La permutation importance agrupada (sección 6.4) precisa además que esa señal institucional no es homogénea: el tipo de institución (<code>INST_ORIGEN</code>, <code>INST_CARACTER_ACADEMICO</code>) es señal real y generalizable, mientras que el nombre puntual de la institución es en gran parte memorización sin poder predictivo transferible a instituciones nuevas. La magnitud y estabilidad causal de esa asociación requiere análisis temporal y diseños que controlen los mecanismos de selección.</div>
</body></html>"""

for filename in ("Analisis_Completo_Saber_Pro_Medicina.pdf", "Analisis_Variables_Puntaje_Global.pdf"):
    destination = OUT / filename
    if HTML is not None:
        HTML(string=html_doc, base_url=str(ROOT)).write_pdf(str(destination))
    else:
        # Fallback para macOS: Chrome renderiza el HTML sin requerir las
        # bibliotecas nativas que WeasyPrint necesita.
        chrome = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if not chrome.exists():
            raise RuntimeError(
                "WeasyPrint no está disponible y no se encontró Google Chrome para generar el PDF"
            )
        html_path = OUT / ".informe_temporal.html"
        html_path.write_text(html_doc, encoding="utf-8")
        try:
            subprocess.run(
                [
                    str(chrome), "--headless", "--no-sandbox", "--disable-gpu",
                    f"--print-to-pdf={destination}", f"file://{html_path}",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
        finally:
            html_path.unlink(missing_ok=True)
    print(f"PDF generado: {destination}")

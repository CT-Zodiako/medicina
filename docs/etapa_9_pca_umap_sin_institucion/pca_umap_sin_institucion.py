"""
Etapa 9 - PCA/UMAP con el feature set honesto (sin identidad puntual de institucion).

Motivacion:
- Etapa_4 (docs/etapa_4_pca_umap) corrio PCA + UMAP sobre el feature set COMPLETO
  original, que incluye INST_NOMBRE_INSTITUCION (variable categorica de ~55
  instituciones distintas). Ese analisis encontro ~55 agrupaciones visuales en
  el scatter de UMAP, que coincidian exactamente con clusters por institucion
  puntual: probablemente "memorizacion de identidad de universidad", no
  estructura sustantiva.
- Etapas 6 y 7 confirmaron que INST_NOMBRE_INSTITUCION, ESTU_INST_DEPARTAMENTO
  y ESTU_INST_MUNICIPIO son fuente de memorizacion/sobreajuste (no senal real),
  mientras que INST_ORIGEN e INST_CARACTER_ACADEMICO SI son senal real y
  transferible.
- Etapa_8 (docs/etapa_8_modelo_final_honesto) definio el feature set "honesto"
  del proyecto: todas las variables demograficas/socioeconomicas/familiares +
  INST_ORIGEN + INST_CARACTER_ACADEMICO, EXCLUYENDO explicitamente
  INST_NOMBRE_INSTITUCION, ESTU_INST_DEPARTAMENTO y ESTU_INST_MUNICIPIO.

Este script repite EXACTAMENTE el pipeline de etapa_4 (mismo preprocesamiento,
mismos hiperparametros de PCA y UMAP, mismo estilo de graficos), cambiando
unicamente el feature set de entrada al de etapa_8, para ver si al sacar la
identidad puntual de institucion los ~55 clusters desaparecen (esperable, si
eran solo "un cluster por universidad") o si persiste estructura real.

Adicional respecto a etapa_4: se cuantifica el numero de clusters visuales en
el embedding UMAP 2D con KMeans + seleccion de k por silhouette score (k en
2..15), ya que scikit-learn ya esta instalado y no suma dependencias nuevas.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import umap
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

df = pd.read_excel("ESTU_MEDICINA_3_MODULOS.xlsx")

df["EDAD"] = (
    pd.Timestamp("2024-01-01") - pd.to_datetime(df["ESTU_FECHANACIMIENTO"])
).dt.days // 365

target = "PUNT_GLOBAL"

# Feature set "honesto" de etapa_8 (copiado exactamente): demografia/
# socioeconomia/familia completas + INST_ORIGEN + INST_CARACTER_ACADEMICO.
# EXCLUYE explicitamente INST_NOMBRE_INSTITUCION, ESTU_INST_DEPARTAMENTO y
# ESTU_INST_MUNICIPIO (memorizacion, confirmado por etapa_6/etapa_7).
numeric_features = ["ESTU_INSE_INDIVIDUAL", "EDAD"]

categorical_features = [
    "INST_ORIGEN", "INST_CARACTER_ACADEMICO",
    "ESTU_GENERO", "ESTU_SEMESTRECURSA", "PERIODO",
    "FAMI_ESTRATOVIVIENDA", "FAMI_EDUCACIONMADRE", "FAMI_EDUCACIONPADRE",
    "FAMI_CUANTOSCOMPARTEBAÑO", "FAMI_TIENEAUTOMOVIL", "FAMI_TIENECOMPUTADOR",
    "FAMI_TIENECONSOLAVIDEOJUEGOS", "FAMI_TIENEHORNOMICROOGAS", "FAMI_TIENEINTERNET",
    "FAMI_TIENELAVADORA", "FAMI_TIENEMOTOCICLETA", "FAMI_TIENESERVICIOTV",
    "ESTU_HORASSEMANATRABAJA", "ESTU_PAGOMATRICULABECA", "ESTU_PAGOMATRICULACREDITO",
    "ESTU_PAGOMATRICULAPADRES", "ESTU_PAGOMATRICULAPROPIO",
]

work = df[[target] + numeric_features + categorical_features].copy()
work = work.loc[:, ~work.columns.duplicated()]

work[numeric_features[0]] = work[numeric_features[0]].fillna(work[numeric_features[0]].median())
for c in categorical_features:
    work[c] = work[c].fillna(work[c].mode().iloc[0])

X_raw = pd.get_dummies(work[numeric_features + categorical_features], columns=categorical_features)
X = StandardScaler().fit_transform(X_raw)

# --- PCA ---
pca = PCA(n_components=10, random_state=0)
pca_coords = pca.fit_transform(X)

explained = pd.Series(pca.explained_variance_ratio_, index=[f"PC{i+1}" for i in range(10)])
explained_cum = explained.cumsum()
print("=== Varianza explicada por componente ===")
print(explained.to_string())
print("\n=== Varianza explicada acumulada ===")
print(explained_cum.to_string())
explained.to_csv("docs/etapa_9_pca_umap_sin_institucion/pca_explained_variance.csv", header=["explained_variance_ratio"])

fig, ax = plt.subplots(figsize=(8, 6))
sc = ax.scatter(pca_coords[:, 0], pca_coords[:, 1], c=work[target], cmap="viridis", s=5, alpha=0.5)
plt.colorbar(sc, label="PUNT_GLOBAL")
ax.set_xlabel(f"PC1 ({explained.iloc[0]*100:.1f}% var)")
ax.set_ylabel(f"PC2 ({explained.iloc[1]*100:.1f}% var)")
ax.set_title("PCA (feature set honesto, sin institucion) - coloreado por PUNT_GLOBAL")
plt.tight_layout()
plt.savefig("docs/etapa_9_pca_umap_sin_institucion/pca_scatter_puntaje.png", dpi=150)
plt.close()

# --- UMAP ---
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=0)
umap_coords = reducer.fit_transform(X)

fig, ax = plt.subplots(figsize=(8, 6))
sc = ax.scatter(umap_coords[:, 0], umap_coords[:, 1], c=work[target], cmap="viridis", s=5, alpha=0.5)
plt.colorbar(sc, label="PUNT_GLOBAL")
ax.set_title("UMAP (feature set honesto, sin institucion) - coloreado por PUNT_GLOBAL")
plt.tight_layout()
plt.savefig("docs/etapa_9_pca_umap_sin_institucion/umap_scatter_puntaje.png", dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(8, 6))
for categoria in work["INST_CARACTER_ACADEMICO"].unique():
    mask = work["INST_CARACTER_ACADEMICO"] == categoria
    ax.scatter(umap_coords[mask, 0], umap_coords[mask, 1], s=5, alpha=0.5, label=categoria)
ax.legend()
ax.set_title("UMAP (feature set honesto, sin institucion) - coloreado por caracter academico")
plt.tight_layout()
plt.savefig("docs/etapa_9_pca_umap_sin_institucion/umap_scatter_caracter.png", dpi=150)
plt.close()

print("\nGraficos guardados en docs/etapa_9_pca_umap_sin_institucion/")

# --- Cuantificacion de clusters visuales en el embedding UMAP 2D ---
# Criterio simple y documentado: KMeans con seleccion de k por silhouette
# score, probando k en 2..15 sobre el embedding UMAP de 2D (no sobre X
# original), ya que scikit-learn ya esta instalado (sin sumar dependencias
# nuevas como HDBSCAN).
print("\n=== Seleccion de numero de clusters (KMeans + silhouette sobre embedding UMAP 2D) ===")
best_k = None
best_score = -1
scores = {}
for k in range(2, 16):
    km = KMeans(n_clusters=k, random_state=0, n_init=10)
    labels = km.fit_predict(umap_coords)
    score = silhouette_score(umap_coords, labels)
    scores[k] = score
    print(f"k={k:2d}  silhouette={score:.4f}")
    if score > best_score:
        best_score = score
        best_k = k

print(f"\nNumero de clusters estimado (mejor silhouette): k={best_k} (silhouette={best_score:.4f})")

pd.Series(scores, name="silhouette_score").rename_axis("k").to_csv(
    "docs/etapa_9_pca_umap_sin_institucion/kmeans_silhouette_scores.csv"
)
print("Scores de silhouette guardados en docs/etapa_9_pca_umap_sin_institucion/kmeans_silhouette_scores.csv")

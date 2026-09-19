import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import umap
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

df = pd.read_excel("ESTU_MEDICINA_3_MODULOS.xlsx")

df["EDAD"] = (
    pd.Timestamp("2024-01-01") - pd.to_datetime(df["ESTU_FECHANACIMIENTO"])
).dt.days // 365

target = "PUNT_GLOBAL"

numeric_features = ["ESTU_INSE_INDIVIDUAL", "EDAD"]

categorical_features = [
    "INST_NOMBRE_INSTITUCION", "INST_CARACTER_ACADEMICO", "INST_ORIGEN",
    "ESTU_GENERO", "ESTU_SEMESTRECURSA", "PERIODO",
    "ESTU_INST_DEPARTAMENTO", "ESTU_INST_MUNICIPIO",
    "FAMI_ESTRATOVIVIENDA", "FAMI_EDUCACIONMADRE", "FAMI_EDUCACIONPADRE",
    "FAMI_CUANTOSCOMPARTEBAÑO", "FAMI_TIENEAUTOMOVIL", "FAMI_TIENECOMPUTADOR",
    "FAMI_TIENECONSOLAVIDEOJUEGOS", "FAMI_TIENEHORNOMICROOGAS", "FAMI_TIENEINTERNET",
    "FAMI_TIENELAVADORA", "FAMI_TIENEMOTOCICLETA", "FAMI_TIENESERVICIOTV",
    "ESTU_HORASSEMANATRABAJA", "ESTU_PAGOMATRICULABECA", "ESTU_PAGOMATRICULACREDITO",
    "ESTU_PAGOMATRICULAPADRES", "ESTU_PAGOMATRICULAPROPIO",
]

work = df[[target, "INST_CARACTER_ACADEMICO", "FAMI_ESTRATOVIVIENDA"] + numeric_features + categorical_features].copy()
work = work.loc[:, ~work.columns.duplicated()]

work[numeric_features[0]] = work[numeric_features[0]].fillna(work[numeric_features[0]].median())
for c in categorical_features:
    work[c] = work[c].fillna(work[c].mode().iloc[0])
work["FAMI_ESTRATOVIVIENDA"] = work["FAMI_ESTRATOVIVIENDA"].fillna(work["FAMI_ESTRATOVIVIENDA"].mode().iloc[0])

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
explained.to_csv("docs/etapa_4_pca_umap/pca_explained_variance.csv", header=["explained_variance_ratio"])

fig, ax = plt.subplots(figsize=(8, 6))
sc = ax.scatter(pca_coords[:, 0], pca_coords[:, 1], c=work[target], cmap="viridis", s=5, alpha=0.5)
plt.colorbar(sc, label="PUNT_GLOBAL")
ax.set_xlabel(f"PC1 ({explained.iloc[0]*100:.1f}% var)")
ax.set_ylabel(f"PC2 ({explained.iloc[1]*100:.1f}% var)")
ax.set_title("PCA - coloreado por PUNT_GLOBAL")
plt.tight_layout()
plt.savefig("docs/etapa_4_pca_umap/pca_scatter_puntaje.png", dpi=150)
plt.close()

# --- UMAP ---
reducer = umap.UMAP(n_neighbors=15, min_dist=0.1, random_state=0)
umap_coords = reducer.fit_transform(X)

fig, ax = plt.subplots(figsize=(8, 6))
sc = ax.scatter(umap_coords[:, 0], umap_coords[:, 1], c=work[target], cmap="viridis", s=5, alpha=0.5)
plt.colorbar(sc, label="PUNT_GLOBAL")
ax.set_title("UMAP - coloreado por PUNT_GLOBAL")
plt.tight_layout()
plt.savefig("docs/etapa_4_pca_umap/umap_scatter_puntaje.png", dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(8, 6))
for categoria in work["INST_CARACTER_ACADEMICO"].unique():
    mask = work["INST_CARACTER_ACADEMICO"] == categoria
    ax.scatter(umap_coords[mask, 0], umap_coords[mask, 1], s=5, alpha=0.5, label=categoria)
ax.legend()
ax.set_title("UMAP - coloreado por caracter academico")
plt.tight_layout()
plt.savefig("docs/etapa_4_pca_umap/umap_scatter_caracter.png", dpi=150)
plt.close()

print("\nGraficos guardados en docs/etapa_4_pca_umap/")

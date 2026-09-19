"""
Etapa 6 - Random Forest CON variables de institucion, validado con GroupKFold
(k=5) agrupando por INST_NOMBRE_INSTITUCION, para medir generalizacion a
instituciones NUNCA VISTAS durante el entrenamiento.

Ataca la limitacion senalada en docs/conclusiones/conclusion_final.md:
"se requiere validacion cruzada y, preferiblemente, evaluacion temporal o
por institucion".

La etapa_5 ya hizo KFold CV (k=5), pero fue aleatorio (sin agrupar por
institucion): la misma institucion puede aparecer en train y test dentro de
un mismo fold, por lo que el modelo podria estar memorizando instituciones
en vez de generalizar. Aqui se usa GroupKFold con groups=INST_NOMBRE_INSTITUCION,
de forma que en cada fold las instituciones del conjunto de validacion NO
aparecen en el conjunto de entrenamiento.

Mismo feature set completo (CON institucion) que el script de referencia
docs/etapa_3_random_forest_shap/random_forest_shap_analysis.py, y mismos
hiperparametros del Random Forest que etapa_3/etapa_5:
n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1.

Comparacion esperada en consola contra:
  - etapa_3: R2=0.374 (split unico 80/20, CON institucion, instituciones
    compartidas entre train/test)
  - etapa_5: R2=0.186 +/- 0.011 (KFold aleatorio k=5, SIN institucion)
"""
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

df = pd.read_excel("ESTU_MEDICINA_3_MODULOS.xlsx")

df["EDAD"] = (
    pd.Timestamp("2024-01-01") - pd.to_datetime(df["ESTU_FECHANACIMIENTO"])
).dt.days // 365

target = "PUNT_GLOBAL"
group_col = "INST_NOMBRE_INSTITUCION"

numeric_features = ["ESTU_INSE_INDIVIDUAL", "EDAD"]

# Mismas categoricas que el script de referencia (etapa_3), CON institucion:
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

# group_col (INST_NOMBRE_INSTITUCION) ya esta dentro de categorical_features,
# igual que en etapa_3, asi que no se agrega dos veces a la seleccion de columnas.
work = df[[target] + numeric_features + categorical_features].copy()

# El vector de grupos se captura ANTES de imputar/filtrar filas, a partir del
# mismo DataFrame "work" (mismo indice que X e y), para que quede alineado
# indice a indice tras cualquier dropna/fillna posterior. No se imputa la
# institucion (es la variable de agrupacion): las filas sin institucion se
# descartan en vez de asignarles una institucion inventada.
groups_raw = work[group_col]
work = work[groups_raw.notna()].copy()

work[numeric_features[0]] = work[numeric_features[0]].fillna(work[numeric_features[0]].median())
for c in categorical_features:
    work[c] = work[c].fillna(work[c].mode().iloc[0])

groups = work[group_col]
X = pd.get_dummies(work[numeric_features + categorical_features], columns=categorical_features)
y = work[target]

n_groups = groups.nunique()
print(f"Instituciones unicas (grupos) disponibles: {n_groups}")

gkf = GroupKFold(n_splits=5)

fold_rows = []
importance_by_fold = []

print("=== Random Forest CON institucion, GroupKFold (300 arboles, max_depth=8, min_samples_leaf=20) ===")
print("GroupKFold: n_splits=5, groups=INST_NOMBRE_INSTITUCION (instituciones de validacion no vistas en entrenamiento)\n")

for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=groups), start=1):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    train_insts = set(groups.iloc[train_idx])
    val_insts = set(groups.iloc[val_idx])
    overlap = train_insts & val_insts
    assert not overlap, f"Fold {fold_idx}: instituciones solapadas entre train y val: {overlap}"

    rf = RandomForestRegressor(
        n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    pred = rf.predict(X_val)

    r2 = r2_score(y_val, pred)
    mae = mean_absolute_error(y_val, pred)
    rmse = root_mean_squared_error(y_val, pred)

    print(f"Fold {fold_idx}: instituciones_val={len(val_insts)}  n_val={len(val_idx)}  R2={r2:.4f}  MAE={mae:.2f}  RMSE={rmse:.2f}")

    fold_rows.append({"fold": fold_idx, "r2": r2, "mae": mae, "rmse": rmse})
    importance_by_fold.append(pd.Series(rf.feature_importances_, index=X.columns))

metrics_df = pd.DataFrame(fold_rows)

mean_row = {
    "fold": "mean",
    "r2": metrics_df["r2"].mean(),
    "mae": metrics_df["mae"].mean(),
    "rmse": metrics_df["rmse"].mean(),
}
std_row = {
    "fold": "std",
    "r2": metrics_df["r2"].std(),
    "mae": metrics_df["mae"].std(),
    "rmse": metrics_df["rmse"].std(),
}
metrics_df = pd.concat([metrics_df, pd.DataFrame([mean_row, std_row])], ignore_index=True)

print("\n=== Metricas agregadas entre folds (mean +/- std) ===")
print(f"R2:   {mean_row['r2']:.4f} +/- {std_row['r2']:.4f}")
print(f"MAE:  {mean_row['mae']:.2f} +/- {std_row['mae']:.2f}")
print(f"RMSE: {mean_row['rmse']:.2f} +/- {std_row['rmse']:.2f}")

print("\n=== Comparacion contra etapas previas ===")
print(f"Etapa 3 (split unico 80/20, CON institucion, instituciones compartidas train/test): R2=0.374")
print(f"Etapa 5 (KFold aleatorio k=5, SIN institucion):                                    R2=0.186 +/- 0.011")
print(f"Etapa 6 (GroupKFold k=5, CON institucion, instituciones NUNCA vistas en val):       R2={mean_row['r2']:.4f} +/- {std_row['r2']:.4f}")

diff_etapa3 = mean_row["r2"] - 0.374
print(f"\nDiferencia Etapa 6 vs Etapa 3: {diff_etapa3:+.4f}")
if diff_etapa3 < -0.05:
    print("Interpretacion: caida notable de R2 al exigir instituciones nunca vistas -> evidencia de que el")
    print("modelo de etapa_3 memorizaba instituciones especificas en vez de generalizar.")
elif diff_etapa3 > 0.05:
    print("Interpretacion: R2 de etapa_6 es mayor al de etapa_3 (resultado atipico, revisar folds/datos).")
else:
    print("Interpretacion: R2 similar al de etapa_3 -> el modelo generaliza razonablemente bien a")
    print("instituciones nuevas, no depende criticamente de haber visto la institucion en entrenamiento.")

metrics_df.to_csv("docs/etapa_6_groupkfold_institucion/metrics_groupkfold.csv", index=False)
print("\nMetricas por fold guardadas en docs/etapa_6_groupkfold_institucion/metrics_groupkfold.csv")

importance_matrix = pd.concat(importance_by_fold, axis=1)
importance_matrix.columns = [f"fold_{i}" for i in range(1, len(importance_by_fold) + 1)]

importance_summary = pd.DataFrame({
    "importance_mean": importance_matrix.mean(axis=1),
    "importance_std": importance_matrix.std(axis=1),
}).sort_values("importance_mean", ascending=False)

top20 = importance_summary[importance_summary["importance_mean"] > 0].head(20)

print("\n=== Top 20 feature importance (media +/- std entre folds) ===")
for feature, row in top20.iterrows():
    print(f"{feature:45s}  {row['importance_mean']:.4f} +/- {row['importance_std']:.4f}")

top20.to_csv("docs/etapa_6_groupkfold_institucion/feature_importance_groupkfold.csv", index_label="feature")
print("\nImportancias guardadas en docs/etapa_6_groupkfold_institucion/feature_importance_groupkfold.csv")

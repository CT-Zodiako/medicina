"""
Etapa 5 - Random Forest SIN variables de institucion/ubicacion institucional,
con validacion cruzada (K-Fold, k=5).

Ataca las dos limitaciones senaladas en docs/conclusiones/conclusion_final.md:
1. INST_NOMBRE_INSTITUCION (y columnas relacionadas) es un proxy de alta
   cardinalidad que domina las importancias en todos los analisis previos.
   Aqui se elimina junto con INST_CARACTER_ACADEMICO, INST_ORIGEN,
   ESTU_INST_DEPARTAMENTO y ESTU_INST_MUNICIPIO.
2. El script de referencia (docs/etapa_3_random_forest_shap/random_forest_shap_analysis.py)
   usa un unico train_test_split. Aqui se reemplaza por KFold(n_splits=5) para
   ver si las metricas y las importancias son estables entre folds.

Mismos hiperparametros del Random Forest que el script de referencia:
n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

df = pd.read_excel("ESTU_MEDICINA_3_MODULOS.xlsx")

df["EDAD"] = (
    pd.Timestamp("2024-01-01") - pd.to_datetime(df["ESTU_FECHANACIMIENTO"])
).dt.days // 365

target = "PUNT_GLOBAL"

numeric_features = ["ESTU_INSE_INDIVIDUAL", "EDAD"]

# Mismas categoricas que el script de referencia, EXCEPTO las ligadas a
# institucion/ubicacion institucional (proxy de alta cardinalidad):
#   INST_NOMBRE_INSTITUCION, INST_CARACTER_ACADEMICO, INST_ORIGEN,
#   ESTU_INST_DEPARTAMENTO, ESTU_INST_MUNICIPIO
categorical_features = [
    "ESTU_GENERO", "ESTU_SEMESTRECURSA", "PERIODO",
    "FAMI_ESTRATOVIVIENDA", "FAMI_EDUCACIONMADRE", "FAMI_EDUCACIONPADRE",
    "FAMI_CUANTOSCOMPARTEBAÑO", "FAMI_TIENEAUTOMOVIL", "FAMI_TIENECOMPUTADOR",
    "FAMI_TIENECONSOLAVIDEOJUEGOS", "FAMI_TIENEHORNOMICROOGAS", "FAMI_TIENEINTERNET",
    "FAMI_TIENELAVADORA", "FAMI_TIENEMOTOCICLETA", "FAMI_TIENESERVICIOTV",
    "ESTU_HORASSEMANATRABAJA", "ESTU_PAGOMATRICULABECA", "ESTU_PAGOMATRICULACREDITO",
    "ESTU_PAGOMATRICULAPADRES", "ESTU_PAGOMATRICULAPROPIO",
]

work = df[[target] + numeric_features + categorical_features].copy()

work[numeric_features[0]] = work[numeric_features[0]].fillna(work[numeric_features[0]].median())
for c in categorical_features:
    work[c] = work[c].fillna(work[c].mode().iloc[0])

X = pd.get_dummies(work[numeric_features + categorical_features], columns=categorical_features)
y = work[target]

kf = KFold(n_splits=5, shuffle=True, random_state=0)

fold_rows = []
importance_by_fold = []

print("=== Random Forest SIN institucion (300 arboles, max_depth=8, min_samples_leaf=20) ===")
print(f"K-Fold: n_splits=5, shuffle=True, random_state=0\n")

for fold_idx, (train_idx, val_idx) in enumerate(kf.split(X), start=1):
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

    rf = RandomForestRegressor(
        n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1
    )
    rf.fit(X_train, y_train)
    pred = rf.predict(X_val)

    r2 = r2_score(y_val, pred)
    mae = mean_absolute_error(y_val, pred)
    rmse = root_mean_squared_error(y_val, pred)

    print(f"Fold {fold_idx}: R2={r2:.4f}  MAE={mae:.2f}  RMSE={rmse:.2f}")

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

metrics_df.to_csv("docs/etapa_5_sin_institucion_cv/metrics_cv.csv", index=False)
print("\nMetricas por fold guardadas en docs/etapa_5_sin_institucion_cv/metrics_cv.csv")

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

top20.to_csv("docs/etapa_5_sin_institucion_cv/feature_importance_cv.csv", index_label="feature")
print("\nImportancias guardadas en docs/etapa_5_sin_institucion_cv/feature_importance_cv.csv")

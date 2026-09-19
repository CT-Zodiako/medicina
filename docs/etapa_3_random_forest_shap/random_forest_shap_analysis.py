import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

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

work = df[[target] + numeric_features + categorical_features].copy()

work[numeric_features[0]] = work[numeric_features[0]].fillna(work[numeric_features[0]].median())
for c in categorical_features:
    work[c] = work[c].fillna(work[c].mode().iloc[0])

X = pd.get_dummies(work[numeric_features + categorical_features], columns=categorical_features)
y = work[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

rf = RandomForestRegressor(
    n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1
)
rf.fit(X_train, y_train)
pred = rf.predict(X_test)

print("=== Random Forest (300 arboles, max_depth=8, min_samples_leaf=20) ===")
print(f"R2:   {r2_score(y_test, pred):.4f}")
print(f"MAE:  {mean_absolute_error(y_test, pred):.2f}")
print(f"RMSE: {root_mean_squared_error(y_test, pred):.2f}")

importances = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False)
importances = importances[importances > 0].head(20)
print("\n=== Top 20 feature importance (Random Forest, Gini/varianza) ===")
print(importances.to_string())
importances.to_csv("docs/random_forest_shap/rf_feature_importance.csv", header=["importance"])

# SHAP: explica el modelo ya entrenado. Se usa una muestra del test para que el calculo sea rapido.
sample = X_test.sample(n=min(2000, len(X_test)), random_state=0)
explainer = shap.TreeExplainer(rf)
shap_values = explainer(sample)

mean_abs_shap = pd.Series(
    abs(shap_values.values).mean(axis=0), index=X.columns
).sort_values(ascending=False)
mean_abs_shap = mean_abs_shap[mean_abs_shap > 0].head(20)
print("\n=== Top 20 variables por SHAP (impacto promedio absoluto en puntos de PUNT_GLOBAL) ===")
print(mean_abs_shap.to_string())
mean_abs_shap.to_csv("docs/random_forest_shap/shap_ranking.csv", header=["mean_abs_shap"])

plt.figure(figsize=(14, 8))
shap.summary_plot(shap_values, sample, show=False, max_display=15)
plt.subplots_adjust(left=0.45)
plt.savefig("docs/random_forest_shap/shap_summary_plot.png", dpi=150, bbox_inches="tight")
print("\nGrafico SHAP guardado en docs/random_forest_shap/shap_summary_plot.png")

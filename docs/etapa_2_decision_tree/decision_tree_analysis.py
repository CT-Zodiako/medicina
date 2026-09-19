import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, export_text
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

# One-hot: un arbol de decision no soporta categorias nativas, y ordinal encoding
# introduciria un orden arbitrario que el arbol cortaria sin sentido real.
X = pd.get_dummies(work[numeric_features + categorical_features], columns=categorical_features)
y = work[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Arbol profundo: mide el techo de desempeno, referencia para comparar contra el podado
deep_tree = DecisionTreeRegressor(random_state=0)
deep_tree.fit(X_train, y_train)
deep_pred = deep_tree.predict(X_test)

# Arbol podado (max_depth=4): interpretable, evita memorizar por institucion/estudiante
tree = DecisionTreeRegressor(max_depth=4, min_samples_leaf=50, random_state=0)
tree.fit(X_train, y_train)
pred = tree.predict(X_test)

print("=== Arbol profundo (sin podar, referencia de techo) ===")
print(f"R2:   {r2_score(y_test, deep_pred):.4f}")
print(f"MAE:  {mean_absolute_error(y_test, deep_pred):.2f}")
print(f"RMSE: {root_mean_squared_error(y_test, deep_pred):.2f}")
print(f"Profundidad real: {deep_tree.get_depth()}, hojas: {deep_tree.get_n_leaves()}")

print("\n=== Arbol podado (max_depth=4, min_samples_leaf=50) ===")
print(f"R2:   {r2_score(y_test, pred):.4f}")
print(f"MAE:  {mean_absolute_error(y_test, pred):.2f}")
print(f"RMSE: {root_mean_squared_error(y_test, pred):.2f}")

importances = pd.Series(tree.feature_importances_, index=X.columns).sort_values(ascending=False)
importances = importances[importances > 0]
print("\n=== Feature importance (arbol podado) ===")
print(importances.to_string())
importances.to_csv("docs/etapa_2_decision_tree/feature_importance.csv", header=["importance"])

with open("docs/etapa_2_decision_tree/tree_rules.txt", "w") as f:
    f.write(export_text(tree, feature_names=list(X.columns), max_depth=4))

print("\nReglas del arbol guardadas en docs/etapa_2_decision_tree/tree_rules.txt")

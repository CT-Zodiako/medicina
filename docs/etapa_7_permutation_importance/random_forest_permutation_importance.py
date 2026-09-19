"""
Etapa 7 - Permutation importance agrupada vs. MDI/Gini clasica del Random Forest
(GroupKFold k=5 por INST_NOMBRE_INSTITUCION), para detectar el sesgo conocido
de MDI hacia variables categoricas de alta cardinalidad.

Hipotesis: la importancia MDI/Gini de scikit-learn tiende a sobreestimar
variables categoricas con muchas categorias (aqui, INST_NOMBRE_INSTITUCION
se expande a 55+ columnas dummy vía one-hot encoding), porque el algoritmo de
construccion de arboles tiene mas oportunidades de encontrar un split que
reduzca impureza en una variable con muchos niveles, aunque ese split no
generalice bien fuera de muestra. Permutation importance (caida de R^2 en
validacion held-out al romper aleatoriamente una variable) no depende de la
estructura interna del arbol y por lo tanto es mas robusta a ese sesgo.

Replica EXACTAMENTE el pipeline de datos y el esquema de validacion de
docs/etapa_6_groupkfold_institucion/random_forest_groupkfold_institucion.py:
mismo dataset, mismo feature set (numeric_features + categorical_features,
CON institucion), mismo pd.get_dummies, mismo GroupKFold(n_splits=5) agrupado
por INST_NOMBRE_INSTITUCION, y mismos hiperparametros del RandomForestRegressor
(n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1).

Para cada uno de los 5 folds:
  1. Se entrena un RF igual al de etapa_6 en el conjunto de entrenamiento.
  2. Se calcula la importancia MDI de scikit-learn (rf.feature_importances_,
     por columna dummy) y se agrega por variable ORIGINAL sumando las columnas
     one-hot que pertenecen a esa variable (agrupador = prefijo "col_" armado
     a partir de la lista categorical_features; NO se usa un split() ingenuo
     por "_" porque varios valores de categoria tambien contienen guiones
     bajos, ej. "FAMI_TIENECOMPUTADOR" no debe confundirse con un valor de
     categoria que empiece distinto).
  3. Se calcula permutation importance agrupada por variable ORIGINAL: para
     cada variable categorica se genera una permutacion aleatoria de filas del
     fold de validacion y se aplica esa MISMA permutacion a TODAS las columnas
     dummy de esa variable a la vez (preserva la estructura one-hot valida —
     cada fila permutada sigue teniendo exactamente un 1 entre sus dummies —
     y rompe la asociacion conjunta de la variable original con el target y
     con el resto de las variables). Para numericas se permuta la columna
     individual (patron estandar). Se mide la caida de R^2 (R^2 base del fold
     menos R^2 con la variable permutada), con n_repeats=5 por variable y
     fold.

Criterio de agregacion final (documentado explicitamente, ver mas abajo):
  - MDI: un solo valor agregado por variable y por fold (la suma de sus
    columnas dummy en ese fold). Se agregan mean/std de esos 5 valores
    (uno por fold) por variable.
  - Permutation importance: NO se colapsa primero a un promedio por fold.
    Se conservan los 5 (repeats) x 5 (folds) = 25 valores crudos de caida de
    R^2 por variable, y se calcula mean/std directamente sobre esos 25
    valores. Esto se ajusta literalmente a la consigna de agregar "across
    folds x repeats": la variabilidad reportada combina tanto la variabilidad
    entre folds (distintas instituciones held-out) como la variabilidad del
    muestreo aleatorio de la permutacion dentro de cada fold, en vez de
    esconder la segunda al promediarla primero por fold.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score

df = pd.read_excel("ESTU_MEDICINA_3_MODULOS.xlsx")

df["EDAD"] = (
    pd.Timestamp("2024-01-01") - pd.to_datetime(df["ESTU_FECHANACIMIENTO"])
).dt.days // 365

target = "PUNT_GLOBAL"
group_col = "INST_NOMBRE_INSTITUCION"

numeric_features = ["ESTU_INSE_INDIVIDUAL", "EDAD"]

# Mismas categoricas que etapa_6 (== etapa_3), CON institucion:
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

# --- Mapeo columna dummy -> variable ORIGINAL --------------------------------
# Se usa el prefijo "col_" (col = nombre EXACTO de la variable categorica
# original) para asignar cada columna dummy a su variable de origen, en vez de
# un split() ingenuo por "_" (varias variables y valores de categoria tienen
# guiones bajos internos). Cuando una columna podria calzar con mas de un
# prefijo (no ocurre en este feature set, pero se blinda por robustez), se usa
# el prefijo mas largo (mas especifico).
cat_features_by_len = sorted(categorical_features, key=len, reverse=True)


def resolve_original_variable(column_name: str) -> str:
    if column_name in numeric_features:
        return column_name
    for cat in cat_features_by_len:
        if column_name.startswith(f"{cat}_"):
            return cat
    raise ValueError(f"No se pudo mapear la columna dummy '{column_name}' a ninguna variable original")


dummy_to_original = {col: resolve_original_variable(col) for col in X.columns}

# Columnas dummy agrupadas por variable original (para permutation importance
# agrupada y para sumar MDI por variable original).
original_variables = numeric_features + categorical_features
columns_by_variable = {
    var: [col for col in X.columns if dummy_to_original[col] == var]
    for var in original_variables
}

gkf = GroupKFold(n_splits=5)

N_REPEATS = 5
RF_PARAMS = dict(n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1)

mdi_rows = []  # una fila por (fold, variable)
perm_rows = []  # una fila por (fold, repeat, variable)

print("=== Etapa 7: MDI vs permutation importance agrupada (GroupKFold k=5, groups=INST_NOMBRE_INSTITUCION) ===\n")

for fold_idx, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=groups), start=1):
    X_train = X.iloc[train_idx]
    y_train = y.iloc[train_idx]
    # Reset a indice posicional limpio: se necesita indexar por POSICION para
    # aplicar las permutaciones fila a fila dentro del fold de validacion.
    X_val = X.iloc[val_idx].reset_index(drop=True)
    y_val = y.iloc[val_idx].reset_index(drop=True)

    train_insts = set(groups.iloc[train_idx])
    val_insts = set(groups.iloc[val_idx])
    overlap = train_insts & val_insts
    assert not overlap, f"Fold {fold_idx}: instituciones solapadas entre train y val: {overlap}"

    rf = RandomForestRegressor(**RF_PARAMS)
    rf.fit(X_train, y_train)

    base_pred = rf.predict(X_val)
    base_r2 = r2_score(y_val, base_pred)

    print(f"Fold {fold_idx}: instituciones_val={len(val_insts)}  n_val={len(val_idx)}  R2_base={base_r2:.4f}")

    # --- MDI agregado por variable original ---------------------------------
    mdi_per_dummy = pd.Series(rf.feature_importances_, index=X.columns)
    for var in original_variables:
        mdi_agg = mdi_per_dummy[columns_by_variable[var]].sum()
        mdi_rows.append({"fold": fold_idx, "variable": var, "mdi_importance": mdi_agg})

    # --- Permutation importance agrupada por variable original --------------
    rng = np.random.default_rng(1000 + fold_idx)
    n_val = len(X_val)
    for var in original_variables:
        cols = columns_by_variable[var]
        for repeat in range(N_REPEATS):
            perm = rng.permutation(n_val)
            X_val_perm = X_val.copy()
            # Se permutan TODAS las columnas dummy de la variable A LA VEZ con
            # la MISMA permutacion de filas: cada fila conserva su patron
            # one-hot valido (un solo 1 entre las dummies de esa variable),
            # pero se rompe la asociacion de esa variable con el target y con
            # el resto de las variables. Para numericas, cols tiene un solo
            # elemento y el efecto es el patron estandar de permutation
            # importance.
            X_val_perm.loc[:, cols] = X_val.loc[:, cols].to_numpy()[perm, :]
            perm_pred = rf.predict(X_val_perm)
            perm_r2 = r2_score(y_val, perm_pred)
            drop = base_r2 - perm_r2
            perm_rows.append({"fold": fold_idx, "repeat": repeat, "variable": var, "r2_drop": drop})

mdi_df = pd.DataFrame(mdi_rows)
perm_df = pd.DataFrame(perm_rows)

# --- Agregacion final ---------------------------------------------------------
# MDI: mean/std de los 5 valores por fold (uno por variable y fold).
mdi_summary = mdi_df.groupby("variable")["mdi_importance"].agg(
    mdi_importance_mean="mean", mdi_importance_std="std"
)

# Permutation importance: mean/std directamente sobre los 25 valores crudos
# (5 folds x 5 repeats) por variable -- ver criterio de agregacion documentado
# en el docstring del modulo.
perm_summary = perm_df.groupby("variable")["r2_drop"].agg(
    permutation_importance_mean="mean", permutation_importance_std="std"
)

summary = mdi_summary.join(perm_summary, how="outer").reset_index()

summary["mdi_rank"] = summary["mdi_importance_mean"].rank(ascending=False, method="min").astype(int)
summary["permutation_rank"] = summary["permutation_importance_mean"].rank(ascending=False, method="min").astype(int)

summary = summary.sort_values("permutation_importance_mean", ascending=False).reset_index(drop=True)

output_cols = [
    "variable", "mdi_importance_mean", "mdi_importance_std",
    "permutation_importance_mean", "permutation_importance_std",
    "mdi_rank", "permutation_rank",
]
summary = summary[output_cols]

out_path = "docs/etapa_7_permutation_importance/permutation_vs_mdi_importance.csv"
summary.to_csv(out_path, index=False)
print(f"\nTabla comparativa guardada en {out_path}\n")

# --- Resumen por consola -------------------------------------------------------
print("=== Tabla completa (ordenada por permutation_importance_mean descendente) ===")
with pd.option_context("display.max_rows", None, "display.width", 160):
    print(
        summary.to_string(
            index=False,
            formatters={
                "mdi_importance_mean": "{:.4f}".format,
                "mdi_importance_std": "{:.4f}".format,
                "permutation_importance_mean": "{:.4f}".format,
                "permutation_importance_std": "{:.4f}".format,
            },
        )
    )

summary_by_var = summary.set_index("variable")

institution_vars = [v for v in ["INST_NOMBRE_INSTITUCION", "INST_CARACTER_ACADEMICO", "INST_ORIGEN"] if v in summary_by_var.index]
low_cardinality_watch = [v for v in ["EDAD", "ESTU_INSE_INDIVIDUAL", "ESTU_GENERO"] if v in summary_by_var.index]

print("\n=== Variables de institucion: MDI vs permutation ===")
for var in institution_vars:
    row = summary_by_var.loc[var]
    delta = int(row["mdi_rank"]) - int(row["permutation_rank"])
    direction = "SUBE" if delta > 0 else ("BAJA" if delta < 0 else "SIN CAMBIO")
    print(
        f"{var:30s} mdi_rank={int(row['mdi_rank']):>2d}  permutation_rank={int(row['permutation_rank']):>2d}  "
        f"({direction} {abs(delta)} puesto(s) al pasar de MDI a permutacion)  "
        f"mdi_mean={row['mdi_importance_mean']:.4f}  permutation_mean={row['permutation_importance_mean']:.4f}"
    )

print("\n=== Variables de baja cardinalidad de interes: MDI vs permutation ===")
for var in low_cardinality_watch:
    row = summary_by_var.loc[var]
    delta = int(row["mdi_rank"]) - int(row["permutation_rank"])
    direction = "SUBE" if delta > 0 else ("BAJA" if delta < 0 else "SIN CAMBIO")
    print(
        f"{var:30s} mdi_rank={int(row['mdi_rank']):>2d}  permutation_rank={int(row['permutation_rank']):>2d}  "
        f"({direction} {abs(delta)} puesto(s) al pasar de MDI a permutacion)  "
        f"mdi_mean={row['mdi_importance_mean']:.4f}  permutation_mean={row['permutation_importance_mean']:.4f}"
    )

print("\n=== Todas las variables que cambian de ranking (MDI -> permutation) ===")
changed = summary.copy()
changed["rank_delta"] = changed["mdi_rank"] - changed["permutation_rank"]
changed = changed[changed["rank_delta"] != 0].sort_values("rank_delta", ascending=False)
for _, row in changed.iterrows():
    direction = "SUBE" if row["rank_delta"] > 0 else "BAJA"
    print(
        f"{row['variable']:30s} mdi_rank={int(row['mdi_rank']):>2d} -> permutation_rank={int(row['permutation_rank']):>2d}  "
        f"({direction} {abs(int(row['rank_delta']))} puesto(s))"
    )

print("\nListo. Ver docs/etapa_7_permutation_importance/permutation_vs_mdi_importance.csv para la tabla completa.")

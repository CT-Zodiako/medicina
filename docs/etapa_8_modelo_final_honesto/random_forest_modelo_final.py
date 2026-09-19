"""
Etapa 8 - Modelo final honesto: combina la senal institucional que SI es real
con una validacion que mide generalizacion genuina a instituciones nuevas.

Motivacion (sintesis de etapa_5, etapa_6 y etapa_7):
- Etapa_5 (docs/etapa_5_sin_institucion_cv) elimino las 5 variables
  institucionales/de ubicacion institucional y valido con KFold aleatorio
  k=5: R2=0.186 +/- 0.011. Conservador, pero descarta senal institucional
  real junto con la memorizacion.
- Etapa_6 (docs/etapa_6_groupkfold_institucion) mantuvo las 5 variables
  institucionales pero valido con GroupKFold k=5 agrupando por
  INST_NOMBRE_INSTITUCION (instituciones nunca vistas en validacion):
  R2=0.120 +/- 0.146. La caida y la altisima varianza entre folds confirman
  que buena parte de la senal "institucional" de etapa_3 (R2=0.374, split
  unico) era memorizacion de instituciones especificas, no aprendizaje
  transferible.
- Etapa_7 (docs/etapa_7_permutation_importance) descompuso las 5 variables
  institucionales con permutation importance vs MDI: SOLO INST_ORIGEN e
  INST_CARACTER_ACADEMICO suben de ranking (senal real y transferible);
  INST_NOMBRE_INSTITUCION, ESTU_INST_DEPARTAMENTO y ESTU_INST_MUNICIPIO caen
  a los ultimos puestos con importancia por permutacion ~0 o negativa
  (memorizacion/sobreajuste puro).

Este script:
- Usa el feature set de etapa_5 (SIN institucion) MAS INST_ORIGEN e
  INST_CARACTER_ACADEMICO (las dos variables institucionales confirmadas
  como senal real por etapa_7).
- Excluye explicitamente INST_NOMBRE_INSTITUCION, ESTU_INST_DEPARTAMENTO y
  ESTU_INST_MUNICIPIO (memorizacion, confirmado por etapa_6 y etapa_7).
- Valida con GroupKFold(n_splits=5) agrupando por INST_NOMBRE_INSTITUCION
  (igual que etapa_6), aunque esa columna NO se usa como feature del modelo:
  solo define los folds, para seguir midiendo generalizacion a instituciones
  nunca vistas en entrenamiento.

Mismos hiperparametros del Random Forest que los scripts de referencia:
n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1.

Comparacion esperada en consola contra:
  - etapa_3: R2=0.374 (split unico 80/20, CON toda institucion incl. memorizacion)
  - etapa_5: R2=0.186 +/- 0.011 (KFold aleatorio k=5, SIN ninguna institucional)
  - etapa_6: R2=0.120 +/- 0.146 (GroupKFold k=5, CON toda institucion)
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

# Categoricas de etapa_5 (SIN institucion/ubicacion institucional) MAS las dos
# variables institucionales confirmadas como senal real por etapa_7:
# INST_ORIGEN e INST_CARACTER_ACADEMICO.
# EXCLUIDAS a proposito (memorizacion, confirmado por etapa_6/etapa_7):
#   INST_NOMBRE_INSTITUCION, ESTU_INST_DEPARTAMENTO, ESTU_INST_MUNICIPIO
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

# group_col (INST_NOMBRE_INSTITUCION) se incluye solo para definir los folds
# de GroupKFold; NUNCA entra en X (no es feature del modelo).
work = df[[target, group_col] + numeric_features + categorical_features].copy()

# El vector de grupos se captura ANTES de imputar/filtrar filas, igual que en
# etapa_6, para que quede alineado indice a indice tras cualquier dropna/fillna
# posterior. No se imputa la institucion (es la variable de agrupacion, no una
# feature): las filas sin institucion se descartan en vez de asignarles una
# institucion inventada.
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

print("=== Modelo final honesto: SIN memorizacion institucional, CON senal institucional real ===")
print("Features: set de etapa_5 (sin institucion) + INST_ORIGEN + INST_CARACTER_ACADEMICO")
print("Validacion: GroupKFold n_splits=5, groups=INST_NOMBRE_INSTITUCION (instituciones de validacion no vistas en entrenamiento)")
print("RandomForest: n_estimators=300, max_depth=8, min_samples_leaf=20, random_state=0, n_jobs=-1\n")

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
print("Etapa 3 (split unico 80/20, CON toda institucion incl. memorizacion):        R2=0.374")
print("Etapa 5 (KFold aleatorio k=5, SIN ninguna variable institucional):            R2=0.186 +/- 0.011")
print("Etapa 6 (GroupKFold k=5, CON toda institucion incl. memorizacion):            R2=0.120 +/- 0.146")
print(f"Etapa 8 (GroupKFold k=5, CON solo senal institucional real [ORIGEN+CARACTER]): R2={mean_row['r2']:.4f} +/- {std_row['r2']:.4f}")

diff_etapa5 = mean_row["r2"] - 0.186
diff_etapa6 = mean_row["r2"] - 0.120
print(f"\nDiferencia Etapa 8 vs Etapa 5 (aporte de INST_ORIGEN + INST_CARACTER_ACADEMICO): {diff_etapa5:+.4f}")
print(f"Diferencia Etapa 8 vs Etapa 6 (costo de descartar la memorizacion institucional): {diff_etapa6:+.4f}")
if mean_row["r2"] > 0.186 and mean_row["r2"] > 0.120:
    print("Interpretacion: el modelo final honesto supera tanto a etapa_5 como a etapa_6 en su propia")
    print("validacion honesta -> la senal institucional real (tipo/origen de institucion) aporta poder")
    print("predictivo transferible, sin depender de memorizar instituciones especificas.")
elif mean_row["r2"] > 0.186:
    print("Interpretacion: el modelo final honesto supera a etapa_5 pero no a etapa_6 -> la senal")
    print("institucional real aporta algo sobre no usar institucion, aunque etapa_6 (con memorizacion)")
    print("todavia reporta un R2 mayor pese a su alta varianza entre folds.")
else:
    print("Interpretacion: el modelo final honesto no logra superar a etapa_5 en esta validacion ->")
    print("la senal de INST_ORIGEN/INST_CARACTER_ACADEMICO, aislada de la memorizacion, aporta poco")
    print("poder predictivo transferible adicional. Se reporta el numero real, sin forzarlo.")

metrics_df.to_csv("docs/etapa_8_modelo_final_honesto/metrics_final.csv", index=False)
print("\nMetricas por fold guardadas en docs/etapa_8_modelo_final_honesto/metrics_final.csv")

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

top20.to_csv("docs/etapa_8_modelo_final_honesto/feature_importance_final.csv", index_label="feature")
print("\nImportancias guardadas en docs/etapa_8_modelo_final_honesto/feature_importance_final.csv")

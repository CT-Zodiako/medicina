import pandas as pd
from sklearn.feature_selection import mutual_info_regression
from sklearn.preprocessing import OrdinalEncoder

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

encoder = OrdinalEncoder()
work[categorical_features] = encoder.fit_transform(work[categorical_features].astype(str))

X = work[numeric_features + categorical_features]
y = work[target]

discrete_mask = [c in categorical_features for c in X.columns]

mi = mutual_info_regression(X, y, discrete_features=discrete_mask, random_state=0)

result = pd.Series(mi, index=X.columns).sort_values(ascending=False)
print(result.to_string())
result.to_csv("docs/etapa_1_mutual_information/mutual_info_ranking_24.csv", header=["mutual_info"])

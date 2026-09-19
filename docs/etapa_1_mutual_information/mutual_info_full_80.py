import pandas as pd
from sklearn.feature_selection import mutual_info_regression
from sklearn.preprocessing import OrdinalEncoder

df = pd.read_excel("ESTU_MEDICINA_3_MODULOS.xlsx")

target = "PUNT_GLOBAL"
excluded_as_id = ["ESTU_CONSECUTIVO"]  # ID unico por fila, no es una feature valida para MI
feature_cols = [c for c in df.columns if c != target and c not in excluded_as_id]

work = df[feature_cols].copy()

date_cols = ["ESTU_FECHANACIMIENTO"]
for c in date_cols:
    work[c] = pd.to_datetime(work[c]).astype("int64") // 10**9  # epoch seconds, numerico continuo

numeric_cols = work.select_dtypes(include="number").columns.tolist()
categorical_cols = [c for c in feature_cols if c not in numeric_cols]

for c in numeric_cols:
    work[c] = work[c].fillna(work[c].median())
for c in categorical_cols:
    mode = work[c].mode()
    work[c] = work[c].fillna(mode.iloc[0] if not mode.empty else "SIN_DATO")

encoder = OrdinalEncoder()
work[categorical_cols] = encoder.fit_transform(work[categorical_cols].astype(str))

X = work[feature_cols]
y = df[target]

discrete_mask = [c in categorical_cols for c in X.columns]

mi = mutual_info_regression(X, y, discrete_features=discrete_mask, random_state=0)

result = pd.Series(mi, index=X.columns).sort_values(ascending=False)
print(result.to_string())
result.to_csv("docs/etapa_1_mutual_information/mutual_info_ranking_78.csv", header=["mutual_info"])

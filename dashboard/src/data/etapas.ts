// Datos numéricos exactos de las 9 etapas del análisis Saber Pro Medicina.
// Fuente de verdad: docs/etapa_1_* … docs/etapa_9_*, portados desde el
// dashboard de referencia (dashboard.html). No leer ni escribir docs/ en
// runtime — todo vive hardcodeado aquí.

/** Token semántico de color: se traduce a `var(--<token>)` en los charts. */
export type ColorToken = "accent" | "flag" | "real" | "good" | "critical" | "muted";

export interface HBarDatum {
  label: string;
  value: number;
  color?: ColorToken;
}

export interface GroupedBarDatum {
  label: string;
  a: number;
  b: number;
}

export interface SlopeRow {
  name: string;
  mdi: number;
  perm: number;
  flag: "name" | "type" | "demo";
}

export interface E7FullRow {
  name: string;
  mdi: number;
  perm: number;
  rankMdi: number;
  rankPerm: number;
}

// ---------------------------------------------------------------------------
// Etapa 01 — Mutual Information
// ---------------------------------------------------------------------------
export const e1Data: HBarDatum[] = [
  { label: "Nombre institución", value: 0.2549, color: "flag" },
  { label: "Origen institucional", value: 0.0594, color: "flag" },
  { label: "Municipio institución", value: 0.0581, color: "flag" },
  { label: "Departamento institución", value: 0.0516, color: "flag" },
  { label: "Estrato vivienda", value: 0.0392, color: "accent" },
  { label: "Carácter académico", value: 0.0300, color: "accent" },
  { label: "Edad", value: 0.0246, color: "accent" },
  { label: "Educación padre", value: 0.0239, color: "accent" },
  { label: "Educación madre", value: 0.0230, color: "accent" },
  { label: "Pago matrícula crédito", value: 0.0226, color: "accent" },
  { label: "INSE individual", value: 0.0225, color: "accent" },
  { label: "Horas trabajo/semana", value: 0.0210, color: "accent" },
];

// ---------------------------------------------------------------------------
// Etapa 02 — Árbol de decisión (podado, profundidad 4)
// ---------------------------------------------------------------------------
export const e2Data: HBarDatum[] = [
  { label: "Origen institucional", value: 0.3223, color: "flag" },
  { label: "Carácter académico", value: 0.2409, color: "flag" },
  { label: "Nombre (Uniandes)", value: 0.1685, color: "flag" },
  { label: "Edad", value: 0.0918, color: "accent" },
  { label: "Nombre (Icesi)", value: 0.0836, color: "flag" },
  { label: "Nombre (Uniboyacá)", value: 0.0366, color: "flag" },
  { label: "Nombre (FUCS)", value: 0.0261, color: "flag" },
  { label: "INSE individual", value: 0.0131, color: "accent" },
];

export const e2Stats = { r2: 0.288, mae: 15.84, rmse: 20.86 };

// ---------------------------------------------------------------------------
// Etapa 03 — Random Forest de referencia + SHAP
// ---------------------------------------------------------------------------
export const e3Stats = { r2: 0.374, mae: 14.77, rmse: 19.56 };

export const e3Data: GroupedBarDatum[] = [
  { label: "Origen institucional", a: 0.2489, b: 8.35 / 25 },
  { label: "Edad", a: 0.096, b: 2.76 / 25 },
  { label: "Carácter (inst. univ.)", a: 0.0963, b: 2.32 / 25 },
  { label: "Carácter (universidad)", a: 0.0912, b: 2.19 / 25 },
  { label: "Nombre (Uniandes)", a: 0.131, b: 1.27 / 25 },
  { label: "INSE individual", a: 0.0511, b: 1.22 / 25 },
  { label: "Nombre (Icesi)", a: 0.0647, b: 0.8 / 25 },
];

// ---------------------------------------------------------------------------
// Etapa 04 / 09 — Varianza explicada PCA (con y sin institución)
// ---------------------------------------------------------------------------
export const varianzaEtapa4: number[] = [4.3, 2.48, 2.36, 2.17, 1.94, 1.92, 1.83, 1.77, 1.72, 1.71];
export const varianzaEtapa9: number[] = [8.03, 3.27, 3.0, 2.75, 2.68, 2.53, 2.25, 2.13, 2.09, 1.98];

export const e4Stats = { islas: "~55–60", varianzaAcumulada: "22.2%" };

// ---------------------------------------------------------------------------
// Etapa 05 — Sin institución + KFold aleatorio
// ---------------------------------------------------------------------------
export const e5Folds = { values: [0.1868, 0.1851, 0.1978, 0.192, 0.1693], mean: 0.1862, std: 0.0107 };

export const e5bData: HBarDatum[] = [
  { label: "Edad", value: 0.1497 },
  { label: "No trabaja h/sem", value: 0.1027 },
  { label: "INSE individual", value: 0.1007 },
  { label: "Crédito matrícula: no", value: 0.0775 },
  { label: "Crédito matrícula: sí", value: 0.0734 },
  { label: "Beca matrícula: sí", value: 0.0441 },
  { label: "Estrato 6", value: 0.0397 },
];

// ---------------------------------------------------------------------------
// Etapa 06 — GroupKFold institucional
// ---------------------------------------------------------------------------
export const e6Folds = { values: [0.1592, 0.0125, 0.2497, 0.2523, -0.0741], mean: 0.1199, std: 0.1459 };

export const e6bData: HBarDatum[] = [
  { label: "Origen institucional", value: 0.2427, color: "flag" },
  { label: "Nombre (Uniandes)", value: 0.1029, color: "flag" },
  { label: "Carácter (inst. univ.)", value: 0.0923, color: "flag" },
  { label: "Carácter (universidad)", value: 0.0895, color: "flag" },
  { label: "Edad", value: 0.0882, color: "accent" },
  { label: "Nombre (Icesi)", value: 0.064, color: "flag" },
  { label: "INSE individual", value: 0.0435, color: "accent" },
];

// ---------------------------------------------------------------------------
// Etapa 07 — Permutation importance vs. MDI
// ---------------------------------------------------------------------------
export const e7SlopeRows: SlopeRow[] = [
  { name: "INST_ORIGEN", mdi: 2, perm: 1, flag: "type" },
  { name: "INST_CARACTER_ACADEMICO", mdi: 3, perm: 2, flag: "type" },
  { name: "EDAD", mdi: 4, perm: 3, flag: "demo" },
  { name: "ESTU_INSE_INDIVIDUAL", mdi: 5, perm: 4, flag: "demo" },
  { name: "ESTU_HORASSEMANATRABAJA", mdi: 9, perm: 5, flag: "demo" },
  { name: "FAMI_TIENEHORNOMICROOGAS", mdi: 8, perm: 6, flag: "demo" },
  { name: "ESTU_GENERO", mdi: 16, perm: 10, flag: "demo" },
  { name: "ESTU_INST_MUNICIPIO", mdi: 6, perm: 27, flag: "name" },
  { name: "ESTU_INST_DEPARTAMENTO", mdi: 7, perm: 26, flag: "name" },
  { name: "INST_NOMBRE_INSTITUCION", mdi: 1, perm: 24, flag: "name" },
];

export const e7FullTable: E7FullRow[] = [
  { name: "INST_ORIGEN", mdi: 0.2544, perm: 0.2634, rankMdi: 2, rankPerm: 1 },
  { name: "INST_CARACTER_ACADEMICO", mdi: 0.1818, perm: 0.1344, rankMdi: 3, rankPerm: 2 },
  { name: "EDAD", mdi: 0.0882, perm: 0.0616, rankMdi: 4, rankPerm: 3 },
  { name: "ESTU_INSE_INDIVIDUAL", mdi: 0.0435, perm: 0.0138, rankMdi: 5, rankPerm: 4 },
  { name: "ESTU_HORASSEMANATRABAJA", mdi: 0.0095, perm: 0.0048, rankMdi: 9, rankPerm: 5 },
  { name: "FAMI_TIENEHORNOMICROOGAS", mdi: 0.0156, perm: 0.0041, rankMdi: 8, rankPerm: 6 },
  { name: "FAMI_TIENECONSOLAVIDEOJUEGOS", mdi: 0.0057, perm: 0.0024, rankMdi: 13, rankPerm: 7 },
  { name: "PERIODO", mdi: 0.0085, perm: 0.002, rankMdi: 10, rankPerm: 8 },
  { name: "ESTU_PAGOMATRICULABECA", mdi: 0.0034, perm: 0.0014, rankMdi: 17, rankPerm: 9 },
  { name: "ESTU_GENERO", mdi: 0.0036, perm: 0.0009, rankMdi: 16, rankPerm: 10 },
  { name: "FAMI_ESTRATOVIVIENDA", mdi: 0.0065, perm: 0.0007, rankMdi: 11, rankPerm: 11 },
  { name: "FAMI_EDUCACIONMADRE", mdi: 0.0037, perm: 0.0007, rankMdi: 15, rankPerm: 12 },
  { name: "FAMI_EDUCACIONPADRE", mdi: 0.0027, perm: 0.0007, rankMdi: 18, rankPerm: 13 },
  { name: "FAMI_CUANTOSCOMPARTEBAÑO", mdi: 0.006, perm: 0.0006, rankMdi: 12, rankPerm: 14 },
  { name: "FAMI_TIENEMOTOCICLETA", mdi: 0.002, perm: 0.0005, rankMdi: 19, rankPerm: 15 },
  { name: "ESTU_PAGOMATRICULACREDITO", mdi: 0.0017, perm: 0.0005, rankMdi: 20, rankPerm: 16 },
  { name: "FAMI_TIENEINTERNET", mdi: 0.0009, perm: 0.0002, rankMdi: 22, rankPerm: 17 },
  { name: "FAMI_TIENECOMPUTADOR", mdi: 0.0006, perm: 0.0002, rankMdi: 25, rankPerm: 18 },
  { name: "ESTU_SEMESTRECURSA", mdi: 0.0051, perm: 0.0002, rankMdi: 14, rankPerm: 19 },
  { name: "FAMI_TIENELAVADORA", mdi: 0.0005, perm: 0.0001, rankMdi: 26, rankPerm: 20 },
  { name: "ESTU_PAGOMATRICULAPADRES", mdi: 0.0014, perm: 0.0001, rankMdi: 21, rankPerm: 21 },
  { name: "ESTU_PAGOMATRICULAPROPIO", mdi: 0.0006, perm: 0.0001, rankMdi: 24, rankPerm: 22 },
  { name: "FAMI_TIENESERVICIOTV", mdi: 0.0004, perm: 0.0, rankMdi: 27, rankPerm: 23 },
  { name: "INST_NOMBRE_INSTITUCION", mdi: 0.2952, perm: 0.0, rankMdi: 1, rankPerm: 24 },
  { name: "FAMI_TIENEAUTOMOVIL", mdi: 0.0008, perm: -0.0, rankMdi: 23, rankPerm: 25 },
  { name: "ESTU_INST_DEPARTAMENTO", mdi: 0.0286, perm: -0.0317, rankMdi: 7, rankPerm: 26 },
  { name: "ESTU_INST_MUNICIPIO", mdi: 0.0292, perm: -0.0323, rankMdi: 6, rankPerm: 27 },
];

// ---------------------------------------------------------------------------
// Etapa 08 — Modelo final honesto
// ---------------------------------------------------------------------------
export const e8Folds = { values: [0.3012, 0.1026, 0.2624, 0.3022, 0.175], mean: 0.2287, std: 0.0874 };

export const e8bData: HBarDatum[] = [
  { label: "Origen institucional", value: 0.2807, color: "real" },
  { label: "Edad", value: 0.119, color: "accent" },
  { label: "Carácter (inst. univ.)", value: 0.1175, color: "real" },
  { label: "Carácter (universidad)", value: 0.111, color: "real" },
  { label: "INSE individual", value: 0.0855, color: "accent" },
  { label: "No trabaja h/sem", value: 0.0277, color: "accent" },
  { label: "Estrato 6", value: 0.0196, color: "accent" },
];

// ---------------------------------------------------------------------------
// Etapa 09 — UMAP sin institución
// ---------------------------------------------------------------------------
export const e9Silhouette = {
  values: [
    0.4229, 0.4646, 0.4134, 0.4059, 0.4441, 0.4432, 0.4552, 0.4371, 0.4425, 0.4505, 0.4646, 0.4745, 0.4721,
    0.4851,
  ],
  startK: 2,
};

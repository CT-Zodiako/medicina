"use client";

import { useEffect, useState } from "react";

type FieldValue = string | number | undefined;
type Answers = Record<string, FieldValue>;

interface PredictionResult {
  predicted_level: number;
  probabilities: Record<string, number>;
  missing_fields: string[];
  low_confidence: boolean;
  validated_performance: { macro_f1: number; balanced_accuracy: number };
}

interface ComparisonResult {
  produccion_sin_institucion: PredictionResult;
  referencia_con_institucion: PredictionResult;
}

interface Institution {
  inst_cod_institucion: number;
  inst_nombre_institucion: string;
}

const SI_NO = ["Si", "No"];

const HORAS_TRABAJO = [
  "0",
  "Menos de 10 horas",
  "Entre 11 y 20 horas",
  "Entre 21 y 30 horas",
  "Más de 30 horas",
];

const CUANTOS_BANO = ["NINGUNA", "1", "2", "3 o 4", "5 o 6", "MAS DE 6"];

const ESTRATO = [
  "Sin Estrato",
  "Estrato 1",
  "Estrato 2",
  "Estrato 3",
  "Estrato 4",
  "Estrato 5",
  "Estrato 6",
];

const EDUCACION = [
  "Ninguno",
  "Primaria incompleta",
  "Primaria completa",
  "Secundaria (Bachillerato) incompleta",
  "Secundaria (Bachillerato) completa",
  "Técnica o tecnológica incompleta",
  "Técnica o tecnológica completa",
  "Educación profesional incompleta",
  "Educación profesional completa",
  "Postgrado",
  "No sabe",
  "No Aplica",
];

const SEMESTRE = [
  "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12 o más",
];

const OCUPACION = [
  "Hogar",
  "Pensionado",
  "Empresario",
  "Pequeño empresario",
  "Empleado con cargo como director o gerente general",
  "Empleado de nivel directivo",
  "Empleado de nivel técnico o profesional",
  "Empleado de nivel auxiliar o administrativo",
  "Empleado obrero u operario",
  "Profesional Independiente",
  "Trabajador por cuenta propia",
  "Otra actividad u ocupación",
];

const TITULO_BACHILLER = [
  "Bachiller académico",
  "Bachiller técnico",
  "Bachiller pedagógico o normalista",
];

const LEVEL_COLOR: Record<number, string> = {
  1: "var(--critical)",
  2: "var(--flag)",
  3: "var(--accent)",
  4: "var(--good)",
};

const LEVEL_LABEL: Record<number, string> = {
  1: "Bajo (0–129 pts)",
  2: "Medio-bajo (130–156 pts)",
  3: "Medio-alto (157–189 pts)",
  4: "Alto (190–300 pts)",
};

function Select({
  label,
  field,
  options,
  value,
  onChange,
}: {
  label: string;
  field: string;
  options: string[];
  value: FieldValue;
  onChange: (field: string, value: string) => void;
}) {
  return (
    <label className="pf-field" htmlFor={field}>
      <span>{label}</span>
      <select id={field} name={field} value={(value as string) ?? ""} onChange={(e) => onChange(field, e.target.value)}>
        <option value="">Sin dato</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function FormSection({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <div className="pf-section">
      <h4>{title}</h4>
      {description && <p className="pf-section-desc">{description}</p>}
      <div className="pf-grid">{children}</div>
    </div>
  );
}

function ResultCard({ title, subtitle, result }: { title: string; subtitle: string; result: PredictionResult }) {
  const ranked = Object.entries(result.probabilities).sort((a, b) => Number(b[1]) - Number(a[1]));
  return (
    <div className="card pf-result-card">
      <div className="pf-result-head">
        <span className="pf-result-title">{title}</span>
        <span className="pf-level-chip" style={{ background: LEVEL_COLOR[result.predicted_level] }}>
          Nivel {result.predicted_level}
        </span>
      </div>
      <p className="pf-level-desc">{LEVEL_LABEL[result.predicted_level]}</p>
      <p className="pf-hint">{subtitle}</p>
      <div className="pf-bars">
        {ranked.map(([level, probability]) => (
          <div className="pf-bar-row" key={level}>
            <span className="pf-bar-label">Nivel {level}</span>
            <div className="pf-bar-track">
              <div
                className="pf-bar-fill"
                style={{ width: `${(probability * 100).toFixed(1)}%`, background: LEVEL_COLOR[Number(level)] }}
              />
            </div>
            <span className="pf-bar-value num">{(probability * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
      {result.low_confidence && (() => {
        const [, topProbability] = ranked[0];
        const [secondLevel, secondProbability] = ranked[1];
        return (
          <div className="finding flag" style={{ marginTop: 16 }}>
            <span className="dot" />
            <p>
              El nivel {result.predicted_level} ganó con {(Number(topProbability) * 100).toFixed(0)}%,
              pero el nivel {secondLevel} quedó muy cerca con{" "}
              {(Number(secondProbability) * 100).toFixed(0)}%. Este estudiante podría estar en
              cualquiera de los dos — no lo tomes como un resultado seguro.
            </p>
          </div>
        );
      })()}
      {result.missing_fields.length > 0 && (
        <details className="pf-details">
          <summary>
            {result.missing_fields.length} campo{result.missing_fields.length === 1 ? "" : "s"} sin
            responder — completados con el valor por defecto del modelo
          </summary>
          <p className="pf-hint">{result.missing_fields.join(", ")}</p>
        </details>
      )}
      <p className="pf-hint">
        Desempeño validado (instituciones nunca vistas): F1 macro{" "}
        {result.validated_performance.macro_f1.toFixed(2)}, balanced accuracy{" "}
        {result.validated_performance.balanced_accuracy.toFixed(2)}.
      </p>
    </div>
  );
}

export default function PrediccionForm() {
  const [answers, setAnswers] = useState<Answers>({});
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [comparison, setComparison] = useState<ComparisonResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("/api/instituciones")
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data)) setInstitutions(data);
      })
      .catch(() => {});
  }, []);

  function set(field: string, value: string) {
    setAnswers((prev) => ({ ...prev, [field]: value === "" ? undefined : value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setComparison(null);
    try {
      const cleaned: Answers = { ...answers };
      if (cleaned.estu_nse_individual) cleaned.estu_nse_individual = Number(cleaned.estu_nse_individual);
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cleaned),
      });
      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? data.error ?? "Error desconocido");
        return;
      }
      setComparison(data);
    } catch {
      setError("No se pudo conectar con la API de predicción.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="cols2">
      <form className="card pf-form" onSubmit={handleSubmit}>
        <div className="pf-sections">
        <FormSection title="1. Datos personales">
          <label className="pf-field" htmlFor="estu_fechanacimiento">
            <span>Fecha de nacimiento</span>
            <input
              id="estu_fechanacimiento"
              name="estu_fechanacimiento"
              type="date"
              onChange={(e) => {
                const [y, m, d] = e.target.value.split("-");
                set("estu_fechanacimiento", e.target.value ? `${d}/${m}/${y}` : "");
              }}
            />
          </label>
          <Select label="Género" field="estu_genero" options={["F", "M"]} value={answers.estu_genero} onChange={set} />
        </FormSection>

        <FormSection title="2. Situación académica">
          <Select label="Semestre que cursa" field="estu_semestrecursa" options={SEMESTRE} value={answers.estu_semestrecursa} onChange={set} />
          <Select label="Título de bachiller" field="estu_tituloobtenidobachiller" options={TITULO_BACHILLER} value={answers.estu_tituloobtenidobachiller} onChange={set} />
          <Select label="Horas de trabajo semanal" field="estu_horassemanatrabaja" options={HORAS_TRABAJO} value={answers.estu_horassemanatrabaja} onChange={set} />
          <Select label="Beca de matrícula" field="estu_pagomatriculabeca" options={SI_NO} value={answers.estu_pagomatriculabeca} onChange={set} />
          <Select label="Crédito de matrícula" field="estu_pagomatriculacredito" options={SI_NO} value={answers.estu_pagomatriculacredito} onChange={set} />
          <Select label="Padres pagan matrícula" field="estu_pagomatriculapadres" options={SI_NO} value={answers.estu_pagomatriculapadres} onChange={set} />
          <Select label="Matrícula con recursos propios" field="estu_pagomatriculapropio" options={SI_NO} value={answers.estu_pagomatriculapropio} onChange={set} />
        </FormSection>

        <FormSection title="3. Contexto familiar y socioeconómico">
          <Select label="Estrato de vivienda" field="fami_estratovivienda" options={ESTRATO} value={answers.fami_estratovivienda} onChange={set} />
          <label className="pf-field" htmlFor="estu_nse_individual">
            <span>Nivel socioeconómico individual (1-4)</span>
            <select
              id="estu_nse_individual"
              name="estu_nse_individual"
              value={(answers.estu_nse_individual as string) ?? ""}
              onChange={(e) => set("estu_nse_individual", e.target.value)}
            >
              <option value="">Sin dato</option>
              {[1, 2, 3, 4].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </label>
          <Select label="Personas que comparten baño" field="fami_cuantoscompartebaño" options={CUANTOS_BANO} value={answers.fami_cuantoscompartebaño} onChange={set} />
          <Select label="Educación de la madre" field="fami_educacionmadre" options={EDUCACION} value={answers.fami_educacionmadre} onChange={set} />
          <Select label="Educación del padre" field="fami_educacionpadre" options={EDUCACION} value={answers.fami_educacionpadre} onChange={set} />
          <Select label="Ocupación de la madre" field="fami_ocupacionmadre" options={OCUPACION} value={answers.fami_ocupacionmadre} onChange={set} />
          <Select label="Ocupación del padre" field="fami_ocupacionpadre" options={OCUPACION} value={answers.fami_ocupacionpadre} onChange={set} />
        </FormSection>

        <FormSection title="4. Bienes del hogar">
          <Select label="Automóvil" field="fami_tieneautomovil" options={SI_NO} value={answers.fami_tieneautomovil} onChange={set} />
          <Select label="Computador" field="fami_tienecomputador" options={SI_NO} value={answers.fami_tienecomputador} onChange={set} />
          <Select label="Consola de videojuegos" field="fami_tieneconsolavideojuegos" options={SI_NO} value={answers.fami_tieneconsolavideojuegos} onChange={set} />
          <Select label="Horno microondas" field="fami_tienehornomicroogas" options={SI_NO} value={answers.fami_tienehornomicroogas} onChange={set} />
          <Select label="Internet" field="fami_tieneinternet" options={SI_NO} value={answers.fami_tieneinternet} onChange={set} />
          <Select label="Lavadora" field="fami_tienelavadora" options={SI_NO} value={answers.fami_tienelavadora} onChange={set} />
          <Select label="Motocicleta" field="fami_tienemotocicleta" options={SI_NO} value={answers.fami_tienemotocicleta} onChange={set} />
          <Select label="Servicio de TV" field="fami_tieneserviciotv" options={SI_NO} value={answers.fami_tieneserviciotv} onChange={set} />
        </FormSection>

        </div>

        <div className="pf-section pf-section-full">
          <h4>5. Institución</h4>
          <p className="pf-section-desc">
            Opcional. Solo la usa el modelo de referencia — el modelo de producción no la
            necesita ni la utiliza.
          </p>
          <label className="pf-field" htmlFor="inst_cod_institucion">
            <span>Institución</span>
            <select
              id="inst_cod_institucion"
              name="inst_cod_institucion"
              value={(answers.inst_cod_institucion as string) ?? ""}
              onChange={(e) => set("inst_cod_institucion", e.target.value)}
            >
              <option value="">Sin dato (usa la institución más común)</option>
              {institutions.map((inst) => (
                <option key={inst.inst_cod_institucion} value={inst.inst_cod_institucion}>
                  {inst.inst_nombre_institucion}
                </option>
              ))}
            </select>
          </label>
        </div>

        <p className="pf-hint">
          Los campos que dejes en &quot;Sin dato&quot; se completan con el valor que el
          modelo aprendió a usar por defecto (moda o mediana), no con un valor inventado
          por este formulario.
        </p>
        <button type="submit" disabled={loading}>
          {loading ? "Prediciendo…" : "Predecir nivel de desempeño"}
        </button>
      </form>

      <div className="pf-result">
        {error && (
          <div className="finding crit">
            <span className="dot" />
            <p>{error}</p>
          </div>
        )}
        {comparison && (
          <>
            <ResultCard
              title="Modelo de producción"
              subtitle="Recomendado. No usa institución — generaliza mejor a instituciones nunca vistas."
              result={comparison.produccion_sin_institucion}
            />
            <ResultCard
              title="Modelo de referencia"
              subtitle="Solo para comparar. Incluye institución, lo que puede reflejar memorización."
              result={comparison.referencia_con_institucion}
            />
            {comparison.produccion_sin_institucion.predicted_level !==
              comparison.referencia_con_institucion.predicted_level && (
              <div className="finding crit" style={{ marginTop: 16 }}>
                <span className="dot" />
                <p>
                  Los dos modelos no coinciden para este estudiante ({comparison.produccion_sin_institucion.predicted_level}{" "}
                  vs. {comparison.referencia_con_institucion.predicted_level}). Tomá como
                  referencia el modelo de producción — el de institución puede estar
                  reflejando memorización, no una diferencia real.
                </p>
              </div>
            )}
          </>
        )}
        {!comparison && !error && (
          <div className="finding">
            <span className="dot" style={{ background: "var(--muted)" }} />
            <p>Completá el formulario y presioná &quot;Predecir&quot; para ver el resultado acá.</p>
          </div>
        )}
      </div>
    </div>
  );
}

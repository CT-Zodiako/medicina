import SlopeChart from "@/components/charts/SlopeChart";
import DataTableE7 from "@/components/DataTableE7";
import Finding from "@/components/Finding";
import Legend from "@/components/Legend";
import Stat, { StatRow } from "@/components/Stat";
import { e7SlopeRows } from "@/data/etapas";

export default function Etapa07() {
  return (
    <section id="e7">
      <div className="kicker">
        <span className="n">Etapa 07</span>El diagnóstico
      </div>
      <h2>Permutation importance: separar memorización de señal real</h2>
      <p className="lede">
        La importancia MDI/Gini de un Random Forest está sesgada hacia variables categóricas de alta
        cardinalidad — y el nombre de institución tiene 55 categorías. Permutation importance agrupada (romper
        la variable en los datos de validación y medir la caída real de R²) no tiene ese sesgo. Esta es la
        comparación completa, variable por variable.
      </p>
      <div className="card">
        <div style={{ height: 400 }}>
          <SlopeChart rows={e7SlopeRows} />
        </div>
        <Legend
          items={[
            { color: "critical", label: "Nombre / geografía institucional (memorización)" },
            { color: "good", label: "Tipo de institución (señal real)" },
            { color: "muted", label: "Demográfico / socioeconómico" },
          ]}
        />
      </div>
      <StatRow>
        <Stat value="#1 → #24" label="Nombre de institución (de 27)" />
        <Stat value="#2 → #1" label="Origen institucional" />
        <Stat value="#3 → #2" label="Carácter académico" />
      </StatRow>
      <Finding kind="crit" style={{ marginTop: 16 }}>
        <span className="num">INST_NOMBRE_INSTITUCION</span> era la variable #1 en MDI (0.295) y cae al puesto{" "}
        <b>#24 de 27</b> en permutation importance — su caída de R² real es prácticamente cero.{" "}
        <span className="num">ESTU_INST_DEPARTAMENTO</span> y <span className="num">ESTU_INST_MUNICIPIO</span>{" "}
        colapsan igual, con importancia <b>negativa</b> (permutarlas mejora el modelo: puro sobreajuste).
      </Finding>
      <Finding kind="real">
        <span className="num">INST_ORIGEN</span> y <span className="num">INST_CARACTER_ACADEMICO</span> —el{" "}
        <b>tipo</b> de institución, no su identidad puntual— suben de ranking y quedan como las dos variables
        más importantes también bajo el método robusto a sesgo.
      </Finding>
      <DataTableE7 />
    </section>
  );
}

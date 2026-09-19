import FoldChart from "@/components/charts/FoldChart";
import HBarChart from "@/components/charts/HBarChart";
import Finding from "@/components/Finding";
import Legend from "@/components/Legend";
import { e8Folds, e8bData } from "@/data/etapas";

export default function Etapa08() {
  return (
    <section id="e8">
      <div className="kicker">
        <span className="n">Etapa 08</span>La síntesis
      </div>
      <h2>El modelo final: señal real de institución + validación honesta</h2>
      <p className="lede">
        Combina lo que la etapa 7 confirmó como señal real (<span className="num">INST_ORIGEN</span>,{" "}
        <span className="num">INST_CARACTER_ACADEMICO</span>) con las variables demográficas de la etapa 5,
        descartando nombre y geografía institucional. Validado igual que la etapa 6: instituciones nunca vistas
        en cada fold.
      </p>
      <div className="cols2">
        <div className="card">
          <div style={{ height: 220 }}>
            <FoldChart folds={e8Folds.values} mean={e8Folds.mean} std={e8Folds.std} />
          </div>
        </div>
        <div className="card">
          <div style={{ height: 220 }}>
            <HBarChart data={e8bData} format={(v) => v.toFixed(3)} />
          </div>
          <Legend items={[{ color: "real", label: "Importancia media (5 folds)" }]} />
        </div>
      </div>
      <Finding kind="good" style={{ marginTop: 16 }}>
        R² <b>0.229 ± 0.087</b> — supera a la etapa 5 (+0.043) y a la etapa 6 (+0.109), con menos varianza entre
        folds que ambas. <b>Este es el número que el proyecto sostiene con más confianza.</b>
      </Finding>
    </section>
  );
}

import HBarChart from "@/components/charts/HBarChart";
import Finding from "@/components/Finding";
import Stat, { StatRow } from "@/components/Stat";
import { e2Data, e2Stats } from "@/data/etapas";
import { fmt } from "@/components/charts/chartUtils";

export default function Etapa02() {
  return (
    <section id="e2">
      <div className="kicker">
        <span className="n">Etapa 02</span>Primer modelo interpretable
      </div>
      <h2>Árbol de decisión: la misma señal, con interacciones</h2>
      <p className="lede">
        Un árbol sin podar sobreajusta por completo (17.443 hojas, R²=−0.24 en test). Podado a profundidad 4,
        generaliza razonablemente y sigue mostrando el mismo patrón.
      </p>
      <div className="cols2">
        <div className="card">
          <div style={{ height: 360 }}>
            <HBarChart data={e2Data} format={(v) => fmt(v, 4)} />
          </div>
        </div>
        <div>
          <StatRow>
            <Stat value={e2Stats.r2.toString()} label="R² podado" />
            <Stat value={e2Stats.mae.toString()} label="MAE" />
            <Stat value={e2Stats.rmse.toString()} label="RMSE" />
          </StatRow>
          <Finding kind="flag" style={{ marginTop: 16 }}>
            Los primeros tres cortes del árbol son <b>origen institucional</b>, <b>carácter académico</b> y el{" "}
            <b>nombre de una universidad puntual</b> (Uniandes) — el árbol literalmente aprende a reconocer
            instituciones específicas antes que cualquier otra cosa.
          </Finding>
        </div>
      </div>
    </section>
  );
}

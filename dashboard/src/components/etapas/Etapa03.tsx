import HBarGroupedChart from "@/components/charts/HBarGroupedChart";
import EvidenceImage from "@/components/EvidenceImage";
import Legend from "@/components/Legend";
import Stat, { StatRow } from "@/components/Stat";
import { e3Data, e3Stats } from "@/data/etapas";

export default function Etapa03() {
  return (
    <section id="e3">
      <div className="kicker">
        <span className="n">Etapa 03</span>El modelo de referencia
      </div>
      <h2>Random Forest + SHAP: R²=0.374, el número que todo el proyecto puso en duda</h2>
      <p className="lede">
        300 árboles, split único 80/20. Este es el resultado que el resto del proyecto (etapas 5 a 9) termina
        desarmando pieza por pieza.
      </p>
      <StatRow>
        <Stat value={e3Stats.r2.toString()} label="R² (split único)" />
        <Stat value={e3Stats.mae.toString()} label="MAE" />
        <Stat value={e3Stats.rmse.toString()} label="RMSE" />
      </StatRow>
      <div className="cols2" style={{ marginTop: 20 }}>
        <div className="card">
          <div style={{ height: 360 }}>
            <HBarGroupedChart data={e3Data} />
          </div>
          <Legend
            items={[
              { color: "accent", label: "Importancia MDI/Gini" },
              { color: "real", label: "SHAP (puntos de PUNT_GLOBAL)" },
            ]}
          />
        </div>
        <figure className="card">
          <EvidenceImage
            src="/img/shap_summary.png"
            alt="SHAP summary plot: distribución de impacto por variable y estudiante"
            width={1969}
            height={978}
          />
          <figcaption>
            SHAP summary plot original. Cada punto es un estudiante; el color indica el valor de la variable. El
            origen institucional domina con impactos de hasta ±25 puntos.
          </figcaption>
        </figure>
      </div>
    </section>
  );
}

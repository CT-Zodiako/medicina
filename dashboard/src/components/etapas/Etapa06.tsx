import FoldChart from "@/components/charts/FoldChart";
import HBarChart from "@/components/charts/HBarChart";
import Finding from "@/components/Finding";
import Legend from "@/components/Legend";
import { e6Folds, e6bData } from "@/data/etapas";

export default function Etapa06() {
  return (
    <section id="e6">
      <div className="kicker">
        <span className="n">Etapa 06</span>El chequeo decisivo
      </div>
      <h2>GroupKFold: validar contra instituciones que el modelo nunca vio</h2>
      <p className="lede">
        Un KFold aleatorio deja la misma institución en train y en test. Este esquema agrupa los folds por{" "}
        <span className="num">INST_NOMBRE_INSTITUCION</span>, así que cada fold de validación contiene{" "}
        <b>solo</b> instituciones ausentes del entrenamiento — la prueba real de generalización.
      </p>
      <div className="cols2">
        <div className="card">
          <div style={{ height: 220 }}>
            <FoldChart folds={e6Folds.values} mean={e6Folds.mean} std={e6Folds.std} />
          </div>
          <Legend
            items={[
              { color: "accent", label: "R² por fold" },
              { color: "critical", label: "Fold negativo" },
            ]}
          />
        </div>
        <div className="card">
          <div style={{ height: 220 }}>
            <HBarChart data={e6bData} format={(v) => v.toFixed(3)} />
          </div>
        </div>
      </div>
      <Finding kind="crit" style={{ marginTop: 16 }}>
        R² <b>0.120 ± 0.146</b> — peor que sacar la institución por completo (etapa 5), y con un fold en{" "}
        <b>R² negativo</b> (−0.074: el modelo predice peor que la media). Alta varianza entre folds: el modelo
        con institución completa no generaliza, memoriza.
      </Finding>
    </section>
  );
}

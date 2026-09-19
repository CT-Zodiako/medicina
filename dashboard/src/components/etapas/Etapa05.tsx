import FoldChart from "@/components/charts/FoldChart";
import HBarChart from "@/components/charts/HBarChart";
import Finding from "@/components/Finding";
import Legend from "@/components/Legend";
import { e5Folds, e5bData } from "@/data/etapas";

export default function Etapa05() {
  return (
    <section id="e5">
      <div className="kicker">
        <span className="n">Etapa 05</span>Primer control
      </div>
      <h2>¿Y si sacamos toda la institución?</h2>
      <p className="lede">
        Se repitió el Random Forest quitando las cinco variables institucionales por completo (nombre, origen,
        carácter académico, departamento, municipio), y se cambió el split único por{" "}
        <span className="num">KFold</span> aleatorio (k=5) para medir estabilidad.
      </p>
      <div className="cols2">
        <div className="card">
          <div style={{ height: 220 }}>
            <FoldChart folds={e5Folds.values} mean={e5Folds.mean} std={e5Folds.std} />
          </div>
        </div>
        <div className="card">
          <div style={{ height: 220 }}>
            <HBarChart data={e5bData} />
          </div>
          <Legend items={[{ color: "accent", label: "Importancia media (5 folds)" }]} />
        </div>
      </div>
      <Finding kind="real" style={{ marginTop: 16 }}>
        R² <b>0.186 ± 0.011</b> — cae a la mitad respecto al 0.374 original, pero es <b>estable</b> entre folds
        (variación ~7-10%). Sin institución, lo que emerge es edad, no trabajar, INSE individual y forma de pago
        de matrícula.
      </Finding>
    </section>
  );
}

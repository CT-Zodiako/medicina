import HBarChart from "@/components/charts/HBarChart";
import Finding from "@/components/Finding";
import { e1Data } from "@/data/etapas";
import { fmt } from "@/components/charts/chartUtils";

export default function Etapa01() {
  return (
    <section id="e1">
      <div className="kicker">
        <span className="n">Etapa 01</span>Punto de partida
      </div>
      <h2>Mutual Information: el primer barrido univariado</h2>
      <p className="lede">
        Se midió cuánta incertidumbre sobre <span className="num">PUNT_GLOBAL</span> reduce cada variable por
        separado, sin asumir relaciones lineales. No hay techo fijo — es una escala relativa entre variables,
        medida en <i>nats</i>.
      </p>
      <div className="cols2">
        <div className="card">
          <div style={{ height: 420 }}>
            <HBarChart data={e1Data} format={(v) => fmt(v, 4)} />
          </div>
        </div>
        <div>
          <Finding kind="flag">
            <b>El nombre de la institución</b> saca 0.2549 nats — más del <b>cuádruple</b> que la siguiente
            variable (0.0594, origen institucional). Ninguna variable demográfica o socioeconómica se acerca.
          </Finding>
          <Finding>
            Se validó fuga de información contra las 78 columnas originales: la primera variable legítima ya es
            institución (MI=0.2508); percentiles y componentes del mismo examen quedan excluidos del análisis
            por definición.
          </Finding>
        </div>
      </div>
    </section>
  );
}

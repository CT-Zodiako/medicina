import VarianceBars from "@/components/charts/VarianceBars";
import Finding from "@/components/Finding";
import Legend from "@/components/Legend";
import Stat, { StatRow } from "@/components/Stat";
import { e4Stats, varianzaEtapa4 } from "@/data/etapas";

export default function Etapa04() {
  return (
    <section id="e4">
      <div className="kicker">
        <span className="n">Etapa 04</span>Mirada no supervisada
      </div>
      <h2>PCA / UMAP: ~55 agrupaciones que parecían confirmar el patrón</h2>
      <p className="lede">
        Sin usar <span className="num">PUNT_GLOBAL</span> para nada, la reducción de dimensionalidad encuentra
        decenas de islas separadas. En su momento se leyó como confirmación visual independiente de que la
        institución importa — la etapa 9 muestra que era otra cosa.
      </p>
      <div className="cols2">
        <div className="card">
          <div style={{ height: 280 }}>
            <VarianceBars seriesA={varianzaEtapa4} labelA="Etapa 4" />
          </div>
          <Legend items={[{ color: "accent", label: "Varianza explicada por componente" }]} />
        </div>
        <StatRow style={{ margin: 0 }}>
          <Stat value={e4Stats.islas} label="Islas UMAP separadas" />
          <Stat value={e4Stats.varianzaAcumulada} label="Varianza acumulada (10 PC)" />
        </StatRow>
      </div>
      <Finding kind="flag">
        Cada isla es, casi sin excepción, una institución distinta — con el nombre puntual de institución
        todavía en el feature set, el clustering es indistinguible de un mapa de &ldquo;qué universidad asistió
        cada estudiante&rdquo;.
      </Finding>
    </section>
  );
}

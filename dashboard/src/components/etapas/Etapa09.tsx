import LineChart from "@/components/charts/LineChart";
import VarianceBars from "@/components/charts/VarianceBars";
import EvidenceImage from "@/components/EvidenceImage";
import Finding from "@/components/Finding";
import Legend from "@/components/Legend";
import { e9Silhouette, varianzaEtapa4, varianzaEtapa9 } from "@/data/etapas";

export default function Etapa09() {
  return (
    <section id="e9">
      <div className="kicker">
        <span className="n">Etapa 09</span>El cierre del círculo
      </div>
      <h2>UMAP sin institución: ¿los ~55 clusters eran reales?</h2>
      <p className="lede">
        Se repite exactamente el pipeline de la etapa 4, pero con el feature set honesto de la etapa 8. Si los
        clusters eran estructura real, deberían persistir. Si eran identidad institucional disfrazada, deberían
        desaparecer.
      </p>
      <div className="cols2">
        <figure className="card">
          <EvidenceImage
            src="/img/umap_etapa4.png"
            alt="UMAP coloreado por carácter académico, etapa 4, con institución"
            width={1200}
            height={900}
          />
          <figcaption>
            <b>Etapa 4 (con institución):</b> ~55–60 islas monocromáticas — una por institución.
          </figcaption>
        </figure>
        <figure className="card">
          <EvidenceImage
            src="/img/umap_etapa9.png"
            alt="UMAP coloreado por carácter académico, etapa 9, sin institución"
            width={1200}
            height={900}
          />
          <figcaption>
            <b>Etapa 9 (sin institución):</b> un blob difuso con colores mezclados — sin correspondencia 1:1
            institución↔cluster.
          </figcaption>
        </figure>
      </div>
      <div className="cols2" style={{ marginTop: 18 }}>
        <div className="card">
          <div style={{ height: 200 }}>
            <VarianceBars seriesA={varianzaEtapa4} seriesB={varianzaEtapa9} labelA="Etapa 4" labelB="Etapa 9" />
          </div>
          <Legend
            items={[
              { color: "muted", label: "Etapa 4 (con institución)" },
              { color: "real", label: "Etapa 9 (sin institución)" },
            ]}
          />
        </div>
        <div className="card">
          <div style={{ height: 200 }}>
            <LineChart values={e9Silhouette.values} startK={e9Silhouette.startK} />
          </div>
          <Legend items={[{ color: "real", label: "Silhouette (KMeans, k=2…15)" }]} />
        </div>
      </div>
      <Finding kind="good" style={{ marginTop: 16 }}>
        Los clusters <b>desaparecen</b>. La varianza explicada sube de 22.2% a 30.7% (ya no se diluye en
        decenas de columnas dummy de institución), y el silhouette no muestra ningún pico interior claro entre
        k=2 y k=15 — no hay partición nítida que sugerir. Los ~55 clusters de la etapa 4 eran identidad
        institucional, no estructura sustantiva.
      </Finding>
    </section>
  );
}

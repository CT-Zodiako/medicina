export default function Hero() {
  return (
    <div className="hero">
      <div className="page">
        <div className="eyebrow">Saber Pro · Medicina · 23.134 estudiantes · períodos 2019–2024</div>
        <h1>Variables que afectan el Saber Pro</h1>
        <p className="sub">
          Nueve etapas de análisis sobre qué variables se asocian con <span className="num">PUNT_GLOBAL</span> — y
          por qué el hallazgo más obvio (&ldquo;la institución domina&rdquo;) resultó estar mal medido. Esto
          reconstruye la investigación completa, paso a paso, con los números reales de cada etapa.
        </p>
        <div className="thesis">
          <div className="num-block">
            <span className="cap">Random Forest, split único</span>
            <span className="old">R² 0.374</span>
          </div>
          <span className="arrow">→</span>
          <div className="num-block">
            <span className="cap">Modelo honesto recomendado</span>
            <span className="new">R² 0.229</span>
          </div>
        </div>
        <div className="meta-row">
          <span>
            <b>9</b> etapas de validación
          </span>
          <span>
            <b>55</b> instituciones distintas en el dataset
          </span>
          <span>
            <b>0</b> variables de resultado del examen usadas (control de fuga)
          </span>
        </div>
      </div>
    </div>
  );
}

export default function SiteHeader() {
  return (
    <header className="site-header">
      <div className="page">
        <div className="eyebrow">Saber Pro · Medicina · Colombia · 2021–2024</div>
        <h1>Predicción del nivel de desempeño</h1>
        <p className="sub">
          Herramienta de apoyo académico que estima el nivel de desempeño (1 a 4) de un
          estudiante de Medicina a partir de variables demográficas y socioeconómicas
          disponibles antes de presentar el examen — sin usar ningún resultado del
          examen mismo.
        </p>
        <div className="stat-row">
          <div className="stat">
            <div className="v">30.738</div>
            <div className="l">Registros analizados</div>
          </div>
          <div className="stat">
            <div className="v">55</div>
            <div className="l">Instituciones</div>
          </div>
          <div className="stat">
            <div className="v">27</div>
            <div className="l">Variables del modelo</div>
          </div>
          <div className="stat">
            <div className="v">0.38</div>
            <div className="l">F1 macro validado</div>
          </div>
        </div>
      </div>
    </header>
  );
}

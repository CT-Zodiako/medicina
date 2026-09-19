export default function Cierre() {
  return (
    <section id="cierre">
      <div className="kicker">
        <span className="n">Cierre</span>Qué queda
      </div>
      <h2>Lo que el proyecto sostiene, y lo que no puede resolver</h2>
      <div className="cols2">
        <div className="close-card">
          <h3>Modelo y feature set recomendado</h3>
          <p style={{ fontSize: 14, color: "var(--ink-2)", lineHeight: 1.6 }}>
            Para cualquier uso real de este dataset — no solo para reportar un número:
          </p>
          <ul>
            <li>
              <b>Usar:</b> variables demográficas, socioeconómicas y familiares completas, más{" "}
              <span className="num">INST_ORIGEN</span> e <span className="num">INST_CARACTER_ACADEMICO</span>.
            </li>
            <li>
              <b>Descartar:</b> <span className="num">INST_NOMBRE_INSTITUCION</span>,{" "}
              <span className="num">ESTU_INST_DEPARTAMENTO</span>,{" "}
              <span className="num">ESTU_INST_MUNICIPIO</span> — memorización confirmada en dos métodos
              independientes (etapas 6 y 7).
            </li>
            <li>
              <b>Validar</b> siempre con <span className="num">GroupKFold</span> por institución, nunca con un
              split o KFold que mezcle las mismas instituciones entre train y test.
            </li>
          </ul>
        </div>
        <div className="close-card">
          <h3>Límites que no son &ldquo;próximos pasos&rdquo;</h3>
          <p style={{ fontSize: 14, color: "var(--ink-2)", lineHeight: 1.6 }}>
            Dos cosas no se pueden cerrar con este dataset, y no es por falta de análisis:
          </p>
          <ul>
            <li>
              <b>Causalidad.</b> Todo lo anterior es asociación. La institución puede empaquetar selección de
              estudiantes, recursos y currículo — el diseño observacional no permite separar esos mecanismos.
            </li>
            <li>
              <b>Variables omitidas.</b> Preparación para el examen, horas de estudio, salud y trayectoria
              escolar previa no están en el dataset. Ningún modelo puede usar información que no existe.
            </li>
          </ul>
        </div>
      </div>
      <footer>
        Informe completo, metodología y reproducibilidad: <code>docs/conclusiones/conclusion_final.md</code> (y
        su versión en PDF). Cada etapa vive en su propia carpeta <code>docs/etapa_N_*/</code> con su script, sus
        datos crudos y su conclusión puntual. Entorno reproducible en <code>requirements.txt</code>.
      </footer>
    </section>
  );
}

import PrediccionForm from "@/components/PrediccionForm";
import SiteHeader from "@/components/SiteHeader";

export default function Home() {
  return (
    <>
      <SiteHeader />
      <div className="page">
        <main>
          <section>
            <div className="finding flag">
              <span className="dot" />
              <p>
                El modelo de producción tiene un F1 macro de ~0.38 validado sobre
                instituciones nunca vistas — sirve para ver tendencias generales, no para
                decidir sobre un estudiante puntual. Cuando las dos clases más probables
                queden muy cerca, el resultado lo va a advertir explícitamente.
              </p>
            </div>
            <PrediccionForm />
          </section>
        </main>
      </div>
    </>
  );
}

import Cierre from "@/components/Cierre";
import Etapa01 from "@/components/etapas/Etapa01";
import Etapa02 from "@/components/etapas/Etapa02";
import Etapa03 from "@/components/etapas/Etapa03";
import Etapa04 from "@/components/etapas/Etapa04";
import Etapa05 from "@/components/etapas/Etapa05";
import Etapa06 from "@/components/etapas/Etapa06";
import Etapa07 from "@/components/etapas/Etapa07";
import Etapa08 from "@/components/etapas/Etapa08";
import Etapa09 from "@/components/etapas/Etapa09";
import Hero from "@/components/Hero";
import TocNav from "@/components/TocNav";

export default function Home() {
  return (
    <>
      <Hero />
      <div className="page">
        <div className="grid">
          <TocNav />
          <main>
            <Etapa01 />
            <Etapa02 />
            <Etapa03 />
            <Etapa04 />
            <Etapa05 />
            <Etapa06 />
            <Etapa07 />
            <Etapa08 />
            <Etapa09 />
            <Cierre />
          </main>
        </div>
      </div>
    </>
  );
}

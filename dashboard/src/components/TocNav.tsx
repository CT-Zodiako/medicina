const items = [
  { href: "#e1", n: "01", label: "Mutual Information" },
  { href: "#e2", n: "02", label: "Árbol de decisión" },
  { href: "#e3", n: "03", label: "Random Forest + SHAP" },
  { href: "#e4", n: "04", label: "PCA / UMAP" },
  { href: "#e5", n: "05", label: "Sin institución + CV" },
  { href: "#e6", n: "06", label: "GroupKFold institucional" },
  { href: "#e7", n: "07", label: "Permutación vs. MDI" },
  { href: "#e8", n: "08", label: "Modelo final honesto" },
  { href: "#e9", n: "09", label: "UMAP sin institución" },
  { href: "#cierre", n: "·", label: "Conclusión" },
];

/** Sticky side nav (desktop) / scrollable top bar (mobile, <840px). */
export default function TocNav() {
  return (
    <nav className="toc" id="toc">
      {items.map((item) => (
        <a key={item.href} href={item.href}>
          <span className="n">{item.n}</span>
          {item.label}
        </a>
      ))}
    </nav>
  );
}

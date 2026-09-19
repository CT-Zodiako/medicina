import type { CSSProperties, ReactNode } from "react";

export type FindingKind = "flag" | "real" | "good" | "crit";

export interface FindingProps {
  kind?: FindingKind;
  children: ReactNode;
  style?: CSSProperties;
}

/** Callout box with a colored dot — the "hallazgo destacado" pattern used in every etapa. */
export default function Finding({ kind, children, style }: FindingProps) {
  const className = kind ? `finding ${kind}` : "finding";
  return (
    <div className={className} style={style}>
      <span className="dot" style={kind ? undefined : { background: "var(--muted)" }} />
      <p>{children}</p>
    </div>
  );
}

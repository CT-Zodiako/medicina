import type { SlopeRow } from "@/data/etapas";

export interface SlopeChartProps {
  rows: SlopeRow[];
}

/** Slope / bump chart: rank in MDI/Gini (left column) vs. rank in permutation importance (right column). */
export default function SlopeChart({ rows }: SlopeChartProps) {
  const w = 640;
  const h = 380;
  const padT = 34;
  const padB = 20;
  const colL = 180;
  const colR = 460;
  const n = rows.length;
  const rowH = (h - padT - padB) / n;
  const yOfRank = (rank: number) => padT + (rank - 1) * rowH + rowH / 2;

  const colorFor = (flag: SlopeRow["flag"]) =>
    flag === "name" ? "var(--critical)" : flag === "type" ? "var(--good)" : "var(--muted)";

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="100%" preserveAspectRatio="xMinYMin meet">
      <text x={colL} y={18} fontSize="10.5px" textAnchor="middle" style={{ fill: "var(--muted)" }}>
        Ranking MDI/Gini
      </text>
      <text x={colR} y={18} fontSize="10.5px" textAnchor="middle" style={{ fill: "var(--muted)" }}>
        Ranking permutación
      </text>
      {rows.map((r) => {
        const y1 = yOfRank(r.mdi);
        const y2 = yOfRank(r.perm);
        const big = Math.abs(r.perm - r.mdi) >= 8;
        const color = colorFor(r.flag);
        return (
          <g key={r.name}>
            <line
              x1={colL + 10}
              y1={y1}
              x2={colR - 10}
              y2={y2}
              stroke={color}
              strokeWidth={big ? 2.4 : 1.3}
              opacity={big ? 0.9 : 0.55}
            >
              <title>{`${r.name}: MDI #${r.mdi} → permutación #${r.perm}`}</title>
            </line>
            <circle cx={colL + 10} cy={y1} r={3.4} style={{ fill: color }} />
            <circle cx={colR - 10} cy={y2} r={3.4} style={{ fill: color }} />
            <text x={colL} y={y1 + 3.5} textAnchor="end" fontSize="10.5px" style={{ fill: "var(--ink-2)" }}>
              {`${r.name}  #${r.mdi}`}
            </text>
            <text x={colR + 8} y={y2 + 3.5} fontSize="10.5px" style={{ fill: "var(--ink-2)" }}>
              {`#${r.perm}`}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

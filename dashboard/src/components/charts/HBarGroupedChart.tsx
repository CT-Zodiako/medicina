import type { GroupedBarDatum } from "@/data/etapas";
import { fmt } from "./chartUtils";

export interface HBarGroupedChartProps {
  data: GroupedBarDatum[];
}

/** Grouped horizontal bars — two thin series (`a`: MDI/RF, `b`: SHAP) per row. */
export default function HBarGroupedChart({ data }: HBarGroupedChartProps) {
  const w = 640;
  const rowH = 34;
  const padL = 210;
  const padR = 60;
  const padT = 8;
  const h = padT + data.length * rowH + 8;
  const maxV = Math.max(...data.map((d) => Math.max(d.a, d.b)));
  const barMaxW = w - padL - padR;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="100%" preserveAspectRatio="xMinYMin meet">
      {data.map((d, i) => {
        const y = padT + i * rowH;
        return (
          <g key={d.label}>
            <text x={padL - 10} y={y + rowH * 0.5} textAnchor="end" fontSize="11.5px" style={{ fill: "var(--ink-2)" }}>
              {d.label}
            </text>
            {([
              ["a", "var(--accent)", d.a, "MDI/RF"],
              ["b", "var(--real)", d.b, "SHAP"],
            ] as const).map(([key, color, val, seriesLabel], j) => {
              const by = y + j * 11 + 3;
              const bw = Math.max(2, (val / maxV) * barMaxW);
              return (
                <g key={key}>
                  <rect x={padL} y={by} width={barMaxW} height={9} rx={2} style={{ fill: "var(--surface-2)" }} />
                  <rect x={padL} y={by} width={bw} height={9} rx={2} style={{ fill: color }}>
                    <title>{`${d.label} (${seriesLabel}): ${fmt(val, 3)}`}</title>
                  </rect>
                </g>
              );
            })}
            <text x={padL + barMaxW + 8} y={y + rowH * 0.5} fontSize="10.5px" style={{ fill: "var(--muted)" }}>
              {fmt(d.a, 3)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

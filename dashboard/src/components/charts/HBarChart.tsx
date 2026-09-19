import type { HBarDatum } from "@/data/etapas";
import { fmt, tokenToVar } from "./chartUtils";

export interface HBarChartProps {
  data: HBarDatum[];
  /** Fixed max value for the scale; defaults to the max of `data`. */
  max?: number;
  /** Formats the value label next to each bar. Defaults to 3 decimals. */
  format?: (value: number) => string;
  rowH?: number;
  padL?: number;
}

/** Horizontal bar chart — one bar per row, label on the left, value on the right. */
export default function HBarChart({ data, max, format, rowH = 26, padL = 210 }: HBarChartProps) {
  const w = 640;
  const padR = 56;
  const padT = 8;
  const h = padT + data.length * rowH + 8;
  const maxV = max ?? Math.max(...data.map((d) => d.value));
  const barMaxW = w - padL - padR;
  const formatValue = format ?? ((v: number) => fmt(v, 3));

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="100%" preserveAspectRatio="xMinYMin meet">
      {data.map((d, i) => {
        const y = padT + i * rowH;
        const bw = Math.max(2, (d.value / maxV) * barMaxW);
        const color = tokenToVar(d.color);
        return (
          <g key={d.label}>
            <text
              x={padL - 10}
              y={y + rowH * 0.62}
              textAnchor="end"
              className="axis-label"
              fontSize="11.5px"
              style={{ fill: "var(--ink-2)" }}
            >
              {d.label}
            </text>
            <rect x={padL} y={y + 4} width={barMaxW} height={rowH - 12} rx={3} style={{ fill: "var(--surface-2)" }} />
            <rect x={padL} y={y + 4} width={bw} height={rowH - 12} rx={3} style={{ fill: color }}>
              <title>{`${d.label}: ${formatValue(d.value)}`}</title>
            </rect>
            <text x={padL + bw + 8} y={y + rowH * 0.62} fontSize="11px" style={{ fill: "var(--ink-2)" }}>
              {formatValue(d.value)}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

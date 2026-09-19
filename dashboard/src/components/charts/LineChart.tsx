import { fmt } from "./chartUtils";

export interface LineChartProps {
  values: number[];
  startK: number;
}

/** Line + point chart, used for silhouette scores across k. */
export default function LineChart({ values, startK }: LineChartProps) {
  const w = 480;
  const h = 180;
  const padL = 34;
  const padR = 12;
  const padT = 14;
  const padB = 26;
  const lo = Math.min(...values) * 0.95;
  const hi = Math.max(...values) * 1.05;
  const x0 = padL;
  const x1 = w - padR;
  const y0 = h - padB;
  const y1 = padT;
  const xScale = (i: number) => x0 + (i / (values.length - 1)) * (x1 - x0);
  const yScale = (v: number) => y0 - ((v - lo) / (hi - lo)) * (y0 - y1);

  const path = values
    .map((v, i) => `${i === 0 ? "M" : "L"}${xScale(i).toFixed(1)},${yScale(v).toFixed(1)}`)
    .join(" ");

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="100%" preserveAspectRatio="xMinYMin meet">
      <path d={path} fill="none" stroke="var(--real)" strokeWidth={2} />
      {values.map((v, i) => (
        <g key={i}>
          <circle cx={xScale(i)} cy={yScale(v)} r={3} style={{ fill: "var(--real)" }}>
            <title>{`k=${startK + i}: silhouette=${fmt(v, 3)}`}</title>
          </circle>
          {i % 3 === 0 && (
            <text x={xScale(i)} y={h - 8} textAnchor="middle" fontSize="9px" style={{ fill: "var(--muted)" }}>
              {`k=${startK + i}`}
            </text>
          )}
        </g>
      ))}
      <line x1={x0} x2={x1} y1={y0} y2={y0} stroke="var(--axis)" strokeWidth={1} />
    </svg>
  );
}

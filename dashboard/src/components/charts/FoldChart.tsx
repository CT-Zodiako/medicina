import { fmt } from "./chartUtils";

export interface FoldChartProps {
  folds: number[];
  mean: number;
  std: number;
}

/** Per-fold R² bars, with a dashed mean line and a ±std band. */
export default function FoldChart({ folds, mean, std }: FoldChartProps) {
  const w = 520;
  const h = 190;
  const padL = 40;
  const padR = 14;
  const padT = 16;
  const padB = 26;
  const lo = Math.min(-0.1, Math.min(...folds), mean - std);
  const hi = Math.max(0.4, Math.max(...folds), mean + std);
  const x0 = padL;
  const x1 = w - padR;
  const y0 = h - padB;
  const y1 = padT;
  const xScale = (i: number) => x0 + (i + 0.5) * ((x1 - x0) / folds.length);
  const yScale = (v: number) => y0 - ((v - lo) / (hi - lo)) * (y0 - y1);
  const bw = ((x1 - x0) / folds.length) * 0.55;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="100%" preserveAspectRatio="xMinYMin meet">
      <line x1={x0} x2={x1} y1={yScale(0)} y2={yScale(0)} stroke="var(--axis)" strokeWidth={1} />
      <rect
        x={x0}
        y={yScale(mean + std)}
        width={x1 - x0}
        height={Math.max(1, yScale(mean - std) - yScale(mean + std))}
        style={{ fill: "var(--accent)" }}
        opacity={0.08}
      />
      <line
        x1={x0}
        x2={x1}
        y1={yScale(mean)}
        y2={yScale(mean)}
        stroke="var(--accent)"
        strokeWidth={1.5}
        strokeDasharray="4 3"
      />
      <text x={x1} y={yScale(mean) - 6} textAnchor="end" fontSize="10.5px" style={{ fill: "var(--accent)" }}>
        {`media ${fmt(mean, 3)}`}
      </text>
      {folds.map((v, i) => {
        const cx = xScale(i);
        const yv = yScale(v);
        const yzero = yScale(0);
        const barY = Math.min(yv, yzero);
        const barH = Math.max(2, Math.abs(yv - yzero));
        return (
          <g key={i}>
            <rect
              x={cx - bw / 2}
              y={barY}
              width={bw}
              height={barH}
              rx={2}
              style={{ fill: v < 0 ? "var(--critical)" : "var(--accent)" }}
            >
              <title>{`Fold ${i + 1}: R²=${fmt(v, 3)}`}</title>
            </rect>
            <text x={cx} y={h - 8} textAnchor="middle" fontSize="10px" style={{ fill: "var(--muted)" }}>
              {`F${i + 1}`}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

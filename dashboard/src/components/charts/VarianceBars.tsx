import { fmtPct } from "./chartUtils";

export interface VarianceBarsProps {
  seriesA: number[];
  seriesB?: number[];
  labelA: string;
  labelB?: string;
}

/** PCA variance explained per component. With one series: a single accent-colored bar per
 * component. With two: grouped bars (muted vs. real) comparing two runs side by side. */
export default function VarianceBars({ seriesA, seriesB, labelA, labelB }: VarianceBarsProps) {
  const w = 480;
  const h = 180;
  const padL = 30;
  const padR = 10;
  const padT = 10;
  const padB = 24;
  const n = seriesA.length;
  const maxV = Math.max(...seriesA, ...(seriesB ?? []));
  const x0 = padL;
  const x1 = w - padR;
  const y0 = h - padB;
  const y1 = padT;
  const groupW = (x1 - x0) / n;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} width="100%" height="100%" preserveAspectRatio="xMinYMin meet">
      {Array.from({ length: n }, (_, i) => {
        const gx = x0 + i * groupW;
        const bw = seriesB ? groupW * 0.32 : groupW * 0.5;
        const ah = (seriesA[i] / maxV) * (y0 - y1);
        return (
          <g key={i}>
            <rect
              x={gx + groupW * (seriesB ? 0.12 : 0.25)}
              y={y0 - ah}
              width={bw}
              height={ah}
              rx={2}
              style={{ fill: seriesB ? "var(--muted)" : "var(--accent)" }}
            >
              <title>{`${labelA} PC${i + 1}: ${fmtPct(seriesA[i])}`}</title>
            </rect>
            {seriesB && (
              <rect
                x={gx + groupW * 0.12 + bw + 2}
                y={y0 - (seriesB[i] / maxV) * (y0 - y1)}
                width={bw}
                height={(seriesB[i] / maxV) * (y0 - y1)}
                rx={2}
                style={{ fill: "var(--real)" }}
              >
                <title>{`${labelB} PC${i + 1}: ${fmtPct(seriesB[i])}`}</title>
              </rect>
            )}
            {(i % 2 === 0 || n <= 10) && (
              <text x={gx + groupW / 2} y={h - 8} textAnchor="middle" fontSize="9px" style={{ fill: "var(--muted)" }}>
                {`PC${i + 1}`}
              </text>
            )}
          </g>
        );
      })}
      <line x1={x0} x2={x1} y1={y0} y2={y0} stroke="var(--axis)" strokeWidth={1} />
    </svg>
  );
}

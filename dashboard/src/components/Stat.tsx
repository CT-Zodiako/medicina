import type { CSSProperties, ReactNode } from "react";

export function StatRow({ children, style }: { children: ReactNode; style?: CSSProperties }) {
  return <div className="stat-row" style={style}>{children}</div>;
}

export default function Stat({ value, label }: { value: string; label: string }) {
  return (
    <div className="stat">
      <div className="v">{value}</div>
      <div className="l">{label}</div>
    </div>
  );
}

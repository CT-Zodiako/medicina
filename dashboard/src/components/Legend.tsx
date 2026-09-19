import type { CSSProperties } from "react";
import type { ColorToken } from "@/data/etapas";
import { tokenToVar } from "./charts/chartUtils";

export interface LegendItem {
  color: ColorToken;
  label: string;
}

export default function Legend({ items, style }: { items: LegendItem[]; style?: CSSProperties }) {
  return (
    <p className="legend" style={style}>
      {items.map((item) => (
        <span key={item.label}>
          <span className="sw" style={{ background: tokenToVar(item.color) }} />
          {item.label}
        </span>
      ))}
    </p>
  );
}

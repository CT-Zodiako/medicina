import type { ColorToken } from "@/data/etapas";

/** Semantic color token → CSS custom property, so charts stay theme-aware
 * purely through CSS (light/dark) without any redraw-on-theme-change logic. */
export function tokenToVar(token: ColorToken = "accent"): string {
  return `var(--${token})`;
}

export function fmt(v: number, d = 3): string {
  return v.toFixed(d);
}

export function fmtPct(v: number, d = 1): string {
  return `${v.toFixed(d)}%`;
}

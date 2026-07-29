/** Stitch Team Ops palette — rule-based health bands only (no fake scores). */

export const TEAM_OPS = {
  bg: "#13131b",
  surfaceLow: "#1b1b23",
  surface: "#1f1f27",
  surfaceHigh: "#292932",
  surfaceHighest: "#34343d",
  onSurface: "#e4e1ed",
  onVariant: "#c7c4d7",
  outline: "#464554",
  primary: "#c0c1ff",
  primaryContainer: "#8083ff",
  secondary: "#4fdbc8",
  secondaryContainer: "#04b4a2",
  tertiary: "#ffb783",
  tertiaryContainer: "#d97721",
  error: "#ffb4ab",
  fontDisplay: "'Plus Jakarta Sans', sans-serif",
  fontBody: "'Plus Jakarta Sans', sans-serif",
} as const;

export function healthBandColor(band: string | undefined): string {
  switch (band) {
    case "healthy":
      return TEAM_OPS.secondary;
    case "needs_attention":
      return TEAM_OPS.tertiary;
    case "at_risk":
      return TEAM_OPS.error;
    default:
      return TEAM_OPS.onVariant;
  }
}

export function formatOccurredAt(value?: string | null): string {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

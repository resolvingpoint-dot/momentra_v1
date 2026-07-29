/** Stitch Business Runway palette — financial OS theme. */

export const RUNWAY = {
  bg: "#13131b",
  surfaceLow: "#1b1b23",
  surface: "#1f1f27",
  surfaceHigh: "#292932",
  onSurface: "#e4e1ed",
  onVariant: "#c7c4d7",
  outline: "#464554",
  primary: "#4fdbc8",
  primaryContainer: "#04b4a2",
  secondary: "#71f8e4",
  tertiary: "#ffb783",
  error: "#ffb4ab",
  fontDisplay: "'Manrope', 'Plus Jakarta Sans', sans-serif",
  fontBody: "'Inter', 'Plus Jakarta Sans', 'Geist', sans-serif",
} as const;

export function runwayBandColor(band: string | undefined): string {
  switch (band) {
    case "healthy":
      return RUNWAY.primary;
    case "needs_attention":
      return RUNWAY.tertiary;
    case "at_risk":
    case "critical":
      return RUNWAY.error;
    default:
      return RUNWAY.onVariant;
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

export function formatRunwayMonths(months: number | null | undefined): string {
  if (months == null || !Number.isFinite(months)) return "—";
  return `${months.toFixed(1)} months`;
}

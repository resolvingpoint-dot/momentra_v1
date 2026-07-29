/** Stitch Business Operations palette — operating OS theme (distinct from Runway teal). */

export const OPS = {
  bg: "#12151a",
  surfaceLow: "#181c23",
  surface: "#1e2430",
  surfaceHigh: "#2a3344",
  onSurface: "#e9eef5",
  onVariant: "#9ba7b8",
  outline: "#3e4a5c",
  primary: "#7dd3fc",
  primaryContainer: "#0284c7",
  secondary: "#fb923c",
  secondaryContainer: "#c2410c",
  error: "#f87171",
  fontDisplay: "'Manrope', 'Plus Jakarta Sans', sans-serif",
  fontBody: "'Plus Jakarta Sans', 'Inter', 'Geist', sans-serif",
} as const;

/** Health bands are UPPERCASE only — EMPTY / HEALTHY / NEEDS_ATTENTION / AT_RISK. */
export function opsBandColor(band: string | undefined): string {
  switch ((band ?? "").toUpperCase()) {
    case "HEALTHY":
      return OPS.primary;
    case "NEEDS_ATTENTION":
      return OPS.secondary;
    case "AT_RISK":
      return OPS.error;
    default:
      return OPS.onVariant;
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

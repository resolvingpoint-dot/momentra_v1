/** Stitch Group trip tokens — Plus Jakarta Sans + DESIGN.md colors */
export const tripStitchTheme = {
  background: "#131313",
  onSurface: "#e5e2e1",
  onSurfaceVariant: "#dfc0b4",
  surfaceContainer: "#201f1f",
  surfaceContainerHigh: "#2a2a2a",
  outline: "#a78b80",
  primary: "#ffb598",
  onPrimary: "#591d00",
  primaryContainer: "#ff7a3d",
  secondary: "#ffb690",
  tertiary: "#ffb951",
  error: "#ffb4ab",
  fontFamily: '"Plus Jakarta Sans", system-ui, sans-serif',
} as const;

export const tripStitchShellStyle: Record<string, string> = {
  fontFamily: tripStitchTheme.fontFamily,
  color: tripStitchTheme.onSurface,
};

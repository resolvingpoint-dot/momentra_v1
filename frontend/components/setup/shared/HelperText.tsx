"use client";

/** Presentational helper text under a field label. Prefer SetupField `helper` prop. */
export function HelperText({ children }: { children: React.ReactNode }) {
  return <p className="text-xs leading-relaxed opacity-70">{children}</p>;
}

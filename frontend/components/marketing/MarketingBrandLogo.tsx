/** Shared marketing brand mark — same asset as Login / TopBar. */
export function MarketingBrandLogo({
  className = "h-9 w-auto max-w-[160px]",
}: {
  className?: string;
}) {
  return (
    // eslint-disable-next-line @next/next/no-img-element -- static public SVG used across auth chrome
    <img
      src="/momentra_logo_dark.svg"
      alt="Momentra"
      width={160}
      height={53}
      className={className}
      decoding="async"
    />
  );
}

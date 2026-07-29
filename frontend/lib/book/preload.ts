const preloaded = new Set<string>();

export function pageSrc(assetBase: string, filename: string): string {
  const base = assetBase.endsWith("/") ? assetBase.slice(0, -1) : assetBase;
  return `${base}/${filename}`;
}

/** Preload a single image URL into the browser cache. */
export function preloadImage(src: string): void {
  if (typeof window === "undefined") return;
  if (preloaded.has(src)) return;
  preloaded.add(src);
  const img = new window.Image();
  img.decoding = "async";
  img.src = src;
}

/**
 * Only load current, previous, and next pages.
 * Returns the three srcs that should be considered "hot".
 */
export function preloadNeighbors(
  assetBase: string,
  pages: string[],
  /** 0-based index */
  currentIndex: number,
): { prev: string | null; current: string; next: string | null } {
  const current = pageSrc(assetBase, pages[currentIndex]!);
  const prev =
    currentIndex > 0
      ? pageSrc(assetBase, pages[currentIndex - 1]!)
      : null;
  const next =
    currentIndex < pages.length - 1
      ? pageSrc(assetBase, pages[currentIndex + 1]!)
      : null;

  preloadImage(current);
  if (prev) preloadImage(prev);
  if (next) preloadImage(next);

  return { prev, current, next };
}

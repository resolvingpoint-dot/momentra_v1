"use client";

import { useEffect, useState } from "react";

const TAILWIND_BREAKPOINTS: Record<string, number> = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  "2xl": 1536,
};

/**
 * Returns whether the current viewport matches or exceeds a Tailwind breakpoint.
 * Defaults to `false` to avoid hydration mismatches (mobile-first).
 * Only runs on the client after mount.
 */
export function useBreakpoint(breakpoint: keyof typeof TAILWIND_BREAKPOINTS): boolean {
  const [matches, setMatches] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.matchMedia(`(min-width: ${TAILWIND_BREAKPOINTS[breakpoint]}px)`).matches;
  });

  useEffect(() => {
    const query = window.matchMedia(`(min-width: ${TAILWIND_BREAKPOINTS[breakpoint]}px)`);
    const update = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, [breakpoint]);

  return matches;
}

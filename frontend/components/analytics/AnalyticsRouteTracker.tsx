"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { MomentraAnalytics } from "@/lib/analytics";
import { resolveWebRouteScreen } from "@/lib/analyticsScreens";

/**
 * Logs Firebase Analytics screen_view for Next.js routes (marketing, book, invite, app entry).
 * In-app tab/overlay screens under `/app` are owned by home shells — we only log `app` once per entry.
 */
export function AnalyticsRouteTracker() {
  const pathname = usePathname();
  const lastLogged = useRef<string | null>(null);
  const lastAppEntryLogged = useRef(false);

  useEffect(() => {
    const screen = resolveWebRouteScreen(pathname);
    if (!screen) return;

    if (screen === "app") {
      if (lastAppEntryLogged.current && lastLogged.current === "app") return;
      lastAppEntryLogged.current = true;
      lastLogged.current = "app";
      void MomentraAnalytics.logScreen("app");
      return;
    }

    lastAppEntryLogged.current = false;
    if (lastLogged.current === screen) return;
    lastLogged.current = screen;
    void MomentraAnalytics.logScreen(screen);
  }, [pathname]);

  return null;
}

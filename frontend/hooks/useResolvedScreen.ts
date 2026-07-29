"use client";

import { useMemo } from "react";
import type { AppContext } from "@/lib/appContext";
import type { BottomNavTabId } from "@/lib/bottomNavTabs";
import {
  resolveScreen,
  resolveScreenPhase,
  shouldLoadTabData,
  type ResolvedScreen,
  type ScreenPhase,
} from "@/lib/screenResolver";
import { useBootstrapStore } from "@/hooks/useBootstrap";

export function useResolvedScreen(context: AppContext, tab: BottomNavTabId) {
  const { data: bootstrap, isLoading, hasLoadedOnce } = useBootstrapStore();

  return useMemo(() => {
    const resolved = resolveScreen(context, tab, bootstrap);
    const phase = resolveScreenPhase(context, tab, bootstrap);
    return {
      bootstrap,
      resolved,
      phase,
      shouldLoad: shouldLoadTabData(resolved),
      isBootstrapping: !hasLoadedOnce && isLoading,
    };
  }, [context, tab, bootstrap, hasLoadedOnce, isLoading]);
}

export type { ResolvedScreen, ScreenPhase };

import type { AppContext } from "@/lib/appContext";
import type { BootstrapResponse, ContextState } from "@/lib/api/bootstrapTypes";
import type { BottomNavTabId } from "@/lib/bottomNavTabs";
import { appContextToBackend } from "@/lib/contextMapping";

export type ScreenPhase = "loading" | "empty" | "setup" | "active";

export type ResolvedScreen =
  | "loading"
  | "empty_pulse"
  | "empty_moments"
  | "empty_memory"
  | "empty_life"
  | "empty_create"
  | "setup_pulse"
  | "setup_moments"
  | "setup_memory"
  | "setup_life"
  | "setup_create"
  | "active_pulse"
  | "active_moments"
  | "active_memory"
  | "active_life";

export function normalizeModulePhase(state: string | undefined | null): ScreenPhase {
  if (!state || state === "EMPTY") return "empty";
  if (state === "SETUP" || state === "DRAFT") return "setup";
  return "active";
}

export function contextStateFromBootstrap(
  bootstrap: BootstrapResponse | null,
  context: AppContext,
): ContextState {
  if (!bootstrap) return "EMPTY";
  const key = appContextToBackend(context);
  return bootstrap.contexts.find((c) => c.key === key)?.state ?? "EMPTY";
}

export function moduleStateFromBootstrap(
  bootstrap: BootstrapResponse | null,
  moduleKey: string,
): ContextState {
  if (!bootstrap) return "EMPTY";
  return bootstrap.modules[moduleKey]?.state ?? "EMPTY";
}

function moduleKeyForTab(tab: BottomNavTabId, context: AppContext): string {
  if (tab === "pulse") return "pulse";
  if (tab === "moments") return "moments";
  if (context === "personal") {
    if (tab === "memory" || tab === "life") return "moments";
  } else {
    if (tab === "memory") return "memory";
    if (tab === "life") return "life360";
  }
  return "pulse";
}

export function resolveScreenPhase(
  context: AppContext,
  tab: BottomNavTabId,
  bootstrap: BootstrapResponse | null,
): ScreenPhase {
  if (!bootstrap) return "loading";
  const ctxPhase = normalizeModulePhase(contextStateFromBootstrap(bootstrap, context));
  if (ctxPhase === "empty") return "empty";
  if (tab === "add") {
    return ctxPhase === "setup" ? "setup" : ctxPhase;
  }
  // Group Life is the cross-moment command center — follow group context, not Life360 snapshots.
  if (context === "group" && tab === "life") {
    return ctxPhase === "setup" ? "setup" : "active";
  }
  // Group Pulse: prefer context ACTIVE over a stale modules.pulse SETUP left after activation.
  if (context === "group" && tab === "pulse") {
    if (ctxPhase === "setup") return "setup";
    if (ctxPhase === "active") return "active";
  }
  // Business: prefer context ACTIVE so Team Ops verticals aren't stuck on marketing empty.
  if (context === "business") {
    if (ctxPhase === "setup") return "setup";
    if (ctxPhase === "active") return "active";
  }
  // Circle: home is driven by participant snapshots (EMPTY vs FULL), not moment inventory.
  if (context === "circle") {
    if (ctxPhase === "setup") return "setup";
    if (ctxPhase === "active") return "active";
  }
  const modulePhase = normalizeModulePhase(
    moduleStateFromBootstrap(bootstrap, moduleKeyForTab(tab, context)),
  );
  if (ctxPhase === "setup" || modulePhase === "setup") return "setup";
  if (modulePhase === "empty") return "empty";
  return "active";
}

export function resolveScreen(
  context: AppContext,
  tab: BottomNavTabId,
  bootstrap: BootstrapResponse | null,
): ResolvedScreen {
  const phase = resolveScreenPhase(context, tab, bootstrap);
  if (phase === "loading") return "loading";

  const contentTab = tab === "add" ? "pulse" : tab;

  if (tab === "add") {
    if (phase === "empty") return "empty_create";
    if (phase === "setup") return "setup_create";
    return "active_pulse";
  }

  const prefix =
    phase === "empty" ? "empty" : phase === "setup" ? "setup" : "active";

  switch (contentTab) {
    case "pulse":
      return `${prefix}_pulse` as ResolvedScreen;
    case "moments":
      return `${prefix}_moments` as ResolvedScreen;
    case "memory":
      return `${prefix}_memory` as ResolvedScreen;
    case "life":
      return `${prefix}_life` as ResolvedScreen;
    default:
      return `${prefix}_pulse` as ResolvedScreen;
  }
}

export function isActiveScreen(resolved: ResolvedScreen): boolean {
  return resolved.startsWith("active_");
}

export function isEmptyScreen(resolved: ResolvedScreen): boolean {
  return resolved.startsWith("empty_");
}

export function isSetupScreen(resolved: ResolvedScreen): boolean {
  return resolved.startsWith("setup_");
}

export function shouldLoadTabData(resolved: ResolvedScreen): boolean {
  return isActiveScreen(resolved);
}

"use client";

import { useCallback, useSyncExternalStore } from "react";
import type { AppContext } from "@/lib/appContext";
import { DEFAULT_APP_CONTEXT } from "@/lib/appContext";
import { appContextToBackend, backendContextToApp } from "@/lib/contextMapping";
import { cancelInFlightRequests } from "@/lib/requestScope";
import { endSpan, startSpan } from "@/lib/telemetry/performanceTelemetry";
import { AppRepository } from "@/repositories/AppRepository";
import {
  getBootstrap,
  selectedBackendContext,
} from "@/stores/bootstrapStore";

let selectedContext: AppContext = backendContextToApp(selectedBackendContext());
let isSwitching = false;
let switchError: string | null = null;
/** After first hydrate from bootstrap, shell context is client-owned. */
let contextHydrated = false;
/** Monotonic generation so only the latest switch owns PATCH / rollback / isSwitching. */
let switchGeneration = 0;

type DebounceWaiter = {
  generation: number;
  timer: ReturnType<typeof setTimeout>;
  resolve: () => void;
};
let pendingDebounce: DebounceWaiter | null = null;

const contextListeners = new Set<() => void>();

function notifyContext() {
  contextListeners.forEach((fn) => fn());
}

function contextSnapshot() {
  return { selectedContext, isSwitching, switchError, contextHydrated };
}

/** Resolve any in-flight debounce wait immediately so prior switchContext calls do not hang. */
function settleDebounceEarly() {
  if (!pendingDebounce) return;
  clearTimeout(pendingDebounce.timer);
  const { resolve } = pendingDebounce;
  pendingDebounce = null;
  resolve();
}

export function subscribeContextStore(listener: () => void): () => void {
  contextListeners.add(listener);
  return () => contextListeners.delete(listener);
}

export function getContextSnapshot() {
  return contextSnapshot();
}

export function clearSwitchError(): void {
  if (switchError === null) return;
  switchError = null;
  notifyContext();
}

/**
 * Hydrate shell context from bootstrap preferences once.
 * After hydrate, bootstrap refreshes must not overwrite selectedContext
 * (stale GETs caused Group/Business snap-back to My Money).
 */
export function syncContextFromBootstrap(): void {
  if (contextHydrated) return;
  const bootstrap = getBootstrap();
  if (!bootstrap) return;
  if (isSwitching) return;
  const next = backendContextToApp(bootstrap.preferences.selected_context);
  selectedContext = next;
  contextHydrated = true;
  notifyContext();
}

export function setContextLocal(context: AppContext): void {
  if (context === selectedContext) return;
  selectedContext = context;
  contextHydrated = true;
  notifyContext();
}

export function resetContextOnLogout(): void {
  settleDebounceEarly();
  switchGeneration += 1;
  selectedContext = DEFAULT_APP_CONTEXT;
  isSwitching = false;
  switchError = null;
  contextHydrated = false;
  notifyContext();
}

export async function switchContext(context: AppContext): Promise<void> {
  if (context === selectedContext) return;

  const previous = selectedContext;
  const generation = ++switchGeneration;
  selectedContext = context;
  contextHydrated = true;
  isSwitching = true;
  switchError = null;
  // Cancel in-flight home loads only — preference PATCH is not attached to this scope.
  cancelInFlightRequests();
  notifyContext();

  settleDebounceEarly();
  await new Promise<void>((resolve) => {
    const timer = setTimeout(() => {
      if (pendingDebounce?.generation === generation) {
        pendingDebounce = null;
      }
      resolve();
    }, 300);
    pendingDebounce = { generation, timer, resolve };
  });

  if (generation !== switchGeneration) {
    return;
  }

  const spanId = startSpan("context.switch", { context });
  try {
    await AppRepository.updatePreferences({
      selected_context: appContextToBackend(context),
    });
    if (generation !== switchGeneration) return;
  } catch (err) {
    if (generation !== switchGeneration) return;
    // Only roll back if the failed target is still selected (user has not moved on).
    if (selectedContext === context) {
      selectedContext = previous;
      switchError =
        err instanceof Error ? err.message : "Couldn't save context — check connection";
    }
  } finally {
    endSpan(spanId);
    if (generation === switchGeneration) {
      isSwitching = false;
      notifyContext();
    }
  }
}

export function useContextStore() {
  const state = useSyncExternalStore(
    subscribeContextStore,
    contextSnapshot,
    contextSnapshot,
  );

  const switchTo = useCallback(async (context: AppContext) => {
    await switchContext(context);
  }, []);

  return {
    ...state,
    switchContext: switchTo,
    clearSwitchError,
  };
}

/**
 * Bootstrap notify subscription no longer syncs shell context continuously.
 * Kept for call-site compatibility; hydrate happens via BootstrapGate once.
 */
export function wireContextStoreToBootstrap(): () => void {
  return () => {};
}

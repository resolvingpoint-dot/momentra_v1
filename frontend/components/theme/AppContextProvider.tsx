"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import {
  APP_CONTEXTS,
  type AppContext,
} from "@/lib/appContext";
import { MomentraAnalytics } from "@/lib/analytics";
import {
  tokensFor,
  type ContextThemeTokens,
} from "@/lib/contextTokens";
import {
  subscribeContextStore,
  switchContext,
  getContextSnapshot,
  syncContextFromBootstrap,
} from "@/stores/contextStore";

type AppContextValue = {
  context: AppContext;
  setContext: (context: AppContext) => void;
  tokens: ContextThemeTokens;
  mountedContexts: ReadonlySet<AppContext>;
  isSwitchingContext: boolean;
};

const AppContextReactContext = createContext<AppContextValue | null>(null);

export function AppContextProvider({ children }: { children: ReactNode }) {
  const [mountedContexts, setMountedContexts] = useState<Set<AppContext>>(
    () => new Set([getContextSnapshot().selectedContext]),
  );
  const [context, setContextState] = useState<AppContext>(
    () => getContextSnapshot().selectedContext,
  );
  const [isSwitchingContext, setIsSwitchingContext] = useState(false);

  useEffect(() => {
    const unsubscribe = subscribeContextStore(() => {
      const { selectedContext, isSwitching } = getContextSnapshot();
      setMountedContexts((prev) => {
        if (prev.has(selectedContext)) return prev;
        const next = new Set(prev);
        next.add(selectedContext);
        return next;
      });
      setContextState((prev) => {
        if (prev !== selectedContext) {
          void MomentraAnalytics.logCustomEvent("context_switch", {
            from_context: prev,
            to_context: selectedContext,
          });
          void MomentraAnalytics.setActiveContext(selectedContext);
        }
        return selectedContext;
      });
      setIsSwitchingContext(isSwitching);
    });
    // Subscribe first so hydrate notify mounts the restored context.
    syncContextFromBootstrap();
    return unsubscribe;
  }, []);

  const setContext = useCallback((next: AppContext) => {
    setMountedContexts((prev) => {
      if (prev.has(next)) return prev;
      const updated = new Set(prev);
      updated.add(next);
      return updated;
    });
    void switchContext(next).catch(() => {
      // rollback handled in contextStore
    });
  }, []);

  const value = useMemo(
    () => ({
      context,
      setContext,
      tokens: tokensFor(context),
      mountedContexts,
      isSwitchingContext,
    }),
    [context, setContext, mountedContexts, isSwitchingContext],
  );

  return (
    <AppContextReactContext.Provider value={value}>
      <div data-momentra-context={context} className="contents">
        {children}
      </div>
    </AppContextReactContext.Provider>
  );
}

export function useAppContext(): AppContext {
  const value = useContext(AppContextReactContext);
  if (!value) {
    throw new Error("useAppContext must be used within AppContextProvider");
  }
  return value.context;
}

export function useSetAppContext(): (context: AppContext) => void {
  const value = useContext(AppContextReactContext);
  if (!value) {
    throw new Error("useSetAppContext must be used within AppContextProvider");
  }
  return value.setContext;
}

export function useAppContextState(): AppContextValue {
  const value = useContext(AppContextReactContext);
  if (!value) {
    throw new Error("useAppContextState must be used within AppContextProvider");
  }
  return value;
}

export function useThemeTokens(): ContextThemeTokens {
  return useAppContextState().tokens;
}

export { APP_CONTEXTS };

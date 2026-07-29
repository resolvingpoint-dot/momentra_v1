"use client";

import { APP_CONTEXTS, useAppContextState } from "@/components/theme/AppContextProvider";
import { contextDisplayName, contextIcon } from "@/lib/bottomNavTabs";
import { tokensFor } from "@/lib/contextTokens";

const shellTokens = tokensFor("personal");

export function MomentraContextSwitcher() {
  const { context, setContext } = useAppContextState();

  return (
    <div
      className="flex h-11 shrink-0 items-center gap-1 px-3 sm:px-4"
      style={{ background: shellTokens.colors.surfaceContainer }}
    >
      {APP_CONTEXTS.map((ctx) => {
        const isSelected = context === ctx;
        const tabTokens = tokensFor(ctx);
        const Icon = contextIcon(ctx);

        return (
          <button
            key={ctx}
            type="button"
            onClick={() => setContext(ctx)}
            className="flex flex-1 items-center justify-center gap-1 rounded-md px-1 py-1.5 text-xs font-semibold transition-colors motion-reduce:transition-none sm:gap-1.5 sm:px-2"
            style={{
              background: isSelected
                ? tabTokens.colors.primaryContainer
                : "transparent",
              color: isSelected
                ? tabTokens.colors.onPrimaryContainer
                : shellTokens.colors.textSecondary,
            }}
          >
            <Icon className="h-3.5 w-3.5 shrink-0" aria-hidden />
            <span className="truncate">{contextDisplayName(ctx)}</span>
          </button>
        );
      })}
    </div>
  );
}

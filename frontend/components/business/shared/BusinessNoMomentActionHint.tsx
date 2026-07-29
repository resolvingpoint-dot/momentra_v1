"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";

/** Shown when FAB is pressed without an active business moment. */
export function BusinessNoMomentActionHint({ onClose }: { onClose: () => void }) {
  const { colors } = useThemeTokens();
  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 p-4 md:items-center"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="w-full max-w-md rounded-2xl p-6 shadow-xl"
        style={{ background: colors.background, color: colors.textPrimary }}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="business-ac-hint-title"
      >
        <h2 id="business-ac-hint-title" className="text-xl font-bold">
          Action Center
        </h2>
        <p className="mt-3 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Activate a Team Operations, Runway, or Operations moment to open the Business Action Center.
        </p>
        <button
          type="button"
          onClick={onClose}
          className="mt-6 w-full rounded-xl py-3 text-sm font-semibold"
          style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
        >
          OK
        </button>
      </div>
    </div>
  );
}

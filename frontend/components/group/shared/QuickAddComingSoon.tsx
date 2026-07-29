"use client";

/**
 * @deprecated Group FAB uses Action Center (`GroupMomentQuickAddRouter`).
 * Do not mount this on the Group path — kept only for legacy references.
 */
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type QuickAddComingSoonProps = {
  onClose: () => void;
};

/** @deprecated Prefer GroupActionCenterShell */
export function QuickAddComingSoon({ onClose }: QuickAddComingSoonProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

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
        aria-labelledby="group-quick-add-title"
      >
        <h2 id="group-quick-add-title" className="text-xl font-bold">
          Quick Add
        </h2>
        <p className="mt-3 text-sm opacity-80" style={{ color: colors.textSecondary }}>
          Legacy placeholder — Group moments open Action Center instead.
        </p>
        <button
          type="button"
          onClick={onClose}
          className="mt-6 w-full rounded-xl py-3 text-sm font-semibold"
          style={{
            background: colors.primaryContainer,
            color: colors.brandOnPrimary,
          }}
        >
          OK
        </button>
      </div>
    </div>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { momentTypeLabel } from "@/components/personal/shared/personalMomentRouting";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";

type PersonalQuickAddFallbackSheetProps = {
  momentTypeCode: PersonalMomentTypeCode;
  open?: boolean;
  onClose: () => void;
  onBeginSetup?: () => void;
};

export function PersonalQuickAddFallbackSheet({
  momentTypeCode,
  open = true,
  onClose,
  onBeginSetup,
}: PersonalQuickAddFallbackSheetProps) {
  const { colors } = useThemeTokens();
  const label = momentTypeLabel(momentTypeCode);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 sm:items-center"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-t-2xl border p-6 sm:rounded-2xl"
        style={{ borderColor: colors.border, background: colors.surface }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
          Quick Add
        </h2>
        <p className="mt-2" style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
          Activate a {label} moment to capture entries from here.
        </p>
        {onBeginSetup ? (
          <button
            type="button"
            onClick={onBeginSetup}
            className="mt-4 w-full rounded-xl py-3 font-semibold"
            style={{ background: colors.brandPrimary, color: colors.onPrimary }}
          >
            Set up {label}
          </button>
        ) : null}
        <button
          type="button"
          onClick={onClose}
          className="mt-6 w-full rounded-xl border py-3"
          style={{ borderColor: colors.border, color: colors.textSecondary }}
        >
          Close
        </button>
      </div>
    </div>
  );
}

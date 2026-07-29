"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GuidedSetupSaveIndicator } from "@/components/setup/GuidedSetupSaveIndicator";
import type { GuidedSetupSaveState } from "@/components/setup/guidedSetupTypes";

type Props = {
  saveState: GuidedSetupSaveState;
  canGoBack?: boolean;
  canContinue?: boolean;
  canActivate?: boolean;
  canPreview?: boolean;
  isReview?: boolean;
  submitting?: boolean;
  interactionsDisabled?: boolean;
  footerPrimaryLabel?: string;
  footerSecondaryLabel?: string;
  onBack?: () => void;
  onContinue?: () => void;
  onPreview?: () => void;
  onActivate?: () => void;
  onRetrySave?: () => void;
};

export function GuidedSetupFooter({
  saveState,
  canGoBack,
  canContinue,
  canActivate = true,
  canPreview,
  isReview,
  submitting,
  interactionsDisabled,
  footerPrimaryLabel = "Continue",
  footerSecondaryLabel = "Preview",
  onBack,
  onContinue,
  onPreview,
  onActivate,
  onRetrySave,
}: Props) {
  const { colors } = useThemeTokens();

  return (
    <footer
      className="sticky bottom-0 z-10 shrink-0 border-t px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3 backdrop-blur"
      style={{
        borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
        background: `color-mix(in srgb, ${colors.background} 94%, transparent)`,
      }}
      data-guided-setup-footer
    >
      <div className="mx-auto flex w-full max-w-[1200px] flex-wrap items-center gap-2">
        {canGoBack && onBack ? (
          <button
            type="button"
            onClick={onBack}
            disabled={interactionsDisabled}
            className="min-h-11 rounded-xl border px-4 py-2.5 text-sm font-semibold disabled:opacity-50"
            style={{ borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)` }}
          >
            Back
          </button>
        ) : null}

        <div className="min-w-0 flex-1 px-1">
          <GuidedSetupSaveIndicator saveState={saveState} onRetrySave={onRetrySave} />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {canPreview && onPreview ? (
            <button
              type="button"
              onClick={onPreview}
              disabled={interactionsDisabled}
              className="min-h-11 rounded-xl px-4 py-2.5 text-sm font-semibold disabled:opacity-50"
              style={{ background: colors.surfaceContainer }}
            >
              {footerSecondaryLabel}
            </button>
          ) : null}
          {isReview && onActivate ? (
            <button
              type="button"
              disabled={!canActivate || submitting || interactionsDisabled}
              onClick={onActivate}
              className="min-h-11 rounded-xl px-5 py-2.5 text-sm font-semibold disabled:opacity-50"
              style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
            >
              {submitting ? "Activating…" : footerPrimaryLabel}
            </button>
          ) : canContinue && onContinue ? (
            <button
              type="button"
              onClick={onContinue}
              disabled={interactionsDisabled}
              className="min-h-11 rounded-xl px-5 py-2.5 text-sm font-semibold disabled:opacity-50"
              style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
            >
              {footerPrimaryLabel}
            </button>
          ) : null}
        </div>
      </div>
    </footer>
  );
}

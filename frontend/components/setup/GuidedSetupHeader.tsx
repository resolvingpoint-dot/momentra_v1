"use client";

import { List, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type Props = {
  title: string;
  subtitle?: string;
  currentStep: number;
  totalSteps: number;
  estimatedDuration?: number;
  /** Hide "Step N of M" for single-scroll personal setup. */
  hideStepProgress?: boolean;
  showSummaryButton?: boolean;
  onOpenSummary?: () => void;
  onClose: () => void;
};

export function GuidedSetupHeader({
  title,
  subtitle,
  currentStep,
  totalSteps,
  estimatedDuration,
  hideStepProgress = false,
  showSummaryButton,
  onOpenSummary,
  onClose,
}: Props) {
  const { colors } = useThemeTokens();

  return (
    <header
      className="sticky top-0 z-10 flex shrink-0 items-center justify-between gap-3 border-b px-4 py-3 backdrop-blur"
      style={{
        borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
        background: `color-mix(in srgb, ${colors.background} 92%, transparent)`,
      }}
    >
      <div className="min-w-0">
        {hideStepProgress ? (
          estimatedDuration ? (
            <p className="text-[10px] font-bold tracking-widest opacity-60" aria-live="polite">
              About {estimatedDuration} minutes
            </p>
          ) : null
        ) : (
          <p className="text-[10px] font-bold tracking-widest opacity-60" aria-live="polite">
            Step {currentStep} of {totalSteps}
            {estimatedDuration ? ` · About ${estimatedDuration} minutes` : ""}
          </p>
        )}
        <h2 className="truncate text-lg font-semibold">{title}</h2>
        {subtitle ? (
          <p className="truncate text-xs opacity-60" style={{ color: colors.textSecondary }}>
            {subtitle}
          </p>
        ) : null}
      </div>
      <div className="flex items-center gap-1">
        {showSummaryButton ? (
          <button
            type="button"
            className="flex size-11 items-center justify-center rounded-full lg:hidden"
            style={{ background: colors.surfaceContainer }}
            aria-label="Open summary"
            onClick={onOpenSummary}
          >
            <List className="size-5" />
          </button>
        ) : null}
        <button
          type="button"
          onClick={onClose}
          aria-label="Close setup"
          className="flex size-11 items-center justify-center rounded-full"
          style={{ background: colors.surfaceContainer }}
        >
          <X className="size-5" />
        </button>
      </div>
    </header>
  );
}

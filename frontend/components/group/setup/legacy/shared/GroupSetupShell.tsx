"use client";

/**
 * @deprecated Legacy Group create-wizard chrome.
 * Production setup reopen uses GuidedSetupShell via SharedExperienceSetup /
 * SharedPurchaseSetup / SharedLivingSetup. This legacy shell remains for quarantined wizards.
 * Do not wire new home/setup routes to this shell.
 * See docs/platform/GUIDED_SETUP_PARITY.md
 */
import { ArrowLeft, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type GroupSetupShellProps = {
  step: number;
  totalSteps: number;
  title: string;
  subtitle?: string;
  onBack?: () => void;
  onClose: () => void;
  children: React.ReactNode;
};

export function GroupSetupShell({
  step,
  totalSteps,
  title,
  subtitle,
  onBack,
  onClose,
  children,
}: GroupSetupShellProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col overflow-y-auto"
      style={{ background: colors.background, color: colors.textPrimary }}
    >
      {/* Header */}
      <div className="relative flex items-center justify-between px-5 py-4">
        <button
          type="button"
          onClick={onBack}
          disabled={!onBack}
          className="flex size-10 items-center justify-center rounded-full disabled:opacity-30"
          style={{ background: `${colors.background}E6` }}
        >
          <ArrowLeft className="size-5" />
        </button>
        
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
          <h2 className="text-lg font-semibold">{title}</h2>
          {subtitle && (
            <p className="text-xs opacity-70" style={{ color: colors.textSecondary }}>
              {subtitle}
            </p>
          )}
        </div>
        
        <button
          type="button"
          onClick={onClose}
          className="flex size-10 items-center justify-center rounded-full"
          style={{ background: `${colors.background}E6` }}
        >
          <X className="size-5" />
        </button>
      </div>
      
      {/* Progress bar */}
      <div className="px-5 pb-4">
        <div className="flex items-center justify-between text-xs" style={{ color: colors.textSecondary }}>
          <span>Step {step} of {totalSteps}</span>
          <span>{Math.round((step / totalSteps) * 100)}% complete</span>
        </div>
        <div className="mt-2 h-2 rounded-full" style={{ background: colors.surfaceContainer }}>
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{
              width: `${(step / totalSteps) * 100}%`,
              background: colors.primaryContainer,
            }}
          />
        </div>
      </div>
      
      {/* Content */}
      <div className="flex-1 px-5 pb-8">
        {children}
      </div>
    </div>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";

type GroupSetupStepIndicatorProps = {
  currentStep: number;
  totalSteps: number;
};

export function GroupSetupStepIndicator({ currentStep, totalSteps }: GroupSetupStepIndicatorProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div className="flex items-center justify-center gap-2">
      {Array.from({ length: totalSteps }).map((_, index) => {
        const step = index + 1;
        const isCompleted = step < currentStep;
        const isCurrent = step === currentStep;
        
        return (
          <div key={step} className="flex items-center">
            <div
              className="flex size-8 items-center justify-center rounded-full text-sm font-semibold"
              style={{
                background: isCompleted || isCurrent ? colors.primaryContainer : colors.surfaceContainer,
                color: isCompleted || isCurrent ? colors.brandOnPrimary : colors.textSecondary,
              }}
            >
              {isCompleted ? "✓" : step}
            </div>
            {step < totalSteps && (
              <div
                className="h-0.5 w-4"
                style={{
                  background: step < currentStep ? colors.primaryContainer : colors.surfaceContainer,
                }}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

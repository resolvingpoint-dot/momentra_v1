"use client";

import type { ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { GuidedSetupStep } from "@/components/setup/guidedSetupTypes";
import { GuidedSetupTip } from "@/components/setup/GuidedSetupTip";

type Props = {
  activeStep?: GuidedSetupStep | null;
  tip?: string | null;
  children: ReactNode;
};

export function GuidedSetupContent({ activeStep, tip, children }: Props) {
  const { colors } = useThemeTokens();

  return (
    <div className="min-w-0" data-guided-setup-content>
      {activeStep ? (
        <div className="mb-4 space-y-1.5">
          <h3 className="text-lg font-semibold" id="guided-setup-step-title">
            {activeStep.title}
          </h3>
          {activeStep.description ? (
            <p className="text-sm leading-snug opacity-75" style={{ color: colors.textSecondary }}>
              {activeStep.description}
            </p>
          ) : null}
          {tip ? <GuidedSetupTip tip={tip} /> : null}
        </div>
      ) : null}
      {children}
    </div>
  );
}

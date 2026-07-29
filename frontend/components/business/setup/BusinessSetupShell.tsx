"use client";

import type { ReactNode } from "react";
import {
  GuidedSetupShell,
  type GuidedSetupSaveState,
  type GuidedSetupStep,
  type GuidedSetupSummaryRow,
} from "@/components/setup/GuidedSetupShell";
import type { GuidedSetupSummary } from "@/components/setup/guidedSetupSummary";
import type { GuidedSetupAnalyticsHandler } from "@/components/setup/guidedSetupAnalytics";
import { SETUP_ESTIMATED_MINUTES } from "@/lib/business/setupCatalog";

type BusinessSetupShellProps = {
  contextType?: "business";
  templateId?: string;
  momentTypeCode?: string;
  momentId?: string;
  title: string;
  /** @deprecated Prefer step description from GuidedSetupShell steps. */
  subtitle?: string;
  /** @deprecated Prefer catalog steps. */
  stepTitle?: string;
  /** @deprecated Prefer catalog steps. */
  stepIntro?: string;
  /** @deprecated Prefer GuidedSetupShell step nav. */
  stepLabel?: string;
  currentStep?: number;
  totalSteps?: number;
  steps?: GuidedSetupStep[];
  estimatedMinutes?: number;
  saveStatus?: GuidedSetupSaveState | "idle" | "saving" | "saved" | "error";
  liveSummary?: GuidedSetupSummary | GuidedSetupSummaryRow[];
  contextHelp?: string | null;
  tip?: string | null;
  onRetrySave?: () => void;
  error?: string | null;
  submitting?: boolean;
  canActivate?: boolean;
  interactionsDisabled?: boolean;
  activationSuccess?: boolean;
  activationSuccessMessage?: string;
  activateLabel?: string;
  continueLabel?: string;
  onActivationSuccessDone?: () => void;
  onClose: () => void;
  onBack?: () => void;
  onNext?: () => void;
  onPreview?: () => void;
  onActivate?: () => void;
  onAnalytics?: GuidedSetupAnalyticsHandler;
  children: ReactNode;
};

function fallbackSteps(total: number, currentTitle?: string, currentIntro?: string): GuidedSetupStep[] {
  return Array.from({ length: total }, (_, i) => {
    const n = i + 1;
    const isCurrent = Boolean(currentTitle) && n === 1;
    return {
      id: `step-${n}`,
      title: isCurrent && currentTitle ? currentTitle : `Step ${n}`,
      shortTitle: `Step ${n}`,
      description: isCurrent && currentIntro ? currentIntro : "",
    };
  });
}

/**
 * Business adapter over GuidedSetupShell.
 * Loads flow/answers/save state in parent templates; this shell only maps props.
 */
export function BusinessSetupShell({
  contextType = "business",
  templateId,
  momentTypeCode,
  momentId,
  title,
  subtitle,
  stepTitle,
  stepIntro,
  currentStep = 1,
  totalSteps = 4,
  steps,
  estimatedMinutes = SETUP_ESTIMATED_MINUTES,
  saveStatus = "idle",
  liveSummary = [],
  contextHelp,
  tip,
  onRetrySave,
  error,
  submitting = false,
  canActivate = true,
  interactionsDisabled = false,
  activationSuccess = false,
  activationSuccessMessage = "Moment activated",
  activateLabel = "Activate",
  continueLabel = "Continue",
  onActivationSuccessDone,
  onClose,
  onBack,
  onNext,
  onPreview,
  onActivate,
  onAnalytics,
  children,
}: BusinessSetupShellProps) {
  const guidedSteps =
    steps && steps.length > 0
      ? steps
      : fallbackSteps(totalSteps, stepTitle, stepIntro ?? subtitle).map((s, i) =>
          i + 1 === currentStep
            ? {
                ...s,
                title: stepTitle ?? s.title,
                description: stepIntro ?? subtitle ?? s.description,
              }
            : s,
        );

  const normalizedSave: GuidedSetupSaveState =
    saveStatus === "dirty" ||
    saveStatus === "saving" ||
    saveStatus === "saved" ||
    saveStatus === "error" ||
    saveStatus === "idle"
      ? saveStatus
      : "idle";

  const isReview = currentStep >= guidedSteps.length;

  return (
    <GuidedSetupShell
      contextType={contextType}
      templateId={templateId}
      momentTypeCode={momentTypeCode}
      momentId={momentId}
      title={title}
      estimatedDuration={estimatedMinutes}
      currentStep={currentStep}
      steps={guidedSteps}
      saveState={normalizedSave}
      canGoBack={Boolean(onBack)}
      canContinue={Boolean(onNext) && !isReview}
      canPreview={Boolean(onPreview) && isReview}
      liveSummary={liveSummary}
      contextHelp={contextHelp ?? stepIntro ?? subtitle}
      tip={tip}
      footerPrimaryLabel={isReview ? activateLabel : continueLabel}
      error={error}
      submitting={submitting}
      canActivate={canActivate}
      interactionsDisabled={interactionsDisabled}
      activationSuccess={activationSuccess}
      activationSuccessMessage={activationSuccessMessage}
      onActivationSuccessDone={onActivationSuccessDone}
      onBack={onBack}
      onContinue={onNext}
      onClose={onClose}
      onRetrySave={onRetrySave}
      onPreview={onPreview}
      onActivate={isReview ? onActivate : undefined}
      onAnalytics={onAnalytics}
    >
      {children}
    </GuidedSetupShell>
  );
}

"use client";

import { useEffect, useId, useRef, useState } from "react";
import { Check, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GuidedSetupContent } from "@/components/setup/GuidedSetupContent";
import { GuidedSetupFooter } from "@/components/setup/GuidedSetupFooter";
import { GuidedSetupHeader } from "@/components/setup/GuidedSetupHeader";
import { GuidedSetupLiveSummary } from "@/components/setup/GuidedSetupLiveSummary";
import { GuidedSetupStepNav } from "@/components/setup/GuidedSetupStepNav";
import { GuidedSetupThemeProvider } from "@/components/setup/GuidedSetupTheme";
import { normalizeLiveSummary } from "@/components/setup/guidedSetupSummary";
import type { GuidedSetupShellProps } from "@/components/setup/guidedSetupTypes";

export type {
  GuidedSetupContextType,
  GuidedSetupLayout,
  GuidedSetupSaveState,
  GuidedSetupShellProps,
  GuidedSetupStep,
  GuidedSetupStepVisualState,
  GuidedSetupSummaryRow,
} from "@/components/setup/guidedSetupTypes";

export type { GuidedSetupSummary, GuidedSetupSummaryItem } from "@/components/setup/guidedSetupSummary";
export type { GuidedSetupAnalyticsEvent } from "@/components/setup/guidedSetupAnalytics";

/**
 * Shared guided setup presentation shell.
 * Owns layout, theme, summary chrome, and generic analytics hooks only —
 * no Business / Group / Personal field keys or template labels.
 */
export function GuidedSetupShell({
  contextType = "business",
  templateId,
  momentTypeCode,
  momentId,
  title,
  subtitle,
  estimatedDuration,
  layout = "guided",
  currentStep,
  steps,
  saveState = "idle",
  canGoBack = false,
  canContinue = false,
  canPreview = false,
  liveSummary,
  contextHelp,
  tip,
  footerPrimaryLabel = "Continue",
  footerSecondaryLabel = "Preview",
  error,
  submitting = false,
  canActivate = true,
  interactionsDisabled = false,
  activationSuccess = false,
  activationSuccessMessage = "Moment activated",
  activationSuccessSubtitle = "Your moment is live on Pulse.",
  onActivationSuccessDone,
  onBack,
  onContinue,
  onClose,
  onRetrySave,
  onOpenSummary,
  onPreview,
  onActivate,
  onAnalytics,
  children,
}: GuidedSetupShellProps) {
  const { colors } = useThemeTokens();
  const [summaryOpen, setSummaryOpen] = useState(false);
  const summaryCloseRef = useRef<HTMLButtonElement>(null);
  const summaryTitleId = useId();
  const singleScroll = layout === "singleScroll";
  const totalSteps = Math.max(1, steps.length);
  const active = steps[Math.min(currentStep, totalSteps) - 1];
  const isReview = singleScroll || currentStep >= totalSteps;
  const summaryRows = normalizeLiveSummary(liveSummary);
  const openedAtRef = useRef(
    typeof performance !== "undefined" ? performance.now() : Date.now(),
  );

  const elapsedMs = () =>
    Math.round(
      (typeof performance !== "undefined" ? performance.now() : Date.now()) -
        openedAtRef.current,
    );

  useEffect(() => {
    onAnalytics?.({
      type: "setup_open",
      contextType,
      templateId,
      momentTypeCode,
      momentId,
      elapsedMs: 0,
    });
    // Fire once per mount for this setup session.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional mount-only
  }, []);

  useEffect(() => {
    if (!active) return;
    onAnalytics?.({
      type: "step_changed",
      stepId: active.id,
      stepIndex: currentStep,
      templateId,
      contextType,
      saveState,
      elapsedMs: elapsedMs(),
    });
  }, [active, currentStep, onAnalytics, templateId, contextType, saveState]);

  useEffect(() => {
    if (!isReview) return;
    onAnalytics?.({
      type: "review_opened",
      templateId,
      contextType,
      elapsedMs: elapsedMs(),
    });
  }, [isReview, onAnalytics, templateId, contextType]);

  useEffect(() => {
    if (saveState === "saving") {
      onAnalytics?.({
        type: "autosave_started",
        templateId,
        contextType,
        stepId: active?.id,
        saveState,
      });
    } else if (saveState === "saved") {
      onAnalytics?.({
        type: "autosave_completed",
        templateId,
        contextType,
        stepId: active?.id,
        elapsedMs: elapsedMs(),
      });
    } else if (saveState === "error") {
      onAnalytics?.({
        type: "autosave_failed",
        templateId,
        contextType,
        stepId: active?.id,
      });
    }
  }, [saveState, onAnalytics, templateId, contextType, active?.id]);

  useEffect(() => {
    if (!activationSuccess || !onActivationSuccessDone) return;
    onAnalytics?.({
      type: "activation_completed",
      templateId,
      momentId,
      contextType,
      elapsedMs: elapsedMs(),
    });
    const timer = window.setTimeout(() => onActivationSuccessDone(), 1200);
    return () => window.clearTimeout(timer);
  }, [
    activationSuccess,
    onActivationSuccessDone,
    onAnalytics,
    templateId,
    momentId,
    contextType,
  ]);

  useEffect(() => {
    if (!summaryOpen) return;
    summaryCloseRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSummaryOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [summaryOpen]);

  const openSummary = () => {
    onOpenSummary?.();
    setSummaryOpen(true);
  };

  const handleActivate = () => {
    onAnalytics?.({
      type: "activation_started",
      templateId,
      momentId,
      contextType,
    });
    onActivate?.();
  };

  const summaryPanel = (
    <GuidedSetupLiveSummary
      rows={summaryRows}
      contextHelp={contextHelp}
      estimatedDuration={estimatedDuration}
      currentStepTitle={active?.shortTitle ?? active?.title}
    />
  );

  return (
    <GuidedSetupThemeProvider contextType={contextType}>
      <div
        className="fixed inset-0 z-50 flex flex-col motion-safe:animate-in motion-safe:fade-in motion-reduce:animate-none"
        style={{ background: colors.background, color: colors.textPrimary }}
        data-guided-setup-shell
        data-guided-setup-context={contextType}
        data-guided-setup-template={templateId ?? ""}
      >
        {activationSuccess ? (
          <div
            className="absolute inset-0 z-30 flex items-center justify-center"
            style={{ background: `color-mix(in srgb, ${colors.background} 88%, transparent)` }}
            role="status"
            aria-live="polite"
          >
            <div
              className="mx-6 flex max-w-sm flex-col items-center gap-3 rounded-2xl px-8 py-7 text-center shadow-lg"
              style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
            >
              <span
                className="flex size-12 items-center justify-center rounded-full"
                style={{ background: "color-mix(in srgb, white 22%, transparent)" }}
              >
                <Check className="size-6" strokeWidth={2.5} aria-hidden />
              </span>
              <p className="text-lg font-bold">{activationSuccessMessage}</p>
              {activationSuccessSubtitle ? (
                <p className="text-sm opacity-90">{activationSuccessSubtitle}</p>
              ) : null}
            </div>
          </div>
        ) : null}

        <GuidedSetupHeader
          title={title}
          subtitle={subtitle}
          currentStep={currentStep}
          totalSteps={totalSteps}
          estimatedDuration={estimatedDuration}
          hideStepProgress={singleScroll}
          showSummaryButton={summaryRows.length > 0 || Boolean(contextHelp) || Boolean(tip)}
          onOpenSummary={openSummary}
          onClose={onClose}
        />

        {error ? (
          <div
            className="mx-4 mt-3 shrink-0 rounded-xl px-3 py-2 text-sm"
            style={{ background: "rgba(239,68,68,0.12)", color: colors.error }}
            role="alert"
          >
            {error}
          </div>
        ) : null}

        {singleScroll ? null : (
          <GuidedSetupStepNav steps={steps} currentStep={currentStep} orientation="horizontal" />
        )}

        <div className="min-h-0 flex-1 overflow-y-auto">
          <div
            className={
              singleScroll
                ? "mx-auto grid w-full max-w-[1200px] gap-4 px-4 pb-28 pt-4 lg:grid-cols-[minmax(0,1fr)_260px]"
                : "mx-auto grid w-full max-w-[1200px] gap-4 px-4 pb-28 pt-4 lg:grid-cols-[180px_minmax(0,1fr)_240px]"
            }
          >
            {singleScroll ? null : (
              <GuidedSetupStepNav steps={steps} currentStep={currentStep} orientation="vertical" />
            )}
            <GuidedSetupContent activeStep={active} tip={tip}>
              {children}
            </GuidedSetupContent>
            <div className="hidden lg:block">{summaryPanel}</div>
          </div>
        </div>

        {summaryOpen ? (
          <div
            className="absolute inset-0 z-20 flex flex-col justify-end bg-black/40 lg:hidden"
            role="dialog"
            aria-modal="true"
            aria-labelledby={summaryTitleId}
            onClick={() => setSummaryOpen(false)}
          >
            <div
              className="max-h-[70vh] overflow-y-auto rounded-t-2xl p-4 pb-[max(1rem,env(safe-area-inset-bottom))]"
              style={{ background: colors.background }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mb-3 flex items-center justify-between">
                <p id={summaryTitleId} className="text-sm font-semibold">
                  Summary
                </p>
                <button
                  ref={summaryCloseRef}
                  type="button"
                  className="flex size-11 items-center justify-center"
                  aria-label="Close summary"
                  onClick={() => setSummaryOpen(false)}
                >
                  <X className="size-5" aria-hidden />
                </button>
              </div>
              {summaryPanel}
            </div>
          </div>
        ) : null}

        <GuidedSetupFooter
          saveState={saveState}
          canGoBack={canGoBack}
          canContinue={canContinue}
          canActivate={canActivate}
          canPreview={canPreview}
          isReview={isReview}
          submitting={submitting}
          interactionsDisabled={interactionsDisabled}
          footerPrimaryLabel={footerPrimaryLabel}
          footerSecondaryLabel={footerSecondaryLabel}
          onBack={onBack}
          onContinue={onContinue}
          onPreview={onPreview}
          onActivate={onActivate ? handleActivate : undefined}
          onRetrySave={onRetrySave}
        />
      </div>
    </GuidedSetupThemeProvider>
  );
}

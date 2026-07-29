import type { ReactNode } from "react";
import type { GuidedSetupSummary } from "@/components/setup/guidedSetupSummary";
import type { GuidedSetupAnalyticsHandler } from "@/components/setup/guidedSetupAnalytics";

export type GuidedSetupContextType = "personal" | "group" | "business";

export type GuidedSetupStep = {
  id: string;
  title: string;
  shortTitle: string;
  description: string;
  optional?: boolean;
  hiddenWhen?: string | null;
};

export type GuidedSetupSaveState = "idle" | "dirty" | "saving" | "saved" | "error";

export type GuidedSetupStepVisualState =
  | "incomplete"
  | "current"
  | "complete"
  | "warning"
  | "blocked";

export type GuidedSetupSummaryRow = {
  label: string;
  value: string;
};

export type GuidedSetupLayout = "guided" | "singleScroll";

export type GuidedSetupShellProps = {
  contextType?: GuidedSetupContextType;
  templateId?: string;
  momentTypeCode?: string;
  momentId?: string;
  title: string;
  subtitle?: string;
  estimatedDuration?: number;
  /** `singleScroll` hides step nav / "Step N of M" (Personal screen-spec layout). */
  layout?: GuidedSetupLayout;
  steps: GuidedSetupStep[];
  currentStep: number;
  saveState?: GuidedSetupSaveState;
  /** Structured summary or legacy label/value rows */
  liveSummary?: GuidedSetupSummary | GuidedSetupSummaryRow[];
  contextHelp?: string | null;
  tip?: string | null;
  canGoBack?: boolean;
  canContinue?: boolean;
  canActivate?: boolean;
  canPreview?: boolean;
  footerPrimaryLabel?: string;
  footerSecondaryLabel?: string;
  error?: string | null;
  submitting?: boolean;
  interactionsDisabled?: boolean;
  activationSuccess?: boolean;
  activationSuccessMessage?: string;
  /** Secondary line under activation success (defaults to generic copy). */
  activationSuccessSubtitle?: string;
  onActivationSuccessDone?: () => void;
  onBack?: () => void;
  onContinue?: () => void;
  onClose: () => void;
  onRetrySave?: () => void;
  onOpenSummary?: () => void;
  onPreview?: () => void;
  onActivate?: () => void;
  /** Generic setup funnel events — no Business-specific names. */
  onAnalytics?: GuidedSetupAnalyticsHandler;
  children: ReactNode;
};

export function stepVisualState(
  index: number,
  currentStep: number,
  warningSteps?: number[],
  blockedSteps?: number[],
): GuidedSetupStepVisualState {
  const n = index + 1;
  if (blockedSteps?.includes(n)) return "blocked";
  if (warningSteps?.includes(n)) return "warning";
  if (n === currentStep) return "current";
  if (n < currentStep) return "complete";
  return "incomplete";
}

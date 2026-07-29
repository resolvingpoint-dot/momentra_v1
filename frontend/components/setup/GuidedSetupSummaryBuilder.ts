import type { GuidedSetupSummary } from "@/components/setup/guidedSetupSummary";

/**
 * Context-owned summary builders map local draft answers → GuidedSetupSummary.
 * The shell never branches on Business / Group / Personal.
 */
export type GuidedSetupSummaryBuilderInput<TAnswers = Record<string, unknown>> = {
  answers: TAnswers;
  currentStep: number;
  totalSteps: number;
  estimatedMinutes: number;
  memberCount?: number;
  /** Presentation catalog slice — opaque to the shell */
  catalog?: unknown;
};

export interface GuidedSetupSummaryBuilder<TAnswers = Record<string, unknown>> {
  build(input: GuidedSetupSummaryBuilderInput<TAnswers>): GuidedSetupSummary;
}

import type { GuidedSetupSummary } from "@/components/setup/guidedSetupSummary";
import type {
  GuidedSetupSummaryBuilder,
  GuidedSetupSummaryBuilderInput,
} from "@/components/setup/GuidedSetupSummaryBuilder";
import {
  choiceLabel,
  type SetupTemplateId,
} from "@/lib/business/setupCatalog";
import { guidedSummaryToRows } from "@/components/setup/guidedSetupSummary";
import type { GuidedSetupSummaryRow } from "@/components/setup/guidedSetupTypes";

export type BusinessSummaryAnswers = Record<string, unknown> & {
  templateId: SetupTemplateId;
};

function formatBudget(amountMinor: unknown, currency: string): string {
  if (amountMinor == null || amountMinor === "") return "";
  const n = typeof amountMinor === "number" ? amountMinor : Number(amountMinor);
  if (!Number.isFinite(n)) return "";
  const major = n / 100;
  return `${currency} ${major.toLocaleString(undefined, {
    maximumFractionDigits: 0,
  })}`;
}

function templateTypeLabel(id: SetupTemplateId): string {
  switch (id) {
    case "team_ops":
      return "Team Operations";
    case "business_runway":
      return "Business Runway";
    case "business_operations":
      return "Business Operations";
  }
}

export class BusinessSummaryBuilder
  implements GuidedSetupSummaryBuilder<BusinessSummaryAnswers>
{
  build(input: GuidedSetupSummaryBuilderInput<BusinessSummaryAnswers>): GuidedSetupSummary {
    const { answers, currentStep, totalSteps, estimatedMinutes, memberCount = 0 } = input;
    const templateId = answers.templateId;
    const currency = String(
      answers.operating_currency_code ?? answers.default_currency_code ?? "",
    );
    const budget =
      formatBudget(answers.monthly_team_budget_minor, currency) ||
      formatBudget(answers.monthly_budget_minor, currency) ||
      formatBudget(answers.monthly_burn_minor, currency);

    const completed = Math.max(0, currentStep - 1);
    const progress = Math.round((completed / Math.max(1, totalSteps)) * 100);

    const extras: GuidedSetupSummary["extras"] = [];
    if (templateId === "team_ops") {
      const size = choiceLabel("team_size", String(answers.team_size ?? ""));
      if (size) extras.push({ label: "Team size", value: size });
    }
    if (templateId === "business_runway") {
      const stage = choiceLabel("business_stage", String(answers.business_stage ?? ""));
      if (stage) extras.push({ label: "Stage", value: stage });
    }
    if (templateId === "business_operations") {
      const scope = choiceLabel(
        "operations_scope",
        String(answers.operations_scope ?? ""),
      );
      if (scope) extras.push({ label: "Scope", value: scope });
    }

    return {
      primaryType: templateTypeLabel(templateId),
      title: "",
      members: memberCount,
      currency: currency || undefined,
      budget: budget || undefined,
      progress,
      estimatedMinutes,
      currentStepLabel: `${currentStep} of ${totalSteps}`,
      extras,
    };
  }
}

export const businessSummaryBuilder = new BusinessSummaryBuilder();

/** @deprecated Prefer BusinessSummaryBuilder / buildBusinessLiveSummaryModel */
export function buildBusinessLiveSummaryModel(args: {
  templateId: SetupTemplateId;
  answers: Record<string, unknown>;
  currentStep: number;
  totalSteps: number;
  estimatedMinutes: number;
  memberCount: number;
}): GuidedSetupSummary {
  return businessSummaryBuilder.build({
    answers: { ...args.answers, templateId: args.templateId },
    currentStep: args.currentStep,
    totalSteps: args.totalSteps,
    estimatedMinutes: args.estimatedMinutes,
    memberCount: args.memberCount,
  });
}

export function buildBusinessLiveSummary(args: {
  templateId: SetupTemplateId;
  answers: Record<string, unknown>;
  currentStep: number;
  totalSteps: number;
  estimatedMinutes: number;
  memberCount: number;
}): GuidedSetupSummaryRow[] {
  return guidedSummaryToRows(buildBusinessLiveSummaryModel(args));
}

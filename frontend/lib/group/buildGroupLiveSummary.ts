import type { GuidedSetupSummary } from "@/components/setup/guidedSetupSummary";
import type {
  GuidedSetupSummaryBuilder,
  GuidedSetupSummaryBuilderInput,
} from "@/components/setup/GuidedSetupSummaryBuilder";
import {
  groupChoiceLabel,
  type GroupSetupTemplateId,
} from "@/lib/group/setupCatalog";
import { guidedSummaryToRows } from "@/components/setup/guidedSetupSummary";
import type { GuidedSetupSummaryRow } from "@/components/setup/guidedSetupTypes";

export type GroupSummaryAnswers = Record<string, unknown> & {
  templateId: GroupSetupTemplateId;
};

function answerString(answers: Record<string, unknown>, ...keys: string[]): string {
  for (const key of keys) {
    const value = answers[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return "";
}

function formatBudget(amount: unknown, currency: string): string {
  if (amount == null || amount === "") return "";
  const n = typeof amount === "number" ? amount : Number(amount);
  if (!Number.isFinite(n)) return "";
  // Group purchase/experience amounts are stored as major units (target_amount_major).
  return `${currency} ${n.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function templateTypeLabel(id: GroupSetupTemplateId): string {
  switch (id) {
    case "shared_experience":
      return "Shared Experience";
    case "shared_purchase":
      return "Shared Purchase";
    case "shared_living":
      return "Shared Living";
  }
}

export class GroupSummaryBuilder
  implements GuidedSetupSummaryBuilder<GroupSummaryAnswers>
{
  build(input: GuidedSetupSummaryBuilderInput<GroupSummaryAnswers>): GuidedSetupSummary {
    const { answers, currentStep, totalSteps, estimatedMinutes, memberCount = 0 } =
      input;
    const templateId = answers.templateId;
    const title = answerString(
      answers,
      "moment_name",
      "experience_name",
      "trip_name",
      "purchase_name",
      "home_name",
      "living_name",
    );
    const currency = answerString(
      answers,
      "budget_currency",
      "currency_code",
      "operating_currency_code",
    );
    const budget =
      formatBudget(answers.estimated_budget, currency) ||
      formatBudget(answers.expected_amount, currency) ||
      formatBudget(answers.target_amount_major, currency) ||
      formatBudget(answers.monthly_budget, currency) ||
      formatBudget(answers.monthly_budget_major, currency) ||
      formatBudget(answers.budget_minor, currency) ||
      formatBudget(answers.monthly_budget_minor, currency) ||
      formatBudget(answers.target_amount_minor, currency);

    const completed = Math.max(0, currentStep - 1);
    const progress = Math.round((completed / Math.max(1, totalSteps)) * 100);

    const extras: GuidedSetupSummary["extras"] = [];
    if (templateId === "shared_experience") {
      const kind = groupChoiceLabel(
        "experience_type",
        answerString(answers, "experience_type", "experience_profile", "trip_style"),
      );
      if (kind) extras.push({ label: "Experience", value: kind });
      const destination = answerString(answers, "destination");
      if (destination) extras.push({ label: "Destination", value: destination });
      const split = groupChoiceLabel(
        "split_style",
        answerString(answers, "split_style", "split_method"),
      );
      if (split) extras.push({ label: "Money", value: split });
    }
    if (templateId === "shared_purchase") {
      const profile = groupChoiceLabel(
        "purchase_profile",
        answerString(answers, "purchase_profile"),
      );
      if (profile) extras.push({ label: "Purchase", value: profile });
      const deadline = answerString(answers, "decision_deadline", "target_date");
      if (deadline) extras.push({ label: "Target date", value: deadline });
      const contribution = groupChoiceLabel(
        "payment_plan",
        answerString(answers, "payment_plan", "funding_style"),
      );
      if (contribution) extras.push({ label: "Contribution", value: contribution });
      const ownership = groupChoiceLabel(
        "ownership_style",
        answerString(answers, "ownership_style"),
      );
      if (ownership) extras.push({ label: "Ownership", value: ownership });
    }
    if (templateId === "shared_living") {
      const living = groupChoiceLabel(
        "living_type",
        answerString(answers, "living_type", "living_profile"),
      );
      if (living) extras.push({ label: "Living type", value: living });
      const rentSplit = groupChoiceLabel(
        "rent_split_style",
        answerString(answers, "rent_split_style", "management"),
      );
      if (rentSplit) extras.push({ label: "Cost split", value: rentSplit });
      const chores = groupChoiceLabel(
        "chores_style",
        answerString(answers, "chores_style"),
      );
      if (chores) extras.push({ label: "Chores", value: chores });
    }

    return {
      primaryType: templateTypeLabel(templateId),
      title,
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

export const groupSummaryBuilder = new GroupSummaryBuilder();

export function buildGroupLiveSummaryModel(args: {
  templateId: GroupSetupTemplateId;
  answers: Record<string, unknown>;
  currentStep: number;
  totalSteps: number;
  estimatedMinutes: number;
  memberCount?: number;
}): GuidedSetupSummary {
  return groupSummaryBuilder.build({
    answers: { ...args.answers, templateId: args.templateId },
    currentStep: args.currentStep,
    totalSteps: args.totalSteps,
    estimatedMinutes: args.estimatedMinutes,
    memberCount: args.memberCount ?? 0,
  });
}

export function buildGroupLiveSummary(args: {
  templateId: GroupSetupTemplateId;
  answers: Record<string, unknown>;
  currentStep: number;
  totalSteps: number;
  estimatedMinutes: number;
  memberCount?: number;
}): GuidedSetupSummaryRow[] {
  return guidedSummaryToRows(buildGroupLiveSummaryModel(args));
}

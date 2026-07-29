/**
 * Personal setup presentation catalog (copy only — not validation).
 */
import copyJson from "@/lib/personal/personal_setup_copy.json";
import type { GuidedSetupStep } from "@/components/setup/GuidedSetupShell";

export type PersonalSetupTemplateId =
  | "life_operations"
  | "future_building"
  | "lifestyle"
  | "relationships";

export const PERSONAL_SETUP_COPY = copyJson;

export function personalTemplateForMomentType(
  momentTypeCode: string | null | undefined,
): PersonalSetupTemplateId {
  const code = (momentTypeCode ?? "").toUpperCase();
  if (code === "FUTURE_BUILDING") return "future_building";
  if (code === "LIFESTYLE") return "lifestyle";
  if (code === "RELATIONSHIPS" || code === "EMOTIONAL_SECURITY") return "relationships";
  return "life_operations";
}

export function personalSetupTemplate(id: PersonalSetupTemplateId) {
  return PERSONAL_SETUP_COPY.templates[id];
}

/** Evaluate simple `answers.key === value` / truthy checks for hiddenWhen. */
export function evaluateHiddenWhen(
  expression: string | undefined,
  answers: Record<string, unknown>,
): boolean {
  if (!expression?.trim()) return false;
  const eq = expression.match(/^answers\.([a-zA-Z0-9_]+)\s*===\s*(true|false|"[^"]*"|'[^']*')$/);
  if (eq) {
    const key = eq[1];
    const raw = eq[2];
    const expected =
      raw === "true" ? true : raw === "false" ? false : raw.slice(1, -1);
    return answers[key] === expected;
  }
  const truthy = expression.match(/^answers\.([a-zA-Z0-9_]+)$/);
  if (truthy) return Boolean(answers[truthy[1]]);
  return false;
}

export function personalGuidedSteps(
  id: PersonalSetupTemplateId,
  answers: Record<string, unknown> = {},
): GuidedSetupStep[] {
  return personalSetupTemplate(id)
    .steps.filter((s) => !evaluateHiddenWhen(s.hiddenWhen, answers))
    .map((s) => ({
      id: s.id,
      title: s.title,
      shortTitle: s.shortTitle,
      description: s.description,
      optional: s.optional,
      hiddenWhen: s.hiddenWhen,
    }));
}

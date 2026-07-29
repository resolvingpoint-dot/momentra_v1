import type { PersonalSetupAnswers, PersonalSetupResponse } from "@/lib/api/personal";
import { getTemplate, getTemplateByMomentType } from "./registry";
import {
  LEGACY_FIELD_ALIASES,
  TEMPLATE_META_KEYS,
  templateSectionToSetupField,
  type MomentSetupTemplate,
} from "./types";

function isStubSetup(response: PersonalSetupResponse): boolean {
  if (response.fields.length < 3) return true;
  return response.fields.some((f) => f.field_type === f.field_type.toUpperCase());
}

export function normalizeAnswerKeys(answers: PersonalSetupAnswers): PersonalSetupAnswers {
  const normalized: PersonalSetupAnswers = {};
  for (const [key, value] of Object.entries(answers)) {
    const mappedKey = LEGACY_FIELD_ALIASES[key] ?? key;
    if (mappedKey === "pressure_sources" && key === "stress_sources") {
      normalized[mappedKey] = value;
      continue;
    }
    normalized[mappedKey] = value;
  }
  return normalized;
}

export function resolveTemplateForSetup(
  response: PersonalSetupResponse,
): MomentSetupTemplate | null {
  const saved = response.saved_answers ?? {};
  const savedTemplateId =
    typeof saved[TEMPLATE_META_KEYS.templateId] === "string"
      ? (saved[TEMPLATE_META_KEYS.templateId] as string)
      : null;
  if (savedTemplateId) {
    return getTemplate(savedTemplateId);
  }
  return getTemplateByMomentType(response.moment_type_code);
}

export function mergeSetupWithTemplate(
  response: PersonalSetupResponse,
  template: MomentSetupTemplate | null,
): PersonalSetupResponse {
  if (!template) return response;

  const templateFields = template.sections.map(templateSectionToSetupField);
  const fields = isStubSetup(response) ? templateFields : response.fields;

  return {
    ...response,
    title: template.title,
    subtitle: template.subtitle,
    fields,
    mission: response.mission ?? {
      badge_label: template.hero.badge_label,
      title: template.identity_card.title,
      body: template.hero.body,
    },
    cta_label: response.cta_label ?? template.activation_cta.label,
    footer_note: response.footer_note ?? template.activation_cta.footer_note ?? null,
    saved_answers: response.saved_answers
      ? normalizeAnswerKeys(response.saved_answers)
      : null,
  };
}

export function enrichAnswersWithTemplateMeta(
  answers: PersonalSetupAnswers,
  template: MomentSetupTemplate | null,
): PersonalSetupAnswers {
  const normalized = normalizeAnswerKeys(answers);
  if (!template) return normalized;
  return {
    ...normalized,
    [TEMPLATE_META_KEYS.templateId]: template.template_id,
    [TEMPLATE_META_KEYS.templateVersion]: String(template.template_version),
  };
}

export function templateFieldsForValidation(template: MomentSetupTemplate | null) {
  if (!template) return [];
  return template.sections.map(templateSectionToSetupField);
}

import { BUSINESS_TEMPLATES } from "./business";
import { GROUP_TEMPLATES } from "./group";
import { MY_MONEY_TEMPLATES } from "./myMoney";
import type { MomentSetupTemplate, SetupContext } from "./types";

export const SETUP_TEMPLATES: MomentSetupTemplate[] = [
  ...MY_MONEY_TEMPLATES,
  ...GROUP_TEMPLATES,
  ...BUSINESS_TEMPLATES,
];

const TEMPLATE_BY_ID = new Map(SETUP_TEMPLATES.map((t) => [t.template_id, t]));

const MOMENT_TYPE_TO_TEMPLATE: Record<string, string> = {
  LIFE_OPERATIONS: "life_operations",
  FUTURE_BUILDING: "future_building",
  LIFESTYLE: "lifestyle",
  RELATIONSHIPS: "relationships",
  EMOTIONAL_SECURITY: "relationships",
  SHARED_EXPERIENCE: "group_trip",
  SHARED_PURCHASE: "group_purchase",
  SHARED_LIVING: "group_coliving",
  team_operations: "team_ops",
  business_runway: "business_runway",
  business_operations: "business_operations",
};

export function getTemplate(templateId: string): MomentSetupTemplate | null {
  return TEMPLATE_BY_ID.get(templateId) ?? null;
}

export function getTemplateByMomentType(momentTypeCode: string): MomentSetupTemplate | null {
  const templateId = MOMENT_TYPE_TO_TEMPLATE[momentTypeCode];
  if (!templateId) return null;
  return getTemplate(templateId);
}

export function getTemplatesByContext(context: SetupContext): MomentSetupTemplate[] {
  return SETUP_TEMPLATES.filter((t) => t.context === context);
}

/** True when template metadata routes active state to the pulse dashboard. */
export function shouldRenderActivePulseDashboard(momentTypeCode: string): boolean {
  const template = getTemplateByMomentType(momentTypeCode);
  return template?.active_dashboard.screen === "pulse";
}

export function assertRegistryComplete(): void {
  if (SETUP_TEMPLATES.length !== 10) {
    throw new Error(`Expected 10 setup templates, found ${SETUP_TEMPLATES.length}`);
  }
}

assertRegistryComplete();

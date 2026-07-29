import type { QuickAddActionTemplate, QuickAddContext, QuickAddTemplateBundle } from "./types";
import { GROUP_LIVING_QUICK_ADD } from "./registries/groupLiving";
import { GROUP_PURCHASE_QUICK_ADD } from "./registries/groupPurchase";
import { GROUP_TRIP_QUICK_ADD } from "./registries/groupTrip";
import { FUTURE_BUILDING_QUICK_ADD } from "./registries/personalFutureBuilding";
import { LIFE_OPERATIONS_QUICK_ADD } from "./registries/personalLifeOperations";
import { LIFESTYLE_QUICK_ADD } from "./registries/personalLifestyle";
import { RELATIONSHIPS_QUICK_ADD } from "./registries/personalRelationships";

export const QUICK_ADD_TEMPLATE_BUNDLES: QuickAddTemplateBundle[] = [
  LIFE_OPERATIONS_QUICK_ADD,
  FUTURE_BUILDING_QUICK_ADD,
  LIFESTYLE_QUICK_ADD,
  RELATIONSHIPS_QUICK_ADD,
  GROUP_TRIP_QUICK_ADD,
  GROUP_PURCHASE_QUICK_ADD,
  GROUP_LIVING_QUICK_ADD,
];

const BUNDLE_BY_ID = new Map(QUICK_ADD_TEMPLATE_BUNDLES.map((b) => [b.template_id, b]));

const MOMENT_TYPE_TO_TEMPLATE: Record<string, string> = {
  LIFE_OPERATIONS: "personal.life_operations",
  FUTURE_BUILDING: "personal.future_building",
  LIFESTYLE: "personal.lifestyle",
  RELATIONSHIPS: "personal.relationships",
  EMOTIONAL_SECURITY: "personal.relationships",
  SHARED_EXPERIENCE: "group.trip",
  SHARED_PURCHASE: "group.purchase",
  SHARED_LIVING: "group.living",
};

function allActions(bundle: QuickAddTemplateBundle): QuickAddActionTemplate[] {
  return [...bundle.actions, ...(bundle.sub_flows ?? [])];
}

const ACTION_BY_KEY = new Map<string, QuickAddActionTemplate>();
for (const bundle of QUICK_ADD_TEMPLATE_BUNDLES) {
  for (const action of allActions(bundle)) {
    ACTION_BY_KEY.set(`${bundle.template_id}:${action.action_id}`, action);
  }
}

export function getQuickAddBundle(templateId: string): QuickAddTemplateBundle | null {
  return BUNDLE_BY_ID.get(templateId) ?? null;
}

export function getQuickAddBundleByContext(context: QuickAddContext): QuickAddTemplateBundle | null {
  const bundle = QUICK_ADD_TEMPLATE_BUNDLES.find((b) => b.context === context);
  return bundle ?? null;
}

export function getQuickAddBundleByMomentType(momentTypeCode: string): QuickAddTemplateBundle | null {
  const templateId = MOMENT_TYPE_TO_TEMPLATE[momentTypeCode];
  if (!templateId) return null;
  return getQuickAddBundle(templateId);
}

export function getQuickAddAction(
  templateId: string,
  actionId: string,
): QuickAddActionTemplate | null {
  return ACTION_BY_KEY.get(`${templateId}:${actionId}`) ?? null;
}

export function getQuickAddActionsForTemplate(templateId: string): QuickAddActionTemplate[] {
  const bundle = getQuickAddBundle(templateId);
  if (!bundle) return [];
  return allActions(bundle);
}

export function listQuickAddTemplateIds(): string[] {
  return QUICK_ADD_TEMPLATE_BUNDLES.map((b) => b.template_id);
}

export function assertQuickAddRegistryComplete(): void {
  if (QUICK_ADD_TEMPLATE_BUNDLES.length !== 7) {
    throw new Error(`Expected 7 quick-add templates, found ${QUICK_ADD_TEMPLATE_BUNDLES.length}`);
  }
  const lifeOps = getQuickAddBundle("personal.life_operations");
  if (!lifeOps || lifeOps.actions.length !== 5) {
    throw new Error("Life Operations must register 5 hub actions");
  }
  const trip = getQuickAddBundle("group.trip");
  if (!trip || trip.actions.length < 10) {
    throw new Error("Group Trip must register all major hub actions");
  }
}

assertQuickAddRegistryComplete();

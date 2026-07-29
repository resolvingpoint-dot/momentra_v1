import type { QuickAddActionTemplate } from "./types";

/**
 * Interpolate `{field_key}` placeholders in impact preview summary templates.
 */
export function buildImpactPreviewSummary(
  template: string,
  values: Record<string, string | number | undefined | null>,
): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) => {
    const value = values[key];
    if (value === undefined || value === null || value === "") {
      return `{${key}}`;
    }
    return String(value);
  });
}

export function buildImpactPreviewFromAction(
  action: QuickAddActionTemplate,
  values: Record<string, string | number | undefined | null>,
): {
  summary: string;
  modules: string[];
  teaches_items?: string[];
  insight?: { title: string; body: string };
} {
  return {
    summary: buildImpactPreviewSummary(action.impact_preview.summary_template, values),
    modules: action.impact_preview.modules,
    teaches_items: action.impact_preview.teaches_items,
    insight: action.impact_preview.insight,
  };
}

/**
 * Merge affected modules from action and optional cross-module fan-out targets.
 */
export function resolveAffectedModules(
  action: QuickAddActionTemplate,
  extraModules: string[] = [],
): string[] {
  return Array.from(new Set([...action.affects_modules, ...extraModules]));
}

/**
 * Master expense fan-out: one expense action may affect multiple personal moments.
 */
export const MASTER_EXPENSE_FAN_OUT_MODULES = [
  "LIFE_OPERATIONS",
  "LIFESTYLE",
  "EMOTIONAL_SECURITY",
] as const;

export function masterExpenseImpactPreview(
  amount: string,
  category: string,
): {
  summary: string;
  modules: string[];
  fan_out_contexts: readonly string[];
} {
  return {
    summary: `Records ₹${amount} across My Money domains in ${category}`,
    modules: ["pulse", "live", "memory", "life"],
    fan_out_contexts: MASTER_EXPENSE_FAN_OUT_MODULES,
  };
}

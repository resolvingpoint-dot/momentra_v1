"use client";

import dynamic from "next/dynamic";
import type { ComponentType } from "react";
import type { QuickAddActionTemplate } from "@/lib/quick_add/types";

export type ActionRendererProps = {
  action: QuickAddActionTemplate;
  momentId: string;
  templateId: string;
  onClose: () => void;
  onSuccess?: () => void;
  /** Switch to another action (e.g. expense empty → PARTICIPANT). */
  onSwitchAction?: (actionId: string) => void;
};

const loading = () => (
  <div className="py-10 text-center text-sm opacity-70" role="status">
    Loading action…
  </div>
);

function lazy(loader: () => Promise<{ default: ComponentType<ActionRendererProps> }>) {
  return dynamic(loader, { loading, ssr: false });
}

/** Shell only resolves by renderer_id — never by action name. */
export const ACTION_RENDERER_REGISTRY: Record<string, ComponentType<ActionRendererProps>> = {
  "experience.expense": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceExpenseForm };
  }),
  "experience.booking": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceBookingForm };
  }),
  "experience.participant": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceParticipantForm };
  }),
  "experience.contribution": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceContributionForm };
  }),
  "experience.budget": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceBudgetForm };
  }),
  "experience.vendor": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceVendorForm };
  }),
  "experience.poll": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperiencePollForm };
  }),
  "experience.attendance": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceAttendanceForm };
  }),
  "experience.planning_item": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperiencePlanningItemForm };
  }),
  "experience.memory": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceMemoryForm };
  }),
  "experience.update": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/experience");
    return { default: m.ExperienceUpdateForm };
  }),
  "purchase.contribution": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchaseContributionForm };
  }),
  "purchase.expense": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchaseExpenseForm };
  }),
  "purchase.ownership": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchaseOwnershipForm };
  }),
  "purchase.purchase": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchasePurchaseForm };
  }),
  "purchase.vendor": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchaseVendorForm };
  }),
  "purchase.delivery": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchaseDeliveryForm };
  }),
  "purchase.participant": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchaseParticipantForm };
  }),
  "purchase.poll": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchasePollForm };
  }),
  "purchase.memory": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchaseMemoryForm };
  }),
  "purchase.update": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/purchase");
    return { default: m.PurchaseUpdateForm };
  }),
  "living.rent": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingRentForm };
  }),
  "living.utility": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingUtilityForm };
  }),
  "living.expense": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingExpenseForm };
  }),
  "living.contributor": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingContributorForm };
  }),
  "living.task": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingTaskForm };
  }),
  "living.maintenance": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingMaintenanceForm };
  }),
  "living.rule": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingRuleForm };
  }),
  "living.asset": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingAssetForm };
  }),
  "living.resident": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingResidentForm };
  }),
  "living.poll": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingPollForm };
  }),
  "living.memory": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingMemoryForm };
  }),
  "living.update": lazy(async () => {
    const m = await import("@/components/group/action-center/renderers/living");
    return { default: m.LivingUpdateForm };
  }),
};

export function resolveActionRenderer(rendererId: string | undefined): ComponentType<ActionRendererProps> | null {
  if (!rendererId) return null;
  return ACTION_RENDERER_REGISTRY[rendererId] ?? null;
}

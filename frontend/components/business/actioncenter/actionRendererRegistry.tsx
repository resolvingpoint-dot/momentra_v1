"use client";

import dynamic from "next/dynamic";
import type { ComponentType } from "react";
import type {
  BusinessCatalogAction,
  BusinessCatalogMember,
  BusinessRendererMeta,
} from "@/repositories/BusinessActionRepository";

export type BusinessActionRendererProps = {
  action: BusinessCatalogAction;
  momentId: string;
  templateId: string;
  members: BusinessCatalogMember[];
  rendererMeta: BusinessRendererMeta | null;
  onSubmit: (payload: Record<string, unknown>) => Promise<void>;
  onClose: () => void;
  onSuccess?: (result?: { action_type: string; title: string }) => void;
  onSwitchAction?: (actionId: string) => void;
};

const loading = () => (
  <div className="py-10 text-center text-sm opacity-70" role="status">
    Loading action…
  </div>
);

function lazy(loader: () => Promise<{ default: ComponentType<BusinessActionRendererProps> }>) {
  return dynamic(loader, { loading, ssr: false });
}

export const BUSINESS_RENDERER_REGISTRY: Record<string, ComponentType<BusinessActionRendererProps>> = {
  "team_ops.team_update": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.TeamUpdateRenderer })),
  ),
  "team_ops.recognition": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.RecognitionRenderer })),
  ),
  "team_ops.meeting": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.MeetingRenderer })),
  ),
  "team_ops.issue": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.IssueRenderer })),
  ),
  "team_ops.approval": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.ApprovalRenderer })),
  ),
  "team_ops.review": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.ReviewRenderer })),
  ),
  "team_ops.escalation": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.EscalationRenderer })),
  ),
  "team_ops.participation": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.ParticipationRenderer })),
  ),
  "team_ops.member_update": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.MemberUpdateRenderer })),
  ),
  "team_ops.note": lazy(() =>
    import("@/components/business/actioncenter/renderers/team_ops").then((m) => ({ default: m.NoteRenderer })),
  ),

  "runway.cash_inflow": lazy(() =>
    import("@/components/business/actioncenter/renderers/runway").then((m) => ({ default: m.CashInflowRenderer })),
  ),
  "runway.expense_burn": lazy(() =>
    import("@/components/business/actioncenter/renderers/runway").then((m) => ({ default: m.ExpenseBurnRenderer })),
  ),
  "runway.runway_risk": lazy(() =>
    import("@/components/business/actioncenter/renderers/runway").then((m) => ({ default: m.RunwayRiskRenderer })),
  ),
  "runway.financial_update": lazy(() =>
    import("@/components/business/actioncenter/renderers/runway").then((m) => ({ default: m.FinancialUpdateRenderer })),
  ),
  "runway.strategic_decision": lazy(() =>
    import("@/components/business/actioncenter/renderers/runway").then((m) => ({ default: m.StrategicDecisionRenderer })),
  ),

  "ops.spend_entry": lazy(() =>
    import("@/components/business/actioncenter/renderers/ops").then((m) => ({ default: m.SpendEntryRenderer })),
  ),
  "ops.vendor_update": lazy(() =>
    import("@/components/business/actioncenter/renderers/ops").then((m) => ({ default: m.VendorUpdateRenderer })),
  ),
  "ops.approval": lazy(() =>
    import("@/components/business/actioncenter/renderers/ops").then((m) => ({ default: m.OpsApprovalRenderer })),
  ),
  "ops.issue": lazy(() =>
    import("@/components/business/actioncenter/renderers/ops").then((m) => ({ default: m.OpsIssueRenderer })),
  ),
  "ops.operational_improvement": lazy(() =>
    import("@/components/business/actioncenter/renderers/ops").then((m) => ({ default: m.OperationalImprovementRenderer })),
  ),
};

export const ALL_BUSINESS_RENDERER_IDS = Object.keys(BUSINESS_RENDERER_REGISTRY);

export function resolveBusinessActionRenderer(
  rendererId: string | undefined,
): ComponentType<BusinessActionRendererProps> | null {
  if (!rendererId) return null;
  return BUSINESS_RENDERER_REGISTRY[rendererId] ?? null;
}

"use client";

import { Lock } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  businessCardStyle,
  businessScrollShellStyle,
} from "@/components/business/empty/shared/emptyStyles";
import type {
  BusinessDashboardSummary,
  BusinessModuleTile,
  BusinessMomentResponse,
  BusinessWorkspaceSummary,
} from "@/lib/api/business";

type BusinessWorkspaceDashboardProps = {
  workspace: BusinessWorkspaceSummary;
  dashboard?: BusinessDashboardSummary | null;
  moduleTiles?: BusinessModuleTile[] | null;
  recentMoments?: BusinessMomentResponse[] | null;
  onCreateMoment: () => void;
  onInviteMember: () => void;
  onOpenMoment: (momentId: string, typeCode: string) => void;
  bottomPadding?: number;
  /** When true, omit the in-page company title (sheet provides chrome). */
  hidePageHeader?: boolean;
};

function Kpi({
  label,
  value,
  surface,
  textPrimary,
  textSecondary,
  border,
  radius,
}: {
  label: string;
  value: string;
  surface: string;
  textPrimary: string;
  textSecondary: string;
  border: string;
  radius: number;
}) {
  return (
    <div
      className="px-3 py-3"
      style={{
        background: surface,
        border: `1px solid color-mix(in srgb, ${border} 35%, transparent)`,
        borderRadius: radius,
      }}
    >
      <p
        className="text-[11px] font-semibold uppercase tracking-[0.08em]"
        style={{ color: textSecondary }}
      >
        {label}
      </p>
      <p
        className="mt-1 text-xl font-bold tracking-tight"
        style={{ color: textPrimary }}
      >
        {value}
      </p>
    </div>
  );
}

export function BusinessWorkspaceDashboard({
  workspace,
  dashboard,
  moduleTiles,
  recentMoments,
  onCreateMoment,
  onInviteMember,
  onOpenMoment,
  bottomPadding = 0,
  hidePageHeader = false,
}: BusinessWorkspaceDashboardProps) {
  const tokens = useThemeTokens();
  const { colors, radius, spacing } = tokens;

  const tiles = moduleTiles?.length
    ? moduleTiles
    : [
        {
          key: "finance",
          label: "Finance",
          status: "coming_soon",
          description: "Cash, expenses, and P&L for this company.",
        },
        {
          key: "inventory",
          label: "Inventory",
          status: "coming_soon",
          description: "Stock levels, SKUs, and warehouse moves.",
        },
        {
          key: "sales",
          label: "Sales",
          status: "coming_soon",
          description: "Orders, invoices, and revenue tracking.",
        },
        {
          key: "gst",
          label: "GST",
          status: "coming_soon",
          description: "Returns, invoices, and tax compliance.",
        },
      ];

  const recent = (recentMoments ?? []).slice(0, 5);

  return (
    <div
      data-momentra-context="business"
      className="min-h-0 flex-1 overflow-y-auto font-[family-name:var(--font-plus-jakarta)]"
      style={businessScrollShellStyle(tokens, bottomPadding)}
    >
      <div
        className="mx-auto flex w-full max-w-3xl flex-col"
        style={{ gap: spacing.lg, padding: `${spacing.md}px ${spacing.screenHorizontal}px` }}
      >
        {hidePageHeader ? null : (
          <header>
            <p
              className="text-[11px] font-bold uppercase tracking-[0.12em]"
              style={{ color: colors.onPrimaryContainer }}
            >
              Company Home
            </p>
            <h1
              className="mt-1 text-[28px] font-bold leading-tight tracking-tight"
              style={{ color: colors.textPrimary }}
            >
              {workspace.name}
            </h1>
            <p className="mt-1 text-sm" style={{ color: colors.textSecondary }}>
              {workspace.role}
              {workspace.currency ? ` · ${workspace.currency}` : ""}
            </p>
          </header>
        )}

        <section className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          <Kpi
            label="Open Moments"
            value={String(dashboard?.open_moments ?? recent.length)}
            surface={colors.surfaceContainer}
            textPrimary={colors.textPrimary}
            textSecondary={colors.textSecondary}
            border={colors.border}
            radius={radius.card}
          />
          <Kpi
            label="Pending Approvals"
            value={String(dashboard?.pending_approvals ?? 0)}
            surface={colors.surfaceContainer}
            textPrimary={colors.textPrimary}
            textSecondary={colors.textSecondary}
            border={colors.border}
            radius={radius.card}
          />
          <Kpi
            label="Members"
            value={String(dashboard?.member_count ?? 1)}
            surface={colors.surfaceContainer}
            textPrimary={colors.textPrimary}
            textSecondary={colors.textSecondary}
            border={colors.border}
            radius={radius.card}
          />
          <Kpi
            label="Revenue Today"
            value={
              dashboard?.revenue_today != null ? String(dashboard.revenue_today) : "—"
            }
            surface={colors.surfaceContainer}
            textPrimary={colors.textPrimary}
            textSecondary={colors.textSecondary}
            border={colors.border}
            radius={radius.card}
          />
          <Kpi
            label="Cash Balance"
            value={
              dashboard?.cash_balance != null ? String(dashboard.cash_balance) : "—"
            }
            surface={colors.surfaceContainer}
            textPrimary={colors.textPrimary}
            textSecondary={colors.textSecondary}
            border={colors.border}
            radius={radius.card}
          />
        </section>

        <section>
          <h2
            className="mb-3 text-sm font-semibold"
            style={{ color: colors.textSecondary }}
          >
            Quick actions
          </h2>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={onCreateMoment}
              className="px-4 py-2.5 text-sm font-semibold transition-opacity hover:opacity-90"
              style={{
                background: colors.brandPrimary,
                color: colors.brandOnPrimary,
                borderRadius: radius.button,
              }}
            >
              + Create Moment
            </button>
            <button
              type="button"
              onClick={onInviteMember}
              className="px-4 py-2.5 text-sm font-semibold"
              style={{
                ...businessCardStyle(tokens),
                color: colors.textPrimary,
                borderRadius: radius.button,
              }}
            >
              Invite Member
            </button>
            <span
              className="px-4 py-2.5 text-sm font-medium"
              style={{
                border: `1px dashed color-mix(in srgb, ${colors.border} 60%, transparent)`,
                color: colors.textSubtle,
                borderRadius: radius.button,
              }}
            >
              View Reports · Coming soon
            </span>
          </div>
        </section>

        <section>
          <h2
            className="mb-3 text-sm font-semibold"
            style={{ color: colors.textSecondary }}
          >
            Recent Moments
          </h2>
          {recent.length === 0 ? (
            <p
              className="px-4 py-6 text-sm"
              style={{
                ...businessCardStyle(tokens),
                borderRadius: radius.card,
                color: colors.textSecondary,
              }}
            >
              No moments yet. Create your first Team Operations, Runway, or Operations
              moment.
            </p>
          ) : (
            <ul className="space-y-2">
              {recent.map((m) => (
                <li key={m.moment_id}>
                  <button
                    type="button"
                    onClick={() =>
                      onOpenMoment(m.moment_id, (m.moment_type_code ?? "").trim())
                    }
                    className="flex w-full items-center justify-between px-4 py-3 text-left transition-opacity hover:opacity-90"
                    style={{
                      ...businessCardStyle(tokens),
                      borderRadius: radius.card,
                    }}
                  >
                    <span>
                      <span
                        className="block text-sm font-semibold"
                        style={{ color: colors.textPrimary }}
                      >
                        {m.moment_name}
                      </span>
                      <span
                        className="block text-xs"
                        style={{ color: colors.textSecondary }}
                      >
                        {m.moment_type_code ?? "Moment"} · {m.status}
                      </span>
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section>
          <h2
            className="mb-3 text-sm font-semibold"
            style={{ color: colors.textSecondary }}
          >
            Modules
          </h2>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
            {tiles.map((tile) => (
              <div
                key={tile.key}
                className="flex cursor-not-allowed items-start gap-3 px-4 py-3"
                style={{
                  ...businessCardStyle(tokens),
                  borderRadius: radius.card,
                  opacity: 0.92,
                }}
                aria-disabled="true"
              >
                <Lock
                  className="mt-0.5 h-4 w-4 shrink-0"
                  style={{ color: colors.textSubtle }}
                />
                <div>
                  <p
                    className="text-sm font-semibold"
                    style={{ color: colors.textPrimary }}
                  >
                    {tile.label}
                  </p>
                  <p
                    className="text-[11px] font-bold uppercase tracking-[0.1em]"
                    style={{ color: colors.warning }}
                  >
                    Coming Soon
                  </p>
                  {tile.description ? (
                    <p
                      className="mt-1 text-xs leading-relaxed"
                      style={{ color: colors.textSecondary }}
                    >
                      {tile.description}
                    </p>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

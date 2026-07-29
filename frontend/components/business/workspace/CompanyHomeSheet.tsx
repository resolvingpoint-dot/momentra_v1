"use client";

import { X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { BusinessWorkspaceDashboard } from "@/components/business/workspace/BusinessWorkspaceDashboard";
import type {
  BusinessDashboardSummary,
  BusinessModuleTile,
  BusinessMomentResponse,
  BusinessWorkspaceSummary,
} from "@/lib/api/business";

type CompanyHomeSheetProps = {
  open: boolean;
  onClose: () => void;
  workspace: BusinessWorkspaceSummary | null;
  dashboard?: BusinessDashboardSummary | null;
  moduleTiles?: BusinessModuleTile[] | null;
  recentMoments?: BusinessMomentResponse[] | null;
  onCreateMoment: () => void;
  onInviteMember: () => void;
  onOpenMoment: (momentId: string, typeCode: string) => void;
};

export function CompanyHomeSheet({
  open,
  onClose,
  workspace,
  dashboard,
  moduleTiles,
  recentMoments,
  onCreateMoment,
  onInviteMember,
  onOpenMoment,
}: CompanyHomeSheetProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  if (!open || !workspace) return null;

  return (
    <div
      className="fixed inset-0 z-[85] flex flex-col font-[family-name:var(--font-plus-jakarta)]"
      role="dialog"
      aria-label="Company Home"
      data-momentra-context="business"
    >
      <button
        type="button"
        className="absolute inset-0"
        style={{ background: "rgba(11, 16, 32, 0.72)" }}
        aria-label="Close Company Home"
        onClick={onClose}
      />
      <div
        className="relative z-10 mx-auto mt-[max(0.75rem,env(safe-area-inset-top))] flex h-[min(94dvh,920px)] w-full max-w-lg flex-col overflow-hidden shadow-2xl sm:mt-4 sm:rounded-2xl"
        style={{
          background: colors.background,
          border: `1px solid color-mix(in srgb, ${colors.border} 45%, transparent)`,
          color: colors.textPrimary,
        }}
      >
        <header
          className="flex shrink-0 items-start justify-between gap-3 px-4 py-4"
          style={{
            borderBottom: `1px solid color-mix(in srgb, ${colors.border} 40%, transparent)`,
            background: colors.surfaceElevated,
          }}
        >
          <div className="min-w-0">
            <h2
              className="truncate text-lg font-bold tracking-tight"
              style={{ color: colors.textPrimary }}
            >
              {workspace.name}
            </h2>
            <p
              className="mt-0.5 text-xs font-semibold uppercase tracking-[0.1em]"
              style={{ color: colors.textSecondary }}
            >
              Company Home
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close"
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
            style={{
              background: colors.surfaceContainer,
              color: colors.textPrimary,
            }}
          >
            <X className="h-4 w-4" strokeWidth={2.5} />
          </button>
        </header>

        <div className="min-h-0 flex-1 overflow-hidden">
          <BusinessWorkspaceDashboard
            workspace={workspace}
            dashboard={dashboard}
            moduleTiles={moduleTiles}
            recentMoments={recentMoments}
            bottomPadding={24}
            hidePageHeader
            onCreateMoment={onCreateMoment}
            onInviteMember={onInviteMember}
            onOpenMoment={onOpenMoment}
          />
        </div>
      </div>
    </div>
  );
}

"use client";

import { X } from "lucide-react";
import { BottomSheet } from "@/components/shared/BottomSheet";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { useBusinessActionCenter } from "@/hooks/useBusinessActionCenter";
import { BusinessActionHub } from "@/components/business/actioncenter/BusinessActionHub";
import { resolveBusinessActionRenderer } from "@/components/business/actioncenter/actionRendererRegistry";
import { BUSINESS_ACCENT } from "@/components/business/actioncenter/ui/BusinessActionDesignSystem";

type BusinessActionCenterShellProps = {
  momentId: string;
  momentTypeCode: string;
  onClose: () => void;
  onSuccess?: (result?: {
    action_type: string;
    title: string;
    mutationResponse?: unknown;
  }) => void;
  userId?: string;
  momentName?: string | null;
  pulseHint?: Record<string, unknown> | null;
};

export function BusinessActionCenterShell({
  momentId,
  momentTypeCode,
  onClose,
  onSuccess,
  userId = "local",
  momentName,
}: BusinessActionCenterShellProps) {
  const { colors } = useThemeTokens();
  const {
    catalog,
    loading,
    error,
    selectedAction,
    rendererMeta,
    rendererLoading,
    favorites,
    recentIds,
    selectAction,
    toggleFavorite,
    submitAction,
  } = useBusinessActionCenter(momentId, userId);

  const templateId = catalog?.template_id ?? "business.default";
  const Renderer = selectedAction ? resolveBusinessActionRenderer(selectedAction.renderer_id) : null;

  return (
    <BottomSheet open onClose={onClose} ariaLabelledBy="biz-action-center-title" panelClassName="bg-inherit">
      <div
        className="relative flex max-h-[92vh] flex-col"
        style={{ background: colors.background, color: colors.textPrimary }}
      >
        <div
          className="sticky top-0 z-10 border-b px-5 py-4 backdrop-blur-xl"
          style={{ borderColor: `${colors.textSecondary}18`, background: `${colors.background}CC` }}
        >
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => {
                if (selectedAction) selectAction(null);
                else onClose();
              }}
              className="flex size-10 items-center justify-center rounded-full"
              style={{ background: colors.surfaceContainer }}
              aria-label={selectedAction ? "Back to Action Center" : "Close"}
            >
              <X className="size-4" style={{ color: BUSINESS_ACCENT.teal }} />
            </button>
            <div className="text-center">
              <h2
                id="biz-action-center-title"
                className="text-xl font-semibold"
                style={{ color: BUSINESS_ACCENT.navy, fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                Action Center
              </h2>
              <p className="text-xs" style={{ color: colors.textSecondary }}>
                {selectedAction ? selectedAction.label : "What would you like to record?"}
              </p>
            </div>
            <div className="size-10" />
          </div>
        </div>

        <div className="overflow-y-auto px-5 py-4">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div
                className="size-8 animate-spin rounded-full border-2 border-t-transparent"
                style={{ borderColor: `${BUSINESS_ACCENT.teal}40`, borderTopColor: BUSINESS_ACCENT.teal }}
              />
            </div>
          ) : error ? (
            <div className="py-12 text-center">
              <p className="text-sm" style={{ color: colors.error }}>{error}</p>
              <button
                type="button"
                onClick={onClose}
                className="mt-4 rounded-full px-6 py-2 text-sm font-semibold"
                style={{ background: colors.surfaceContainer, color: colors.textPrimary }}
              >
                Close
              </button>
            </div>
          ) : selectedAction && Renderer ? (
            rendererLoading ? (
              <div className="flex items-center justify-center py-20">
                <div
                  className="size-8 animate-spin rounded-full border-2 border-t-transparent"
                  style={{ borderColor: `${BUSINESS_ACCENT.teal}40`, borderTopColor: BUSINESS_ACCENT.teal }}
                />
              </div>
            ) : (
              <Renderer
                action={selectedAction}
                momentId={momentId}
                templateId={templateId}
                members={catalog?.members ?? []}
                rendererMeta={rendererMeta}
                onSubmit={async (payload) => {
                  await submitAction(payload);
                }}
                onClose={() => selectAction(null)}
                onSuccess={onSuccess}
                onSwitchAction={selectAction}
              />
            )
          ) : selectedAction && !Renderer ? (
            <p className="py-8 text-center text-sm opacity-70">
              This action is not available yet.
            </p>
          ) : catalog ? (
            <BusinessActionHub
              categories={catalog.categories}
              actions={catalog.actions}
              favorites={favorites}
              recentIds={recentIds}
              momentName={momentName}
              onSelect={selectAction}
              onToggleFavorite={toggleFavorite}
            />
          ) : null}
        </div>
      </div>
    </BottomSheet>
  );
}

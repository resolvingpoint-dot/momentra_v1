"use client";

import { useEffect, useMemo, useState } from "react";
import { X } from "lucide-react";
import { BottomSheet } from "@/components/shared/BottomSheet";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupActionCenterHub } from "@/components/group/action-center/GroupActionCenterHub";
import { resolveActionRenderer } from "@/components/group/action-center/actionRendererRegistry";
import { getActionCenterAction, getActionCenterActions } from "@/lib/action-center/actionCenterMeta";
import { getRecentActionIds } from "@/lib/action-center/actionCenterPrefs";
import {
  deriveSuggestionSignals,
  rankSmartSuggestions,
} from "@/lib/action-center/smartSuggestions";
import { getQuickAddBundleByMomentType } from "@/lib/quick_add/registry";
import { prefetchTripQuickAddContexts } from "@/repositories/GroupTripQuickAddRepository";
import {
  prefetchLivingQuickAddContexts,
  prefetchPurchaseQuickAddContexts,
} from "@/repositories/GroupTemplateQuickAddRepository";

type GroupActionCenterShellProps = {
  momentId: string;
  momentTypeCode: string;
  onClose: () => void;
  onSuccess?: () => void;
  /** Optional already-fetched pulse for smart suggestions */
  pulseHint?: Record<string, unknown> | null;
  userId?: string;
  momentName?: string | null;
  stageLabel?: string | null;
  heroImageUrl?: string | null;
  /** When set, open directly on this Action Center form (skip hub). */
  initialActionId?: string | null;
};

const HERO: Record<string, { label: string; title: string; subtitle: string }> = {
  SHARED_EXPERIENCE: {
    label: "Shared Experience",
    title: "Bring your experience to life",
    subtitle: "Add people, plans, money, memories and decisions as your experience evolves.",
  },
  SHARED_PURCHASE: {
    label: "Shared Purchase",
    title: "Keep this purchase moving",
    subtitle: "Contributors, items, ownership, and delivery.",
  },
  SHARED_LIVING: {
    label: "Shared Living",
    title: "Keep home life in sync",
    subtitle: "Rent, utilities, chores, and house updates.",
  },
};

export function GroupActionCenterShell({
  momentId,
  momentTypeCode,
  onClose,
  onSuccess,
  pulseHint,
  userId = "local",
  momentName,
  stageLabel,
  heroImageUrl,
  initialActionId = null,
}: GroupActionCenterShellProps) {
  const { colors } = useThemeTokens();
  const bundle = getQuickAddBundleByMomentType(momentTypeCode);
  const templateId = bundle?.template_id ?? "group.trip";
  const hero = HERO[momentTypeCode] ?? HERO.SHARED_EXPERIENCE;

  const actions = useMemo(() => getActionCenterActions(templateId), [templateId]);
  const recentIds = useMemo(() => getRecentActionIds(userId, templateId), [userId, templateId]);
  const suggested = useMemo(() => {
    const signals = deriveSuggestionSignals(templateId, pulseHint);
    return rankSmartSuggestions(templateId, actions, signals);
  }, [templateId, actions, pulseHint]);

  const resolvedInitial =
    initialActionId && getActionCenterAction(templateId, initialActionId) ? initialActionId : null;
  const [selectedActionId, setSelectedActionId] = useState<string | null>(resolvedInitial);

  useEffect(() => {
    setSelectedActionId(resolvedInitial);
  }, [resolvedInitial]);

  const selected = selectedActionId ? getActionCenterAction(templateId, selectedActionId) : null;
  const Renderer = selected ? resolveActionRenderer(selected.renderer_id) : null;

  const contextChips = useMemo(() => {
    const chips: string[] = [];
    const name = momentName?.trim();
    if (name) chips.push(name);
    if (hero.label && hero.label !== name) chips.push(hero.label);
    if (stageLabel?.trim() && stageLabel !== name && stageLabel !== hero.label) {
      chips.push(stageLabel.trim());
    }
    // Fallback so hub always has at least one chip
    if (!chips.length) chips.push(hero.label);
    return chips;
  }, [momentName, hero.label, stageLabel]);

  useEffect(() => {
    const warmActions = suggested
      .slice(0, 4)
      .map((action) => action.action_id)
      .concat(actions.slice(0, 3).map((action) => action.action_id));
    if (templateId === "group.purchase") {
      void prefetchPurchaseQuickAddContexts(momentId, warmActions);
    } else if (templateId === "group.living") {
      void prefetchLivingQuickAddContexts(momentId, warmActions);
    } else if (templateId === "group.trip") {
      void prefetchTripQuickAddContexts(momentId, warmActions);
    }
  }, [momentId, actions, suggested, templateId]);

  return (
    <BottomSheet open onClose={onClose} ariaLabelledBy="action-center-title" panelClassName="bg-inherit">
      <div className="relative flex max-h-[92vh] flex-col" style={{ background: colors.background, color: colors.textPrimary }}>
        <div
          className="sticky top-0 z-10 border-b px-5 py-4 backdrop-blur-xl"
          style={{ borderColor: `${colors.textSecondary}18`, background: `${colors.background}CC` }}
        >
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={() => {
                if (selectedActionId) setSelectedActionId(null);
                else onClose();
              }}
              className="flex size-10 items-center justify-center rounded-full"
              style={{ background: colors.surfaceContainer }}
              aria-label={selectedActionId ? "Back to Quick Add" : "Close"}
            >
              <X className="size-4" style={{ color: colors.primaryContainer }} />
            </button>
            <div className="text-center">
              <h2 id="action-center-title" className="text-xl font-semibold" style={{ color: colors.primaryContainer }}>
                Quick Add
              </h2>
              <p className="text-xs" style={{ color: colors.textSecondary }}>
                {selected ? selected.label : "What would you like to add?"}
              </p>
            </div>
            <div className="size-10" />
          </div>
        </div>

        <div className="overflow-y-auto px-5 py-4">
          {selected && Renderer ? (
            <Renderer
              action={selected}
              momentId={momentId}
              templateId={templateId}
              onClose={() => setSelectedActionId(null)}
              onSuccess={onSuccess}
              onSwitchAction={setSelectedActionId}
            />
          ) : selected && !Renderer ? (
            <p className="py-8 text-center text-sm opacity-70">This action is not available yet.</p>
          ) : (
            <GroupActionCenterHub
              templateId={templateId}
              templateLabel={hero.label}
              heroTitle={hero.title}
              heroSubtitle={hero.subtitle}
              contextChips={contextChips}
              heroImageUrl={heroImageUrl}
              actions={actions}
              suggested={suggested}
              recentIds={recentIds}
              userId={userId}
              onSelect={setSelectedActionId}
            />
          )}
        </div>
      </div>
    </BottomSheet>
  );
}

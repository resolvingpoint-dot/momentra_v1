"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";
import type { PersonalLiveRecentActivityItem } from "@/lib/api/personal";
import { relationshipsPulseCopy } from "@/lib/personal/emotional_security/pulse/relationshipsPulseCopy";
import { resolveActivityIcon } from "@/lib/personal/life_operations/pulse/pulseIcons";
import {
  recentActivityChips,
  recentActivityDomainTypeLine,
  recentActivityIsEditable,
  recentActivityMoodLabel,
  recentActivityPrimaryMetric,
  recentActivityTitle,
} from "@/lib/personal/life_operations/pulse/recentActivityDisplay";
import { Pencil } from "lucide-react";

const MOMENT_TYPE = "RELATIONSHIPS";

type RelationshipsRecentActivityListProps = {
  items: PersonalLiveRecentActivityItem[];
  emptyMessage?: string | null;
  onViewAll?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
};

export function RelationshipsRecentActivityList({
  items,
  emptyMessage,
  onViewAll,
  onEditActivity,
}: RelationshipsRecentActivityListProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const visible = items.slice(0, 5);

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <PersonalWidgetSectionHeader
            title={relationshipsPulseCopy.recentActivityTitle}
            explainerId="PULSE-004"
            momentTypeCode={MOMENT_TYPE}
          />
          <p style={{ fontSize: 11, opacity: 0.6, marginTop: 2 }}>Latest relationship moments</p>
        </div>
        <button
          type="button"
          onClick={onViewAll}
          className="text-[10px] font-bold uppercase"
          style={{ color: colors.brandPrimary, background: "none", border: "none" }}
        >
          {relationshipsPulseCopy.viewAll}
        </button>
      </div>
      {visible.length === 0 ? (
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>
          {emptyMessage ?? relationshipsPulseCopy.recentActivityEmpty}
        </p>
      ) : (
        <div className="mx-auto w-full max-w-2xl space-y-0">
          {visible.map((item, index) => {
            const eventType = (item.activity_type || item.event_type || "").toUpperCase();
            const Icon = resolveActivityIcon(eventType, item.icon);
            const titleText = recentActivityTitle({
              title: item.title,
              subtitle: item.subtitle,
              detail_line: item.detail_line,
            });
            const domainType = recentActivityDomainTypeLine(item) ?? item.category_label;
            const mood = recentActivityMoodLabel(item);
            const metric = recentActivityPrimaryMetric(item);
            const chips = recentActivityChips(item, 2);
            const editable = recentActivityIsEditable(item);
            const isLast = index === visible.length - 1;
            return (
              <div
                key={item.id}
                className={`flex items-start gap-3 ${isLast ? "" : "border-b pb-3"} ${index > 0 ? "pt-3" : ""}`}
                style={{ borderColor: "rgba(255,255,255,0.05)" }}
              >
                <div
                  className="flex size-9 shrink-0 items-center justify-center rounded-lg"
                  style={{ background: `${colors.brandPrimary}1a` }}
                  aria-label={domainType || eventType}
                >
                  <Icon size={16} color={colors.brandPrimary} aria-hidden />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-bold" style={{ color: colors.textPrimary }}>
                        {titleText}
                      </p>
                      {domainType ? (
                        <p className="mt-0.5 truncate text-xs" style={{ color: colors.textSecondary, opacity: 0.75 }}>
                          {domainType}
                        </p>
                      ) : null}
                      {mood ? (
                        <p
                          className="mt-1 inline-flex rounded-full px-2 py-0.5"
                          style={{
                            fontSize: 10,
                            fontWeight: 600,
                            color: colors.brandPrimary,
                            background: `${colors.brandPrimary}22`,
                          }}
                        >
                          {mood}
                        </p>
                      ) : null}
                      {chips.length > 0 ? (
                        <p className="mt-1 text-[10px] font-semibold" style={{ color: colors.brandTertiary }}>
                          {chips.join(" · ")}
                        </p>
                      ) : null}
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-1">
                      <span className="text-[10px] uppercase opacity-45">{item.relative_time}</span>
                      {metric ? <span className="text-xs font-bold">{metric}</span> : null}
                      {editable && onEditActivity ? (
                        <button
                          type="button"
                          onClick={() =>
                            onEditActivity(item.id, item.edit_event_type ?? eventType)
                          }
                          className="border-0 bg-transparent p-1"
                          aria-label={`Edit ${titleText}`}
                        >
                          <Pencil size={14} color={colors.textSecondary} style={{ opacity: 0.5 }} />
                        </button>
                      ) : null}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

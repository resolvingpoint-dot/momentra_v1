"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy, quickActionColor } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { BarChart3, Clock, Plus, Sparkles, Zap } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type LifeQuickActionsBarProps = {
  quote: string;
  actions: PersonalLifeMetrics["quick_actions"];
  onQuickAdd?: (eventType: string) => void;
  onCreateMoment?: () => void;
};

function quickActionIcon(actionCode: string): LucideIcon {
  switch (actionCode) {
    case "LOG_RECOVERY":
      return Zap;
    case "LOG_PROGRESS":
      return BarChart3;
    case "LOG_EXPERIENCE":
      return Clock;
    case "CREATE_MOMENT":
      return Plus;
    default:
      return Zap;
  }
}

export function LifeQuickActionsBar({
  quote,
  actions,
  onQuickAdd,
  onCreateMoment,
}: LifeQuickActionsBarProps) {
  const { colors } = useThemeTokens();

  return (
    <footer
      className="sticky bottom-0 z-10 flex flex-col gap-3 rounded-2xl border px-4 py-3 backdrop-blur-xl sm:flex-row sm:items-center sm:justify-between"
      style={{
        borderColor: colors.border,
        background: `color-mix(in srgb, ${colors.surfaceContainer} 90%, transparent)`,
      }}
    >
      <div className="flex shrink-0 items-center gap-0.5">
        <p
          className="flex items-center gap-2 italic"
          style={{ ...personalTypography.microLabel, opacity: 0.6, color: colors.textSecondary }}
        >
          <Sparkles className="size-3.5" style={{ color: colors.brandPrimary }} />
          {quote}
        </p>
        <WidgetInfoButton explainerId="LIFE-012" />
      </div>
      <div className="flex gap-2 overflow-x-auto [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {actions.map((action) => {
          const isPrimary = action.action_code === "CREATE_MOMENT";
          const accent = quickActionColor(action.color_token, colors);
          const Icon = quickActionIcon(action.action_code);
          return (
            <button
              key={action.action_code}
              type="button"
              onClick={() => {
                if (action.action_code === "CREATE_MOMENT") onCreateMoment?.();
                else if (action.event_type) onQuickAdd?.(action.event_type);
              }}
              className="flex shrink-0 items-center gap-2 rounded-xl px-3 py-1.5 whitespace-nowrap"
              style={{
                ...personalTypography.microLabel,
                fontWeight: 700,
                ...(isPrimary
                  ? { background: colors.brandPrimary, color: colors.brandOnPrimary }
                  : {
                      border: `1px solid color-mix(in srgb, ${colors.border} 80%, transparent)`,
                      background: `color-mix(in srgb, ${accent} 12%, transparent)`,
                      color: accent,
                    }),
              }}
            >
              <Icon className="size-3.5 shrink-0" />
              {action.label}
            </button>
          );
        })}
      </div>
    </footer>
  );
}

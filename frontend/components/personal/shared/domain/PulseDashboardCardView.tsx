"use client";

import type { PulseDashboardCard } from "@/lib/api/personal";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";

export function PulseDashboardCardView({ card }: { card: PulseDashboardCard }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="rounded-2xl p-4" style={personalGlassCardStyle(tokens)}>
      {card.moment_name ? (
        <p className="mb-1 text-xs font-medium uppercase tracking-widest opacity-70" style={{ color: colors.textSecondary }}>
          {card.moment_name}
        </p>
      ) : null}
      <div className="mb-3 grid grid-cols-2 gap-3">
        {card.kpis.map((kpi) => (
          <div key={kpi.kpi_id}>
            <p className="text-[10px] uppercase tracking-wide opacity-60" style={{ color: colors.textSecondary }}>
              {kpi.label}
            </p>
            <p className="text-lg font-semibold" style={{ color: colors.brandPrimary }}>
              {kpi.value}
            </p>
          </div>
        ))}
      </div>
      {card.recent_items.length > 0 ? (
        <ul className="space-y-2 border-t pt-3" style={{ borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)` }}>
          {card.recent_items.slice(0, 3).map((item) => (
            <li key={item.id} className="flex justify-between gap-2 text-xs">
              <span className="truncate">{item.title}</span>
              <span className="shrink-0 opacity-60">{item.relative_time}</span>
            </li>
          ))}
        </ul>
      ) : card.empty_recent_message ? (
        <p className="text-xs opacity-60" style={{ color: colors.textSecondary }}>
          {card.empty_recent_message}
        </p>
      ) : null}
    </div>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type LifestyleSectionBadgeProps = {
  index: number | string;
  label: string;
  accent?: boolean;
  explainerId?: string;
  momentTypeCode?: string | null;
};

export function LifestyleSectionBadge({
  index,
  label,
  accent,
  explainerId,
  momentTypeCode = "LIFESTYLE",
}: LifestyleSectionBadgeProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div className="mb-4 flex items-center gap-2">
      <span
        className="flex size-5 items-center justify-center rounded-full border text-[10px] font-bold"
        style={{
          borderColor: accent ? colors.brandPrimary : `${colors.textSecondary}66`,
          color: accent ? colors.brandPrimary : colors.textSecondary,
        }}
      >
        {index}
      </span>
      <span
        className="text-[10px] font-bold uppercase tracking-widest"
        style={{ color: accent ? colors.brandPrimary : colors.textSecondary, opacity: accent ? 1 : 0.7 }}
      >
        {label}
      </span>
      {explainerId ? <WidgetInfoButton explainerId={explainerId} momentTypeCode={momentTypeCode} /> : null}
    </div>
  );
}

"use client";

import { Lightbulb } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type Props = {
  tip: string;
};

export function GuidedSetupTip({ tip }: Props) {
  const { colors } = useThemeTokens();
  if (!tip.trim()) return null;

  return (
    <div
      className="flex gap-2 rounded-xl px-3 py-2.5 text-xs leading-relaxed"
      style={{
        background: `color-mix(in srgb, ${colors.primary} 10%, transparent)`,
        color: colors.textSecondary,
      }}
      role="note"
    >
      <Lightbulb className="mt-0.5 size-4 shrink-0 opacity-70" aria-hidden />
      <p>{tip}</p>
    </div>
  );
}

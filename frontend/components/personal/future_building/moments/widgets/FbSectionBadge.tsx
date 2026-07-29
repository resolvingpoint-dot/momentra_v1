"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";

type Props = { number: number };

export function FbSectionBadge({ number }: Props) {
  const { colors } = useThemeTokens();
  return (
    <span
      className="rounded-full px-2 py-0.5 text-[10px] font-bold"
      style={{ background: colors.brandPrimary, color: colors.brandOnPrimary }}
    >
      {number}
    </span>
  );
}

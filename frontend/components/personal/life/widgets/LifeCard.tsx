"use client";

import type { CSSProperties, ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";

type LifeCardProps = {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
  glow?: boolean;
};

export function LifeCard({ children, className = "", style, glow }: LifeCardProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <section
      className={`rounded-2xl p-5 md:p-6 ${className}`}
      style={{
        ...personalGlassCardStyle(tokens, glow ? { glow: true } : undefined),
        borderRadius: 16,
        color: colors.textPrimary,
        ...style,
      }}
    >
      {children}
    </section>
  );
}

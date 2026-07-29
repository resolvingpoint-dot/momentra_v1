"use client";

import type { CSSProperties, ReactNode } from "react";
import type { ContextThemeTokens } from "@/lib/contextTokens";
import {
  personalGlassInnerStyle,
  personalGlowWrapperStyle,
  premiumGlowCardStyle,
  premiumGlowWrapperStyle,
} from "@/components/personal/empty/shared/emptyStyles";

type PersonalGlassGlowSectionProps = {
  tokens: ContextThemeTokens;
  cornerRadius?: number;
  className?: string;
  innerClassName?: string;
  innerStyle?: CSSProperties;
  children: ReactNode;
};

/** Outward glow wrapper + inner glass card (matches mobile/web design intent). */
export function PersonalGlassGlowSection({
  tokens,
  cornerRadius = 16,
  className,
  innerClassName,
  innerStyle,
  children,
}: PersonalGlassGlowSectionProps) {
  return (
    <section style={personalGlowWrapperStyle(tokens, cornerRadius)} className={className}>
      <div
        className={innerClassName}
        style={personalGlassInnerStyle(tokens, cornerRadius, innerStyle)}
      >
        {children}
      </div>
    </section>
  );
}

type PersonalPremiumGlowSectionProps = {
  tokens: ContextThemeTokens;
  cornerRadius?: number;
  className?: string;
  innerClassName?: string;
  innerStyle?: CSSProperties;
  children: ReactNode;
};

/** Outward premium halo + inner glass card (no inset wash). */
export function PersonalPremiumGlowSection({
  tokens,
  cornerRadius = 16,
  className,
  innerClassName,
  innerStyle,
  children,
}: PersonalPremiumGlowSectionProps) {
  return (
    <section style={premiumGlowWrapperStyle(cornerRadius)} className={className}>
      <div
        className={innerClassName}
        style={{
          ...premiumGlowCardStyle(tokens),
          borderRadius: Math.max(0, cornerRadius - 2),
          ...innerStyle,
        }}
      >
        {children}
      </div>
    </section>
  );
}

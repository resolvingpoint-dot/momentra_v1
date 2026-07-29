import type { CSSProperties, ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { groupGlassCardStyle } from "@/components/group/empty/shared/emptyStyles";

type ExperienceGlassCardProps = {
  children: ReactNode;
  className?: string;
  style?: CSSProperties;
  glow?: boolean;
  accentBorder?: "left" | "none";
};

export function ExperienceGlassCard({
  children,
  className = "",
  style,
  glow = false,
  accentBorder = "none",
}: ExperienceGlassCardProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  const glass = groupGlassCardStyle(tokens);
  const { border: glassBorder, ...glassRest } = glass;

  return (
    <div
      className={`rounded-[24px] p-6 ${className}`}
      style={{
        ...glassRest,
        boxShadow: glow ? "0 10px 40px rgba(255,122,61,0.10)" : undefined,
        ...(accentBorder === "left"
          ? {
              borderTop: "1px solid rgba(255, 255, 255, 0.08)",
              borderRight: "1px solid rgba(255, 255, 255, 0.08)",
              borderBottom: "1px solid rgba(255, 255, 255, 0.08)",
              borderLeft: `4px solid ${colors.brandPrimary}`,
            }
          : { border: glassBorder }),
        ...style,
      }}
    >
      {children}
    </div>
  );
}

"use client";

import type { ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type Props = {
  title?: string;
  children: ReactNode;
  className?: string;
};

/** Quiet section wrapper — title optional so shell step headline stays primary. */
export function SetupSectionCard({ title, children, className }: Props) {
  const { colors } = useThemeTokens();
  return (
    <section
      className={`space-y-3 rounded-2xl border p-3.5 sm:p-4 ${className ?? ""}`}
      style={{
        borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
        background: colors.surfaceContainer,
      }}
    >
      {title ? (
        <h3
          className="text-[11px] font-semibold uppercase tracking-wide opacity-55"
          style={{ color: colors.textSecondary }}
        >
          {title}
        </h3>
      ) : null}
      <div className="space-y-3">{children}</div>
    </section>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy, sentimentColor } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeConnection } from "@/lib/api/personal";
import { LifeCard } from "./LifeCard";
import { LifeSectionLabel } from "./LifeSectionLabel";

type LifeConnectionsCardProps = {
  connections: PersonalLifeConnection[];
};

export function LifeConnectionsCard({ connections }: LifeConnectionsCardProps) {
  const { colors } = useThemeTokens();

  return (
    <LifeCard>
      <LifeSectionLabel explainerId="LIFE-006">{personalLifeCopy.sections.lifeConnections}</LifeSectionLabel>
      <p className="mb-4" style={{ ...personalTypography.microLabel, opacity: 0.5, color: colors.textSecondary }}>
        {personalLifeCopy.sections.lifeConnectionsSubtitle}
      </p>
      <div className="space-y-2">
        {connections.map((c) => (
          <div
            key={`${c.from_type_code}-${c.to_type_code}`}
            className="flex items-center justify-between rounded-xl border p-3"
            style={{ borderColor: colors.border }}
          >
            <div>
              <p style={{ ...personalTypography.microLabel, fontWeight: 600, color: colors.textPrimary }}>
                {c.from_label} <span style={{ opacity: 0.4 }}>→</span> {c.to_label}
              </p>
              <p style={{ ...personalTypography.microLabel, opacity: 0.6, color: colors.textSecondary }}>
                {c.summary}
              </p>
            </div>
            <span
              style={{
                ...personalTypography.microLabel,
                fontWeight: 600,
                color: sentimentColor(c.sentiment, colors),
              }}
            >
              {c.sentiment.replace("_", " ")}
            </span>
          </div>
        ))}
      </div>
    </LifeCard>
  );
}

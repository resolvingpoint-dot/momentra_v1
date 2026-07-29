"use client";

import { Building2 } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupSkeletonBlocks } from "@/components/group/shared/skeleton/GroupSkeletonBlocks";
import { ExperienceScrollShell } from "@/components/group/active/experience/ui/ExperienceUiParts";
import { GroupLifeMetricsView } from "@/components/group/life/ui/GroupLifeUiParts";
import { useGroupLife } from "@/hooks/useGroupTabCache";

type GroupLifeCommandCenterProps = {
  bottomPadding?: number;
  onCreateMomentType?: (momentTypeCode: string) => void;
};

export function GroupLifeCommandCenter({
  bottomPadding = 0,
  onCreateMomentType,
}: GroupLifeCommandCenterProps) {
  const { data, loading, error, reload } = useGroupLife(true);
  const tokens = useThemeTokens();
  const { colors } = tokens;

  if (loading && !data) {
    return (
      <ExperienceScrollShell bottomPadding={bottomPadding}>
        <GroupSkeletonBlocks variant="life" />
      </ExperienceScrollShell>
    );
  }

  if (error && !data) {
    return (
      <ExperienceScrollShell bottomPadding={bottomPadding}>
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Building2 size={40} style={{ color: colors.textSecondary }} />
          <p className="mt-3 text-sm" style={{ color: colors.textSecondary }}>{error}</p>
          <button
            type="button"
            onClick={() => void reload()}
            className="mt-4 rounded-full px-4 py-2 text-sm font-semibold"
            style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
          >
            Retry
          </button>
        </div>
      </ExperienceScrollShell>
    );
  }

  if (!data || data.is_empty || !data.metrics) {
    return (
      <ExperienceScrollShell bottomPadding={bottomPadding}>
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Building2 size={48} style={{ color: colors.textSecondary }} />
          <h2 className="mt-4 text-lg font-semibold" style={{ color: colors.textPrimary }}>
            No Active Groups
          </h2>
          <p className="mt-2 text-sm" style={{ color: colors.textSecondary }}>
            Create a group moment to see your command center.
          </p>
        </div>
      </ExperienceScrollShell>
    );
  }

  return (
    <ExperienceScrollShell bottomPadding={bottomPadding}>
      <GroupLifeMetricsView metrics={data.metrics} onQuickAction={onCreateMomentType} />
    </ExperienceScrollShell>
  );
}

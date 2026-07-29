"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalTypography, scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { Calendar } from "lucide-react";
import { DominantEmotionCard } from "./widgets/DominantEmotionCard";
import { EmotionalTrendChart } from "./widgets/EmotionalTrendChart";
import { HappinessDriversCard } from "./widgets/HappinessDriversCard";
import { LifeBalanceModel } from "./widgets/LifeBalanceModel";
import { LifeConnectionsCard } from "./widgets/LifeConnectionsCard";
import { LifeDriftAlert } from "./widgets/LifeDriftAlert";
import { MotionStaggerRoot, MotionSection } from "@/components/shared/MotionStagger";
import { FloatingParticles } from "@/lib/motion/FloatingParticles";
import { AnimatedNumber } from "@/lib/motion/AnimatedNumber";
import { LifeHealthHero } from "./widgets/LifeHealthHero";
import { LifeIntelligenceCard } from "./widgets/LifeIntelligenceCard";
import { LifeJourneyTimeline } from "./widgets/LifeJourneyTimeline";
import { LifeLeverageCard } from "./widgets/LifeLeverageCard";
import { LifeQuickActionsBar } from "./widgets/LifeQuickActionsBar";
import { MonthlyChangesCard } from "./widgets/MonthlyChangesCard";

export { PersonalLifeSkeleton } from "./PersonalLifeSkeleton";

type PersonalLifeProps = {
  metrics: PersonalLifeMetrics;
  dateRangeLabel?: string | null;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
  onQuickAdd?: (eventType: string) => void;
  onCreateMoment?: () => void;
};

export function PersonalLife({
  metrics,
  dateRangeLabel,
  bottomPadding = 0,
  hideScreenHeader = false,
  onQuickAdd,
  onCreateMoment,
}: PersonalLifeProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />
      <FloatingParticles density={0.6} color={`${colors.brandPrimary}44`} />
      <div
        className="relative mx-auto flex w-full max-w-[1080px] flex-col gap-4 px-5 py-6 md:px-8 md:py-8"
        style={{ gap: tokens.spacing.sectionGap }}
      >
        <MotionStaggerRoot>
        <MotionSection>
        {!hideScreenHeader ? (
        <header className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 style={{ ...personalTypography.heroTitle, color: colors.textPrimary }}>
              {personalLifeCopy.screenTitle}
            </h1>
            <p style={{ ...personalTypography.bodyMd, opacity: 0.7, color: colors.textSecondary }}>
              {personalLifeCopy.screenSubtitle}
            </p>
          </div>
          {dateRangeLabel ? (
            <div
              className="flex items-center gap-2 rounded-full border px-3 py-1.5"
              style={{
                ...personalTypography.labelSm,
                borderColor: colors.border,
                color: colors.textSecondary,
              }}
            >
              <Calendar className="size-3.5 opacity-60" />
              {dateRangeLabel}
            </div>
          ) : null}
        </header>
        ) : null}
        </MotionSection>

        <MotionSection><LifeHealthHero lifeHealth={metrics.life_health} /></MotionSection>

        <MotionSection>
        <div className="grid gap-4 md:grid-cols-2">
          <EmotionalTrendChart
            windowLabel={metrics.emotional_trend.window_label}
            series={metrics.emotional_trend.series}
            isSparse={metrics.emotional_trend.is_sparse}
            onQuickAdd={onQuickAdd}
          />
          <DominantEmotionCard dominant={metrics.dominant_emotion} onQuickAdd={onQuickAdd} />
        </div>
        </MotionSection>

        <MotionSection><LifeBalanceModel balance={metrics.balance_model} /></MotionSection>

        <MotionSection>
        <div className="grid gap-4 md:grid-cols-2">
          <LifeConnectionsCard connections={metrics.connections} />
          {metrics.drift_alert ? (
            <LifeDriftAlert alert={metrics.drift_alert} onQuickAdd={onQuickAdd} />
          ) : null}
        </div>
        </MotionSection>

        {metrics.leverage ? (
          <MotionSection><LifeLeverageCard leverage={metrics.leverage} onQuickAdd={onQuickAdd} /></MotionSection>
        ) : null}

        <MotionSection><HappinessDriversCard happiness={metrics.happiness} /></MotionSection>

        <MotionSection>
        <div className="grid gap-4 md:grid-cols-2">
          <LifeIntelligenceCard intelligence={metrics.intelligence} onQuickAdd={onQuickAdd} />
          <MonthlyChangesCard changes={metrics.monthly_changes} />
        </div>
        </MotionSection>

        <MotionSection><LifeJourneyTimeline journey={metrics.journey} /></MotionSection>

        <MotionSection>
        <LifeQuickActionsBar
          quote={metrics.footer_quote}
          actions={metrics.quick_actions}
          onQuickAdd={onQuickAdd}
          onCreateMoment={onCreateMoment}
        />
        </MotionSection>
        </MotionStaggerRoot>
      </div>
    </div>
  );
}

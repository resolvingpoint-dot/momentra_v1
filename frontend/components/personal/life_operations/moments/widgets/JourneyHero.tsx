"use client";

import { motion } from "framer-motion";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassInnerStyle, personalGlowWrapperStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsJourneyHero } from "@/lib/api/personal";
import { lifeOpsMomentsCopy } from "@/lib/personal/life_operations/moments/lifeOpsMomentsCopy";
import { MOTION_DURATION_S } from "@/lib/motion/tokens";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type JourneyHeroProps = {
  hero: PersonalLifeOpsJourneyHero;
};

function phaseProgress(hero: PersonalLifeOpsJourneyHero): number {
  const activeIdx = hero.phases.findIndex((p) => p.is_active);
  if (activeIdx <= 0) return 33;
  if (activeIdx === 1) return 66;
  return 100;
}

export function JourneyHero({ hero }: JourneyHeroProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const reducedMotion = useReducedMotion();
  const progress = phaseProgress(hero);
  const statusLabel = lifeOpsMomentsCopy.statusBandLabel(hero.status_band);

  return (
    <motion.section
      style={personalGlowWrapperStyle(tokens, 24)}
      initial={reducedMotion ? false : { opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: MOTION_DURATION_S.medium }}
    >
      <div style={personalGlassInnerStyle(tokens, 24, { padding: 16 })}>
        <p style={{ ...personalTypography.labelSm, opacity: 0.6, textTransform: "uppercase", letterSpacing: "0.08em" }}>
          {lifeOpsMomentsCopy.journeyHeroSection}
        </p>
        <div className="mt-1.5 flex items-center gap-0.5">
          <h2 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
            {lifeOpsMomentsCopy.journeyHeroTitle}
          </h2>
          <WidgetInfoButton explainerId="MOMENT-001" momentTypeCode="LIFE_OPERATIONS" />
        </div>
        <div className="mt-3 flex flex-wrap items-end gap-2">
          <span style={{ fontSize: 56, fontWeight: 700, lineHeight: 1, color: colors.textPrimary }}>
            {hero.journey_score}
          </span>
          <span
            className="rounded-full px-3 py-1 text-sm font-bold"
            style={{ background: `${colors.brandPrimary}33`, color: colors.brandPrimary }}
          >
            {statusLabel}
          </span>
        </div>

        <div className="mt-4 flex items-center gap-3">
          {hero.phases.map((phase) => (
            <span
              key={phase.phase_id}
              className="text-[10px] font-bold uppercase tracking-widest"
              style={{
                color: phase.is_active ? colors.brandPrimary : colors.textSecondary,
                opacity: phase.is_active ? 1 : 0.45,
              }}
            >
              {phase.label}
            </span>
          ))}
        </div>
        <div className="mt-2 h-1 overflow-hidden rounded-full" style={{ background: `${colors.textSecondary}22` }}>
          <motion.div
            className="h-full rounded-full"
            style={{ background: colors.brandPrimary }}
            initial={{ width: reducedMotion ? `${progress}%` : "0%" }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: reducedMotion ? 0 : MOTION_DURATION_S.slow, ease: [0.22, 1, 0.36, 1] }}
          />
        </div>

        <div className="relative mt-4 min-h-[120px] w-full">
          <svg viewBox="0 0 400 150" className="h-full w-full" aria-hidden>
            <path
              d="M0,120 Q50,110 100,100 T200,80 T300,40 T400,20"
              fill="none"
              stroke="rgba(255,255,255,0.06)"
              strokeWidth={4}
            />
            <motion.path
              d={`M0,120 Q50,110 100,100 T200,80 T300,${120 - hero.journey_score * 0.8}`}
              fill="none"
              stroke="url(#journeyGradient)"
              strokeLinecap="round"
              strokeWidth={6}
              initial={{ pathLength: reducedMotion ? 1 : 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: reducedMotion ? 0 : MOTION_DURATION_S.slow, ease: "easeOut" }}
            />
            <defs>
              <linearGradient id="journeyGradient" x1="0%" x2="100%" y1="0%" y2="0%">
                <stop offset="0%" stopColor={colors.brandPrimary} />
                <stop offset="100%" stopColor={colors.brandTertiary} />
              </linearGradient>
            </defs>
          </svg>
          <p className="mt-2 max-w-xs text-xs leading-relaxed" style={{ color: colors.textSecondary }}>
            {hero.insight_body}
          </p>
        </div>

        <div className="mt-3 grid grid-cols-2 gap-2 text-center sm:grid-cols-4">
          {[
            { value: hero.days_active, label: lifeOpsMomentsCopy.statDaysActive },
            { value: hero.recovery_events, label: lifeOpsMomentsCopy.statRecoveryEvents },
            { value: hero.adjustments_made, label: lifeOpsMomentsCopy.statAdjustmentsMade },
            { value: `${hero.pressure_reduced_percent}%`, label: lifeOpsMomentsCopy.statPressureReduced },
          ].map((stat) => (
            <div key={stat.label}>
              <p className="text-base font-bold" style={{ color: colors.textPrimary }}>
                {stat.value}
              </p>
              <p className="mt-0.5 text-[9px] uppercase leading-tight tracking-tight sm:text-[10px]" style={{ color: colors.textSecondary }}>
                {stat.label}
              </p>
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  );
}

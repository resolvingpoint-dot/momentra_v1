"use client";

import type { CSSProperties } from "react";
import {
  Activity,
  ArrowRight,
  CircleDot,
  Lightbulb,
  Minimize2,
  PlusCircle,
  Sparkles,
  Stethoscope,
  TrendingUp,
  Users,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import type { ContextThemeTokens } from "@/lib/contextTokens";

type PulseEmptyMode = "no_moment" | "draft_resume";

type PulseEmptyProps = {
  onCreateMoment: () => void;
  onContinueSetup?: () => void;
  mode?: PulseEmptyMode;
  momentTypeLabel?: string;
  bottomPadding?: number;
};

const operationalSignals = [
  { icon: Activity, label: "No active moments yet" },
  { icon: Stethoscope, label: "No runtime available" },
  { icon: CircleDot, label: "No patterns discovered" },
  { icon: Lightbulb, label: "No guidance generated" },
] as const;

const learnChips = [
  { icon: Minimize2, label: "Pressure" },
  { icon: Stethoscope, label: "Recovery" },
  { icon: TrendingUp, label: "Progress" },
  { icon: Sparkles, label: "Experiences" },
  { icon: Users, label: "Relationships" },
] as const;

function glassCardStyle(tokens: ContextThemeTokens) {
  return personalGlassCardStyle(tokens);
}

export function PulseEmpty({
  onCreateMoment,
  onContinueSetup,
  mode = "no_moment",
  momentTypeLabel = "Life Operations",
  bottomPadding = 0,
}: PulseEmptyProps) {
  const isDraftResume = mode === "draft_resume";
  const primaryAction = isDraftResume && onContinueSetup ? onContinueSetup : onCreateMoment;
  const primaryLabel = isDraftResume
    ? `Continue ${momentTypeLabel} Setup`
    : "Create My First Moment";
  const previewHint = isDraftResume
    ? "Your setup is in progress — finish to activate your pulse."
    : "Your future pulse will form here.";
  const signals = isDraftResume
    ? [
        { icon: Activity, label: "Setup in progress" },
        { icon: Stethoscope, label: "Not activated yet" },
        { icon: CircleDot, label: "Complete setup to begin" },
        { icon: Lightbulb, label: "Rhythm unlocks after activation" },
      ]
    : operationalSignals;
  const tokens = useThemeTokens();
  const { colors, spacing, shadows, gradients } = tokens;

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={{
        background: colors.background,
        color: colors.textPrimary,
        paddingBottom: bottomPadding || spacing.md,
      }}
    >
      <PersonalAtmosphericOrbs />

      <div
        className="relative mx-auto flex w-full max-w-[600px] flex-col gap-4 px-5 py-6 md:max-w-[1080px] md:gap-4 md:px-20 md:py-8"
      >
        <section className="space-y-3 py-4 text-center md:py-6">
          <h2
            className="text-[28px] font-bold leading-9 tracking-tight md:text-[32px] md:leading-10"
            style={{ color: colors.textPrimary }}
          >
            Your Personal Operating System
          </h2>
          <p
            className="mx-auto max-w-[280px] text-sm leading-5 opacity-70 md:max-w-md md:text-base"
            style={{ color: colors.textSecondary }}
          >
            Life moves through commitments, money, energy, experiences, and relationships.
          </p>
        </section>

        <button
          type="button"
          onClick={onCreateMoment}
          className="flex w-full items-center justify-between rounded-[2rem] p-6 text-left transition-colors"
          style={{
            ...glassCardStyle(tokens),
            borderColor: "rgba(108, 78, 242, 0.2)",
            color: colors.textPrimary,
          }}
        >
          <div>
            <h4 className="text-[17px] font-semibold leading-[22px]">Start Your Journey</h4>
            <p className="text-xs font-medium opacity-70" style={{ color: colors.textSecondary }}>
              Activate your personal operating system.
            </p>
          </div>
          <div
            className="flex size-12 items-center justify-center rounded-full"
            style={{
              background: colors.primaryContainer,
              color: colors.brandOnPrimary,
              boxShadow: `0 0 20px ${shadows.glowColor}`,
            }}
          >
            <ArrowRight className="size-5" />
          </div>
        </button>

        <section
          className="relative flex min-h-[240px] w-full flex-col items-center justify-center overflow-hidden rounded-[2rem] md:min-h-[280px]"
          style={glassCardStyle(tokens)}
        >
          <img
            src="/personal/pulse-hero.jpg"
            alt=""
            className="absolute inset-0 size-full object-cover opacity-50"
          />
          <div
            className="absolute inset-0"
            style={{
              background: `linear-gradient(to bottom, transparent, color-mix(in srgb, ${colors.background} 40%, transparent), color-mix(in srgb, ${colors.background} 80%, transparent))`,
            }}
          />
          <div className="relative z-10 px-8 pb-8 pt-12 text-center">
            <p className="mb-8 text-[17px] font-semibold leading-[22px] md:mb-10">
              {previewHint}
            </p>
            <button
              type="button"
              onClick={primaryAction}
              className="mx-auto flex items-center gap-2 rounded-xl px-8 py-3 text-[17px] font-semibold transition-transform hover:scale-[1.02] active:scale-95"
              style={{
                background: colors.primaryContainer,
                color: colors.brandOnPrimary,
                boxShadow: `0 10px 30px ${shadows.glowColor}`,
              }}
            >
              <PlusCircle className="size-5" />
              {primaryLabel}
            </button>
          </div>
        </section>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 lg:gap-6">
          <section className="rounded-[2rem] p-6" style={glassCardStyle(tokens)}>
            <PulseSectionHeader title="Operational Signals" badge="SYSTEM 01" tokens={tokens} />
            <div className="mt-6 space-y-5 opacity-40">
              {signals.map((signal) => (
                <div key={signal.label} className="flex items-center gap-4">
                  <signal.icon className="size-5" style={{ color: colors.brandPrimary }} />
                  <p className="text-sm leading-5">{signal.label}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-[2rem] p-6" style={glassCardStyle(tokens)}>
            <PulseSectionHeader title="What Momentra Learns" badge="INTEL 02" tokens={tokens} />
            <div className="mb-6 mt-6 flex flex-wrap gap-2">
              {learnChips.map((chip) => (
                <div
                  key={chip.label}
                  className="flex items-center gap-2 rounded-full border border-white/5 px-4 py-2"
                  style={{ background: colors.surfaceHigh }}
                >
                  <chip.icon className="size-4" style={{ color: colors.brandPrimary }} />
                  <span className="text-xs font-medium">{chip.label}</span>
                </div>
              ))}
            </div>
            <p className="text-sm italic opacity-60" style={{ color: colors.textSecondary }}>
              Start your journey to unlock system introspection.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

function PulseSectionHeader({
  title,
  badge,
  tokens,
}: {
  title: string;
  badge: string;
  tokens: ContextThemeTokens;
}) {
  return (
    <div className="flex items-start justify-between">
      <span
        className="text-[10px] font-bold tracking-[0.2em] opacity-60"
        style={{ color: tokens.colors.textSecondary }}
      >
        {title.toUpperCase()}
      </span>
      <span
        className="rounded px-2 py-0.5 text-[10px] font-bold"
        style={{
          background: tokens.colors.surfaceHigh,
          color: tokens.colors.textSecondary,
        }}
      >
        {badge}
      </span>
    </div>
  );
}

"use client";

import type { CSSProperties } from "react";
import {
  Activity,
  ArrowRight,
  BatteryCharging,
  Brain,
  Heart,
  Lock,
  Moon,
  PlusCircle,
  Rocket,
  Smile,
  Sparkles,
  Target,
  TrendingUp,
  Users,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  glassCardStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import { LifeGraphVisual } from "@/components/personal/shared/LifeGraphVisual";
import type { ContextThemeTokens } from "@/lib/contextTokens";

type LifeEmptyProps = {
  onCreateMoment: () => void;
  onBeginLifeOps?: () => void;
  bottomPadding?: number;
};

type MomentCard = {
  title: string;
  description: string;
  icon: LucideIcon;
  accent: "tertiary" | "secondary" | "primary" | "error";
};

const momentCards: MomentCard[] = [
  {
    title: "Life Operations",
    description: "Understand stress, capacity, money pressure, recovery, and daily rhythm.",
    icon: Target,
    accent: "tertiary",
  },
  {
    title: "Future Building",
    description: "Track growth, learning, milestones, investments, and future direction.",
    icon: TrendingUp,
    accent: "secondary",
  },
  {
    title: "Lifestyle",
    description: "Learn how experiences, wellbeing, creativity, and spending create fulfilment.",
    icon: Moon,
    accent: "primary",
  },
  {
    title: "Relationships",
    description: "See how time, support, shared experiences, and money strengthen connection.",
    icon: Heart,
    accent: "error",
  },
];

const learnSteps = [
  { icon: Target, label: "Setup\nMoments" },
  { icon: PlusCircle, label: "Log Quick\nAdds" },
  { icon: Zap, label: "Pulse\nUpdates" },
  { icon: Sparkles, label: "Live\nRecs" },
  { icon: Brain, label: "Memory\nPatterns" },
  { icon: Activity, label: "Life Graph\nForms" },
] as const;

const unlockTiles = ["Stress", "Capacity", "Growth", "Fulfillment"] as const;

const whyTrack = [
  { title: "Stress", description: "Your pressure and mental load.", icon: Activity, accent: "error" },
  {
    title: "Capacity",
    description: "Your energy and recovery.",
    icon: BatteryCharging,
    accent: "tertiary",
  },
  {
    title: "Growth",
    description: "Your progress and future momentum.",
    icon: Rocket,
    accent: "secondary",
  },
  {
    title: "Fulfillment",
    description: "Your meaning and happiness.",
    icon: Smile,
    accent: "primary",
  },
] as const;

const setupChips = [
  { title: "Life Operations", icon: Activity, accent: "tertiary" as const },
  { title: "Future Building", icon: TrendingUp, accent: "secondary" as const },
  { title: "Lifestyle", icon: Moon, accent: "primary" as const },
  { title: "Relationships", icon: Users, accent: "error" as const },
];

function accentColor(tokens: ContextThemeTokens, accent: MomentCard["accent"]): string {
  switch (accent) {
    case "tertiary":
      return tokens.colors.brandTertiary;
    case "secondary":
      return tokens.colors.textSecondary;
    case "error":
      return tokens.colors.error;
    default:
      return tokens.colors.brandPrimary;
  }
}

const EMPTY_SATELLITES = [
  { moment_type_code: "LIFE_OPERATIONS", label: "Life Operations", score: null, color_token: "node_blue" },
  { moment_type_code: "FUTURE_BUILDING", label: "Future Building", score: null, color_token: "node_green" },
  { moment_type_code: "LIFESTYLE", label: "Lifestyle", score: null, color_token: "node_orange" },
  { moment_type_code: "RELATIONSHIPS", label: "Relationships", score: null, color_token: "node_pink" },
] as const;

export function LifeEmpty({
  onCreateMoment,
  onBeginLifeOps,
  bottomPadding = 0,
}: LifeEmptyProps) {
  const tokens = useThemeTokens();
  const { colors, shadows, gradients } = tokens;
  const setupLifeOps = onBeginLifeOps ?? onCreateMoment;

  const glowButtonStyle: CSSProperties = {
    background: colors.primaryContainer,
    color: colors.brandOnPrimary,
    boxShadow: `0 0 30px ${shadows.glowColor}`,
  };

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <div
        className="pointer-events-none absolute -left-20 -top-20 size-[400px] rounded-full blur-[80px]"
        style={{ background: gradients.brandFadeStart }}
      />
      <div
        className="pointer-events-none absolute right-0 top-1/3 size-[300px] rounded-full blur-[70px]"
        style={{ background: gradients.brandFadeEnd }}
      />

      <div className="relative mx-auto flex w-full max-w-[1080px] flex-col gap-4 px-5 py-6 md:px-20 md:py-8">
        <section className="space-y-2">
          <h2 style={{ ...personalTypography.heroTitle, color: colors.textPrimary }}>Life</h2>
          <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
            Money follows moments. We help you understand life.
          </p>
        </section>

        <section
          className="relative flex flex-col items-center gap-8 overflow-hidden rounded-xl p-6 md:flex-row md:p-8"
          style={glassCardStyle(tokens)}
        >
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background: `radial-gradient(circle at center, color-mix(in srgb, ${colors.brandPrimary} 15%, transparent) 0%, transparent 70%)`,
            }}
          />
          <div className="relative z-10 max-w-md space-y-4">
            <h3 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
              Your Life Graph Is Waiting
            </h3>
            <p className="text-sm leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
              Activate your personal moments and log real decisions so Momentra can understand how
              money, stress, growth, lifestyle, and relationships shape your life.
            </p>
          </div>
          <div className="relative z-10 w-full md:w-auto">
            <LifeGraphVisual tokens={tokens} empty satelliteScores={[...EMPTY_SATELLITES]} />
          </div>
        </section>

        <section className="space-y-4">
          <header>
            <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
              Build Your Personal Life Map
            </h3>
            <p className="text-xs opacity-60" style={{ color: colors.textSecondary }}>
              Set up all 4 moments to unlock your full life intelligence.
            </p>
          </header>
          <div className="space-y-3">
            {momentCards.map((card, index) => {
              const accent = accentColor(tokens, card.accent);
              const onSetup = index === 0 ? setupLifeOps : onCreateMoment;
              return (
                <div
                  key={card.title}
                  className="flex flex-col gap-4 rounded-xl p-5 sm:flex-row sm:items-center"
                  style={glassCardStyle(tokens)}
                >
                  <div
                    className="flex size-12 shrink-0 items-center justify-center rounded-lg border"
                    style={{
                      borderColor: `color-mix(in srgb, ${accent} 20%, transparent)`,
                      background: `color-mix(in srgb, ${accent} 15%, transparent)`,
                      color: accent,
                    }}
                  >
                    <card.icon className="size-6" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="font-bold" style={{ color: colors.textPrimary }}>
                      {card.title}
                    </div>
                    <p className="text-sm opacity-60" style={{ color: colors.textSecondary }}>
                      {card.description}
                    </p>
                  </div>
                  <span
                    className="shrink-0 rounded px-2 py-1 text-[11px] font-bold"
                    style={{
                      color: `color-mix(in srgb, ${colors.error} 60%, transparent)`,
                      background: `color-mix(in srgb, ${colors.error} 10%, transparent)`,
                    }}
                  >
                    Not Activated
                  </span>
                  <button
                    type="button"
                    onClick={onSetup}
                    className="shrink-0 rounded-lg px-6 py-2 text-sm font-bold transition-transform active:scale-95"
                    style={glowButtonStyle}
                  >
                    Set Up
                  </button>
                </div>
              );
            })}
          </div>
        </section>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <section className="space-y-6 rounded-xl p-6 md:col-span-2" style={glassCardStyle(tokens)}>
            <header>
              <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
                What Momentra Will Learn
              </h3>
              <p className="text-xs opacity-60" style={{ color: colors.textSecondary }}>
                Your life intelligence forms when you log real moments.
              </p>
            </header>
            <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2">
              {learnSteps.map((step, index) => (
                <div key={step.label} className="flex items-center gap-2">
                  <div className="flex min-w-[70px] flex-col items-center gap-3">
                    <div
                      className="flex size-10 items-center justify-center rounded-full border border-white/5"
                      style={{ background: colors.surfaceHigh }}
                    >
                      <step.icon className="size-4" style={{ color: colors.brandPrimary }} />
                    </div>
                    <span className="whitespace-pre-line text-center text-[10px] font-semibold leading-tight">
                      {step.label}
                    </span>
                  </div>
                  {index < learnSteps.length - 1 ? (
                    <ArrowRight className="size-4 shrink-0 opacity-20" />
                  ) : null}
                </div>
              ))}
            </div>
          </section>

          <section
            className="relative flex flex-col items-center justify-center overflow-hidden rounded-xl p-6 text-center"
            style={glassCardStyle(tokens)}
          >
            <div
              className="pointer-events-none absolute inset-0 opacity-40"
              style={{ background: `color-mix(in srgb, ${colors.brandPrimary} 5%, transparent)` }}
            />
            <h3 className="relative z-10 mb-4" style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
              Future Life Health
            </h3>
            <div className="relative z-10 mb-4 flex size-32 items-center justify-center">
              <svg className="absolute inset-0 -rotate-90" viewBox="0 0 128 128">
                <circle cx="64" cy="64" r="58" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
                <circle
                  cx="64"
                  cy="64"
                  r="58"
                  fill="none"
                  stroke={colors.brandPrimary}
                  strokeWidth="8"
                  strokeDasharray={`${2 * Math.PI * 58}`}
                  strokeDashoffset={`${2 * Math.PI * 58}`}
                />
              </svg>
              <div className="flex flex-col items-center">
                <span className="text-3xl font-bold">0</span>
                <span className="text-xs opacity-40">/100</span>
              </div>
            </div>
            <p className="relative z-10 max-w-[140px] text-[10px] opacity-60" style={{ color: colors.textSecondary }}>
              Start logging moments to build your life graph.
            </p>
          </section>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <section className="space-y-6 rounded-xl p-6" style={glassCardStyle(tokens)}>
            <header>
              <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
                Life Intelligence Unlocks
              </h3>
              <p className="text-xs opacity-60" style={{ color: colors.textSecondary }}>
                Complete setup and activity to unlock.
              </p>
            </header>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {unlockTiles.map((tile) => (
                <div
                  key={tile}
                  className="flex aspect-square flex-col items-center justify-center gap-2 rounded-lg opacity-50 grayscale"
                  style={glassCardStyle(tokens)}
                >
                  <Lock className="size-5" />
                  <span className="text-[10px] font-bold">{tile}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="space-y-5 rounded-xl p-6" style={glassCardStyle(tokens)}>
            <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
              Why Momentra Tracks These
            </h3>
            <div className="grid gap-4">
              {whyTrack.map((item) => (
                <div key={item.title} className="flex items-start gap-4">
                  <item.icon className="mt-1 size-5 shrink-0" style={{ color: accentColor(tokens, item.accent) }} />
                  <div>
                    <div className="text-xs font-bold">{item.title}</div>
                    <p className="text-[11px] opacity-70" style={{ color: colors.textSecondary }}>
                      {item.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        <section className="flex flex-col items-center space-y-8 py-8">
          <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
            Start With One Action
          </h3>
          <button
            type="button"
            onClick={onCreateMoment}
            className="flex w-full max-w-lg items-center justify-center gap-3 rounded-xl py-4 text-base font-bold transition-transform active:scale-95"
            style={glowButtonStyle}
          >
            <PlusCircle className="size-5" />
            Create First Personal Moment
          </button>
          <div className="text-xs font-bold uppercase tracking-widest opacity-40">
            Or set up a moment to begin
          </div>
          <div className="flex flex-wrap justify-center gap-4">
            {setupChips.map((chip, index) => {
              const onClick = index === 0 ? setupLifeOps : onCreateMoment;
              return (
                <button
                  key={chip.title}
                  type="button"
                  onClick={onClick}
                  className="flex items-center gap-4 rounded-xl px-6 py-4 transition-transform active:scale-95"
                  style={glassCardStyle(tokens)}
                >
                  <chip.icon className="size-5" style={{ color: accentColor(tokens, chip.accent) }} />
                  <div className="text-left">
                    <div className="text-[10px] font-bold uppercase opacity-40">Set Up</div>
                    <div className="text-sm font-bold">{chip.title}</div>
                  </div>
                </button>
              );
            })}
          </div>
        </section>

        <footer className="group relative overflow-hidden rounded-2xl p-8" style={glassCardStyle(tokens)}>
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background: `linear-gradient(to right, color-mix(in srgb, ${colors.brandPrimary} 5%, transparent), color-mix(in srgb, ${colors.textSecondary} 5%, transparent))`,
            }}
          />
          <div className="relative z-10 flex flex-col items-center gap-10 md:flex-row">
            <div
              className="flex size-16 shrink-0 items-center justify-center rounded-2xl border border-white/5 shadow-inner"
              style={{ background: colors.surfaceHigh }}
            >
              <Heart className="size-8" style={{ color: colors.brandPrimary }} fill="currentColor" />
            </div>
            <div className="flex-1 text-center md:text-left">
              <p className="mb-2" style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
                Life is a series of moments.
              </p>
              <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
                Momentra learns from those moments and helps you understand how your financial decisions
                shape your actual life.
              </p>
            </div>
            <div className="relative hidden h-24 w-48 overflow-hidden rounded-xl opacity-30 grayscale transition-all duration-700 group-hover:opacity-100 group-hover:grayscale-0 md:block">
              <img
                src="/personal/life-footer-landscape.jpg"
                alt=""
                className="size-full object-cover"
              />
              <div
                className="absolute inset-0"
                style={{
                  background: `linear-gradient(to top, ${colors.background}, transparent)`,
                }}
              />
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

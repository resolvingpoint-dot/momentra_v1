"use client";

import {
  Brain,
  ChartLine,
  LineChart,
  RefreshCw,
  Sparkles,
  Star,
  Users,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { glassCardStyle, scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";

type MemoryEmptyProps = {
  onCreateMoment: () => void;
  momentTypeLabel?: string;
  bottomPadding?: number;
  maturationProgress?: number;
};

const modules = [
  { title: "Patterns", description: "Analyzing recurring behaviors and cognitive loops across captured inputs.", icon: LineChart, progress: 12 },
  { title: "Recovery Anchors", description: "Identifying effective reset patterns and emotional stabilizers.", icon: Sparkles, progress: 8 },
  { title: "Progress Signals", description: "Mapping indicators of momentum and intentional growth vectors.", icon: ChartLine, progress: 0 },
  { title: "Experience Highlights", description: "Extracting peak emotional resonance moments and core memories.", icon: Star, progress: 0 },
  { title: "Relationship Learning", description: "Synthesizing lessons from meaningful connections and social dynamics.", icon: Users, progress: 0 },
] as const;

export function MemoryEmpty({
  onCreateMoment,
  bottomPadding = 0,
  maturationProgress = 0,
}: MemoryEmptyProps) {
  const tokens = useThemeTokens();
  const { colors, shadows, gradients } = tokens;

  return (
    <div
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

      <div className="relative mx-auto flex w-full max-w-[600px] flex-col gap-6 px-5 py-6 md:max-w-[1080px] md:px-20 md:py-8">
        <section className="text-center">
          <div className="relative -mx-5 mb-6 md:-mx-20">
            <img
              src="/personal/memory-brain.jpg"
              alt=""
              className="h-[220px] w-full object-cover opacity-90 md:h-[260px]"
            />
            <div
              className="absolute inset-0"
              style={{
                background: `linear-gradient(to bottom, transparent, color-mix(in srgb, ${colors.background} 85%, transparent))`,
              }}
            />
            <div className="absolute right-5 top-4 flex size-24 flex-col items-center justify-center opacity-80">
              <svg className="absolute inset-0 -rotate-90" viewBox="0 0 96 96">
                <circle cx="48" cy="48" r="40" fill="none" stroke={colors.surfaceHigh} strokeWidth="3" />
                <circle
                  cx="48"
                  cy="48"
                  r="40"
                  fill="none"
                  stroke={colors.brandPrimary}
                  strokeWidth="3"
                  strokeLinecap="round"
                  strokeDasharray={`${2 * Math.PI * 40 * maturationProgress} ${2 * Math.PI * 40}`}
                />
              </svg>
              <span className="relative text-lg font-bold" style={{ color: colors.brandPrimary }}>
                {Math.round(maturationProgress * 100)}%
              </span>
              <span className="relative text-[8px] font-bold tracking-widest opacity-60">ACTIVE</span>
            </div>
          </div>
          <h2 className="mb-2 text-[28px] font-bold text-white">Growing Intelligence</h2>
          <p className="mx-auto max-w-sm text-sm opacity-80" style={{ color: colors.textSecondary }}>
            Active learning in progress. System evolving with every moment captured.
          </p>
        </section>

        <section className="space-y-5 rounded-2xl p-6 text-center" style={glassCardStyle(tokens)}>
          <div
            className="mx-auto flex size-12 items-center justify-center rounded-full"
            style={{ background: `color-mix(in srgb, ${colors.brandPrimary} 15%, transparent)` }}
          >
            <Brain className="size-6" style={{ color: colors.brandPrimary }} />
          </div>
          <div>
            <h3 className="mb-1 text-[17px] font-semibold text-white">Intelligence is forming.</h3>
            <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
              Your digital subconscious requires more data points. Capture moments to accelerate system
              maturation.
            </p>
          </div>
          <button
            type="button"
            onClick={onCreateMoment}
            className="w-full rounded-xl px-8 py-4 text-[17px] font-bold transition-transform hover:scale-[1.02] active:scale-95"
            style={{
              background: colors.primaryContainer,
              color: colors.brandOnPrimary,
              boxShadow: `0 8px 20px ${shadows.glowColor}`,
            }}
          >
            Initialize New Memory
          </button>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <span
              className="text-xs font-bold tracking-widest opacity-80"
              style={{ color: colors.textSecondary }}
            >
              INTELLIGENCE MODULES
            </span>
            <span
              className="flex items-center gap-1.5 text-[11px] font-bold"
              style={{ color: colors.brandPrimary }}
            >
              <RefreshCw className="size-3.5 animate-spin" />
              SYNCING...
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {modules.map((module) => (
              <div
                key={module.title}
                className="flex min-h-[144px] flex-col gap-3 rounded-xl p-4 md:min-h-[144px]"
                style={glassCardStyle(tokens)}
              >
                <div
                  className="flex size-10 shrink-0 items-center justify-center rounded-lg"
                  style={{ background: colors.surfaceHigh }}
                >
                  <module.icon className="size-5 opacity-70" style={{ color: colors.textSecondary }} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <h4 className="text-sm font-bold text-white">{module.title}</h4>
                    <span className="text-[9px] font-bold tracking-widest opacity-40">LOCKED</span>
                  </div>
                  <p
                    className="mb-3 line-clamp-2 text-[11px] leading-tight opacity-60"
                    style={{ color: colors.textSecondary }}
                  >
                    {module.description}
                  </p>
                  <div
                    className="h-1 w-full overflow-hidden rounded-full"
                    style={{ background: colors.surfaceHigh }}
                  >
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${module.progress}%`,
                        background: `color-mix(in srgb, ${colors.brandPrimary} 30%, transparent)`,
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

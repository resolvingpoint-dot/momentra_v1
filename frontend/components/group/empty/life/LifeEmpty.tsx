"use client";

import type { CSSProperties } from "react";
import { Lock, PlusCircle } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupLifeGraphVisual, GroupLifeHeroSection } from "@/components/group/shared/GroupLifeGraphVisual";
import { groupTypography } from "@/lib/group/groupTypography";
import { groupGlassCardStyle, groupScrollShellStyle } from "@/components/group/empty/shared/emptyStyles";
import {
  GROUP_LIFE_DIMENSIONS,
  GROUP_LIFE_HERO_SUBTITLE,
  GROUP_LIFE_PRIMARY_CTA,
  GROUP_LIFE_SECONDARY_CTA,
  GROUP_LIFE_UNLOCKS,
  GROUP_LIFE_UNLOCKS_FOOTNOTE,
  GROUP_LIFE_UNLOCKS_TITLE,
  GROUP_LIFE_WHY_TITLE,
} from "@/lib/group/groupLifeCopy";

type LifeEmptyProps = {
  onCreateMoment: () => void;
  bottomPadding?: number;
};

export function LifeEmpty({ onCreateMoment, bottomPadding = 0 }: LifeEmptyProps) {
  const tokens = useThemeTokens();
  const { colors, shadows, gradients } = tokens;

  const primaryCtaStyle: CSSProperties = {
    background: `linear-gradient(135deg, ${gradients.heroStart} 0%, ${gradients.heroEnd} 100%)`,
    color: colors.brandOnPrimary,
    boxShadow: `0 10px 40px ${shadows.glowColor}`,
  };

  return (
    <div
      data-momentra-context="group"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={groupScrollShellStyle(tokens, bottomPadding)}
    >
      <GroupLifeHeroSection>
        <GroupLifeGraphVisual className="absolute inset-0 size-full" />
      </GroupLifeHeroSection>

      <div
        className="relative mx-auto flex w-full max-w-[600px] flex-col px-5 py-6 md:max-w-[1080px] md:px-8 md:py-8"
        style={{ gap: tokens.spacing.sectionGap }}
      >
        <section className="space-y-4 px-2 text-center">
          <h1 style={{ ...groupTypography.brandTitle, fontSize: 28, color: colors.textPrimary }}>
            Your Group{" "}
            <span style={{ color: colors.brandPrimary }}>Life Graph</span> Is Waiting
          </h1>
          <p className="mx-auto max-w-sm text-base leading-relaxed" style={{ color: colors.textSecondary }}>
            {GROUP_LIFE_HERO_SUBTITLE}
          </p>
        </section>

        <section data-group-life-dimensions>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {GROUP_LIFE_DIMENSIONS.map((dimension) => {
              const Icon = dimension.icon;
              return (
                <div
                  key={dimension.code}
                  className="flex flex-col items-center rounded-xl p-3 text-center"
                  style={{
                    ...groupGlassCardStyle(tokens),
                    borderTop: `4px solid ${dimension.accent}`,
                  }}
                >
                  <div
                    className="mb-2 flex size-8 items-center justify-center rounded-lg"
                    style={{ background: `${dimension.accent}1A` }}
                  >
                    <Icon className="size-5" style={{ color: dimension.accent }} />
                  </div>
                  <h3 className="mb-1 text-[11px] font-semibold leading-tight" style={{ color: colors.textPrimary }}>
                    {dimension.title}
                  </h3>
                  <p
                    className="mb-2 text-[9px] font-medium uppercase tracking-tighter"
                    style={{ color: `${dimension.accent}99` }}
                  >
                    Inactive
                  </p>
                  <button
                    type="button"
                    onClick={onCreateMoment}
                    className="w-full rounded-full border py-1 text-[10px] font-bold uppercase tracking-wider transition-colors active:scale-95"
                    style={{
                      borderColor: `${dimension.accent}4D`,
                      color: dimension.accent,
                    }}
                  >
                    Set Up
                  </button>
                </div>
              );
            })}
          </div>
        </section>

        <section className="space-y-6">
          <h2 className="px-2 text-2xl font-semibold" style={{ color: colors.textPrimary }}>{GROUP_LIFE_UNLOCKS_TITLE}</h2>
          <div className="grid grid-cols-2 gap-4">
            {GROUP_LIFE_UNLOCKS.map((label, index) => (
              <div
                key={label}
                className={`group relative flex flex-col items-center justify-center overflow-hidden rounded-3xl p-6 text-center ${
                  index === GROUP_LIFE_UNLOCKS.length - 1 ? "col-span-2" : ""
                }`}
                style={groupGlassCardStyle(tokens)}
              >
                <div className="pointer-events-none absolute inset-0 bg-violet-500/5 opacity-0 transition-opacity group-hover:opacity-100" />
                <Lock className="mb-3 size-8" style={{ color: colors.textSecondary, opacity: 0.4 }} />
                <span className="text-xs font-medium" style={{ color: colors.textSecondary }}>{label}</span>
              </div>
            ))}
          </div>
          <p
            className="text-center text-[11px] italic"
            style={{ color: `${colors.brandPrimary}99` }}
          >
            {GROUP_LIFE_UNLOCKS_FOOTNOTE}
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="px-2 text-2xl font-semibold" style={{ color: colors.textPrimary }}>{GROUP_LIFE_WHY_TITLE}</h2>
          <div className="space-y-3">
            {GROUP_LIFE_DIMENSIONS.map((dimension) => {
              const Icon = dimension.icon;
              return (
                <div
                  key={`why-${dimension.code}`}
                  className="flex items-center gap-4 rounded-xl p-4"
                  style={{
                    ...groupGlassCardStyle(tokens),
                    border: "1px solid rgba(255, 255, 255, 0.05)",
                  }}
                >
                  <div
                    className="flex size-10 shrink-0 items-center justify-center rounded-lg"
                    style={{ background: `${dimension.accent}1A` }}
                  >
                    <Icon className="size-5" style={{ color: dimension.accent }} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold" style={{ color: colors.textPrimary }}>{dimension.shortTitle}</h4>
                    <p className="text-xs" style={{ color: colors.textSecondary, opacity: 0.6 }}>{dimension.whyDescription}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="space-y-4 pb-8">
          <button
            type="button"
            onClick={onCreateMoment}
            className="flex w-full items-center justify-center gap-2 rounded-full py-5 text-sm font-bold uppercase tracking-widest transition-transform active:scale-95"
            style={primaryCtaStyle}
          >
            <PlusCircle className="size-5" />
            {GROUP_LIFE_PRIMARY_CTA}
          </button>
          <button
            type="button"
            onClick={() => {
              document
                .querySelector('[data-group-life-dimensions]')
                ?.scrollIntoView({ behavior: "smooth", block: "center" });
            }}
            className="w-full rounded-full border py-4 text-sm font-medium uppercase tracking-wider transition-colors active:scale-95 active:bg-white/5"
            style={{ borderColor: colors.border, color: colors.textPrimary }}
          >
            {GROUP_LIFE_SECONDARY_CTA}
          </button>
        </section>
      </div>
    </div>
  );
}

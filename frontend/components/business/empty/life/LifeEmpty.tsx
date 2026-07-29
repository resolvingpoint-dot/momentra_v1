"use client";

import type { CSSProperties } from "react";
import {
  ArrowRight,
  CalendarPlus,
  ChevronRight,
  Eye,
  Handshake,
  Heart,
  IndianRupee,
  Plus,
  Settings,
  Star,
  TrendingUp,
  UserPlus,
  Users,
  type LucideIcon,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { businessCardStyle, businessScrollShellStyle } from "@/components/business/empty/shared/emptyStyles";
import { BUSINESS_LIFE_EMPTY_COPY } from "@/lib/business/businessLifeEmptyCopy";
import { BusinessLifeHeroVisual } from "@/components/business/empty/life/BusinessLifeHeroVisual";

type LifeEmptyProps = {
  onCreateMoment: () => void;
  bottomPadding?: number;
};

const futureIcons: LucideIcon[] = [Users, IndianRupee, Settings, Handshake];
const stepIcons: LucideIcon[] = [CalendarPlus, UserPlus, Settings, TrendingUp, Star];
const benefitIcons: LucideIcon[] = [Eye, Users, Handshake, Heart];

function darkCardStyle(): CSSProperties {
  return {
    background: "rgba(255, 255, 255, 0.03)",
    border: "1px solid rgba(255, 255, 255, 0.05)",
  };
}

export function LifeEmpty({ onCreateMoment, bottomPadding = 0 }: LifeEmptyProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const copy = BUSINESS_LIFE_EMPTY_COPY;

  const primaryCtaStyle: CSSProperties = {
    background: colors.primaryContainer,
    color: colors.brandOnPrimary,
    boxShadow: "0 10px 30px rgba(91, 92, 235, 0.25)",
  };

  const gradientTitleStyle: CSSProperties = {
    background: "linear-gradient(to right, #a855f7, #6d5dfc)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
    backgroundClip: "text",
  };

  return (
    <div
      data-momentra-context="business"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={businessScrollShellStyle(tokens, bottomPadding)}
    >
      <div className="relative mx-auto flex w-full max-w-[600px] flex-col gap-8 px-5 py-6 md:max-w-[1080px] md:px-8">
        {/* Hero */}
        <section className="space-y-4">
          <div>
            <p className="text-sm font-medium opacity-70" style={{ color: colors.textSecondary }}>
              {copy.hero.eyebrow}
            </p>
            <h2 className="text-[28px] font-bold leading-9 tracking-tight md:text-[32px]" style={gradientTitleStyle}>
              {copy.hero.title}
            </h2>
          </div>
          <p className="max-w-[280px] text-xs leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
            {copy.hero.subtitle}
          </p>
          <BusinessLifeHeroVisual />
          <button
            type="button"
            onClick={onCreateMoment}
            className="flex w-full items-center justify-center gap-2 rounded-xl px-6 py-4 text-sm font-bold transition-transform active:scale-[0.98]"
            style={primaryCtaStyle}
          >
            {copy.hero.ctaLabel}
            <Plus className="size-5" />
          </button>
        </section>

        {/* Your Future Business */}
        <section className="space-y-4">
          <h3 className="text-base font-semibold">{copy.futureBusiness.sectionTitle}</h3>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {copy.futureBusiness.cards.map((card, i) => {
              const Icon = futureIcons[i] ?? Users;
              return (
                <div
                  key={card.title}
                  className="flex flex-col items-center space-y-2 rounded-xl p-3 text-center"
                  style={darkCardStyle()}
                >
                  <div
                    className="flex size-10 items-center justify-center rounded-lg"
                    style={{ background: card.accentBg, color: card.accent }}
                  >
                    {card.title === "Financial Strength" ? (
                      <span className="text-xl font-bold">₹</span>
                    ) : (
                      <Icon className="size-6" />
                    )}
                  </div>
                  <p className="text-[10px] font-bold leading-tight">{card.title}</p>
                  <p className="text-[8px] leading-tight opacity-60" style={{ color: colors.textSecondary }}>
                    {card.description}
                  </p>
                </div>
              );
            })}
          </div>
        </section>

        {/* How Business Life Works */}
        <section className="space-y-4">
          <h3 className="text-base font-semibold">{copy.howItWorks.sectionTitle}</h3>
          <div className="relative flex items-start justify-between pt-2">
            <div className="absolute left-6 right-6 top-6 z-0 flex items-center justify-between px-4 opacity-40">
              {Array.from({ length: 4 }).map((_, i) => (
                <ChevronRight key={i} className="size-4" style={{ color: colors.brandPrimary }} />
              ))}
            </div>
            {copy.howItWorks.steps.map((step, i) => {
              const Icon = stepIcons[i] ?? CalendarPlus;
              return (
                <div key={step.label} className="relative z-10 flex w-1/5 flex-col items-center gap-2">
                  <div
                    className="flex size-10 items-center justify-center rounded-lg border"
                    style={{
                      background: `${step.accent}30`,
                      borderColor: `${step.accent}66`,
                      color: step.accent,
                    }}
                  >
                    <Icon className="size-5" />
                  </div>
                  <p className="whitespace-pre-line text-center text-[9px] font-medium leading-tight opacity-80">
                    {step.label}
                  </p>
                </div>
              );
            })}
          </div>
        </section>

        {/* Why Teams Use Life */}
        <section className="space-y-4">
          <h3 className="text-base font-semibold">{copy.whyTeams.sectionTitle}</h3>
          <div className="grid grid-cols-2 gap-4">
            {copy.whyTeams.cards.map((card, i) => {
              const Icon = benefitIcons[i] ?? Eye;
              return (
                <div key={card.title} className="flex flex-col gap-3 rounded-2xl p-4" style={darkCardStyle()}>
                  <div
                    className="flex size-8 items-center justify-center rounded-full"
                    style={{ background: card.accentBg, color: card.accent }}
                  >
                    <Icon className="size-4" />
                  </div>
                  <div>
                    <p className="mb-1 text-xs font-bold">{card.title}</p>
                    <p className="text-[10px] leading-tight opacity-60" style={{ color: colors.textSecondary }}>
                      {card.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Footer */}
        <section>
          <div
            className="relative flex flex-col gap-4 overflow-hidden rounded-3xl p-6"
            style={{
              background: "linear-gradient(135deg, #1e1b4b 0%, #0d141d 100%)",
              border: "1px solid rgba(109, 93, 252, 0.2)",
            }}
          >
            <div className="pointer-events-none absolute -bottom-4 -left-4 opacity-20">
              <TrendingUp className="size-32 rotate-45" style={{ color: colors.brandPrimary }} />
            </div>
            <div className="relative z-10 space-y-2 pr-12">
              <h4 className="text-xl font-bold leading-tight">{copy.footer.title}</h4>
              <p className="text-xs opacity-70" style={{ color: colors.textSecondary }}>
                {copy.footer.subtitle}
              </p>
            </div>
            <div className="relative z-10 flex justify-end">
              <button
                type="button"
                onClick={onCreateMoment}
                className="flex items-center gap-2 rounded-xl px-5 py-3 text-xs font-bold"
                style={primaryCtaStyle}
              >
                {copy.footer.ctaLabel}
                <ArrowRight className="size-4" />
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

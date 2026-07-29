"use client";

import {
  ArrowRight,
  Bell,
  Heart,
  Loader2,
  Lightbulb,
  User,
  BarChart3,
  X,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalCreateOptionsResponse } from "@/lib/api/personal";
import {
  PERSONAL_CREATE_HERO_IMAGE,
  createCardImageForType,
} from "@/lib/personal/empty/create/createAssets";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";

type CreateEmptyProps = {
  options: PersonalCreateOptionsResponse | null;
  loadingOptions: boolean;
  creatingTypeCode: PersonalMomentTypeCode | null;
  createError: string | null;
  onBeginMoment: (typeCode: PersonalMomentTypeCode) => void;
  onClose: () => void;
};

type MomentCardMeta = {
  moment_type_code: PersonalMomentTypeCode;
  title: string;
  description: string;
  badge: string;
  tags: string[];
  accent: "primary" | "secondary" | "tertiary" | "warning";
};

const FALLBACK_CARDS: MomentCardMeta[] = [
  {
    moment_type_code: "LIFE_OPERATIONS",
    title: "Life Operations",
    description:
      "Build the foundation for everyday life with routines, responsibilities and essential activities.",
    badge: "Recommended First Moment",
    tags: ["Daily Life", "Home", "Health", "Finances", "Personal Admin"],
    accent: "primary",
  },
  {
    moment_type_code: "FUTURE_BUILDING",
    title: "Future Building",
    description: "Plan the milestones, habits and achievements that shape your future.",
    badge: "Grow With Purpose",
    tags: ["Career", "Learning", "Savings", "Dreams", "Personal Goals"],
    accent: "secondary",
  },
  {
    moment_type_code: "LIFESTYLE",
    title: "Lifestyle",
    description: "Capture the experiences, hobbies and moments that make life enjoyable.",
    badge: "Live Intentionally",
    tags: ["Travel", "Fitness", "Food", "Hobbies", "Wellbeing"],
    accent: "warning",
  },
  {
    moment_type_code: "RELATIONSHIPS",
    title: "Emotional Security",
    description:
      "Strengthen the relationships and support systems that help you feel connected and secure.",
    badge: "Strengthen Connections",
    tags: ["Family", "Friends", "Partner", "Parents", "Children"],
    accent: "tertiary",
  },
];

const BENEFITS = [
  { label: "Your life in one place", Icon: User, tone: "primary" as const },
  { label: "Track your progress", Icon: BarChart3, tone: "secondary" as const },
  { label: "Stay on track", Icon: Bell, tone: "warning" as const },
  { label: "Build lasting memories", Icon: Heart, tone: "tertiary" as const },
];

function accentColor(
  accent: MomentCardMeta["accent"] | "primary" | "secondary" | "tertiary" | "warning",
  colors: ReturnType<typeof useThemeTokens>["colors"],
): string {
  switch (accent) {
    case "secondary":
      return colors.brandSecondary;
    case "tertiary":
      return colors.tertiary;
    case "warning":
      // Lifestyle accent — warm amber (personal warning token is cyan)
      return "#F59E0B";
    default:
      return colors.primaryContainer;
  }
}

export function CreateEmpty({
  options,
  loadingOptions,
  creatingTypeCode,
  createError,
  onBeginMoment,
  onClose,
}: CreateEmptyProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const busy = creatingTypeCode != null || loadingOptions;

  const cards = FALLBACK_CARDS.map((fallback) => {
    const api = options?.cards.find((c) => c.moment_type_code === fallback.moment_type_code);
    return {
      ...fallback,
      title: api?.moment_type_name ?? fallback.title,
      description: api?.create_tagline?.trim() || fallback.description,
      image:
        api?.background_image_url?.trim() ||
        createCardImageForType(fallback.moment_type_code),
      featured: fallback.moment_type_code === "LIFE_OPERATIONS",
    };
  });

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col overflow-y-auto"
      style={{ background: colors.background, color: colors.textPrimary }}
    >
      <div className="mx-auto flex w-full max-w-lg flex-col px-5 pb-12 pt-4">
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="mb-6 flex size-10 items-center justify-center rounded-full self-start"
          style={{
            background: `color-mix(in srgb, ${colors.surfaceContainer} 90%, transparent)`,
          }}
        >
          <X className="size-5" />
        </button>

        <section className="mb-8 flex flex-col gap-6 md:flex-row md:items-center">
          <div className="flex-1">
            <p
              className="mb-3 text-sm font-medium uppercase tracking-wide"
              style={{ color: colors.textSecondary }}
            >
              Choose Your Personal Moment
            </p>
            <h1 className="mb-4 text-[28px] font-bold leading-9 tracking-tight">
              Organize every part of{" "}
              <span style={{ color: colors.primaryContainer }}>your life.</span>
            </h1>
            <p className="text-base leading-relaxed" style={{ color: colors.textSecondary }}>
              Create a personal moment to plan, improve and remember what matters most.
            </p>
          </div>
          <div
            className="hidden aspect-square w-[40%] overflow-hidden rounded-2xl border md:block"
            style={{ borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)` }}
          >
            <img
              src={PERSONAL_CREATE_HERO_IMAGE}
              alt=""
              className="size-full object-cover"
            />
          </div>
        </section>

        <section
          className="mb-10 grid grid-cols-4 gap-2 rounded-2xl p-4 text-center"
          style={personalGlassCardStyle(tokens)}
        >
          {BENEFITS.map(({ label, Icon, tone }) => {
            const tint = accentColor(tone, colors);
            return (
              <div key={label} className="flex flex-col items-center gap-2">
                <div
                  className="flex size-12 items-center justify-center rounded-xl"
                  style={{ background: `color-mix(in srgb, ${tint} 20%, transparent)` }}
                >
                  <Icon className="size-5" style={{ color: tint }} />
                </div>
                <p className="text-[11px] leading-tight" style={{ color: colors.textSecondary }}>
                  {label}
                </p>
              </div>
            );
          })}
        </section>

        <section className="mb-6">
          <h2 className="text-lg font-semibold">Choose the part of your life</h2>
          <p className="text-sm" style={{ color: colors.textSecondary }}>
            you want to organize.
          </p>
        </section>

        {createError ? (
          <p className="mb-4 text-sm" style={{ color: colors.error }}>
            {createError}
          </p>
        ) : null}

        <section className="space-y-4">
          {cards.map((card) => {
            const accent = accentColor(card.accent, colors);
            const isCreating = creatingTypeCode === card.moment_type_code;
            return (
              <button
                key={card.moment_type_code}
                type="button"
                onClick={() => onBeginMoment(card.moment_type_code)}
                disabled={busy}
                className="relative flex w-full flex-col overflow-hidden rounded-3xl text-left transition-transform enabled:hover:scale-[1.01] enabled:active:scale-[0.99] disabled:opacity-60 sm:flex-row sm:min-h-[210px]"
                style={{
                  ...personalGlassCardStyle(tokens, { glow: card.featured }),
                  border: card.featured
                    ? `2px solid ${colors.primaryContainer}`
                    : `1px solid color-mix(in srgb, ${colors.border} 50%, transparent)`,
                  background: colors.surfaceContainer,
                }}
              >
                <div className="relative aspect-[4/3] w-full shrink-0 sm:aspect-auto sm:w-1/3">
                  <img src={card.image} alt="" className="absolute inset-0 size-full object-cover" />
                  <div
                    className="absolute left-3 top-3 flex size-10 items-center justify-center rounded-xl shadow-lg"
                    style={{ background: accent, color: "#ffffff" }}
                  >
                    {card.moment_type_code === "LIFE_OPERATIONS" ? (
                      <BarChart3 className="size-5" />
                    ) : card.moment_type_code === "FUTURE_BUILDING" ? (
                      <Lightbulb className="size-5" />
                    ) : card.moment_type_code === "LIFESTYLE" ? (
                      <Heart className="size-5" />
                    ) : (
                      <User className="size-5" />
                    )}
                  </div>
                </div>
                <div className="relative flex flex-1 flex-col justify-between gap-4 p-5 pr-16">
                  <div className="space-y-3">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-xl font-bold">{card.title}</h3>
                      <span
                        className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                        style={{
                          background: `color-mix(in srgb, ${accent} 20%, transparent)`,
                          color: accent,
                        }}
                      >
                        {card.badge}
                      </span>
                    </div>
                    <p
                      className="line-clamp-2 text-sm leading-relaxed"
                      style={{ color: colors.textSecondary }}
                    >
                      {card.description}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {card.tags.map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full px-2.5 py-1 text-xs"
                          style={{
                            background: `color-mix(in srgb, ${colors.textPrimary} 5%, transparent)`,
                            color: colors.textSecondary,
                          }}
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <span
                    className="absolute bottom-5 right-5 flex size-11 items-center justify-center rounded-full shadow-lg"
                    style={{ background: accent, color: "#ffffff" }}
                    aria-hidden
                  >
                    {isCreating ? (
                      <Loader2 className="size-5 animate-spin" />
                    ) : (
                      <ArrowRight className="size-5" />
                    )}
                  </span>
                </div>
              </button>
            );
          })}
        </section>

        <section
          className="mt-10 flex flex-col gap-4 rounded-3xl p-5 sm:flex-row sm:items-center sm:justify-between"
          style={{
            ...personalGlassCardStyle(tokens),
            background: colors.surfaceContainer,
            border: `1px solid color-mix(in srgb, ${colors.border} 50%, transparent)`,
          }}
        >
          <div className="flex items-start gap-4">
            <div
              className="flex size-12 shrink-0 items-center justify-center rounded-2xl"
              style={{
                background: `color-mix(in srgb, ${colors.textPrimary} 10%, transparent)`,
              }}
            >
              <Lightbulb className="size-6" style={{ color: colors.brandPrimary }} />
            </div>
            <div>
              <h3 className="mb-1 text-lg font-bold">Not sure where to start?</h3>
              <p className="max-w-sm text-sm leading-relaxed" style={{ color: colors.textSecondary }}>
                Start with Life Operations and build your personal operating system one moment at a
                time.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => onBeginMoment("LIFE_OPERATIONS")}
            disabled={busy}
            className="rounded-full border-2 px-8 py-3 text-center text-sm font-semibold transition-colors disabled:opacity-60"
            style={{
              borderColor: colors.primaryContainer,
              color: colors.textPrimary,
              background: "transparent",
            }}
          >
            {creatingTypeCode === "LIFE_OPERATIONS" ? (
              <Loader2 className="mx-auto size-5 animate-spin" />
            ) : (
              "Start with Life Operations"
            )}
          </button>
        </section>
      </div>
    </div>
  );
}

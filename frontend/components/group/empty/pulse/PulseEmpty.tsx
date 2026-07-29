"use client";

import {
  ArrowRight,
  BookOpen,
  Calendar,
  Network,
  Wallet,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { groupGlassCardStyle, groupScrollShellStyle } from "@/components/group/empty/shared/emptyStyles";
import { groupTypography } from "@/lib/group/groupTypography";

type PulseEmptyMode = "no_moment" | "draft_resume";

type PulseEmptyProps = {
  onCreateMoment: () => void;
  onContinueSetup?: () => void;
  mode?: PulseEmptyMode;
  bottomPadding?: number;
};

const momentTypes = [
  {
    title: "Shared Experience",
    description: "Trips, weddings, celebrations, outings and events.",
    image: "/group/type-experience.jpg",
    accent: "#FFB598",
  },
  {
    title: "Shared Purchase",
    description: "Group buying, gifting and shared assets.",
    image: "/group/type-purchase.jpg",
    accent: "#FFB690",
  },
  {
    title: "Shared Living",
    description: "Households, families and shared living.",
    image: "/group/type-living.jpg",
    accent: "#FFB598",
  },
  {
    title: "Shared Goal",
    description: "Savings goals, fundraising and milestones.",
    image: "/group/type-goal.jpg",
    accent: "#FFB951",
    comingSoon: true,
  },
  {
    title: "Community Coordination",
    description: "Gatherings, clubs and community events.",
    image: "/group/type-community.jpg",
    accent: "#FFB598",
    comingSoon: true,
  },
  {
    title: "Custom",
    description: "Build a completely custom shared moment.",
    image: "/group/type-custom.jpg",
    accent: "#FF7A3D",
    wide: true,
    comingSoon: true,
  },
] as const;

const whyGroups = [
  { icon: Network, title: "Coordinate Together", description: "Keep people, plans and money aligned in real-time." },
  { icon: Wallet, title: "Manage Shared Money", description: "Track contributions, spending and settlements effortlessly." },
  { icon: Calendar, title: "Stay Organized", description: "Plans, tasks and updates all in one unified dashboard." },
  { icon: BookOpen, title: "Remember Together", description: "Capture milestones, updates and memories as they happen." },
] as const;

const magicSteps = [
  { title: "Plans become moments", description: "Create with people around shared experiences and lifestyles." },
  { title: "Moments become memories", description: "Live them, capture them and celebrate them together." },
  { title: "Memories make future smarter", description: "Our intelligence engine helps you achieve more as a group." },
] as const;

export function PulseEmpty({
  onCreateMoment,
  onContinueSetup,
  mode = "no_moment",
  bottomPadding = 0,
}: PulseEmptyProps) {
  const tokens = useThemeTokens();
  const { colors, gradients } = tokens;
  const isDraftResume = mode === "draft_resume";
  const primaryAction = isDraftResume && onContinueSetup ? onContinueSetup : onCreateMoment;
  const primaryLabel = isDraftResume ? "Continue Group Setup" : "Create Your First Group Moment";
  const heroTitle = isDraftResume
    ? "Finish setting up your shared moment."
    : "Every unforgettable experience begins with people.";
  const heroSubtitle = isDraftResume
    ? "Your draft is saved — continue setup to activate coordination, money, and memories."
    : "Create trips, celebrations, shared goals, purchases and communities that bring people together.";

  return (
    <div
      data-momentra-context="group"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={groupScrollShellStyle(tokens, bottomPadding)}
    >
      <div
        className="pointer-events-none absolute -left-20 -top-20 size-[400px] rounded-full blur-[80px]"
        style={{ background: gradients.brandFadeStart }}
      />
      <div
        className="pointer-events-none absolute right-0 top-1/3 size-[300px] rounded-full blur-[70px]"
        style={{ background: gradients.brandFadeEnd }}
      />

      <div
        className="relative mx-auto flex w-full max-w-[600px] flex-col px-5 py-6 md:max-w-[1080px] md:px-20 md:py-8"
        style={{ gap: tokens.spacing.sectionGap }}
      >
        <section className="-mx-5 overflow-hidden rounded-none md:-mx-20 md:rounded-3xl">
          <div className="relative h-[320px] md:h-[400px]">
            <img
              src="/group/pulse-hero.jpg"
              alt=""
              className="absolute inset-0 size-full object-cover transition-transform duration-700 hover:scale-105"
            />
            <div
              className="absolute inset-0"
              style={{
                background: `linear-gradient(to top, ${colors.background}, color-mix(in srgb, ${colors.background} 40%, transparent), transparent)`,
              }}
            />
            <div className="absolute inset-x-0 bottom-0 px-5 pb-8 pt-16 text-center md:px-12">
              <h2
                className="leading-9 tracking-tight"
                style={{ ...groupTypography.brandTitle, color: colors.textPrimary }}
              >
                {heroTitle}
              </h2>
              <p className="mx-auto mt-3 max-w-md text-sm opacity-80 md:text-base" style={{ color: colors.textSecondary }}>
                {heroSubtitle}
              </p>
              <button
                type="button"
                onClick={primaryAction}
                className="mt-6 inline-flex items-center gap-2 rounded-2xl px-6 py-3 text-sm font-semibold uppercase tracking-widest transition-transform active:scale-95"
                style={{
                  background: `linear-gradient(135deg, ${gradients.heroStart} 0%, ${gradients.heroEnd} 100%)`,
                  color: colors.brandOnPrimary,
                  boxShadow: `0 10px 40px ${tokens.shadows.glowColor}`,
                }}
              >
                {primaryLabel}
                <ArrowRight className="size-4" />
              </button>
            </div>
          </div>
        </section>

        <section className="space-y-3">
          <div>
            <h3 className="text-xl font-semibold md:text-2xl">Group Pulse</h3>
            <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
              Select a type of moment to start organizing with your circle.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {momentTypes.map((type) => {
              const comingSoon = "comingSoon" in type && type.comingSoon;
              return (
                <button
                  key={type.title}
                  type="button"
                  onClick={comingSoon ? undefined : onCreateMoment}
                  disabled={!!comingSoon}
                  className={`group relative overflow-hidden rounded-2xl border text-left transition-transform duration-200 ${
                    "wide" in type && type.wide ? "md:col-span-2" : "h-48 md:h-44"
                  } ${comingSoon ? "cursor-not-allowed opacity-80" : "hover:-translate-y-0.5"}`}
                  style={{ borderColor: "rgba(255,255,255,0.05)" }}
                >
                  <img
                    src={type.image}
                    alt=""
                    className={`absolute inset-0 size-full object-cover transition-transform duration-500 ${
                      comingSoon ? "opacity-60" : "group-hover:scale-105"
                    }`}
                  />
                  <div
                    className="absolute inset-0"
                    style={{
                      background: `linear-gradient(to top, color-mix(in srgb, ${colors.background} 95%, transparent), transparent)`,
                    }}
                  />
                  <div className="relative flex h-full flex-col justify-end p-5">
                    {comingSoon ? (
                      <span
                        className="absolute right-4 top-4 rounded-full px-2.5 py-1 text-[11px] font-semibold"
                        style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
                      >
                        Coming Soon
                      </span>
                    ) : null}
                    <h4 className="text-lg font-semibold">{type.title}</h4>
                    <p className="mt-1 line-clamp-2 text-xs opacity-80">{type.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </section>

        <section className="space-y-4 rounded-2xl p-5" style={groupGlassCardStyle(tokens)}>
          <h3 className="text-lg font-semibold">Why Groups Use Momentra</h3>
          <div className="space-y-4">
            {whyGroups.map((item) => (
              <div key={item.title} className="flex gap-4">
                <div
                  className="flex size-10 shrink-0 items-center justify-center rounded-xl"
                  style={{ background: "rgba(255, 122, 61, 0.15)" }}
                >
                  <item.icon className="size-5" style={{ color: colors.primaryContainer }} />
                </div>
                <div>
                  <p className="font-medium">{item.title}</p>
                  <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="space-y-4 rounded-2xl p-5" style={groupGlassCardStyle(tokens)}>
          <h3 className="text-lg font-semibold">The Momentra Magic?</h3>
          <p className="text-sm opacity-80" style={{ color: colors.textSecondary }}>
            Plans become moments. Moments become memories. Memories make every future moment smarter.
          </p>
          <div className="space-y-3">
            {magicSteps.map((step, i) => (
              <div key={step.title} className="flex gap-3">
                <span
                  className="flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-bold"
                  style={{
                    background: `linear-gradient(135deg, ${gradients.heroStart} 0%, ${gradients.heroEnd} 100%)`,
                    color: colors.brandOnPrimary,
                  }}
                >
                  {i + 1}
                </span>
                <div>
                  <p className="font-medium">{step.title}</p>
                  <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

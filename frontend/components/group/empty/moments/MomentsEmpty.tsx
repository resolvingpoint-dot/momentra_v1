"use client";

import { Plus } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { groupTypography } from "@/lib/group/groupTypography";
import { groupGlassCardStyle, groupScrollShellStyle } from "@/components/group/empty/shared/emptyStyles";

type MomentsEmptyProps = {
  onCreateMoment: () => void;
  bottomPadding?: number;
};

const previewCards = [
  { title: "Shared Experience", description: "Plan unforgettable experiences with your circle.", image: "/group/moments-preview-1.jpg" },
  { title: "Shared Purchase", description: "Buy, gift and share assets together.", image: "/group/moments-preview-2.jpg" },
  { title: "Shared Living", description: "Coordinate daily life under one roof.", image: "/group/moments-preview-3.jpg" },
  { title: "Shared Goal", description: "Reach milestones together.", image: "/group/moments-preview-4.jpg" },
  { title: "Community Coordination", description: "Organize your community with ease.", image: "/group/moments-preview-5.jpg" },
  { title: "Custom", description: "Create a moment your own way.", image: "/group/moments-preview-6.jpg" },
] as const;

const howItWorks = ["Create", "Invite", "Coordinate", "Track", "Remember"] as const;

export function MomentsEmpty({ onCreateMoment, bottomPadding = 0 }: MomentsEmptyProps) {
  const tokens = useThemeTokens();
  const { colors, gradients } = tokens;

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
        <section className="space-y-3">
          <h2
            className="text-[28px] font-bold leading-9 tracking-tight md:text-[32px]"
            style={{ ...groupTypography.brandTitle, color: colors.textPrimary }}
          >
            Every shared plan becomes a living moment
          </h2>
          <p className="max-w-xl text-sm opacity-80 md:text-base" style={{ color: colors.textSecondary }}>
            Create once. Coordinate together. Let people, plans, money and memories evolve in one place.
          </p>
        </section>

        <section className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-xl font-semibold">Group Moments</h3>
            <span
              className="rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-widest"
              style={{
                background: `color-mix(in srgb, ${colors.brandPrimary} 12%, transparent)`,
                color: colors.brandPrimary,
              }}
            >
              Active
            </span>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {previewCards.map((card, index) => (
              <button
                key={card.title}
                type="button"
                onClick={onCreateMoment}
                className={`group relative h-56 overflow-hidden rounded-3xl border text-left transition-transform duration-200 hover:-translate-y-0.5 ${
                  index === 0 || index === previewCards.length - 1 ? "md:col-span-2" : ""
                }`}
                style={{ borderColor: "rgba(255,255,255,0.05)" }}
              >
                <img
                  src={card.image}
                  alt=""
                  className="absolute inset-0 size-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div
                  className="absolute inset-0"
                  style={{
                    background: `linear-gradient(to top, color-mix(in srgb, ${colors.background} 92%, transparent), color-mix(in srgb, ${colors.background} 20%, transparent))`,
                  }}
                />
                <div className="relative flex h-full flex-col justify-end p-5">
                  <h3 className="text-base font-semibold md:text-lg">{card.title}</h3>
                  <p className="mt-1 line-clamp-2 text-xs opacity-80 md:text-sm">{card.description}</p>
                  <span
                    className="mt-3 inline-flex w-fit items-center rounded-full border px-3 py-1 text-[11px] font-semibold"
                    style={{
                      borderColor: `color-mix(in srgb, ${colors.brandPrimary} 30%, transparent)`,
                      color: colors.brandPrimary,
                      background: `color-mix(in srgb, ${colors.brandPrimary} 12%, transparent)`,
                    }}
                  >
                    Explore
                  </span>
                </div>
              </button>
            ))}
          </div>
        </section>

        <section className="rounded-2xl p-5" style={groupGlassCardStyle(tokens)}>
          <h3 className="text-lg font-semibold">How It Works</h3>
          <div className="mt-4 flex flex-wrap justify-between gap-3">
            {howItWorks.map((step, i) => (
              <div key={step} className="flex flex-col items-center gap-1 text-center">
                <span
                  className="flex size-8 items-center justify-center rounded-full text-xs font-bold"
                  style={{
                    background: `linear-gradient(135deg, ${gradients.heroStart} 0%, ${gradients.heroEnd} 100%)`,
                    color: colors.brandOnPrimary,
                  }}
                >
                  {i + 1}
                </span>
                <span className="text-xs font-medium">{step}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-2xl p-6 text-center" style={groupGlassCardStyle(tokens)}>
          <button
            type="button"
            onClick={onCreateMoment}
            className="inline-flex items-center gap-2 rounded-2xl px-6 py-3 text-sm font-semibold uppercase tracking-widest transition-transform active:scale-95"
            style={{
              background: `linear-gradient(135deg, ${gradients.heroStart} 0%, ${gradients.heroEnd} 100%)`,
              color: colors.brandOnPrimary,
              boxShadow: `0 10px 40px ${tokens.shadows.glowColor}`,
            }}
          >
            <Plus className="size-4" />
            Start Your First Moment
          </button>
          <p className="mt-3 text-xs opacity-70">Every shared story starts with a single moment.</p>
        </section>
      </div>
    </div>
  );
}

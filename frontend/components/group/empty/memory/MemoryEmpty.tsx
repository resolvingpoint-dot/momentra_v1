"use client";

import { BookOpen, Heart, History, Sparkles, Users, Wallet } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { groupTypography } from "@/lib/group/groupTypography";
import { groupGlassCardStyle, groupScrollShellStyle } from "@/components/group/empty/shared/emptyStyles";

type MemoryEmptyProps = {
  onCreateMoment: () => void;
  bottomPadding?: number;
};

const insightCards = [
  { title: "People Who Always Show Up", description: "How people show up across moments.", image: "/group/memory-insight-1.jpg", icon: Users },
  { title: "How Your Groups Support Each Other", description: "How groups support and contribute.", image: "/group/memory-insight-2.jpg", icon: Wallet },
  { title: "Traditions You've Created", description: "Trips, events and traditions that repeat.", image: "/group/memory-insight-3.jpg", icon: Heart },
  { title: "Experiences You Keep Returning To", description: "Places, activities and things you love.", image: "/group/memory-insight-4.jpg", icon: BookOpen },
  { title: "Moments Worth Remembering", description: "Important achievements and life moments.", image: "/group/memory-insight-5.jpg", icon: History },
  { title: "Lessons From Your Journey", description: "Smarter insights from your shared journey.", image: "/group/memory-insight-6.jpg", icon: Sparkles },
] as const;

const polaroids = [
  { src: "/group/memory-polaroid-1.jpg", alt: "Friends laughing together at a candlelit dinner party", rotate: "-4deg" },
  { src: "/group/memory-polaroid-2.jpg", alt: "Professionals collaborating in a sun-drenched loft", rotate: "2deg" },
  { src: "/group/memory-polaroid-3.jpg", alt: "Friends toasting at sunset", rotate: "-2deg" },
] as const;

const magicSteps = [
  { title: "Plans become moments", description: "Create with people around shared experiences and lifestyles." },
  { title: "Moments become memories", description: "Live them, capture them and celebrate them together." },
  { title: "Memories make future smarter", description: "Our intelligence engine helps you achieve more as a group." },
] as const;

export function MemoryEmpty({ onCreateMoment, bottomPadding = 0 }: MemoryEmptyProps) {
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
        className="relative mx-auto flex w-full max-w-[600px] flex-col md:max-w-[1080px]"
        style={{ gap: tokens.spacing.sectionGap }}
      >
        <section className="-mx-5 md:-mx-20">
          <div className="flex gap-4 overflow-x-auto px-5 py-8 md:justify-center md:px-20">
            {polaroids.map((photo) => (
              <div
                key={photo.src}
                className="shrink-0 rounded-sm bg-white p-2 pb-8 shadow-xl transition-transform duration-300 hover:scale-[1.03]"
                style={{ transform: `rotate(${photo.rotate})` }}
              >
                <img
                  src={photo.src}
                  alt={photo.alt}
                  className="h-44 w-36 object-cover md:h-52 md:w-44"
                />
              </div>
            ))}
          </div>
        </section>

        <div className="space-y-8 px-5 pb-8 md:px-20">
          <section className="text-center">
            <h2 style={{ ...groupTypography.headlineMd, fontWeight: 700, color: colors.textPrimary }}>
              Shared moments become lasting memory
            </h2>
            <p className="mt-2 text-sm opacity-80 md:text-base" style={{ color: colors.textSecondary }}>
              Capture milestones, traditions and lessons from every shared journey.
            </p>
          </section>

          <section className="space-y-4">
            <h3 className="text-lg font-semibold">What Momentra Will Learn</h3>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {insightCards.map((card) => (
                <div
                  key={card.title}
                  className="group relative overflow-hidden rounded-2xl border"
                  style={{ ...groupGlassCardStyle(tokens), borderColor: "rgba(255,255,255,0.06)" }}
                >
                  <div className="relative h-36 overflow-hidden">
                    <img
                      src={card.image}
                      alt=""
                      className="size-full object-cover grayscale transition-all duration-500 group-hover:scale-105 group-hover:grayscale-0"
                    />
                    <div
                      className="absolute inset-0"
                      style={{
                        background: `linear-gradient(to top, ${colors.background}, transparent)`,
                      }}
                    />
                    <div
                      className="absolute bottom-3 left-3 flex size-9 items-center justify-center rounded-xl"
                      style={{ background: colors.primaryContainer }}
                    >
                      <card.icon className="size-4" style={{ color: colors.brandOnPrimary }} />
                    </div>
                  </div>
                  <div className="relative p-4 pt-2">
                    <h4 className="font-medium">{card.title}</h4>
                    <p className="mt-1 text-sm opacity-70" style={{ color: colors.textSecondary }}>
                      {card.description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="space-y-4 rounded-2xl p-5" style={groupGlassCardStyle(tokens)}>
            <h3 className="text-lg font-semibold">The Momentra Magic?</h3>
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

          <section className="rounded-3xl p-6 text-center" style={groupGlassCardStyle(tokens)}>
            <h3 className="text-lg font-semibold">No memories yet</h3>
            <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
              Your shared story begins with its first moment. The experiences you create today become the memories and
              lessons that shape future moments.
            </p>
            <button
              type="button"
              onClick={onCreateMoment}
              className="mt-5 rounded-full px-6 py-3 text-sm font-semibold uppercase tracking-widest transition-transform active:scale-95"
              style={{
                background: `linear-gradient(135deg, ${gradients.heroStart} 0%, ${gradients.heroEnd} 100%)`,
                color: colors.brandOnPrimary,
                boxShadow: `0 10px 40px ${tokens.shadows.glowColor}`,
              }}
            >
              Create First Group Moment
            </button>
          </section>
        </div>
      </div>
    </div>
  );
}

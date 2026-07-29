"use client";

import { Bolt, HeartPulse, Radio, TrendingUp } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { businessCardStyle, businessScrollShellStyle } from "@/components/business/empty/shared/emptyStyles";

type MomentsEmptyProps = {
  onCreateMoment: () => void;
  bottomPadding?: number;
};

const previewCards = [
  {
    title: "Team Operations",
    description: "Align teams, approvals and execution.",
    image: "/business/moments-preview-1.jpg",
  },
  {
    title: "Business Runway",
    description: "Monitor cash, burn and runway health.",
    image: "/business/moments-preview-2.jpg",
  },
  {
    title: "Business Operations",
    description: "Run daily operations efficiently.",
    image: "/business/moments-preview-3.jpg",
  },
  {
    title: "Project Operations",
    description: "Coming soon.",
    image: "/business/moments-preview-4.jpg",
    gated: true,
  },
  {
    title: "Event Operations",
    description: "Coming soon.",
    image: "/business/moments-preview-5.jpg",
    gated: true,
  },
  {
    title: "Vendor Operations",
    description: "Coming soon.",
    image: "/business/moments-preview-6.jpg",
    gated: true,
  },
] as const;

const infoItems = [
  { icon: Bolt, title: "Activity", description: "Recent operational activity" },
  { icon: HeartPulse, title: "Health", description: "Operational health and status" },
  { icon: TrendingUp, title: "Progress", description: "Advancement toward outcomes" },
  { icon: Radio, title: "Signals", description: "Emerging opportunities and risks" },
] as const;

export function MomentsEmpty({ onCreateMoment, bottomPadding = 0 }: MomentsEmptyProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={businessScrollShellStyle(tokens, bottomPadding)}
    >
      <div className="relative mx-auto flex w-full max-w-[600px] flex-col gap-6 px-5 py-6 md:max-w-[1080px] md:px-20 md:py-8">
        <section className="space-y-2">
          <h2 className="text-[22px] font-bold leading-7">Active Business Moments</h2>
          <p className="text-sm opacity-80" style={{ color: colors.textSecondary }}>
            Create operational moments to coordinate teams, projects, vendors and business execution.
          </p>
        </section>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {previewCards.map((card) => {
            const gated = "gated" in card && card.gated;
            return (
              <button
                key={card.title}
                type="button"
                disabled={!!gated}
                onClick={() => {
                  if (!gated) onCreateMoment();
                }}
                className={`group relative h-40 overflow-hidden rounded-2xl text-left ${gated ? "cursor-not-allowed" : "hover:-translate-y-0.5"}`}
              >
                <img
                  src={card.image}
                  alt=""
                  className={`absolute inset-0 size-full object-cover transition-transform duration-500 ${
                    gated ? "opacity-60" : "group-hover:scale-105"
                  }`}
                />
                <div
                  className="absolute inset-0"
                  style={{
                    background: `linear-gradient(to top, color-mix(in srgb, ${colors.background} 92%, transparent), color-mix(in srgb, ${colors.background} 25%, transparent))`,
                  }}
                />
                <div className="relative flex h-full flex-col justify-between p-4">
                  {gated ? (
                    <span className="text-[9px] font-bold tracking-widest opacity-80">COMING SOON</span>
                  ) : (
                    <span />
                  )}
                  <div>
                    <h3 className="text-sm font-semibold">{card.title}</h3>
                    <p className="line-clamp-2 text-xs opacity-80">{card.description}</p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        <section className="rounded-2xl p-5" style={businessCardStyle(tokens)}>
          <h3 className="text-lg font-semibold">What You&apos;ll See Here</h3>
          <div className="mt-4 grid grid-cols-2 gap-4">
            {infoItems.map((item) => (
              <div key={item.title} className="flex gap-2">
                <item.icon className="size-4 shrink-0" style={{ color: "#5B5CEB" }} />
                <div>
                  <p className="text-sm font-medium">{item.title}</p>
                  <p className="text-xs opacity-70">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
          <p className="mt-4 text-xs opacity-60">Memory: Patterns learned over time</p>
        </section>

        <section className="relative overflow-hidden rounded-2xl">
          <img
            src="/business/pulse-hero.jpg"
            alt=""
            className="absolute inset-0 size-full object-cover opacity-40"
          />
          <div
            className="absolute inset-0"
            style={{
              background: `linear-gradient(145deg, color-mix(in srgb, ${colors.primaryContainer} 55%, transparent) 0%, color-mix(in srgb, ${colors.background} 85%, transparent) 100%)`,
            }}
          />
          <div className="relative flex min-h-32 flex-col items-center justify-center p-6 text-center">
            <h3 className="text-lg font-semibold">Every Business Action Becomes Intelligence</h3>
            <p className="mt-2 max-w-md text-xs opacity-80">
              Create your first operational moment and start building visibility, memory and operational intelligence to scale with precision.
            </p>
            <button
              type="button"
              onClick={onCreateMoment}
              className="mt-4 rounded-xl px-5 py-2.5 text-sm font-semibold"
              style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
            >
              Create First Moment
            </button>
          </div>
        </section>
      </div>
    </div>
  );
}

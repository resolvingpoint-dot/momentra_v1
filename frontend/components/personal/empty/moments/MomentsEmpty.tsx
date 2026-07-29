"use client";

import { Plus } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { glassCardStyle, scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";

type MomentsEmptyProps = {
  onCreateMoment: () => void;
  onBeginLifeOps?: () => void;
  momentTypeLabel?: string;
  bottomPadding?: number;
};

const systemCards = [
  {
    title: "Life Operations",
    badge: "SYSTEM 01",
    description: "Manage daily commitments, money, recovery, and routines.",
    image: "/personal/moments-life-ops.jpg",
  },
  {
    title: "Future Building",
    badge: "SYSTEM 02",
    description: "Track future goals, growth, savings, and progress.",
    image: "/personal/moments-future.jpg",
  },
  {
    title: "Lifestyle",
    badge: "SYSTEM 03",
    description: "Capture experiences, wellbeing, travel, and intentional living.",
    image: "/personal/moments-lifestyle.jpg",
  },
  {
    title: "Relationships",
    badge: "SYSTEM 04",
    description: "Strengthen important relationships, support, care, and shared memories.",
    image: "/personal/moments-relationships.jpg",
  },
] as const;

export function MomentsEmpty({
  onCreateMoment,
  onBeginLifeOps,
  bottomPadding = 0,
}: MomentsEmptyProps) {
  const tokens = useThemeTokens();
  const { colors, gradients } = tokens;

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
        className="pointer-events-none absolute right-0 top-1/2 size-[300px] rounded-full blur-[70px]"
        style={{ background: gradients.brandFadeEnd }}
      />

      <div className="relative mx-auto flex w-full max-w-[600px] flex-col gap-4 px-5 py-6 md:max-w-[1080px] md:px-20 md:py-8">
        <section className="space-y-2">
          <h2 className="text-[22px] font-bold leading-7" style={{ color: colors.textPrimary }}>
            Your Life Systems
          </h2>
          <p className="text-sm opacity-80" style={{ color: colors.textSecondary }}>
            Choose a system to manage an important part of life.
          </p>
        </section>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {systemCards.map((card, index) => {
            const onClick = index === 0 ? (onBeginLifeOps ?? onCreateMoment) : onCreateMoment;
            return (
            <button
              key={card.title}
              type="button"
              onClick={onClick}
              className="relative h-40 overflow-hidden rounded-2xl text-left md:h-36"
            >
              <img src={card.image} alt="" className="absolute inset-0 size-full object-cover" />
              <div
                className="absolute inset-0"
                style={{
                  background: `linear-gradient(to right, color-mix(in srgb, ${colors.background} 95%, transparent), color-mix(in srgb, ${colors.background} 40%, transparent))`,
                }}
              />
              <div className="relative flex h-full flex-col justify-between p-5 md:p-4">
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <h3
                      className="text-[17px] font-semibold md:text-sm"
                      style={{ color: colors.textPrimary }}
                    >
                      {card.title}
                    </h3>
                    <span className="text-[8px] font-bold tracking-widest opacity-50">{card.badge}</span>
                  </div>
                  <p
                    className="mt-1 line-clamp-2 text-xs opacity-80"
                    style={{ color: colors.textSecondary }}
                  >
                    {card.description}
                  </p>
                </div>
                <span
                  className="flex items-center gap-1 text-xs font-semibold"
                  style={{ color: colors.brandPrimary }}
                >
                  <Plus className="size-4" />
                  Create Moment
                </span>
              </div>
            </button>
            );
          })}
        </div>

        <section
          className="flex flex-col items-center gap-4 rounded-2xl px-6 py-12 text-center"
          style={glassCardStyle(tokens)}
        >
          <div
            className="flex size-14 items-center justify-center rounded-full"
            style={{ border: `2px solid ${colors.brandPrimary}` }}
          >
            <span className="text-2xl" style={{ color: colors.brandPrimary }}>
              ✦
            </span>
          </div>
          <h4 className="text-[22px] font-bold" style={{ color: colors.textPrimary }}>
            Build Your Space
          </h4>
          <p className="max-w-[260px] text-sm leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
            Begin by selecting a life system. Your active moments will appear here once created.
          </p>
        </section>
      </div>
    </div>
  );
}

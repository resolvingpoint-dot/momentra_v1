"use client";

import Image from "next/image";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifestyleBestMomentCard } from "@/lib/api/personal";
import { lifestyleMomentsCopy } from "@/lib/personal/lifestyle/moments/lifestyleMomentsCopy";

type Props = { cards: PersonalLifestyleBestMomentCard[] };

const AXIS_COLORS: Record<string, string> = {
  Fulfillment: "#60a5fa",
  Vitality: "#10b981",
  Joy: "#8b5cf6",
};

export function LifestyleBestMomentsCarousel({ cards }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <LifestyleSectionBadge index={4} label="Best Moments" explainerId="MOMENT-008" />
        <button type="button" className="text-xs" style={{ color: "#60a5fa", background: "none", border: "none" }}>
          View all
        </button>
      </div>
      {cards.length === 0 ? (
        <p className="text-sm opacity-70">Your best lifestyle moments will appear here.</p>
      ) : (
        <div className="-mx-1 flex gap-3 overflow-x-auto pb-2">
          {cards.map((card) => {
            const axisTag = card.axis_tag ?? card.impact_lines[0] ?? "Fulfillment";
            const axisColor = AXIS_COLORS[axisTag] ?? colors.brandPrimary;
            return (
              <div
                key={card.card_id}
                className="min-w-[240px] shrink-0 overflow-hidden rounded-2xl border shadow-lg transition-transform hover:scale-[1.02] active:scale-95"
                style={{ background: "#14142b", borderColor: "rgba(255,255,255,0.1)" }}
              >
                <div className="relative h-40">
                  {card.image_url ? (
                    <Image src={card.image_url} alt="" fill className="object-cover" unoptimized />
                  ) : (
                    <div className="h-full w-full" style={{ background: `${axisColor}33` }} />
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-[#14142b] to-transparent" />
                  <div className="absolute bottom-2 left-3">
                    <h5 className="text-lg font-bold">{card.title}</h5>
                    <p className="text-xs opacity-60">{card.period_label}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3">
                  <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: axisColor }}>
                    {axisTag}
                  </span>
                  <span className="text-sm font-bold">
                    {lifestyleMomentsCopy.formatInrMinor(card.spend_amount_minor ?? 0)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

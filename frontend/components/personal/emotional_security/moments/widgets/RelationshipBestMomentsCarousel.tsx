"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { PersonalEmotionalSecurityBestMomentCard } from "@/lib/api/personalDomainTypes";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  relationshipsMomentsAccent,
  relationshipsMomentsCopy,
} from "@/lib/personal/emotional_security/moments/relationshipsMomentsCopy";

type RelationshipBestMomentsCarouselProps = {
  cards: PersonalEmotionalSecurityBestMomentCard[];
};

export function RelationshipBestMomentsCarousel({ cards }: RelationshipBestMomentsCarouselProps) {
  const { colors } = useThemeTokens();
  if (cards.length === 0) return null;

  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-0.5">
          <h3 className="text-[10px] font-bold uppercase tracking-widest opacity-50">
            {relationshipsMomentsCopy.bestMomentsTitle}
          </h3>
          <WidgetInfoButton explainerId="MOMENT-008" momentTypeCode="RELATIONSHIPS" />
        </div>
        <button type="button" className="text-[10px] font-bold" style={{ color: "#818cf8" }}>
          {relationshipsMomentsCopy.viewAll}
        </button>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
        {cards.map((card) => (
          <article
            key={card.card_id}
            className="w-56 shrink-0 overflow-hidden rounded-2xl transition-transform hover:scale-[1.02] active:scale-95"
            style={{ background: relationshipsMomentsAccent.cardBg, border: "1px solid rgba(255,255,255,0.08)" }}
          >
          {card.image_url ? (
            <img src={card.image_url} alt="" className="h-32 w-full object-cover hover:scale-110 transition-transform duration-300" />
          ) : (
            <div className="relative h-32 w-full overflow-hidden bg-gradient-to-br from-purple-500/20 to-pink-500/20">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="size-10 rounded-full bg-white/10 backdrop-blur-sm" />
              </div>
            </div>
          )}
            <div className="p-2">
              <p className="text-[10px] opacity-60">
                {card.period_label} • {card.tag_label}
              </p>
              <h4 className="mt-0.5 text-sm font-semibold" style={{ color: colors.textPrimary }}>
                {card.title}
              </h4>
              <p className="mt-1 text-amber-400">{"★".repeat(card.star_rating)}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

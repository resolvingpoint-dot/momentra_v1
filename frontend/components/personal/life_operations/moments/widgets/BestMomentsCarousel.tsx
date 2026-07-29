"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalPremiumGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsBestMomentCard } from "@/lib/api/personal";
import { lifeOpsMomentsCopy } from "@/lib/personal/life_operations/moments/lifeOpsMomentsCopy";
import { ImageIcon, Sparkles } from "lucide-react";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";

type BestMomentsCarouselProps = {
  cards: PersonalLifeOpsBestMomentCard[];
};

export function BestMomentsCarousel({ cards }: BestMomentsCarouselProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section>
      <PersonalWidgetSectionHeader title={lifeOpsMomentsCopy.bestMomentsTitle} explainerId="MOMENT-008" momentTypeCode="LIFE_OPERATIONS" className="mb-3" />
      {cards.length === 0 ? (
        <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
          {lifeOpsMomentsCopy.bestMomentsEmpty}
        </p>
      ) : (
        <div className="-mx-1 flex gap-3 overflow-x-auto pb-2">
          {cards.map((card) => (
            <PersonalPremiumGlowSection
              key={card.card_id}
              tokens={tokens}
              cornerRadius={20}
              className="min-w-[240px] shrink-0 transition-transform hover:scale-[1.02] active:scale-95"
              innerStyle={{ padding: 16 }}
            >
              <div className="mb-2 flex items-center gap-2">
                <Sparkles className="size-4" style={{ color: colors.brandPrimary }} />
                <span className="text-[10px] font-bold uppercase tracking-widest opacity-50">{card.period_label}</span>
              </div>
              <div className="mb-3 flex items-center gap-3">
                <div className="relative flex size-14 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-gradient-to-br" style={{ background: `${colors.brandPrimary}33` }}>
                  <ImageIcon size={20} style={{ color: colors.brandPrimary, opacity: 0.5 }} />
                </div>
                <p className="flex-1 text-base font-semibold" style={{ color: colors.textPrimary }}>
                  {card.title}
                </p>
              </div>
              <ul className="mt-2 space-y-0.5">
                {card.impact_lines.map((line) => (
                  <li key={line} className="text-xs" style={{ color: colors.textSecondary }}>
                    {line}
                  </li>
                ))}
              </ul>
            </PersonalPremiumGlowSection>
          ))}
        </div>
      )}
    </section>
  );
}

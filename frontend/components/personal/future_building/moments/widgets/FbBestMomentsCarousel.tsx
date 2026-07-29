"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsBestMomentCard } from "@/lib/api/personal";
import { fbMomentsCopy } from "@/lib/personal/future_building/moments/fbMomentsCopy";
import { FbSectionBadge } from "@/components/personal/future_building/moments/widgets/FbSectionBadge";
import { Award, BookOpen, Flag } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

const CARD_ACCENTS = ["#8b5cf6", "#3b82f6", "#ec4899"];

const ICONS = [Award, BookOpen, Flag];

type Props = { cards: PersonalLifeOpsBestMomentCard[] };

export function FbBestMomentsCarousel({ cards }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FbSectionBadge number={4} />
          <h2 style={{ ...personalTypography.labelSm, textTransform: "uppercase", letterSpacing: "0.12em", opacity: 0.6 }}>
            {fbMomentsCopy.bestMomentsTitle}
          </h2>
          <WidgetInfoButton explainerId="MOMENT-008" momentTypeCode="FUTURE_BUILDING" />
        </div>
        <button type="button" style={{ fontSize: 12, color: colors.brandPrimary, background: "none", border: "none" }}>
          {fbMomentsCopy.viewAll}
        </button>
      </div>
      {cards.length === 0 ? (
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>Standout moments surface as patterns emerge.</p>
      ) : (
        <div className="-mx-1 flex gap-3 overflow-x-auto pb-2">
          {cards.map((card, i) => {
            const accent = CARD_ACCENTS[i % CARD_ACCENTS.length];
            const Icon = ICONS[i % ICONS.length];
            const impact = card.impact_lines[0] ?? "Growth +0";
            return (
              <div
                key={card.card_id}
                className="flex min-w-[220px] shrink-0 flex-col justify-between rounded-2xl border-2 p-4 transition-transform hover:scale-[1.02] active:scale-95"
                style={{ ...personalGlassCardStyle(tokens), borderColor: `${accent}4d` }}
              >
                <div>
                  <h4 style={{ fontSize: 18, fontWeight: 700, lineHeight: 1.2, color: colors.textPrimary }}>{card.title}</h4>
                  <p style={{ fontSize: 12, marginTop: 4, color: colors.textSecondary }}>{card.period_label}</p>
                </div>
                <div className="my-6 flex justify-center">
                  <div
                    className="relative flex size-24 items-center justify-center overflow-hidden rounded-full border-4"
                    style={{ borderColor: accent, background: `${accent}33`, boxShadow: `0 0 24px ${accent}66` }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
                    <Icon size={40} color="#fff" className="relative z-10" />
                  </div>
                </div>
                <div className="rounded-xl p-2" style={{ background: `${accent}33` }}>
                  <p style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: `${accent}cc` }}>Impact</p>
                  <p style={{ fontSize: 18, fontWeight: 900, color: accent }}>{impact}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

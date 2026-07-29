"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { businessCardStyle, businessScrollShellStyle } from "@/components/business/empty/shared/emptyStyles";

type MemoryEmptyProps = {
  onCreateMoment: () => void;
  bottomPadding?: number;
};

const patternCards = [
  { title: "Budget Patterns", description: "Understand how spending evolves over time and predict future requirements." },
  { title: "Approval Patterns", description: "Identify approval bottlenecks and systemic delays in your processes." },
  { title: "Vendor Patterns", description: "Track reliability and vendor performance trends across your ecosystem." },
  { title: "Operational Improvements", description: "Learn which changes consistently improve results and scale those successes." },
  { title: "Team Patterns", description: "Understand how teams operate and respond to changing priorities." },
  { title: "Growth Patterns", description: "Identify opportunities hidden inside operations before the market does." },
] as const;

const timelineSteps = [
  "Record Activity",
  "Live Feed",
  "Pulse Updates",
  "Pattern Detection",
  "Business Memory",
] as const;

const insightExamples = [
  { title: "Inventory spending increases during seasonal demand periods.", description: "Derived from 24 months of spend memory" },
  { title: "Vendor approvals take longer on Fridays.", description: "Derived from operational timeline analysis" },
  { title: "Operational improvements reduced approval delays by 18%.", description: "Impact measured against institutional baseline" },
  { title: "Runway improves when vendor payment cycles are optimized.", description: "Projected outcome based on current payment behavior" },
] as const;

export function MemoryEmpty({ onCreateMoment, bottomPadding = 0 }: MemoryEmptyProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <div
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={businessScrollShellStyle(tokens, bottomPadding)}
    >
      <div className="relative mx-auto flex w-full max-w-[600px] flex-col gap-6 md:max-w-[1080px]">
        <section className="-mx-5 md:-mx-20">
          <div className="relative h-[220px] w-full overflow-hidden md:h-[280px]">
            <img
              src="/business/memory-hero.jpg"
              alt=""
              className="absolute inset-0 size-full object-cover"
            />
            <div
              className="absolute inset-0"
              style={{
                background: `linear-gradient(to top, ${colors.background}, color-mix(in srgb, ${colors.background} 35%, transparent), transparent)`,
              }}
            />
          </div>
        </section>

        <div className="space-y-6 px-5 pb-8 md:px-20">
          <section className="text-center">
            <span
              className="inline-block rounded-full px-3 py-1 text-[10px] font-bold tracking-widest"
              style={{ background: "rgba(91, 92, 235, 0.15)", color: "#5B5CEB" }}
            >
              Business Memory Enabled
            </span>
            <h2 className="mt-3 text-[22px] font-bold leading-7">Your Business Gets Smarter Every Day</h2>
            <p className="mt-2 text-sm opacity-80" style={{ color: colors.textSecondary }}>
              Momentra automatically learns from activity, decisions and operational patterns, turning daily actions into institutional intelligence.
            </p>
          </section>

          <section className="space-y-4">
            <h3 className="text-lg font-semibold">What Your Business Will Remember</h3>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {patternCards.map((card) => (
                <div key={card.title} className="rounded-2xl p-4" style={businessCardStyle(tokens)}>
                  <h4 className="font-medium">{card.title}</h4>
                  <p className="mt-1 text-sm opacity-70" style={{ color: colors.textSecondary }}>
                    {card.description}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-2xl p-5" style={businessCardStyle(tokens)}>
            <h3 className="font-semibold">How Memory Is Built</h3>
            <div className="mt-4 flex flex-wrap justify-between gap-2">
              {timelineSteps.map((step, i) => (
                <div key={step} className="flex flex-col items-center gap-1 text-center">
                  <span
                    className="flex size-8 items-center justify-center rounded-full text-xs font-bold"
                    style={{ background: i === 0 || i === 4 ? "#5B5CEB" : colors.surfaceContainer, color: i === 0 || i === 4 ? "#fff" : colors.textPrimary }}
                  >
                    {i + 1}
                  </span>
                  <span className="max-w-[72px] text-[10px] font-medium">{step}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="space-y-3">
            <h3 className="text-lg font-semibold">Examples Of Future Insights</h3>
            {insightExamples.map((insight) => (
              <div key={insight.title} className="rounded-xl border-l-4 p-4" style={{ ...businessCardStyle(tokens), borderLeftColor: "#5B5CEB" }}>
                <p className="text-sm font-medium">{insight.title}</p>
                <p className="mt-1 text-xs opacity-70">{insight.description}</p>
              </div>
            ))}
          </section>

          <section className="rounded-2xl p-6 text-center" style={{ background: colors.surfaceContainer }}>
            <button
              type="button"
              onClick={onCreateMoment}
              className="rounded-2xl px-6 py-3 text-sm font-semibold"
              style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
            >
              Create First Operational Moment
            </button>
            <p className="mt-3 text-xs opacity-60">Secure. Encrypted. Sovereign intelligence.</p>
          </section>
        </div>
      </div>
    </div>
  );
}

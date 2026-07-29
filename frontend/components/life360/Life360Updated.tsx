"use client";

import {
  Activity,
  Bolt,
  Brain,
  ChevronRight,
  Scale,
  Sparkles,
  Star,
  TrendingUp,
  Users,
  Wallet,
  Zap,
} from "lucide-react";
import {
  formatScore,
  formatSignedScore,
  toNumber,
  type Life360AnalyticsResponse,
  type Life360Snapshot,
} from "@/repositories/Life360Repository";

type Life360UpdatedProps = {
  snapshot: Life360Snapshot;
  analytics: Life360AnalyticsResponse | null;
  onExploreLifeModules: () => void;
};

function dimScore(
  analytics: Life360AnalyticsResponse | null,
  snapshot: Life360Snapshot,
  key: "money" | "relationship" | "execution" | "growth",
): number | null {
  const fromSnap = {
    money: snapshot.money_score,
    relationship: snapshot.relationship_score,
    execution: snapshot.execution_score,
    growth: snapshot.growth_score,
  }[key];
  const snapN = toNumber(fromSnap);
  if (snapN != null) return snapN;
  const dim = analytics?.dimensions?.find(
    (d) => d.dimension.toLowerCase() === key || d.dimension.toLowerCase() === `${key}s`,
  );
  return toNumber(dim?.score);
}

function statusChip(
  snapshot: Life360Snapshot,
): Array<{ icon: typeof Activity; label: string }> {
  const chips: Array<{ icon: typeof Activity; label: string }> = [];
  if (snapshot.money_status) chips.push({ icon: Activity, label: snapshot.money_status });
  if (snapshot.execution_status) chips.push({ icon: Zap, label: snapshot.execution_status });
  if (snapshot.relationship_status)
    chips.push({ icon: Users, label: snapshot.relationship_status });
  return chips.slice(0, 3);
}

function trendPath(analytics: Life360AnalyticsResponse | null): string | null {
  const points = analytics?.trend ?? [];
  if (points.length < 2) return null;
  const scores = points.map((p) => toNumber(p.life_alignment_score) ?? 0);
  const min = Math.min(...scores);
  const max = Math.max(...scores);
  const range = max - min || 1;
  return scores
    .map((s, i) => {
      const x = (i / (scores.length - 1)) * 100;
      const y = 20 - ((s - min) / range) * 18;
      return `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
}

export function Life360Updated({
  snapshot,
  analytics,
  onExploreLifeModules,
}: Life360UpdatedProps) {
  const alignment = toNumber(snapshot.life_alignment_score);
  const personalPct = toNumber(
    analytics?.energy?.personal_pct ?? snapshot.personal_energy_pct,
  );
  const groupPct = toNumber(analytics?.energy?.group_pct ?? snapshot.group_energy_pct);
  const businessPct = toNumber(
    analytics?.energy?.business_pct ?? snapshot.business_energy_pct,
  );
  const momentum = toNumber(analytics?.momentum_score ?? snapshot.momentum_score);
  const momentumStatus = analytics?.momentum_status ?? snapshot.momentum_status;
  const strongestDriver = analytics?.strongest_driver ?? snapshot.strongest_driver;
  const biggestTension = analytics?.biggest_tension ?? snapshot.biggest_tension;
  const reflection = snapshot.reflection_summary?.trim() || null;
  const money = dimScore(analytics, snapshot, "money");
  const relationships = dimScore(analytics, snapshot, "relationship");
  const execution = dimScore(analytics, snapshot, "execution");
  const growth = dimScore(analytics, snapshot, "growth");
  const chips = statusChip(snapshot);
  const spark = trendPath(analytics);
  const personalScore = toNumber(snapshot.personal_score);
  const groupScore = toNumber(snapshot.group_score);
  const businessScore = toNumber(snapshot.business_score);

  return (
    <div className="mx-auto w-full max-w-2xl space-y-6 px-6 pb-10 pt-4">

      <div className="space-y-1">
        <h2 className="text-4xl font-bold tracking-tight text-[#e5e2e1]">Life 360</h2>
        <p className="text-base leading-relaxed text-[#d0c5af]/80">
          Your life alignment across{" "}
          <span className="font-medium text-[#f2ca50]">money</span>,{" "}
          <span className="font-medium text-[#f2ca50]">relationships</span>,{" "}
          <span className="font-medium text-[#f2ca50]">execution</span>, and{" "}
          <span className="font-medium text-[#f2ca50]">growth</span>.
        </p>
      </div>

      <section className="relative overflow-hidden rounded-xl border border-[#4d4635]/30 bg-[#1c1b1b] p-5 shadow-[0_0_40px_rgba(242,202,80,0.06)]">
        <div className="mb-6 flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-[#f2ca50]" />
            <span className="text-sm font-semibold uppercase tracking-widest text-[#d0c5af]">
              Life Alignment
            </span>
          </div>
          {snapshot.life_phase ? (
            <div className="rounded-full border border-[#f2ca50]/20 bg-[#f2ca50]/15 px-3 py-1 text-xs font-medium text-[#f2ca50]">
              {snapshot.life_phase}
            </div>
          ) : null}
        </div>
        <div className="mb-4 flex items-baseline gap-2">
          <span className="text-5xl font-bold text-[#f2ca50]">
            {formatScore(alignment)}
          </span>
          <span className="text-xl text-[#d0c5af]/40">/ 100</span>
        </div>
        {chips.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {chips.map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-1.5 rounded-lg border border-[#4d4635]/20 bg-[#201f1f] px-3 py-1.5"
              >
                <Icon className="h-3.5 w-3.5 text-[#f2ca50]" />
                <span className="text-xs font-medium text-[#d0c5af]">{label}</span>
              </div>
            ))}
          </div>
        ) : null}
      </section>

      {reflection ? (
        <section className="rounded-xl border border-[#4d4635]/30 bg-[#1c1b1b] p-5">
          <div className="mb-4 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-[#f2ca50]" />
            <span className="text-sm font-semibold uppercase tracking-widest text-[#d0c5af]">
              Momentra Reflection
            </span>
          </div>
          <p className="text-base italic leading-relaxed text-[#e5e2e1]">
            &ldquo;{reflection}&rdquo;
          </p>
          <div className="mt-4 border-t border-[#4d4635]/20 pt-4">
            <span className="text-xs text-[#d0c5af]/40">
              Generated from your latest Life 360 snapshot
            </span>
          </div>
        </section>
      ) : null}

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <section className="flex flex-col items-center rounded-xl border border-[#4d4635]/30 bg-[#1c1b1b] p-5">
          <div className="mb-8 flex w-full items-center gap-2">
            <Star className="h-4 w-4 fill-[#f2ca50] text-[#f2ca50]" />
            <span className="text-sm font-semibold uppercase tracking-widest text-[#d0c5af]">
              Life Compass
            </span>
          </div>
          <div className="relative mb-8 flex h-64 w-64 items-center justify-center">
            <div className="absolute inset-0 rounded-full border border-[#4d4635]/20" />
            <div className="absolute inset-4 rounded-full border border-[#4d4635]/20" />
            <div className="absolute inset-12 rounded-full border border-[#4d4635]/20" />
            <div className="absolute bottom-0 left-1/2 top-0 w-px bg-[#4d4635]/20" />
            <div className="absolute left-0 right-0 top-1/2 h-px bg-[#4d4635]/20" />
            <div className="absolute flex h-48 w-48 rotate-45 items-center justify-center border border-[#f2ca50]/30 bg-[#f2ca50]/10">
              <div className="-rotate-45 flex flex-col items-center">
                <span className="text-3xl font-semibold leading-none text-[#f2ca50]">
                  {formatScore(alignment)}
                </span>
                <span className="text-xs uppercase text-[#f2ca50]/60">Alignment</span>
              </div>
            </div>
            <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-center">
              <div className="text-xs uppercase text-[#d0c5af]/60">Growth</div>
              <div className="text-sm font-bold text-[#e5e2e1]">{formatScore(growth)}</div>
            </div>
            <div className="absolute -right-10 top-1/2 -translate-y-1/2 text-left">
              <div className="text-xs uppercase text-[#d0c5af]/60">Execution</div>
              <div className="text-sm font-bold text-[#e5e2e1]">{formatScore(execution)}</div>
            </div>
            <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 text-center">
              <div className="text-xs uppercase text-[#d0c5af]/60">Money</div>
              <div className="text-sm font-bold text-[#e5e2e1]">{formatScore(money)}</div>
            </div>
            <div className="absolute -left-14 top-1/2 -translate-y-1/2 text-right">
              <div className="text-xs uppercase text-[#d0c5af]/60">Relationships</div>
              <div className="text-sm font-bold text-[#e5e2e1]">
                {formatScore(relationships)}
              </div>
            </div>
          </div>
          <div className="flex w-full justify-between gap-2 text-center text-xs text-[#d0c5af]/70">
            <div>
              <div className="font-semibold text-[#e5e2e1]">{formatScore(personalScore)}</div>
              Personal
            </div>
            <div>
              <div className="font-semibold text-[#e5e2e1]">{formatScore(groupScore)}</div>
              Group
            </div>
            <div>
              <div className="font-semibold text-[#e5e2e1]">{formatScore(businessScore)}</div>
              Business
            </div>
          </div>
        </section>

        <section className="rounded-xl border border-[#4d4635]/30 bg-[#1c1b1b] p-5">
          <div className="mb-8 flex items-center gap-2">
            <Bolt className="h-4 w-4 fill-[#f2ca50] text-[#f2ca50]" />
            <span className="text-sm font-semibold uppercase tracking-widest text-[#d0c5af]">
              Where your energy is going
            </span>
          </div>
          <div className="space-y-6">
            {(
              [
                { label: "Business", pct: businessPct, color: "#f2ca50" },
                { label: "Personal", pct: personalPct, color: "#a8cdd3" },
                { label: "Group", pct: groupPct, color: "#99907c" },
              ] as const
            ).map((row) => (
              <div key={row.label}>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-semibold text-[#d0c5af]">{row.label}</span>
                  <span className="text-sm font-semibold text-[#e5e2e1]">
                    {row.pct == null ? "—" : `${Math.round(row.pct)}%`}
                  </span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#353534]">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${Math.max(0, Math.min(100, row.pct ?? 0))}%`,
                      backgroundColor: row.color,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <section className="rounded-xl border border-[#4d4635]/30 bg-[#1c1b1b] p-5">
          <div className="mb-6 flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-[#f2ca50]" />
            <span className="text-sm font-semibold uppercase tracking-widest text-[#d0c5af]">
              Life Momentum
            </span>
          </div>
          <div className="mb-6 flex items-baseline gap-3">
            <span className="text-5xl font-bold text-[#f2ca50]">
              {formatSignedScore(momentum)}
            </span>
            {momentumStatus ? (
              <span className="ml-auto rounded border border-[#a8cdd3]/20 bg-[#a8cdd3]/15 px-2 py-0.5 text-xs font-medium text-[#a8cdd3]">
                {momentumStatus}
              </span>
            ) : null}
          </div>
          {spark ? (
            <svg className="h-16 w-full overflow-visible" viewBox="0 0 100 20">
              <path
                d={spark}
                fill="none"
                stroke="#f2ca50"
                strokeLinecap="round"
                strokeWidth="2"
              />
            </svg>
          ) : null}
        </section>

        <section className="flex flex-col rounded-xl border border-[#4d4635]/30 bg-[#1c1b1b] p-5">
          <div className="mb-8 flex items-center gap-2">
            <Activity className="h-4 w-4 text-[#f2ca50]" />
            <span className="text-sm font-semibold uppercase tracking-widest text-[#d0c5af]">
              What is shaping your life
            </span>
          </div>
          <div className="flex flex-1 flex-col gap-6">
            {strongestDriver ? (
              <div>
                <div className="mb-2 text-xs font-medium uppercase text-[#f2ca50]/60">
                  Strongest Driver
                </div>
                <div className="rounded-lg border border-[#f2ca50]/10 bg-[#f2ca50]/5 p-4 font-bold text-[#e5e2e1]">
                  {strongestDriver}
                </div>
              </div>
            ) : null}
            {biggestTension ? (
              <div>
                <div className="mb-2 text-xs font-medium uppercase text-[#ffb4ab]/60">
                  Biggest Tension
                </div>
                <div className="rounded-lg border border-[#93000a]/30 bg-[#93000a]/10 p-4 font-bold text-[#e5e2e1]">
                  {biggestTension}
                </div>
              </div>
            ) : null}
            {!strongestDriver && !biggestTension ? (
              <p className="text-sm text-[#d0c5af]/60">No driver signals yet.</p>
            ) : null}
          </div>
        </section>
      </div>

      <section className="rounded-xl border border-[#4d4635]/30 bg-[#1c1b1b] p-5">
        <div className="mb-8 flex items-center gap-2">
          <Scale className="h-4 w-4 text-[#f2ca50]" />
          <span className="text-sm font-semibold uppercase tracking-widest text-[#d0c5af]">
            Life Balance
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {(
            [
              { label: "Money", value: money, icon: Wallet },
              { label: "Relationships", value: relationships, icon: Users },
              { label: "Execution", value: execution, icon: Zap },
              { label: "Growth", value: growth, icon: Brain },
            ] as const
          ).map(({ label, value, icon: Icon }) => (
            <div
              key={label}
              className="space-y-2 rounded-xl border border-[#4d4635]/20 bg-[#201f1f] p-4 text-center"
            >
              <Icon className="mx-auto h-6 w-6 text-[#f2ca50]" />
              <div className="text-xs font-medium uppercase text-[#d0c5af]">{label}</div>
              <div className="text-xl font-semibold text-[#e5e2e1]">{formatScore(value)}</div>
            </div>
          ))}
        </div>
      </section>

      <div className="space-y-4 pt-2">
        <button
          type="button"
          onClick={onExploreLifeModules}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#f2ca50] px-6 py-4 font-bold text-[#3c2f00] hover:opacity-90 active:scale-[0.98]"
        >
          <span>Review attention areas</span>
          <span className="text-sm font-semibold opacity-70">Coming Soon</span>
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}

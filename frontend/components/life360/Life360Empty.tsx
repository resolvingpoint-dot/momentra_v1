"use client";

import {
  Activity,
  Brain,
  Network,
  PlusCircle,
  Scale,
  Sparkles,
  TrendingUp,
  Zap,
} from "lucide-react";

type Life360EmptyProps = {
  onCreateMoment: () => void;
  onExploreLifeModules: () => void;
};

const REVEAL_CHIPS = [
  { label: "Life Alignment", icon: Activity },
  { label: "Life Energy", icon: Zap },
  { label: "Life Balance", icon: Scale },
  { label: "Life Momentum", icon: TrendingUp },
  { label: "Life Reflection", icon: Brain },
] as const;

export function Life360Empty({
  onCreateMoment,
  onExploreLifeModules,
}: Life360EmptyProps) {
  return (
    <div className="mx-auto flex w-full max-w-lg flex-col gap-12 px-6 pb-10 pt-4">
      <section className="mt-2 flex flex-col items-center gap-2 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-[#e5e2e1]">Life 360</h1>
        <p className="max-w-[280px] text-lg leading-7 text-[#d0c5af]">
          Your complete life intelligence across{" "}
          <span className="font-bold text-[#f2ca50]">money</span>,{" "}
          <span className="font-bold text-[#a8cdd3]">people</span>,{" "}
          <span className="font-bold text-[#f2cc00]">work</span>, and{" "}
          <span className="font-bold text-[#e9c349]">growth</span>.
        </p>
      </section>

      <section className="relative flex h-[280px] items-center justify-center">
        <div className="relative flex h-[260px] w-[260px] items-center justify-center">
          <div
            className="absolute inset-0 rounded-full border border-[#f2ca50]/15"
            style={{ animation: "life360-orbit 20s linear infinite" }}
          />
          <div
            className="absolute inset-6 rounded-full border border-[#f2ca50]/10"
            style={{ animation: "life360-orbit 28s linear infinite reverse" }}
          />
          <div
            className="absolute inset-14 rounded-full border border-[#f2ca50]/20"
            style={{ animation: "life360-orbit 16s linear infinite" }}
          />
          <div className="relative z-10 flex h-20 w-20 items-center justify-center rounded-full border border-[#f2ca50]/30 bg-[#1c1b1b] shadow-[0_0_40px_rgba(242,202,80,0.15)]">
            <Sparkles className="h-8 w-8 text-[#f2ca50]" strokeWidth={1.75} />
          </div>
        </div>
      </section>

      <section className="flex flex-col gap-6 text-center">
        <div className="space-y-2">
          <div className="flex items-center justify-center gap-2 font-bold text-[#f2ca50]">
            <Sparkles className="h-5 w-5" />
            <h2 className="text-xl font-semibold">Your Life Map is waiting to form</h2>
          </div>
          <p className="px-4 text-base leading-relaxed text-[#d0c5af]">
            Life 360 becomes meaningful when your active moments start creating signals
            across money, relationships, execution, and growth.
          </p>
        </div>

        <div>
          <p className="mb-4 text-sm font-semibold uppercase tracking-widest text-[#f2ca50]/60">
            What Life 360 will reveal
          </p>
          <div className="flex justify-between gap-2 overflow-x-auto pb-2">
            {REVEAL_CHIPS.map(({ label, icon: Icon }) => (
              <div
                key={label}
                className="flex min-w-[80px] flex-col items-center gap-3 rounded-2xl border border-[#99907c]/15 bg-[#161616] p-4"
              >
                <Icon className="h-5 w-5 text-[#f2ca50]" strokeWidth={2} />
                <span className="text-[10px] font-bold leading-tight text-[#e5e2e1]">
                  {label.split(" ").map((part) => (
                    <span key={part} className="block">
                      {part}
                    </span>
                  ))}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="flex flex-col gap-4">
        <button
          type="button"
          onClick={onCreateMoment}
          className="flex h-16 w-full items-center justify-between rounded-2xl bg-[#f2ca50] px-8 text-lg font-bold text-[#3c2f00] shadow-[0_0_20px_rgba(242,202,80,0.2)] active:scale-[0.98]"
        >
          <span>Create your first moment</span>
          <PlusCircle className="h-8 w-8" />
        </button>
        <button
          type="button"
          onClick={onExploreLifeModules}
          className="flex h-14 w-full items-center justify-center rounded-2xl border border-[#f2ca50]/30 font-bold text-[#f2ca50] hover:bg-[#f2ca50]/5 active:scale-[0.98]"
        >
          Explore Life modules
        </button>
      </section>

      <div className="flex items-start gap-4 rounded-3xl border border-[#99907c]/15 bg-[#1c1b1b]/40 p-6">
        <div className="rounded-xl bg-[#f2ca50]/10 p-2.5">
          <Network className="h-5 w-5 text-[#f2ca50]" />
        </div>
        <p className="text-sm font-semibold leading-relaxed text-[#d0c5af]">
          As you create Personal, Group, or Business moments, Momentra connects the
          signals into one unified life view.
        </p>
      </div>
    </div>
  );
}

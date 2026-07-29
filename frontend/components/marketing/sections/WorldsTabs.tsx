"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import CTAButton from "@/components/marketing/CTAButton";
import LivingMomentCard from "@/components/marketing/moments/LivingMomentCard";
import { worlds, type WorldId } from "@/lib/marketing/copy";
import { worldIntroMoments } from "@/lib/marketing/moments";

const tabs: WorldId[] = ["personal", "group", "business"];

const atmosphere: Record<WorldId, string> = {
  personal: "from-indigo-900 via-[#1a1548] to-indigo-900",
  group: "from-[#2a1520] via-[#1f1a2e] to-[#152828]",
  business: "from-[#0f1a2e] via-indigo-900 to-[#12241a]",
};

const accentChip: Record<WorldId, string> = {
  personal: "border-indigo-300/40 bg-indigo-500/20 text-indigo-100",
  group: "border-[#ff8a6a]/40 bg-[#ff8a6a]/15 text-[#ffc4b0]",
  business: "border-amber-500/40 bg-amber-500/15 text-amber-200",
};

const accentTab: Record<WorldId, string> = {
  personal: "bg-indigo-500 text-white",
  group: "bg-[#e8621a] text-white",
  business: "bg-amber-600 text-white",
};

function WorldLivingMoment({ world }: { world: WorldId }) {
  const reduceMotion = useReducedMotion();
  const moments = worldIntroMoments[world];
  const [index, setIndex] = useState(0);

  useEffect(() => {
    setIndex(0);
  }, [world]);

  useEffect(() => {
    if (reduceMotion || moments.length < 2) return;
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % moments.length);
    }, 3200);
    return () => clearInterval(id);
  }, [reduceMotion, moments.length, world]);

  const moment = moments[index] ?? moments[0];

  return (
    <div className="mx-auto w-full max-w-md">
      <div className="mb-3 flex justify-center gap-1.5">
        {moments.map((m, i) => (
          <button
            key={m.id}
            type="button"
            aria-label={m.title}
            onClick={() => setIndex(i)}
            className={`h-1.5 rounded-full transition-all ${
              i === index ? "w-6 bg-ember-500" : "w-1.5 bg-white/25"
            }`}
          />
        ))}
      </div>
      <div className="relative min-h-[400px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={moment.id}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.4 }}
            className="absolute inset-x-0 top-0"
          >
            <LivingMomentCard moment={moment} />
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

export default function WorldsTabs() {
  const [active, setActive] = useState<WorldId>("personal");
  const world = worlds[active];

  return (
    <section
      id="worlds"
      className={`relative overflow-hidden bg-gradient-to-br py-24 transition-colors duration-700 sm:py-32 ${atmosphere[active]}`}
    >
      <div className="pointer-events-none absolute inset-0 opacity-40">
        <div
          className={`absolute -top-20 left-1/4 h-80 w-80 rounded-full blur-[100px] transition-colors duration-700 ${
            active === "personal"
              ? "bg-indigo-500/40"
              : active === "group"
                ? "bg-[#ff8a6a]/35"
                : "bg-emerald-500/30"
          }`}
        />
      </div>

      <div className="relative z-10 mx-auto w-full min-w-0 max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mb-10 flex w-full min-w-0 justify-center">
          <div
            role="tablist"
            aria-label="Personal, Group, and Business"
            className="inline-flex max-w-full snap-x snap-mandatory gap-0 overflow-x-auto rounded-full border border-white/15 bg-black/20 p-1 backdrop-blur-md [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
          >
            {tabs.map((id) => (
              <button
                key={id}
                type="button"
                role="tab"
                aria-selected={active === id}
                onClick={() => setActive(id)}
                className={`shrink-0 snap-start rounded-full px-4 py-2 text-sm font-semibold transition-all duration-300 sm:px-7 sm:py-2.5 ${
                  active === id
                    ? accentTab[id]
                    : "text-white/55 hover:text-white/85"
                }`}
              >
                {worlds[id].label}
              </button>
            ))}
          </div>
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={active}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            className="grid min-w-0 items-start gap-12 lg:grid-cols-2 lg:gap-16"
          >
            <div className="min-w-0 w-full">
              <h2 className="mb-4 text-3xl font-extrabold tracking-tight break-words text-text-on-dark sm:text-4xl md:text-5xl">
                {world.heading}
              </h2>
              <p className="mkt-muted mb-8 max-w-xl break-words text-base leading-relaxed sm:text-lg">
                {world.supporting}
              </p>

              <div className="mb-8 flex w-full min-w-0 max-w-full snap-x gap-2 overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
                {world.examples.map((ex) => (
                  <span
                    key={ex}
                    className={`shrink-0 snap-start rounded-full border px-3 py-1.5 text-xs font-medium ${accentChip[active]}`}
                  >
                    {ex}
                  </span>
                ))}
              </div>

              <div className="mb-8 min-w-0 max-w-full overflow-hidden rounded-2xl border border-white/10 bg-white/[0.03] p-5 sm:p-6">
                <p className="mb-1 text-xs font-medium uppercase tracking-wider text-white/40">
                  Featured
                </p>
                <h3 className="mb-2 break-words text-xl font-bold text-text-on-dark">
                  {world.featured.title}
                </h3>
                <p className="mkt-muted mb-5 break-words text-sm leading-relaxed">
                  {world.featured.copy}
                </p>
                <ol className="space-y-2">
                  {world.lifecycle.map((step, i) => (
                    <li
                      key={step}
                      className="flex min-w-0 gap-3 break-words text-sm text-white/75"
                    >
                      <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-white/10 text-[10px] font-semibold text-white/80">
                        {i + 1}
                      </span>
                      <span className="min-w-0">{step}</span>
                    </li>
                  ))}
                </ol>
                {"roles" in world && Array.isArray(world.roles) ? (
                  <div className="mt-5 flex flex-wrap gap-2">
                    {world.roles.map((role: string) => (
                      <span
                        key={role}
                        className="rounded-md bg-white/5 px-2.5 py-1 text-xs text-white/65"
                      >
                        {role}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>

              <p className="mb-6 max-w-xl break-words text-base font-medium leading-relaxed text-indigo-100/90 italic">
                {world.emotional}
              </p>

              <CTAButton
                variant="primary"
                href={world.cta.href}
                event={world.cta.event}
              >
                {world.cta.label}
              </CTAButton>
            </div>

            <div className="flex min-w-0 w-full justify-center lg:justify-end">
              <WorldLivingMoment world={active} />
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  );
}

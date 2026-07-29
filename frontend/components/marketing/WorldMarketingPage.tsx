"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import CTAButton from "@/components/marketing/CTAButton";
import LivingMomentCard from "@/components/marketing/moments/LivingMomentCard";
import LifeJourney from "@/components/marketing/sections/LifeJourney";
import { worlds, type WorldId, finalCta } from "@/lib/marketing/copy";
import { worldIntroMoments } from "@/lib/marketing/moments";
import { fadeUp, staggerContainer } from "@/lib/marketing/animations";

const atmosphere: Record<WorldId, string> = {
  personal: "from-indigo-900/80 via-transparent to-transparent",
  group: "from-[#2a1520]/90 via-transparent to-transparent",
  business: "from-[#0f1a2e]/90 via-transparent to-transparent",
};

export default function WorldMarketingPage({ worldId }: { worldId: WorldId }) {
  const w = worlds[worldId];
  const moments = worldIntroMoments[worldId];
  const reduceMotion = useReducedMotion();
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (reduceMotion || moments.length < 2) return;
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % moments.length);
    }, 3400);
    return () => clearInterval(id);
  }, [reduceMotion, moments.length]);

  const moment = moments[index] ?? moments[0];

  return (
    <main className="relative min-w-0 pt-24 pb-24 sm:pt-28">
      <section
        className={`relative overflow-hidden bg-gradient-to-b pb-16 sm:pb-20 ${atmosphere[worldId]}`}
      >
        <div className="mx-auto grid w-full min-w-0 max-w-7xl items-center gap-12 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
          >
            <motion.p
              variants={fadeUp}
              className="mb-3 text-sm font-medium uppercase tracking-widest text-ember-500"
            >
              {w.label}
            </motion.p>
            <motion.h1
              variants={fadeUp}
              className="mb-5 text-3xl font-extrabold tracking-tight break-words text-text-on-dark sm:text-4xl md:text-5xl"
            >
              {w.heading}
            </motion.h1>
            <motion.p
              variants={fadeUp}
              className="mkt-muted mb-8 max-w-xl text-base leading-relaxed sm:text-lg"
            >
              {w.supporting}
            </motion.p>
            <motion.div
              variants={fadeUp}
              className="mb-8 flex w-full flex-col gap-3 sm:flex-row"
            >
              <CTAButton
                variant="primary"
                href={finalCta.primaryCta.href}
                event={finalCta.primaryCta.event}
                className="w-full max-w-sm sm:w-auto"
              >
                {finalCta.primaryCta.label}
              </CTAButton>
              <CTAButton
                variant="secondary"
                href="/how-moments-work"
                event="see_how_moments_work"
                className="w-full max-w-sm sm:w-auto"
              >
                See How Moments Work
              </CTAButton>
            </motion.div>
            <motion.p
              variants={fadeUp}
              className="max-w-xl text-base font-medium italic text-indigo-100/90"
            >
              {w.emotional}
            </motion.p>
          </motion.div>

          <div className="relative mx-auto w-full max-w-md">
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
            <div className="relative min-h-[420px]">
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
        </div>
      </section>

      <section className="border-t border-white/5 py-16 sm:py-20">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <h2 className="mb-3 text-2xl font-extrabold text-text-on-dark">
            {w.featured.title}
          </h2>
          <p className="mkt-muted mb-8 text-base leading-relaxed">{w.featured.copy}</p>
          <h3 className="mb-4 text-lg font-bold text-text-on-dark">
            How a {w.label.toLowerCase()} moment unfolds
          </h3>
          <ol className="mb-10 list-decimal space-y-2 pl-5 text-white/75">
            {w.lifecycle.map((step) => (
              <li key={step}>{step}</li>
            ))}
          </ol>
          {"roles" in w && Array.isArray(w.roles) ? (
            <>
              <h3 className="mb-3 text-lg font-bold text-text-on-dark">
                Collaborative roles
              </h3>
              <p className="mkt-muted mb-10">{w.roles.join(" · ")}</p>
            </>
          ) : null}
          <h3 className="mb-3 text-lg font-bold text-text-on-dark">
            Example moments
          </h3>
          <div className="flex flex-wrap gap-2">
            {w.examples.map((ex) => (
              <span
                key={ex}
                className="rounded-full border border-white/12 bg-white/[0.04] px-3 py-1.5 text-sm text-white/75"
              >
                {ex}
              </span>
            ))}
          </div>
        </div>
      </section>

      <LifeJourney id={`${worldId}-journey`} compact />
    </main>
  );
}

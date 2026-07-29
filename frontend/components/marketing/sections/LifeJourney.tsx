"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { lifeJourney } from "@/lib/marketing/copy";
import { lifeJourneyStages } from "@/lib/marketing/moments";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function LifeJourney({
  id = "life-journey",
  compact = false,
}: {
  id?: string;
  compact?: boolean;
}) {
  const reduceMotion = useReducedMotion();
  const [active, setActive] = useState(0);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    if (!inView || reduceMotion) return;
    const idTimer = setInterval(() => {
      setActive((i) => (i + 1) % lifeJourneyStages.length);
    }, 1600);
    return () => clearInterval(idTimer);
  }, [inView, reduceMotion]);

  return (
    <section
      id={id}
      className={compact ? "py-12 sm:py-16" : "overflow-hidden py-24 sm:py-32"}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          onViewportEnter={() => setInView(true)}
          className="mb-12 max-w-3xl"
        >
          <motion.h2
            variants={fadeUp}
            className="mb-3 text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl md:text-5xl"
          >
            {lifeJourney.heading}
          </motion.h2>
          <motion.p
            variants={fadeUp}
            className="mb-4 text-2xl font-semibold text-indigo-100/90 sm:text-3xl"
          >
            {lifeJourney.subheading}
          </motion.p>
          <motion.p variants={fadeUp} className="mkt-muted text-lg leading-relaxed">
            {lifeJourney.supporting}
          </motion.p>
        </motion.div>

        <div className="relative">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            className="flex w-full min-w-0 snap-x snap-mandatory gap-3 overflow-x-auto pb-4 [-ms-overflow-style:none] [scrollbar-width:none] md:grid md:grid-cols-5 md:gap-3 md:overflow-visible lg:grid-cols-5 [&::-webkit-scrollbar]:hidden"
          >
            {lifeJourneyStages.map((stage, i) => {
              const isActive = reduceMotion || active === i;
              return (
                <motion.button
                  key={stage.name}
                  type="button"
                  variants={fadeUp}
                  onClick={() => setActive(i)}
                  className={`relative w-[min(180px,75vw)] shrink-0 snap-start rounded-2xl border p-4 text-left transition-colors md:w-auto md:min-w-0 ${
                    isActive
                      ? "border-ember-500/40 bg-ember-500/10"
                      : "border-white/10 bg-white/[0.03] hover:border-white/20"
                  }`}
                >
                  <div className="mb-3 flex items-center gap-2">
                    <span
                      className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${
                        isActive
                          ? "bg-ember-500 text-white"
                          : "bg-white/10 text-white/70"
                      }`}
                    >
                      {i + 1}
                    </span>
                    {i < lifeJourneyStages.length - 1 ? (
                      <span className="h-px flex-1 bg-gradient-to-r from-white/25 to-transparent md:hidden" />
                    ) : null}
                  </div>
                  <h3 className="mb-1.5 text-sm font-bold text-text-on-dark">
                    {stage.name}
                  </h3>
                  <p className="mkt-muted text-xs leading-relaxed">
                    {stage.description}
                  </p>
                </motion.button>
              );
            })}
          </motion.div>
        </div>
      </div>
    </section>
  );
}

"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { flywheel } from "@/lib/marketing/copy";
import { flywheelStages } from "@/lib/marketing/moments";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function Flywheel() {
  const reduceMotion = useReducedMotion();
  const [active, setActive] = useState(0);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    if (!inView || reduceMotion) return;
    const id = setInterval(() => {
      setActive((i) => (i + 1) % flywheelStages.length);
    }, 1400);
    return () => clearInterval(id);
  }, [inView, reduceMotion]);

  return (
    <section id="flywheel" className="py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          onViewportEnter={() => setInView(true)}
          className="mb-12 text-center"
        >
          <motion.h2
            variants={fadeUp}
            className="mb-4 text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl md:text-5xl"
          >
            {flywheel.heading}
          </motion.h2>
          <motion.p variants={fadeUp} className="mkt-muted mx-auto max-w-2xl text-lg">
            {flywheel.supporting}
          </motion.p>
        </motion.div>

        <div className="relative mx-auto max-w-xl">
          <ul className="space-y-3">
            {flywheelStages.map((stage, i) => {
              const isActive = reduceMotion || active === i;
              return (
                <li key={stage}>
                  <button
                    type="button"
                    onClick={() => setActive(i)}
                    className={`relative flex w-full items-center gap-4 rounded-2xl border px-4 py-3 text-left transition-all ${
                      isActive
                        ? "border-ember-500/40 bg-ember-500/10"
                        : "border-white/8 bg-white/[0.02]"
                    }`}
                  >
                    <span
                      className={`relative z-10 flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                        isActive
                          ? "bg-ember-500 text-white"
                          : "bg-white/10 text-white/60"
                      }`}
                    >
                      {i + 1}
                    </span>
                    <span
                      className={`text-sm font-semibold sm:text-base ${
                        isActive ? "text-text-on-dark" : "text-white/55"
                      }`}
                    >
                      {stage}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </section>
  );
}

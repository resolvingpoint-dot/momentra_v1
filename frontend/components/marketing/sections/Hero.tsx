"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import CTAButton from "@/components/marketing/CTAButton";
import LivingMomentCard from "@/components/marketing/moments/LivingMomentCard";
import { hero } from "@/lib/marketing/copy";
import { heroCycleMoments } from "@/lib/marketing/moments";
import { fadeUp, staggerContainer } from "@/lib/marketing/animations";

const CYCLE_MS = 3800;

export default function Hero() {
  const reduceMotion = useReducedMotion();
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (reduceMotion) return;
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % heroCycleMoments.length);
    }, CYCLE_MS);
    return () => clearInterval(id);
  }, [reduceMotion]);

  const moment = heroCycleMoments[index];

  return (
    <section
      id="hero"
      className="relative flex min-h-[100dvh] w-full items-center justify-center overflow-hidden pt-20"
    >
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <motion.div
          animate={{ x: [0, 30, -20, 0], y: [0, -40, 20, 0], scale: [1, 1.1, 0.95, 1] }}
          transition={{ duration: 14, repeat: Infinity, ease: "easeInOut" }}
          className="orb-personal absolute top-1/5 left-1/2 h-[420px] w-[420px] -translate-x-1/2 rounded-full blur-[100px] sm:h-[700px] sm:w-[700px]"
        />
        <motion.div
          animate={{ x: [0, -25, 15, 0], y: [0, 30, -35, 0], scale: [1, 0.9, 1.05, 1] }}
          transition={{ duration: 16, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          className="orb-group absolute top-1/3 left-1/4 h-[280px] w-[280px] rounded-full blur-[80px] sm:h-[500px] sm:w-[500px]"
        />
        <motion.div
          animate={{ x: [0, 20, -30, 0], y: [0, -25, 15, 0], scale: [1, 1.08, 0.92, 1] }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut", delay: 4 }}
          className="orb-business absolute top-1/3 right-1/4 h-[240px] w-[240px] rounded-full blur-[90px] sm:h-[400px] sm:w-[400px]"
        />
      </div>

      <div className="relative z-10 mx-auto grid w-full min-w-0 max-w-7xl items-center gap-10 px-4 py-12 sm:px-6 sm:py-16 lg:grid-cols-2 lg:gap-14 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="w-full min-w-0 text-center lg:text-left"
        >
          <motion.p
            variants={fadeUp}
            className="mb-4 text-sm font-semibold uppercase tracking-[0.22em] text-ember-400"
          >
            Momentra
          </motion.p>
          <motion.h1
            variants={fadeUp}
            className="mb-5 text-4xl font-extrabold leading-[1.08] tracking-tight break-words text-text-on-dark sm:text-5xl md:text-6xl"
          >
            {hero.headline}
          </motion.h1>

          <motion.p
            variants={fadeUp}
            className="mb-4 text-lg font-medium leading-relaxed text-indigo-100/90 sm:text-xl"
          >
            {hero.momentTypes.join(" ")}
          </motion.p>

          <motion.p
            variants={fadeUp}
            className="mkt-muted mx-auto mb-8 max-w-xl text-base leading-relaxed sm:mb-10 sm:text-lg lg:mx-0"
          >
            {hero.supporting}
          </motion.p>

          <motion.div
            variants={fadeUp}
            className="mb-4 flex w-full flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4 lg:justify-start"
          >
            <CTAButton
              variant="primary"
              size="md"
              href={hero.primaryCta.href}
              event={hero.primaryCta.event}
              className="w-full max-w-sm sm:w-auto sm:max-w-none"
            >
              {hero.primaryCta.label}
            </CTAButton>
            <CTAButton
              variant="secondary"
              size="md"
              href={hero.secondaryCta.href}
              event={hero.secondaryCta.event}
              className="w-full max-w-sm sm:w-auto sm:max-w-none"
            >
              {hero.secondaryCta.label}
            </CTAButton>
          </motion.div>

          <motion.a
            variants={fadeUp}
            href={hero.tertiary.href}
            className="mkt-muted inline-block text-sm underline-offset-4 transition-colors hover:text-text-on-dark hover:underline"
          >
            {hero.tertiary.label}
          </motion.a>
        </motion.div>

        <div className="relative mx-auto w-full max-w-md lg:max-w-none">
          <div className="mb-3 flex flex-wrap justify-center gap-1.5 lg:justify-start">
            {heroCycleMoments.map((m, i) => (
              <button
                key={m.id}
                type="button"
                aria-label={`Show ${m.title}`}
                onClick={() => setIndex(i)}
                className={`h-1.5 rounded-full transition-all ${
                  i === index
                    ? "w-6 bg-ember-500"
                    : "w-1.5 bg-white/25 hover:bg-white/45"
                }`}
              />
            ))}
          </div>

          <div className="relative min-h-[420px] sm:min-h-[460px]">
            <AnimatePresence mode="wait">
              <motion.div
                key={moment.id}
                initial={{ opacity: 0, y: 18, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -14, scale: 0.98 }}
                transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
                className="absolute inset-x-0 top-0"
              >
                <LivingMomentCard moment={moment} animateProgress={!reduceMotion} />
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
}

"use client";

import CTAButton from "@/components/marketing/CTAButton";
import LivingMomentCard from "@/components/marketing/moments/LivingMomentCard";
import LifeJourney from "@/components/marketing/sections/LifeJourney";
import { finalCta, lifeJourney, sharedArchitecture } from "@/lib/marketing/copy";
import { goaTripMoment } from "@/lib/marketing/moments";
import { fadeUp, staggerContainer } from "@/lib/marketing/animations";
import { motion } from "framer-motion";

export default function HowMomentsWorkClient() {
  return (
    <main className="relative min-w-0 pt-24 pb-24 sm:pt-28">
      <section className="pb-8 sm:pb-12">
        <div className="mx-auto w-full min-w-0 max-w-4xl px-4 sm:px-6 lg:px-8">
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
          >
            <motion.p
              variants={fadeUp}
              className="mb-3 text-sm font-medium uppercase tracking-widest text-ember-500"
            >
              How Moments Work
            </motion.p>
            <motion.h1
              variants={fadeUp}
              className="mb-5 text-3xl font-extrabold tracking-tight break-words text-text-on-dark sm:text-4xl md:text-5xl"
            >
              {lifeJourney.heading}
            </motion.h1>
            <motion.p
              variants={fadeUp}
              className="mb-3 text-2xl font-semibold text-indigo-100/90"
            >
              {lifeJourney.subheading}
            </motion.p>
            <motion.p
              variants={fadeUp}
              className="mkt-muted mb-8 max-w-2xl text-base leading-relaxed sm:text-lg"
            >
              {lifeJourney.supporting}
            </motion.p>
            <motion.div
              variants={fadeUp}
              className="flex w-full flex-col gap-3 sm:flex-row"
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
                href="/personal"
                event="explore_personal"
                className="w-full max-w-sm sm:w-auto"
              >
                Explore Personal
              </CTAButton>
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section className="pb-8">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <h2 className="mb-6 text-center text-xl font-bold text-text-on-dark">
            A living moment in practice
          </h2>
          <LivingMomentCard moment={goaTripMoment} variant="expanded" />
        </div>
      </section>

      <LifeJourney id="how-life-journey" />

      <section className="border-t border-white/5 py-16 sm:py-20">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <h2 className="mb-6 text-2xl font-extrabold text-text-on-dark">
            {sharedArchitecture.heading}
          </h2>
          <ul className="space-y-4">
            {sharedArchitecture.areas.map((a) => (
              <li
                key={a.name}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"
              >
                <p className="mb-1 font-semibold text-text-on-dark">{a.name}</p>
                <p className="mkt-muted text-sm leading-relaxed">{a.description}</p>
                {"supporting" in a && a.supporting ? (
                  <p className="mkt-muted mt-2 text-sm leading-relaxed">
                    {a.supporting}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      </section>
    </main>
  );
}

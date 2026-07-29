"use client";

import { motion } from "framer-motion";
import CTAButton from "@/components/marketing/CTAButton";
import { finalCta } from "@/lib/marketing/copy";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function FinalCTA() {
  return (
    <section id="cta" className="relative overflow-hidden py-28 pb-36 sm:py-36 md:pb-36">
      <div className="pointer-events-none absolute inset-0">
        <div className="orb-circle absolute top-1/2 left-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full blur-[100px]" />
      </div>

      <div className="relative z-10 mx-auto w-full min-w-0 max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
        >
          <motion.h2
            variants={fadeUp}
            className="mb-6 text-3xl font-extrabold tracking-tight break-words text-text-on-dark sm:text-4xl md:text-5xl"
          >
            {finalCta.heading}
          </motion.h2>
          <motion.p
            variants={fadeUp}
            className="mkt-muted mb-4 text-base leading-relaxed sm:text-lg"
          >
            {finalCta.supporting}
          </motion.p>
          <motion.p
            variants={fadeUp}
            className="mb-10 text-lg font-semibold text-text-on-dark"
          >
            {finalCta.close}
          </motion.p>
          <motion.div
            variants={fadeUp}
            className="mb-8 flex w-full flex-col items-center justify-center gap-3 sm:flex-row sm:gap-4"
          >
            <CTAButton
              variant="primary"
              size="md"
              href={finalCta.primaryCta.href}
              event={finalCta.primaryCta.event}
              className="w-full max-w-sm sm:w-auto sm:max-w-none"
            >
              {finalCta.primaryCta.label}
            </CTAButton>
            <CTAButton
              variant="secondary"
              size="md"
              href={finalCta.secondaryCta.href}
              event={finalCta.secondaryCta.event}
              className="w-full max-w-sm sm:w-auto sm:max-w-none"
            >
              {finalCta.secondaryCta.label}
            </CTAButton>
          </motion.div>
          <motion.p variants={fadeUp} className="mkt-muted text-sm">
            {finalCta.line}
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
}

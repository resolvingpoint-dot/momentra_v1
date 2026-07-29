"use client";

import { motion } from "framer-motion";
import LivingMomentCard from "@/components/marketing/moments/LivingMomentCard";
import { oneRealMoment } from "@/lib/marketing/copy";
import { goaTripMoment } from "@/lib/marketing/moments";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function OneRealMoment() {
  return (
    <section id="one-real-moment" className="py-24 sm:py-32">
      <div className="mx-auto w-full min-w-0 max-w-6xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="mb-12 max-w-3xl"
        >
          <motion.p
            variants={fadeUp}
            className="mb-3 text-sm font-medium uppercase tracking-widest text-ember-500"
          >
            {oneRealMoment.eyebrow}
          </motion.p>
          <motion.h2
            variants={fadeUp}
            className="mb-4 text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl md:text-5xl"
          >
            {oneRealMoment.heading}
          </motion.h2>
          <motion.p variants={fadeUp} className="mkt-muted text-lg leading-relaxed">
            {oneRealMoment.supporting}
          </motion.p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 28 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={viewportConfig}
          transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
          className="mx-auto max-w-3xl"
        >
          <LivingMomentCard moment={goaTripMoment} variant="expanded" />
        </motion.div>
      </div>
    </section>
  );
}

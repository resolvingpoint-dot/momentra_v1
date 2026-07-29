"use client";

import { motion } from "framer-motion";
import { comparison } from "@/lib/marketing/copy";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function Comparison() {
  return (
    <section id="comparison" className="py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <motion.h2
          variants={fadeUp}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="mb-12 text-center text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl md:text-5xl"
        >
          {comparison.heading}
        </motion.h2>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="grid gap-6 md:grid-cols-2"
        >
          <motion.div
            variants={fadeUp}
            className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 sm:p-8"
          >
            <h3 className="mb-6 text-lg font-semibold text-white/50">
              {comparison.traditional.title}
            </h3>
            <ul className="space-y-3">
              {comparison.traditional.points.map((p) => (
                <li key={p} className="mkt-muted flex gap-3 text-sm leading-relaxed">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-white/25" />
                  {p}
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div
            variants={fadeUp}
            className="rounded-2xl border border-ember-500/25 bg-ember-500/5 p-6 sm:p-8"
          >
            <h3 className="mb-6 text-lg font-semibold text-text-on-dark">
              {comparison.momentra.title}
            </h3>
            <ul className="space-y-3">
              {comparison.momentra.points.map((p) => (
                <li
                  key={p}
                  className="flex gap-3 text-sm leading-relaxed text-indigo-100/90"
                >
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-ember-500" />
                  {p}
                </li>
              ))}
            </ul>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}

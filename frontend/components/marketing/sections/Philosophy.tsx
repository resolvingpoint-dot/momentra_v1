"use client";

import { motion } from "framer-motion";
import { philosophy } from "@/lib/marketing/copy";
import { fadeUp, staggerContainer, viewportConfig } from "@/lib/marketing/animations";

export default function Philosophy() {
  return (
    <section
      id="philosophy"
      className="relative overflow-hidden py-24 sm:py-32 lg:py-40"
    >
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
        >
          <motion.h2
            variants={fadeUp}
            className="mb-8 text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl md:text-5xl lg:text-6xl"
          >
            {philosophy.heading}
          </motion.h2>
          <motion.p
            variants={fadeUp}
            className="mkt-muted mb-14 max-w-2xl text-lg leading-relaxed sm:text-xl"
          >
            {philosophy.body}
          </motion.p>

          <div className="mb-16 space-y-4 sm:space-y-5">
            {philosophy.lines.map((line) => (
              <motion.p
                key={line}
                variants={fadeUp}
                className="text-2xl font-semibold text-text-on-dark sm:text-3xl md:text-4xl"
              >
                {line}
              </motion.p>
            ))}
          </div>

          <motion.p
            variants={fadeUp}
            className="max-w-2xl text-lg leading-relaxed text-indigo-100/90 sm:text-xl"
          >
            {philosophy.closing}
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
}

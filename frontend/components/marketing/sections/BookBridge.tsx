"use client";

import { motion } from "framer-motion";
import CTAButton from "@/components/marketing/CTAButton";
import { book } from "@/lib/marketing/copy";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function BookBridge() {
  return (
    <section id="book" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={viewportConfig}
            transition={{ duration: 0.8 }}
            className="mx-auto w-full max-w-sm"
          >
            <div className="relative aspect-[2/3] overflow-hidden rounded-lg border border-white/15 bg-gradient-to-br from-indigo-700 via-[#1a0f3d] to-[#2a1520] shadow-2xl shadow-indigo-900/50">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(232,98,26,0.25),transparent_50%)]" />
              <div className="absolute inset-0 flex flex-col justify-between p-8">
                <p className="text-xs font-medium uppercase tracking-[0.2em] text-white/50">
                  The beginning of Momentra
                </p>
                <div>
                  <h3 className="mb-3 text-3xl font-extrabold leading-tight text-text-on-dark">
                    {book.title}
                  </h3>
                  <p className="text-sm text-white/55">
                    Where philosophy becomes a living system for life.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>

          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
          >
            <motion.p
              variants={fadeUp}
              className="mb-4 text-sm font-medium uppercase tracking-widest text-ember-500"
            >
              {book.eyebrow}
            </motion.p>
            <motion.h2
              variants={fadeUp}
              className="mb-6 text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl"
            >
              {book.heading}
            </motion.h2>
            <motion.p
              variants={fadeUp}
              className="mb-6 text-xl font-medium leading-snug text-indigo-100/90 sm:text-2xl"
            >
              {book.question}
            </motion.p>
            <motion.p
              variants={fadeUp}
              className="mkt-muted mb-4 text-base leading-relaxed sm:text-lg"
            >
              {book.supporting}
            </motion.p>
            <motion.p
              variants={fadeUp}
              className="mb-2 text-base font-semibold text-text-on-dark"
            >
              {book.bridge}
            </motion.p>
            <motion.p variants={fadeUp} className="mkt-muted mb-8 text-sm">
              {book.bridgeLine}
            </motion.p>
            <motion.div
              variants={fadeUp}
              className="flex flex-col gap-3 sm:flex-row"
            >
              <CTAButton
                variant="primary"
                href={book.exploreCta.href}
                event={book.exploreCta.event}
              >
                {book.exploreCta.label}
              </CTAButton>
              <CTAButton
                variant="secondary"
                href={book.experienceCta.href}
                event={book.experienceCta.event}
              >
                {book.experienceCta.label}
              </CTAButton>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

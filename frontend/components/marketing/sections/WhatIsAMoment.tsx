"use client";

import { motion } from "framer-motion";
import type { CSSProperties } from "react";
import { whatIsAMoment } from "@/lib/marketing/copy";
import {
  fadeUp,
  staggerContainer,
  scaleIn,
  viewportConfig,
} from "@/lib/marketing/animations";

function MomentCore() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.85 }}
      whileInView={{ opacity: 1, scale: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      className="relative z-10 flex h-36 w-36 flex-col items-center justify-center rounded-full border border-white/20 bg-indigo-700/80 text-center shadow-xl backdrop-blur-sm sm:h-44 sm:w-44"
    >
      <span className="text-xs font-medium uppercase tracking-widest text-indigo-200">
        Moment
      </span>
      <span className="mt-1 text-sm font-semibold text-text-on-dark">
        Living space
      </span>
    </motion.div>
  );
}

function FacetChip({
  facet,
  className = "",
  style,
  delay = 0,
}: {
  facet: string;
  className?: string;
  style?: CSSProperties;
  delay?: number;
}) {
  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.7, y: 8 }}
      whileInView={{ opacity: 1, scale: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: 0.2 + delay, duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
      className={`rounded-full border border-white/15 bg-white/5 px-3 py-1.5 text-xs font-medium text-text-on-dark backdrop-blur-sm sm:text-sm ${className}`}
      style={style}
    >
      {facet}
    </motion.span>
  );
}

export default function WhatIsAMoment() {
  return (
    <section id="what-is-a-moment" className="py-24 sm:py-32">
      <div className="mx-auto w-full min-w-0 max-w-6xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="mb-16 text-center"
        >
          <motion.h2
            variants={fadeUp}
            className="mb-6 text-3xl font-extrabold tracking-tight break-words text-text-on-dark sm:text-4xl md:text-5xl"
          >
            {whatIsAMoment.heading}
          </motion.h2>
          <motion.p
            variants={fadeUp}
            className="mkt-muted mx-auto max-w-2xl text-lg leading-relaxed"
          >
            {whatIsAMoment.supporting}
          </motion.p>
        </motion.div>

        <motion.div
          variants={scaleIn}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="relative mx-auto mb-16 flex flex-col items-center gap-8 md:hidden"
        >
          <div className="absolute inset-0 rounded-full bg-indigo-500/10 blur-3xl" />
          <MomentCore />
          <div className="relative z-10 flex w-full max-w-md flex-wrap justify-center gap-2 px-1">
            {whatIsAMoment.facets.map((facet, i) => (
              <FacetChip key={facet} facet={facet} delay={i * 0.08} />
            ))}
          </div>
        </motion.div>

        <motion.div
          variants={scaleIn}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="relative mx-auto mb-16 hidden min-h-[380px] max-w-3xl items-center justify-center md:flex"
        >
          <div className="absolute inset-0 rounded-full bg-indigo-500/10 blur-3xl" />
          <MomentCore />

          {whatIsAMoment.facets.map((facet, i) => {
            const angle =
              (i / whatIsAMoment.facets.length) * Math.PI * 2 - Math.PI / 2;
            const radius = 42;
            const x = 50 + radius * Math.cos(angle);
            const y = 50 + radius * Math.sin(angle);
            return (
              <FacetChip
                key={facet}
                facet={facet}
                delay={i * 0.08}
                className="absolute"
                style={{
                  left: `${x}%`,
                  top: `${y}%`,
                  transform: "translate(-50%, -50%)",
                }}
              />
            );
          })}
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="mx-auto max-w-2xl text-center"
        >
          <motion.p variants={fadeUp} className="mkt-muted mb-6 text-base leading-relaxed sm:text-lg">
            {whatIsAMoment.body}
          </motion.p>
          <motion.p
            variants={fadeUp}
            className="text-lg font-semibold text-text-on-dark sm:text-xl"
          >
            {whatIsAMoment.phrase}
          </motion.p>
        </motion.div>
      </div>
    </section>
  );
}

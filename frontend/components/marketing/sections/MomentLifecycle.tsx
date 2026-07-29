"use client";

import { motion } from "framer-motion";
import { lifecycle } from "@/lib/marketing/copy";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function MomentLifecycle() {
  return (
    <section id="lifecycle" className="overflow-hidden py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="mb-12 max-w-3xl"
        >
          <motion.h2
            variants={fadeUp}
            className="mb-4 text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl md:text-5xl"
          >
            {lifecycle.heading}
          </motion.h2>
          <motion.p variants={fadeUp} className="mkt-muted text-lg leading-relaxed">
            {lifecycle.supporting}
          </motion.p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="flex w-full min-w-0 snap-x snap-mandatory gap-4 overflow-x-auto pb-4 [-ms-overflow-style:none] [scrollbar-width:none] md:grid md:grid-cols-3 md:overflow-visible lg:grid-cols-4 xl:grid-cols-6 [&::-webkit-scrollbar]:hidden"
        >
          {lifecycle.stages.map((stage, i) => (
            <motion.div
              key={stage.name}
              variants={fadeUp}
              className="relative w-[min(200px,80vw)] shrink-0 snap-start rounded-2xl border border-white/10 bg-white/[0.03] p-5 sm:w-[220px] md:w-auto md:min-w-0"
            >
              <div className="mb-3 flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-ember-500/20 text-xs font-bold text-ember-300">
                  {i + 1}
                </span>
                {i < lifecycle.stages.length - 1 ? (
                  <span className="h-px flex-1 bg-gradient-to-r from-white/25 to-transparent md:hidden" />
                ) : null}
              </div>
              <h3 className="mb-2 text-base font-bold text-text-on-dark">
                {stage.name}
              </h3>
              <p className="mkt-muted text-sm leading-relaxed">
                {stage.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

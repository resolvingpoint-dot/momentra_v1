"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { intelligence } from "@/lib/marketing/copy";
import { heroCycleMoments } from "@/lib/marketing/moments";
import MomentPulse from "@/components/marketing/moments/MomentPulse";
import AIInsightLine from "@/components/marketing/moments/AIInsightLine";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function Intelligence() {
  const [insightIdx, setInsightIdx] = useState(0);
  const demo = heroCycleMoments[0];

  useEffect(() => {
    const id = setInterval(() => {
      setInsightIdx((i) => (i + 1) % intelligence.demoInsights.length);
    }, 2800);
    return () => clearInterval(id);
  }, []);

  return (
    <section id="intelligence" className="py-24 sm:py-32">
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
            {intelligence.heading}
          </motion.h2>
          <motion.p variants={fadeUp} className="mkt-muted text-lg leading-relaxed">
            {intelligence.supporting}
          </motion.p>
        </motion.div>

        <div className="grid gap-10 lg:grid-cols-2 lg:items-start">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={viewportConfig}
            transition={{ duration: 0.7 }}
            className="space-y-4 rounded-2xl border border-white/10 bg-indigo-700/30 p-6 sm:p-8"
          >
            <div className="mb-2 flex flex-wrap gap-3 text-sm">
              <span className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-white/80">
                Funding · {demo.progress}%
              </span>
              <span className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-white/80">
                Timeline · {demo.timeline}
              </span>
            </div>
            <MomentPulse
              health={demo.pulse.health}
              score={demo.pulse.score}
              line={demo.pulse.line}
            />
            <AnimatePresence mode="wait">
              <motion.div
                key={intelligence.demoInsights[insightIdx]}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
              >
                <AIInsightLine insight={intelligence.demoInsights[insightIdx]} />
              </motion.div>
            </AnimatePresence>
            <p className="mkt-muted text-sm leading-relaxed">{intelligence.closing}</p>
          </motion.div>

          <motion.ul
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={viewportConfig}
            className="grid grid-cols-1 gap-3 sm:grid-cols-2"
          >
            {intelligence.helpsWith.map((item) => (
              <motion.li
                key={item}
                variants={fadeUp}
                className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-white/80"
              >
                {item}
              </motion.li>
            ))}
          </motion.ul>
        </div>
      </div>
    </section>
  );
}

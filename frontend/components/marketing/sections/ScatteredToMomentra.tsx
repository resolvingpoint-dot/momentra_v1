"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ArrowDown } from "lucide-react";
import { scatteredStory } from "@/lib/marketing/copy";
import { scatteredTools } from "@/lib/marketing/moments";
import { goaTripMoment } from "@/lib/marketing/moments";
import LivingMomentCard from "@/components/marketing/moments/LivingMomentCard";
import {
  fadeUp,
  staggerContainer,
  viewportConfig,
} from "@/lib/marketing/animations";

export default function ScatteredToMomentra() {
  const reduceMotion = useReducedMotion();
  const [toolIndex, setToolIndex] = useState(0);
  const [phase, setPhase] = useState<"tools" | "scattered" | "momentra">("tools");

  useEffect(() => {
    if (reduceMotion) {
      setPhase("momentra");
      return;
    }
    const id = setInterval(() => {
      setToolIndex((i) => {
        const next = i + 1;
        if (next >= scatteredTools.length) {
          setPhase("scattered");
          setTimeout(() => setPhase("momentra"), 900);
          return 0;
        }
        setPhase("tools");
        return next;
      });
    }, 700);
    return () => clearInterval(id);
  }, [reduceMotion]);

  return (
    <section id="scattered" className="py-24 sm:py-32">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={viewportConfig}
          className="mb-14 text-center"
        >
          <motion.h2
            variants={fadeUp}
            className="mb-4 text-3xl font-extrabold tracking-tight text-text-on-dark sm:text-4xl md:text-5xl"
          >
            {scatteredStory.heading}
          </motion.h2>
          <motion.p variants={fadeUp} className="mkt-muted mx-auto max-w-2xl text-lg">
            {scatteredStory.supporting}
          </motion.p>
        </motion.div>

        <div className="grid items-center gap-10 lg:grid-cols-2">
          <div className="flex flex-col items-center">
            <div className="relative mb-4 flex h-28 w-full max-w-sm items-center justify-center">
              <AnimatePresence mode="wait">
                {phase === "tools" ? (
                  <motion.div
                    key={scatteredTools[toolIndex]}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -12 }}
                    className="rounded-2xl border border-white/15 bg-white/[0.05] px-8 py-5 text-xl font-bold text-text-on-dark"
                  >
                    {scatteredTools[toolIndex]}
                  </motion.div>
                ) : phase === "scattered" ? (
                  <motion.div
                    key="scattered"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0 }}
                    className="rounded-2xl border border-red-400/30 bg-red-500/10 px-8 py-5 text-xl font-bold text-red-200"
                  >
                    Scattered
                  </motion.div>
                ) : (
                  <motion.div
                    key="flow"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center"
                  >
                    <p className="mb-2 text-sm font-medium uppercase tracking-widest text-ember-400">
                      {scatteredStory.destination}
                    </p>
                    <p className="text-2xl font-extrabold text-text-on-dark">
                      {scatteredStory.result}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <motion.div
              animate={{ y: [0, 6, 0] }}
              transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
              className="mb-4 text-white/40"
            >
              <ArrowDown size={22} />
            </motion.div>

            <div className="flex flex-wrap justify-center gap-2">
              {scatteredTools.map((tool, i) => (
                <span
                  key={tool}
                  className={`rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
                    phase === "tools" && i === toolIndex
                      ? "border-ember-500/40 bg-ember-500/15 text-ember-200"
                      : "border-white/10 bg-white/[0.03] text-white/45"
                  }`}
                >
                  {tool}
                </span>
              ))}
            </div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={viewportConfig}
            transition={{ duration: 0.7 }}
          >
            <LivingMomentCard moment={goaTripMoment} variant="compact" />
          </motion.div>
        </div>
      </div>
    </section>
  );
}

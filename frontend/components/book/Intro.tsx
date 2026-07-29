"use client";

import { motion } from "framer-motion";

interface IntroProps {
  title: string;
  subtitle: string;
  onBegin: () => void;
}

export function Intro({ title, subtitle, onBegin }: IntroProps) {
  return (
    <motion.div
      className="relative flex min-h-dvh flex-col items-center justify-center overflow-hidden bg-[#0a0614] px-6 text-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
    >
      <div
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_50%_30%,rgba(88,60,140,0.22),transparent_55%)]"
        aria-hidden
      />
      <motion.div
        className="relative z-10 max-w-xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
      >
        <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
          {title}
        </h1>
        <p className="mt-3 text-base text-white/50 sm:text-lg">{subtitle}</p>

        <div className="mx-auto my-10 h-px w-24 bg-white/20" />

        <div className="space-y-5 text-base leading-relaxed text-white/70 sm:text-lg">
          <p>Before there was an app,</p>
          <p>there was a question.</p>
          <p className="pt-2 text-white/85">
            What if life wasn&apos;t organised around
            <br />
            money…
          </p>
          <p>or calendars…</p>
          <p>or tasks…</p>
          <p className="text-white">but around moments?</p>
        </div>

        <div className="mx-auto my-10 h-px w-24 bg-white/20" />

        <motion.button
          type="button"
          onClick={onBegin}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="rounded-full bg-ember-500 px-8 py-3 text-sm font-semibold text-white shadow-lg shadow-ember-500/20 transition hover:brightness-110"
        >
          Begin Reading →
        </motion.button>
      </motion.div>
    </motion.div>
  );
}

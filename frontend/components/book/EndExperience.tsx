"use client";

import Link from "next/link";
import { motion } from "framer-motion";

interface EndExperienceProps {
  onLaunchApp: () => void;
}

export function EndExperience({ onLaunchApp }: EndExperienceProps) {
  return (
    <motion.div
      className="flex min-h-dvh flex-col items-center justify-center bg-[#0a0614] px-6 text-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
    >
      <p className="text-sm uppercase tracking-[0.2em] text-white/40">
        You have reached the end.
      </p>
      <h1 className="mt-6 max-w-lg text-3xl font-semibold tracking-tight text-white sm:text-4xl">
        Life happens in moments.
      </h1>
      <p className="mt-4 text-base text-white/55">
        Now begin creating yours.
      </p>
      <div className="mt-10 flex flex-col gap-3 sm:flex-row">
        <Link
          href="/app"
          onClick={onLaunchApp}
          className="rounded-full bg-ember-500 px-8 py-3 text-sm font-semibold text-white transition hover:brightness-110"
        >
          Launch Momentra
        </Link>
        <Link
          href="/"
          className="rounded-full border border-white/20 px-8 py-3 text-sm font-medium text-white/85 transition hover:bg-white/10"
        >
          Return Home
        </Link>
      </div>
    </motion.div>
  );
}

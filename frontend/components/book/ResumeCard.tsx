"use client";

import { motion } from "framer-motion";

interface ResumeCardProps {
  lastPage: number;
  onResume: () => void;
  onStartOver: () => void;
}

export function ResumeCard({
  lastPage,
  onResume,
  onStartOver,
}: ResumeCardProps) {
  return (
    <motion.div
      className="flex min-h-dvh flex-col items-center justify-center bg-[#0a0614] px-6 text-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <p className="text-sm uppercase tracking-[0.18em] text-white/40">
        Continue Reading
      </p>
      <h1 className="mt-4 text-2xl font-semibold text-white sm:text-3xl">
        Last Page
      </h1>
      <p className="mt-2 text-lg tabular-nums text-white/60">Page {lastPage}</p>
      <div className="mt-10 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onResume}
          className="rounded-full bg-ember-500 px-8 py-3 text-sm font-semibold text-white transition hover:brightness-110"
        >
          Resume →
        </button>
        <button
          type="button"
          onClick={onStartOver}
          className="rounded-full border border-white/20 px-8 py-3 text-sm font-medium text-white/80 transition hover:bg-white/10"
        >
          Start from beginning
        </button>
      </div>
    </motion.div>
  );
}

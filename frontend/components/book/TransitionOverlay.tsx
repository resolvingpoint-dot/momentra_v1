"use client";

import { AnimatePresence, motion } from "framer-motion";
import type { BookTransition } from "@/lib/book/types";

interface TransitionOverlayProps {
  transition: BookTransition | null;
  onContinue: () => void;
  onOpenApp: () => void;
}

export function TransitionOverlay({
  transition,
  onContinue,
  onOpenApp,
}: TransitionOverlayProps) {
  return (
    <AnimatePresence>
      {transition ? (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 px-6 backdrop-blur-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.4 }}
        >
          <motion.div
            className="w-full max-w-md text-center"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="mb-8 h-px w-16 bg-white/20 mx-auto" />
            <p className="text-lg leading-relaxed text-white/90 sm:text-xl">
              {transition.message}
            </p>
            <p className="mt-4 text-sm text-white/50">{transition.cta}</p>
            <div className="mb-8 mt-8 h-px w-16 bg-white/20 mx-auto" />
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
              <button
                type="button"
                onClick={onContinue}
                className="rounded-full border border-white/20 px-6 py-2.5 text-sm font-medium text-white/90 transition hover:bg-white/10"
              >
                Continue Reading
              </button>
              <button
                type="button"
                onClick={onOpenApp}
                className="rounded-full bg-ember-500 px-6 py-2.5 text-sm font-semibold text-white transition hover:brightness-110"
              >
                Open Momentra
              </button>
            </div>
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}

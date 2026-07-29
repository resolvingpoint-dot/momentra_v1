"use client";

import { useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import type { BookMilestone } from "@/lib/book/types";

interface MilestoneToastProps {
  milestone: BookMilestone | null;
  onDismiss: () => void;
}

export function MilestoneToast({ milestone, onDismiss }: MilestoneToastProps) {
  useEffect(() => {
    if (!milestone) return;
    const t = window.setTimeout(onDismiss, 4200);
    return () => window.clearTimeout(t);
  }, [milestone, onDismiss]);

  return (
    <AnimatePresence>
      {milestone ? (
        <motion.div
          role="status"
          className="pointer-events-none fixed bottom-24 left-1/2 z-40 w-[min(90vw,22rem)] -translate-x-1/2"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 8 }}
          transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        >
          <div className="rounded-lg border border-white/10 bg-[#141022]/95 px-4 py-3 text-center shadow-lg backdrop-blur-md">
            <p className="text-sm text-white/85">{milestone.message}</p>
          </div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}

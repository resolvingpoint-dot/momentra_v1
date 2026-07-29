"use client";

import { AnimatePresence, motion } from "framer-motion";
import type { ReactNode } from "react";
import { MOTION_DURATION_MS } from "@/lib/motion/tokens";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";

type SkeletonCrossfadeProps = {
  showSkeleton: boolean;
  skeleton: ReactNode;
  children: ReactNode;
  className?: string;
};

export function SkeletonCrossfade({
  showSkeleton,
  skeleton,
  children,
  className = "",
}: SkeletonCrossfadeProps) {
  const reducedMotion = useReducedMotion();
  const duration = reducedMotion ? 0 : MOTION_DURATION_MS.normal / 1000;

  return (
    <div className={`relative min-h-0 flex-1 ${className}`}>
      <AnimatePresence mode="wait" initial={false}>
        {showSkeleton ? (
          <motion.div
            key="skeleton"
            initial={{ opacity: reducedMotion ? 1 : 0.92 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration }}
            className="min-h-0 flex-1"
          >
            {skeleton}
          </motion.div>
        ) : (
          <motion.div
            key="content"
            initial={{ opacity: reducedMotion ? 1 : 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration }}
            className="min-h-0 flex-1"
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

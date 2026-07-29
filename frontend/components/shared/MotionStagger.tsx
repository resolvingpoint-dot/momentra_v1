"use client";

import { motion } from "framer-motion";
import { useEffect, type ReactNode } from "react";
import { cardEntranceVariants, staggerContainerVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { hasAnimatedOnce, markAnimatedOnce } from "@/lib/motion/useHasAnimatedOnce";

type MotionStaggerRootProps = {
  children: ReactNode;
  className?: string;
  /** When set, stagger runs only on first visit for this key per session. */
  animateOnceKey?: string;
};

export function MotionStaggerRoot({ children, className, animateOnceKey }: MotionStaggerRootProps) {
  const reducedMotion = useReducedMotion();
  const alreadyPlayed = animateOnceKey ? hasAnimatedOnce(animateOnceKey) : false;
  const skipStagger = reducedMotion || alreadyPlayed;

  useEffect(() => {
    if (animateOnceKey && !reducedMotion && !alreadyPlayed) {
      markAnimatedOnce(animateOnceKey);
    }
  }, [animateOnceKey, reducedMotion, alreadyPlayed]);

  return (
    <motion.div
      className={className}
      variants={staggerContainerVariants(reducedMotion || skipStagger)}
      initial={skipStagger ? false : "hidden"}
      animate="show"
    >
      {children}
    </motion.div>
  );
}

type MotionSectionProps = {
  children: ReactNode;
  className?: string;
  skipAnimation?: boolean;
};

export function MotionSection({ children, className, skipAnimation }: MotionSectionProps) {
  const reducedMotion = useReducedMotion();
  const instant = reducedMotion || skipAnimation;
  return (
    <motion.section className={className} variants={cardEntranceVariants(instant)}>
      {children}
    </motion.section>
  );
}

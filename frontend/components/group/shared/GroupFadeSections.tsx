"use client";

import { Children, type ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cardEntranceVariants, staggerContainerVariants } from "@/lib/motion/variants";

type GroupFadeSectionsProps = {
  children: ReactNode;
  className?: string;
  /** When true (e.g. soft SWR refresh), skip entrance so content does not re-animate from zero. */
  skipEntrance?: boolean;
};

/** Staggered section entrance for Group tabs. Respects prefers-reduced-motion. */
export function GroupFadeSections({ children, className = "", skipEntrance = false }: GroupFadeSectionsProps) {
  const reduced = useReducedMotion() ?? false;
  const items = Children.toArray(children);

  if (skipEntrance || reduced) {
    return <div className={`space-y-6 ${className}`}>{children}</div>;
  }

  return (
    <motion.div
      className={`space-y-6 ${className}`}
      variants={staggerContainerVariants(false)}
      initial="hidden"
      animate="show"
    >
      {items.map((child, i) => (
        <motion.div key={i} variants={cardEntranceVariants(false)}>
          {child}
        </motion.div>
      ))}
    </motion.div>
  );
}

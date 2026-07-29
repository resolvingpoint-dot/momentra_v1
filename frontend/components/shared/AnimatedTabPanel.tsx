"use client";

import { AnimatePresence, motion } from "framer-motion";
import type { ReactNode } from "react";
import { fadeSlideVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { MOTION_DURATION_S } from "@/lib/motion/tokens";

const TAB_ORDER = ["pulse", "moments", "life", "memory"] as const;

export type AnimatedTabId = (typeof TAB_ORDER)[number] | string;

function tabDirection(from: string, to: string): 1 | -1 {
  const a = TAB_ORDER.indexOf(from as (typeof TAB_ORDER)[number]);
  const b = TAB_ORDER.indexOf(to as (typeof TAB_ORDER)[number]);
  if (a < 0 || b < 0) return 1;
  return b >= a ? 1 : -1;
}

type AnimatedTabPanelProps = {
  tabKey: string;
  previousTabKey: string;
  children: ReactNode;
  className?: string;
};

/** Legacy: unmounts inactive tab content. Prefer PersistentTabStack for personal home. */
export function AnimatedTabPanel({
  tabKey,
  previousTabKey,
  children,
  className = "flex min-h-0 flex-1 flex-col",
}: AnimatedTabPanelProps) {
  const reducedMotion = useReducedMotion();
  const direction = tabDirection(previousTabKey, tabKey);

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={tabKey}
        className={className}
        variants={fadeSlideVariants(direction, reducedMotion)}
        initial="initial"
        animate="animate"
        exit="exit"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

type PersistentTabStackProps = {
  activeTab: string;
  previousTab: string;
  tabs: { id: string; children: ReactNode }[];
  className?: string;
};

/**
 * Keeps all tab panels mounted; toggles visibility so children retain state
 * and skip remount animations on tab return.
 */
export function PersistentTabStack({
  activeTab,
  previousTab,
  tabs,
  className = "relative flex min-h-0 flex-1 flex-col",
}: PersistentTabStackProps) {
  const reducedMotion = useReducedMotion();
  const direction = tabDirection(previousTab, activeTab);

  return (
    <div className={className}>
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <motion.div
            key={tab.id}
            className="flex min-h-0 flex-1 flex-col"
            aria-hidden={!isActive}
            style={{
              display: isActive ? "flex" : "none",
              pointerEvents: isActive ? "auto" : "none",
            }}
            initial={
              isActive && !reducedMotion
                ? { opacity: 0.96, x: direction * 8 }
                : false
            }
            animate={
              isActive
                ? reducedMotion
                  ? { opacity: 1, x: 0 }
                  : { opacity: 1, x: 0 }
                : { opacity: 0, x: 0 }
            }
            transition={
              isActive && !reducedMotion
                ? {
                    opacity: { duration: MOTION_DURATION_S.fast },
                    x: {
                      duration: MOTION_DURATION_S.normal,
                      ease: [0.22, 1, 0.36, 1],
                    },
                  }
                : { duration: 0 }
            }
          >
            {tab.children}
          </motion.div>
        );
      })}
    </div>
  );
}

import type { Variants, Transition } from "framer-motion";
import {
  MOTION_DURATION_S,
  MOTION_EASE,
  MOTION_SLIDE_PX,
  MOTION_SPRING,
  MOTION_STAGGER,
} from "./tokens";

export function instantTransition(reducedMotion: boolean): Transition {
  return reducedMotion ? { duration: 0 } : { duration: MOTION_DURATION_S.normal, ease: MOTION_EASE.out };
}

export function fadeSlideVariants(
  direction: 1 | -1 = 1,
  reducedMotion = false,
): Variants {
  if (reducedMotion) {
    return {
      initial: { opacity: 1, x: 0 },
      animate: { opacity: 1, x: 0 },
      exit: { opacity: 1, x: 0 },
    };
  }
  const offset = direction * MOTION_SLIDE_PX;
  return {
    initial: { opacity: 0, x: -offset },
    animate: { opacity: 1, x: 0, transition: { duration: MOTION_DURATION_S.medium, ease: MOTION_EASE.out } },
    exit: { opacity: 0, x: offset, transition: { duration: MOTION_DURATION_S.fast, ease: MOTION_EASE.out } },
  };
}

export const staggerContainerVariants = (reducedMotion = false): Variants => ({
  hidden: {},
  show: {
    transition: reducedMotion
      ? { staggerChildren: 0 }
      : { staggerChildren: MOTION_STAGGER.card, delayChildren: 0.04 },
  },
});

export const cardEntranceVariants = (reducedMotion = false): Variants => ({
  hidden: reducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 14 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: MOTION_DURATION_S.medium, ease: MOTION_EASE.out },
  },
});

export const fieldStaggerVariants = (reducedMotion = false): Variants => ({
  hidden: reducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: MOTION_DURATION_S.normal, ease: MOTION_EASE.out },
  },
});

export const fieldStaggerContainer = (reducedMotion = false): Variants => ({
  hidden: {},
  show: {
    transition: reducedMotion
      ? { staggerChildren: 0 }
      : { staggerChildren: MOTION_STAGGER.field },
  },
});

export const sheetBackdropVariants = (reducedMotion = false): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: reducedMotion ? { duration: 0 } : { duration: MOTION_DURATION_S.normal },
  },
  exit: {
    opacity: 0,
    transition: reducedMotion ? { duration: 0 } : { duration: MOTION_DURATION_S.fast },
  },
});

export const sheetPanelVariants = (reducedMotion = false): Variants => ({
  hidden: { y: "100%", opacity: reducedMotion ? 1 : 0.96 },
  visible: {
    y: 0,
    opacity: 1,
    transition: reducedMotion ? { duration: 0 } : MOTION_SPRING.sheet,
  },
  exit: {
    y: "100%",
    opacity: 0,
    transition: reducedMotion ? { duration: 0 } : { duration: MOTION_DURATION_S.fast, ease: MOTION_EASE.out },
  },
});

export const successPulseVariants = (reducedMotion = false): Variants => ({
  idle: { scale: 1 },
  pulse: reducedMotion
    ? { scale: 1 }
    : {
        scale: [1, 1.05, 1],
        transition: { duration: MOTION_DURATION_S.slow, ease: MOTION_EASE.out },
      },
});

export const tabContentVariants = (reducedMotion = false): Variants => ({
  hidden: { opacity: 0, x: reducedMotion ? 0 : 8 },
  visible: {
    opacity: 1,
    x: 0,
    transition: reducedMotion ? { duration: 0 } : { duration: MOTION_DURATION_S.normal, ease: MOTION_EASE.out },
  },
  exit: {
    opacity: 0,
    x: reducedMotion ? 0 : -8,
    transition: reducedMotion ? { duration: 0 } : { duration: MOTION_DURATION_S.fast },
  },
});

/** Cross-platform motion vocabulary — keep in sync with Android PersonalMotionTokens + iOS PersonalMotionTiming */

export const MOTION_DURATION_MS = {
  fast: 120,
  normal: 220,
  medium: 320,
  slow: 500,
  orbLoop: 35000,
  skeleton: 1000,
} as const;

export const MOTION_DURATION_S = {
  fast: MOTION_DURATION_MS.fast / 1000,
  normal: MOTION_DURATION_MS.normal / 1000,
  medium: MOTION_DURATION_MS.medium / 1000,
  slow: MOTION_DURATION_MS.slow / 1000,
  orbLoop: MOTION_DURATION_MS.orbLoop / 1000,
} as const;

export const MOTION_EASE = {
  out: [0.22, 1, 0.36, 1] as const,
  inOut: [0.45, 0, 0.55, 1] as const,
};

export const MOTION_SPRING = {
  soft: { type: "spring" as const, stiffness: 260, damping: 28, mass: 0.8 },
  standard: { type: "spring" as const, stiffness: 380, damping: 32, mass: 0.9 },
  bouncy: { type: "spring" as const, stiffness: 420, damping: 22, mass: 0.85 },
  sheet: { type: "spring" as const, stiffness: 340, damping: 34, mass: 0.95 },
};

export const MOTION_STAGGER = {
  card: 0.12,
  field: 0.06,
};

export const MOTION_SLIDE_PX = 12;

export const MOTION_PRESS = {
  scale: 0.97,
  hoverLiftPx: 2,
};

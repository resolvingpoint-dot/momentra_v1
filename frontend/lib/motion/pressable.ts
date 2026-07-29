import type { CSSProperties } from "react";
import { MOTION_DURATION_MS, MOTION_PRESS } from "./tokens";

export const pressableMotionClass =
  "transition-[transform,box-shadow] duration-[120ms] ease-out hover:-translate-y-0.5 hover:shadow-lg active:scale-[0.97]";

export function pressableMotionStyle(reducedMotion = false): CSSProperties {
  if (reducedMotion) return {};
  return {
    transition: `transform ${MOTION_DURATION_MS.fast}ms ease-out, box-shadow ${MOTION_DURATION_MS.fast}ms ease-out`,
  };
}

export const PRESS_SCALE = MOTION_PRESS.scale;

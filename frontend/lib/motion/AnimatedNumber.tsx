"use client";

import { useEffect } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { useReducedMotion } from "./useReducedMotion";
import { MOTION_SPRING } from "./tokens";

type AnimatedNumberProps = {
  value: number;
  format?: (n: number) => string;
  className?: string;
  style?: React.CSSProperties;
};

export function AnimatedNumber({
  value,
  format = (n) => String(Math.round(n)),
  className,
  style,
}: AnimatedNumberProps) {
  const reducedMotion = useReducedMotion();
  const spring = useSpring(value, reducedMotion ? { stiffness: 1000, damping: 100 } : MOTION_SPRING.soft);
  const display = useTransform(spring, (v) => format(v));

  useEffect(() => {
    spring.set(value);
  }, [value, spring]);

  return <motion.span className={className} style={style}>{display}</motion.span>;
}

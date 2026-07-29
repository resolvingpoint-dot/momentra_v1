"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { successPulseVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";

type SuccessPulseProps = {
  active: boolean;
  children: ReactNode;
  className?: string;
};

export function SuccessPulse({ active, children, className }: SuccessPulseProps) {
  const reducedMotion = useReducedMotion();
  return (
    <motion.div
      className={className}
      variants={successPulseVariants(reducedMotion)}
      animate={active ? "pulse" : "idle"}
    >
      {children}
    </motion.div>
  );
}

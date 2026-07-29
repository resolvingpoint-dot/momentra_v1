"use client";

import type { ButtonHTMLAttributes, ReactNode } from "react";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { pressableMotionClass, pressableMotionStyle } from "@/lib/motion/pressable";

type LoCtaButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  variant?: "primary" | "secondary";
};

export function LoCtaButton({
  children,
  variant = "primary",
  className = "",
  style,
  type = "button",
  ...props
}: LoCtaButtonProps) {
  const reducedMotion = useReducedMotion();
  const base =
    variant === "primary"
      ? "rounded-xl px-4 py-3 text-sm font-semibold"
      : "rounded-xl border px-4 py-3 text-sm font-semibold";

  return (
    <button
      type={type}
      className={`${base} ${reducedMotion ? "" : pressableMotionClass} ${className}`}
      style={{ ...pressableMotionStyle(reducedMotion), ...style }}
      {...props}
    >
      {children}
    </button>
  );
}

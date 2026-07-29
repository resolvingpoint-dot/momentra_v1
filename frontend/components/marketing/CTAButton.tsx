"use client";

import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { ReactNode } from "react";
import { trackMarketingCta } from "@/lib/marketing/track";

interface CTAButtonProps {
  children: ReactNode;
  variant?: "primary" | "secondary";
  size?: "sm" | "md" | "lg";
  href?: string;
  onClick?: (e: React.MouseEvent<HTMLAnchorElement>) => void;
  className?: string;
  /** Analytics event name for CTA tracking */
  event?: string;
}

export default function CTAButton({
  children,
  variant = "primary",
  size = "md",
  href,
  onClick,
  className = "",
  event,
}: CTAButtonProps) {
  const sizeClasses = {
    sm: "px-5 py-2.5 text-sm",
    md: "px-6 py-3 text-sm",
    lg: "px-8 py-4 text-base",
  };

  const base =
    "inline-flex items-center justify-center font-semibold rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-ember-500/50";

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    if (event) trackMarketingCta(event, { href: href || "#" });
    onClick?.(e);
  };

  return (
    <motion.a
      href={href || "#"}
      onClick={handleClick}
      data-cta={event || undefined}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      className={`${base} ${sizeClasses[size]} ${
        variant === "primary"
          ? "bg-gradient-cta shadow-lg shadow-ember-500/25 hover:brightness-110"
          : "border border-text-on-dark/35 bg-transparent text-text-on-dark hover:border-ember-500 hover:bg-white/5"
      } ${className}`}
    >
      {children}
      {variant === "primary" && <ArrowRight size={18} className="ml-2" />}
    </motion.a>
  );
}

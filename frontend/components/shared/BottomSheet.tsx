"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, type ReactNode } from "react";
import { sheetBackdropVariants, sheetPanelVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";

type BottomSheetProps = {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  /** sm+ centered modal; default bottom sheet on mobile */
  className?: string;
  panelClassName?: string;
  ariaLabelledBy?: string;
};

export function BottomSheet({
  open,
  onClose,
  children,
  className = "",
  panelClassName = "",
  ariaLabelledBy,
}: BottomSheetProps) {
  const reducedMotion = useReducedMotion();
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key !== "Tab" || !panelRef.current) return;
      const focusable = panelRef.current.querySelectorAll<HTMLElement>(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
      );
      if (focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    const first = panelRef.current?.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])',
    );
    first?.focus();
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open ? (
        <motion.div
          className={`fixed inset-0 z-50 flex items-end justify-center sm:items-center ${className}`}
          role="presentation"
          initial="hidden"
          animate="visible"
          exit="exit"
        >
          <motion.button
            type="button"
            aria-label="Close"
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            variants={sheetBackdropVariants(reducedMotion)}
            onClick={onClose}
          />
          <motion.div
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby={ariaLabelledBy}
            className={`relative z-10 max-h-[92vh] w-full max-w-lg overflow-hidden rounded-t-2xl sm:rounded-2xl ${panelClassName}`}
            variants={sheetPanelVariants(reducedMotion)}
            onClick={(e) => e.stopPropagation()}
          >
            {children}
          </motion.div>
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}

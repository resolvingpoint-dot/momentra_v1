"use client";

import { useEffect, useId, useRef } from "react";
import { motion } from "framer-motion";
import { sheetBackdropVariants, sheetPanelVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { TEAM_OPS } from "../shared/teamOpsTheme";

type Props = {
  open: boolean;
  title: string;
  busy?: boolean;
  error?: string | null;
  onClose: () => void;
  onConfirm: () => Promise<void> | void;
};

export function TeamOperationsActivityDeleteDialog({
  open,
  title,
  busy,
  error,
  onClose,
  onConfirm,
}: Props) {
  const reduced = useReducedMotion();
  const titleId = useId();
  const confirmRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (open) window.setTimeout(() => confirmRef.current?.focus(), 50);
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="presentation">
      <motion.button
        type="button"
        className="absolute inset-0 bg-black/50"
        aria-label="Dismiss delete dialog"
        variants={sheetBackdropVariants(reduced)}
        initial="hidden"
        animate="visible"
        onClick={onClose}
      />
      <motion.div
        role="alertdialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative z-10 w-full max-w-sm rounded-2xl p-5"
        style={{ background: TEAM_OPS.surface, color: TEAM_OPS.onSurface }}
        variants={sheetPanelVariants(reduced)}
        initial="hidden"
        animate="visible"
      >
        <h2 id={titleId} className="text-lg font-semibold" style={{ fontFamily: TEAM_OPS.fontDisplay }}>
          Soft delete activity?
        </h2>
        <p className="mt-2 text-sm" style={{ color: TEAM_OPS.onVariant }}>
          “{title}” will be voided and removed from active projections.
        </p>
        {error ? (
          <p className="mt-2 text-sm" role="alert" style={{ color: TEAM_OPS.error }}>
            {error}
          </p>
        ) : null}
        <div className="mt-4 flex gap-2">
          <button
            ref={confirmRef}
            type="button"
            disabled={busy}
            className="rounded-xl px-4 py-2 text-sm font-semibold disabled:opacity-50"
            style={{ background: TEAM_OPS.error, color: "#1a0000", minHeight: 44 }}
            onClick={() => void onConfirm()}
          >
            Delete
          </button>
          <button
            type="button"
            disabled={busy}
            className="rounded-xl px-4 py-2 text-sm font-semibold"
            style={{ background: TEAM_OPS.surfaceHigh, color: TEAM_OPS.onVariant, minHeight: 44 }}
            onClick={onClose}
          >
            Cancel
          </button>
        </div>
      </motion.div>
    </div>
  );
}

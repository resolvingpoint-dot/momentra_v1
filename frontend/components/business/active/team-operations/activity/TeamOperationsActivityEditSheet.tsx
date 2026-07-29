"use client";

import { useEffect, useId, useRef, useState } from "react";
import { motion } from "framer-motion";
import { sheetBackdropVariants, sheetPanelVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { TEAM_OPS } from "../shared/teamOpsTheme";

type Props = {
  open: boolean;
  initialTitle: string;
  busy?: boolean;
  error?: string | null;
  onClose: () => void;
  onSave: (title: string) => Promise<void> | void;
};

export function TeamOperationsActivityEditSheet({
  open,
  initialTitle,
  busy,
  error,
  onClose,
  onSave,
}: Props) {
  const reduced = useReducedMotion();
  const [title, setTitle] = useState(initialTitle);
  const titleId = useId();
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setTitle(initialTitle);
      window.setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open, initialTitle]);

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
    <div className="fixed inset-0 z-50 flex items-end justify-center" role="presentation">
      <motion.button
        type="button"
        className="absolute inset-0 bg-black/50"
        aria-label="Dismiss edit sheet"
        variants={sheetBackdropVariants(reduced)}
        initial="hidden"
        animate="visible"
        exit="exit"
        onClick={onClose}
      />
      <motion.div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative z-10 w-full max-w-lg rounded-t-2xl p-5"
        style={{ background: TEAM_OPS.surface, color: TEAM_OPS.onSurface }}
        variants={sheetPanelVariants(reduced)}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        <h2 id={titleId} className="text-lg font-semibold" style={{ fontFamily: TEAM_OPS.fontDisplay }}>
          Edit activity
        </h2>
        <label className="mt-3 block text-xs" style={{ color: TEAM_OPS.onVariant }}>
          Title
          <input
            ref={inputRef}
            className="mt-1 w-full rounded-xl px-3 py-2 text-sm outline-none focus-visible:ring-2"
            style={{
              background: TEAM_OPS.bg,
              color: TEAM_OPS.onSurface,
              border: `1px solid ${TEAM_OPS.outline}55`,
            }}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </label>
        {error ? (
          <p className="mt-2 text-sm" role="alert" style={{ color: TEAM_OPS.error }}>
            {error}
          </p>
        ) : null}
        <div className="mt-4 flex gap-2">
          <button
            type="button"
            disabled={busy || !title.trim()}
            className="rounded-xl px-4 py-2 text-sm font-semibold disabled:opacity-50"
            style={{ background: TEAM_OPS.primaryContainer, color: "#0d0096", minHeight: 44 }}
            onClick={() => void onSave(title.trim())}
          >
            Save
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

"use client";

import type { GuidedSetupSaveState } from "@/components/setup/guidedSetupTypes";

type Props = {
  saveState: GuidedSetupSaveState;
  onRetrySave?: () => void;
};

export function GuidedSetupSaveIndicator({ saveState, onRetrySave }: Props) {
  const label =
    saveState === "dirty"
      ? "Unsaved changes"
      : saveState === "saving"
        ? "Saving…"
        : saveState === "saved"
          ? "Saved"
          : saveState === "error"
            ? "Couldn't save"
            : "";

  if (!label) return null;

  if (saveState === "error" && onRetrySave) {
    return (
      <button
        type="button"
        onClick={onRetrySave}
        className="min-h-11 text-xs font-semibold underline opacity-80"
        aria-live="assertive"
      >
        {label} — Retry
      </button>
    );
  }

  return (
    <span className="text-xs opacity-60" aria-live="polite" role="status">
      {saveState === "saved" ? "✓ Saved" : label}
    </span>
  );
}

"use client";

import { useEffect } from "react";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";

export type AppToastTone = "success" | "error" | "info";

export type AppToastProps = {
  message: string;
  tone?: AppToastTone;
  open: boolean;
  onDismiss?: () => void;
  actionLabel?: string;
  onAction?: () => void;
  /** Auto-dismiss ms; 0 = persist until dismiss. Default 2800 success / 5000 error. */
  durationMs?: number;
};

export function AppToast({
  message,
  tone = "success",
  open,
  onDismiss,
  actionLabel,
  onAction,
  durationMs,
}: AppToastProps) {
  const { colors } = usePersonalDomainTokens();
  const autoMs =
    durationMs ?? (tone === "error" ? 5000 : tone === "success" ? 2800 : 3500);

  useEffect(() => {
    if (!open || !onDismiss || autoMs <= 0) return;
    const id = window.setTimeout(onDismiss, autoMs);
    return () => window.clearTimeout(id);
  }, [open, onDismiss, autoMs]);

  if (!open || !message) return null;

  const bg =
    tone === "error"
      ? colors.error ?? "#c44"
      : tone === "success"
        ? colors.brandPrimaryContainer ?? colors.brandPrimary
        : colors.surfaceContainerHigh ?? colors.surface;
  const fg = tone === "info" ? colors.textPrimary : colors.brandOnPrimary ?? "#fff";

  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      aria-live={tone === "error" ? "assertive" : "polite"}
      className="pointer-events-auto fixed left-1/2 z-[80] flex max-w-[min(92vw,420px)] -translate-x-1/2 items-center gap-3 rounded-2xl px-4 py-3 shadow-lg"
      style={{
        bottom: "max(1.25rem, env(safe-area-inset-bottom))",
        background: bg,
        color: fg,
      }}
    >
      <p className="flex-1 text-sm font-medium" style={{ ...personalTypography.bodyMd, color: fg }}>
        {message}
      </p>
      {actionLabel && onAction ? (
        <button
          type="button"
          onClick={onAction}
          className="shrink-0 text-sm font-semibold underline"
          style={{ color: fg }}
        >
          {actionLabel}
        </button>
      ) : null}
      {onDismiss ? (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss"
          className="shrink-0 text-sm opacity-80"
          style={{ color: fg }}
        >
          ✕
        </button>
      ) : null}
    </div>
  );
}

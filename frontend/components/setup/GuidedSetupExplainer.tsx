"use client";

import { useEffect, useId, useRef, useState } from "react";
import { HelpCircle, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type Props = {
  title: string;
  body: string;
  label?: string;
};

/** Accessible "?" popover for jargon fields. */
export function GuidedSetupExplainer({ title, body, label = "More information" }: Props) {
  const { colors } = useThemeTokens();
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const buttonRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setOpen(false);
        buttonRef.current?.focus();
      }
    };
    const onPointer = (e: MouseEvent) => {
      const t = e.target as Node;
      if (panelRef.current?.contains(t) || buttonRef.current?.contains(t)) return;
      setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    window.addEventListener("mousedown", onPointer);
    return () => {
      window.removeEventListener("keydown", onKey);
      window.removeEventListener("mousedown", onPointer);
    };
  }, [open]);

  return (
    <span className="relative inline-flex align-middle">
      <button
        ref={buttonRef}
        type="button"
        className="inline-flex size-11 items-center justify-center rounded-full"
        aria-label={label}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((v) => !v)}
      >
        <HelpCircle className="size-4 opacity-70" aria-hidden />
      </button>
      {open ? (
        <div
          ref={panelRef}
          id={panelId}
          role="dialog"
          aria-label={title}
          className="absolute left-0 top-full z-20 mt-1 w-[min(18rem,calc(100vw-2rem))] rounded-xl border p-3 shadow-lg"
          style={{
            background: colors.surfaceContainer,
            borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
            color: colors.textPrimary,
          }}
        >
          <div className="mb-1 flex items-start justify-between gap-2">
            <p className="text-sm font-semibold">{title}</p>
            <button
              type="button"
              className="flex size-8 items-center justify-center rounded-full"
              aria-label="Close"
              onClick={() => {
                setOpen(false);
                buttonRef.current?.focus();
              }}
            >
              <X className="size-3.5" />
            </button>
          </div>
          <p className="text-xs leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
            {body}
          </p>
        </div>
      ) : null}
    </span>
  );
}

"use client";

import { useEffect, useId, useRef, useState, type ReactNode } from "react";
import { Info, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { getWidgetExplainer } from "@/lib/personal/widgetExplainers";
import { getGroupWidgetExplainer } from "@/lib/group/widgetExplainers";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";

type WidgetInfoButtonProps = {
  explainerId: string;
  momentTypeCode?: string | null;
  /** Catalog domain; defaults to personal My Money. */
  domain?: "personal" | "group";
  label?: string;
};

/** Accessible "i" popover: What / Why / How for Personal or Group widgets. */
export function WidgetInfoButton({
  explainerId,
  momentTypeCode,
  domain = "personal",
  label = "About this widget",
}: WidgetInfoButtonProps) {
  const { colors } = useThemeTokens();
  const explainer =
    domain === "group"
      ? getGroupWidgetExplainer(explainerId, momentTypeCode)
      : getWidgetExplainer(explainerId, momentTypeCode);
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

  if (!explainer) return null;

  return (
    <span className="relative inline-flex align-middle">
      <button
        ref={buttonRef}
        type="button"
        className="inline-flex size-11 items-center justify-center rounded-full"
        aria-label={label}
        aria-expanded={open}
        aria-controls={panelId}
        onClick={(e) => {
          e.stopPropagation();
          setOpen((v) => !v);
        }}
      >
        <Info className="size-3.5 opacity-70" aria-hidden style={{ color: colors.textSecondary }} />
      </button>
      {open ? (
        <div
          ref={panelRef}
          id={panelId}
          role="dialog"
          aria-label={explainer.title}
          className="absolute left-0 top-full z-30 mt-1 w-[min(20rem,calc(100vw-2rem))] rounded-xl border p-3 shadow-lg"
          style={{
            background: colors.surfaceContainer,
            borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
            color: colors.textPrimary,
          }}
        >
          <div className="mb-2 flex items-start justify-between gap-2">
            <p className="text-sm font-semibold">{explainer.title}</p>
            <button
              type="button"
              className="flex size-8 shrink-0 items-center justify-center rounded-full"
              aria-label="Close"
              onClick={() => {
                setOpen(false);
                buttonRef.current?.focus();
              }}
            >
              <X className="size-3.5" />
            </button>
          </div>
          <ExplainerBlock label="What it shows" body={explainer.what} color={colors.textSecondary} />
          <ExplainerBlock label="Why it matters" body={explainer.why} color={colors.textSecondary} />
          <ExplainerBlock label="How we calculate it" body={explainer.how} color={colors.textSecondary} />
        </div>
      ) : null}
    </span>
  );
}

function ExplainerBlock({
  label,
  body,
  color,
}: {
  label: string;
  body: string;
  color: string;
}) {
  return (
    <div className="mb-2 last:mb-0">
      <p className="text-[10px] font-bold uppercase tracking-wider opacity-60" style={{ color }}>
        {label}
      </p>
      <p className="mt-0.5 text-xs leading-relaxed opacity-90" style={{ color }}>
        {body}
      </p>
    </div>
  );
}

type PersonalWidgetSectionHeaderProps = {
  title: string;
  explainerId?: string;
  momentTypeCode?: string | null;
  trailing?: ReactNode;
  uppercase?: boolean;
  className?: string;
};

/** Section title with optional widget info (i) control. */
export function PersonalWidgetSectionHeader({
  title,
  explainerId,
  momentTypeCode,
  trailing,
  uppercase = false,
  className = "",
}: PersonalWidgetSectionHeaderProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className={`flex items-center justify-between gap-2 ${className}`}>
      <div className="flex min-w-0 items-center gap-0.5">
        <h3
          style={{
            ...personalTypography.sectionHeader,
            color: colors.textPrimary,
            ...(uppercase
              ? { textTransform: "uppercase", letterSpacing: "0.08em", fontSize: 11, opacity: 0.7 }
              : {}),
          }}
        >
          {title}
        </h3>
        {explainerId ? (
          <WidgetInfoButton
            explainerId={explainerId}
            momentTypeCode={momentTypeCode}
            domain="personal"
          />
        ) : null}
      </div>
      {trailing}
    </div>
  );
}

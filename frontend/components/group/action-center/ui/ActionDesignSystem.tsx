"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { successPulseVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";

export function ActionHeader({
  title,
  subtitle,
  estimatedTimeSec,
}: {
  title: string;
  subtitle?: string;
  estimatedTimeSec?: number;
}) {
  const { colors } = useThemeTokens();
  return (
    <header className="space-y-1 pb-2">
      <p className="text-xs font-semibold uppercase tracking-widest" style={{ color: colors.primaryContainer }}>
        Quick Add Action
      </p>
      <div className="flex items-baseline justify-between gap-3">
        <h2 className="text-2xl font-semibold md:text-3xl" style={{ color: colors.textPrimary }}>
          {title}
        </h2>
        {estimatedTimeSec != null ? (
          <span className="shrink-0 text-xs font-medium" style={{ color: colors.textSecondary }}>
            ~{estimatedTimeSec} sec
          </span>
        ) : null}
      </div>
      {subtitle ? (
        <p className="text-sm" style={{ color: colors.textSecondary }}>
          {subtitle}
        </p>
      ) : null}
    </header>
  );
}

export function ActionContextChips({ chips }: { chips: string[] }) {
  const { colors } = useThemeTokens();
  const unique = Array.from(new Set(chips.filter(Boolean)));
  if (!unique.length) return null;
  return (
    <div className="flex flex-wrap gap-2 pb-2">
      {unique.map((chip, index) => (
        <span
          key={`${index}-${chip}`}
          className="rounded-full border px-3 py-1 text-xs"
          style={{
            background: colors.surfaceContainer,
            borderColor: `${colors.textSecondary}30`,
            color: colors.textSecondary,
          }}
        >
          {chip}
        </span>
      ))}
    </div>
  );
}

export function ActionHeroBanner({
  imageUrl,
  heightClass = "h-40 md:h-56",
}: {
  imageUrl?: string | null;
  heightClass?: string;
}) {
  const { colors } = useThemeTokens();
  return (
    <div className={`relative mb-6 overflow-hidden rounded-3xl ${heightClass}`}>
      {imageUrl ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={imageUrl} alt="" className="h-full w-full object-cover" />
      ) : (
        <div
          className="h-full w-full"
          style={{
            background: `linear-gradient(135deg, ${colors.primaryContainer} 0%, ${colors.primaryContainer}66 50%, ${colors.surfaceContainer} 100%)`,
          }}
        />
      )}
      <div
        className="absolute inset-0"
        style={{ background: `linear-gradient(to top, ${colors.background}cc 0%, transparent 60%)` }}
      />
    </div>
  );
}

export function ActionGlassCard({ children }: { children: ReactNode }) {
  const { colors } = useThemeTokens();
  return (
    <div
      className="space-y-5 rounded-3xl border p-5"
      style={{
        background: `${colors.surfaceContainer}A6`,
        borderColor: `${colors.textSecondary}14`,
        backdropFilter: "blur(16px)",
      }}
    >
      {children}
    </div>
  );
}

export function ActionSection({
  title,
  children,
  step,
  totalSteps,
}: {
  title?: string;
  children: ReactNode;
  step?: number;
  totalSteps?: number;
}) {
  const { colors } = useThemeTokens();
  return (
    <section className="space-y-3">
      {(title || step != null) && (
        <div className="flex items-center justify-between">
          {title ? (
            <h3 className="text-xs font-bold uppercase tracking-widest" style={{ color: colors.primaryContainer }}>
              {title}
            </h3>
          ) : (
            <span />
          )}
          {step != null && totalSteps != null ? (
            <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: colors.textSecondary }}>
              Step {step} / {totalSteps}
            </span>
          ) : null}
        </div>
      )}
      {children}
    </section>
  );
}

export function ActionSummaryCard({ rows }: { rows: Array<{ label: string; value: string }> }) {
  const { colors } = useThemeTokens();
  if (!rows.length) return null;
  return (
    <div
      className="rounded-2xl border p-4 space-y-2"
      style={{ background: `${colors.surfaceContainer}CC`, borderColor: `${colors.textSecondary}20` }}
    >
      <p className="text-[10px] font-bold uppercase tracking-widest" style={{ color: colors.textSecondary }}>
        Summary
      </p>
      {rows.map((r) => (
        <div key={r.label} className="flex justify-between gap-3 text-sm">
          <span style={{ color: colors.textSecondary }}>{r.label}</span>
          <span className="font-medium text-right" style={{ color: colors.textPrimary }}>
            {r.value || "—"}
          </span>
        </div>
      ))}
    </div>
  );
}

export function ActionReviewCard({
  title,
  rows,
}: {
  title?: string;
  rows: Array<{ label: string; value: string }>;
}) {
  const { colors } = useThemeTokens();
  return (
    <div
      className="rounded-2xl border p-5 space-y-4"
      style={{ background: colors.surfaceContainer, borderColor: `${colors.primaryContainer}30` }}
    >
      {title ? (
        <h3 className="text-lg font-semibold" style={{ color: colors.textPrimary }}>
          {title}
        </h3>
      ) : null}
      <div className="space-y-3">
        {rows.map((r) => (
          <div key={r.label} className="border-b pb-2 last:border-0" style={{ borderColor: `${colors.textSecondary}15` }}>
            <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: colors.textSecondary }}>
              {r.label}
            </p>
            <p className="mt-0.5 text-sm font-medium" style={{ color: colors.textPrimary }}>
              {r.value || "—"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ActionFooter({
  primaryLabel,
  onPrimary,
  secondaryLabel,
  onSecondary,
  primaryDisabled,
  busy,
}: {
  primaryLabel: string;
  onPrimary: () => void;
  secondaryLabel?: string;
  onSecondary?: () => void;
  primaryDisabled?: boolean;
  busy?: boolean;
}) {
  const { colors } = useThemeTokens();
  return (
    <div
      className="sticky bottom-0 -mx-5 mt-6 flex gap-3 border-t px-5 py-4"
      style={{ background: colors.background, borderColor: `${colors.textSecondary}20` }}
    >
      {secondaryLabel && onSecondary ? (
        <button
          type="button"
          onClick={onSecondary}
          className="flex-1 rounded-full py-3 text-sm font-semibold"
          style={{ background: colors.surfaceContainer, color: colors.textPrimary }}
        >
          {secondaryLabel}
        </button>
      ) : null}
      <button
        type="button"
        disabled={primaryDisabled || busy}
        onClick={onPrimary}
        className="flex-[1.4] rounded-full py-3 text-sm font-bold uppercase tracking-wide disabled:opacity-50"
        style={{
          background: `linear-gradient(135deg, ${colors.primaryContainer} 0%, ${colors.primaryContainer} 100%)`,
          color: colors.brandOnPrimary,
        }}
      >
        {busy ? "Saving…" : primaryLabel}
      </button>
    </div>
  );
}

export function ActionValidationBanner({ messages }: { messages: string[] }) {
  const { colors } = useThemeTokens();
  if (!messages.length) return null;
  return (
    <div
      role="alert"
      className="rounded-xl px-3 py-2 text-sm space-y-1"
      style={{ background: `${colors.error}18`, color: colors.error }}
    >
      {messages.map((m) => (
        <p key={m}>{m}</p>
      ))}
    </div>
  );
}

export function ActionSuccessOverlay({
  open,
  message = "Saved",
  subtitle,
  onDone,
}: {
  open: boolean;
  message?: string;
  subtitle?: string;
  onDone: () => void;
}) {
  const { colors } = useThemeTokens();
  const reduced = useReducedMotion();
  if (!open) return null;
  return (
    <div className="absolute inset-0 z-20 flex items-center justify-center" style={{ background: `${colors.background}E6` }}>
      <motion.div
        variants={successPulseVariants(reduced)}
        initial="idle"
        animate="pulse"
        onAnimationComplete={onDone}
        className="rounded-full px-8 py-4 text-center"
        style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
      >
        <p className="text-lg font-bold">{message}</p>
        {subtitle ? <p className="mt-1 text-sm opacity-90">{subtitle}</p> : null}
      </motion.div>
    </div>
  );
}

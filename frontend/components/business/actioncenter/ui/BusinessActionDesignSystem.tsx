"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { successPulseVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";

const BUSINESS_ACCENT = {
  teal: "#0D9488",
  navy: "#1E3A5F",
  tealLight: "#14B8A6",
  navyLight: "#2563EB",
};

export function BusinessActionHeader({
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
      <p
        className="text-xs font-semibold uppercase tracking-widest"
        style={{ color: BUSINESS_ACCENT.teal }}
      >
        Action Center
      </p>
      <div className="flex items-baseline justify-between gap-3">
        <h2
          className="text-2xl font-semibold md:text-3xl"
          style={{ color: colors.textPrimary, fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
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

export function BusinessGlassCard({ children }: { children: ReactNode }) {
  const { colors } = useThemeTokens();
  return (
    <div
      className="space-y-5 rounded-3xl border p-5"
      style={{
        background: `${colors.surfaceContainer}A6`,
        borderColor: `${BUSINESS_ACCENT.teal}18`,
        backdropFilter: "blur(16px)",
      }}
    >
      {children}
    </div>
  );
}

export function BusinessSection({
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
            <h3
              className="text-xs font-bold uppercase tracking-widest"
              style={{ color: BUSINESS_ACCENT.teal }}
            >
              {title}
            </h3>
          ) : (
            <span />
          )}
          {step != null && totalSteps != null ? (
            <span
              className="text-[10px] font-semibold uppercase tracking-wider"
              style={{ color: colors.textSecondary }}
            >
              Step {step} / {totalSteps}
            </span>
          ) : null}
        </div>
      )}
      {children}
    </section>
  );
}

export function BusinessReviewCard({
  title,
  rows,
}: {
  title?: string;
  rows: Array<{ label: string; value: string }>;
}) {
  const { colors } = useThemeTokens();
  return (
    <div
      className="space-y-4 rounded-2xl border p-5"
      style={{
        background: colors.surfaceContainer,
        borderColor: `${BUSINESS_ACCENT.teal}30`,
      }}
    >
      {title ? (
        <h3
          className="text-lg font-semibold"
          style={{ color: colors.textPrimary, fontFamily: "'Plus Jakarta Sans', sans-serif" }}
        >
          {title}
        </h3>
      ) : null}
      <div className="space-y-3">
        {rows.map((r) => (
          <div
            key={r.label}
            className="border-b pb-2 last:border-0"
            style={{ borderColor: `${colors.textSecondary}15` }}
          >
            <p
              className="text-[10px] font-bold uppercase tracking-wider"
              style={{ color: colors.textSecondary }}
            >
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

export function BusinessFooter({
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
          background: `linear-gradient(135deg, ${BUSINESS_ACCENT.teal} 0%, ${BUSINESS_ACCENT.navy} 100%)`,
          color: "#fff",
        }}
      >
        {busy ? "Saving…" : primaryLabel}
      </button>
    </div>
  );
}

export function BusinessValidationBanner({ messages }: { messages: string[] }) {
  const { colors } = useThemeTokens();
  if (!messages.length) return null;
  return (
    <div
      role="alert"
      className="space-y-1 rounded-xl px-3 py-2 text-sm"
      style={{ background: `${colors.error}18`, color: colors.error }}
    >
      {messages.map((m) => (
        <p key={m}>{m}</p>
      ))}
    </div>
  );
}

export function BusinessSuccessOverlay({
  open,
  message = "Saved",
  onDone,
}: {
  open: boolean;
  message?: string;
  onDone: () => void;
}) {
  const reduced = useReducedMotion();
  if (!open) return null;
  return (
    <div
      className="absolute inset-0 z-20 flex items-center justify-center"
      style={{ background: "rgba(30, 58, 95, 0.9)" }}
    >
      <motion.div
        variants={successPulseVariants(reduced)}
        initial="idle"
        animate="pulse"
        onAnimationComplete={onDone}
        className="rounded-full px-8 py-4 text-center"
        style={{
          background: `linear-gradient(135deg, ${BUSINESS_ACCENT.teal} 0%, ${BUSINESS_ACCENT.navy} 100%)`,
          color: "#fff",
        }}
      >
        <p className="text-lg font-bold">{message}</p>
      </motion.div>
    </div>
  );
}

export function BusinessContextChips({ chips }: { chips: string[] }) {
  const unique = Array.from(new Set(chips.filter(Boolean)));
  if (!unique.length) return null;
  return (
    <div className="flex flex-wrap gap-2 pb-2">
      {unique.map((chip, index) => (
        <span
          key={`${index}-${chip}`}
          className="rounded-full border px-3 py-1 text-xs font-medium"
          style={{
            background: `${BUSINESS_ACCENT.teal}1A`,
            borderColor: `${BUSINESS_ACCENT.teal}33`,
            color: BUSINESS_ACCENT.teal,
          }}
        >
          {chip}
        </span>
      ))}
    </div>
  );
}

export { BUSINESS_ACCENT };

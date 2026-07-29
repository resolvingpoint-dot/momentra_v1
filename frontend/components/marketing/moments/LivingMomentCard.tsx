"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";
import {
  Users,
  Calendar,
  Images,
  Target,
} from "lucide-react";
import type { LivingMoment } from "@/lib/marketing/moments";
import MomentPulse from "@/components/marketing/moments/MomentPulse";
import AIInsightLine from "@/components/marketing/moments/AIInsightLine";

const worldAccent = {
  personal: "border-indigo-300/30 glow-personal-sm",
  group: "border-[#ff8a6a]/35 glow-group-sm",
  business: "border-amber-500/30 glow-business-sm",
} as const;

const statusTone = {
  ok: "border-teal-500/30 bg-teal-500/10 text-teal-200",
  pending: "border-amber-500/30 bg-amber-500/10 text-amber-200",
  warn: "border-red-500/30 bg-red-500/10 text-red-200",
} as const;

export default function LivingMomentCard({
  moment,
  variant = "default",
  className = "",
  animateProgress = true,
}: {
  moment: LivingMoment;
  variant?: "default" | "compact" | "expanded";
  className?: string;
  animateProgress?: boolean;
}) {
  const isExpanded = variant === "expanded";
  const isCompact = variant === "compact";

  return (
    <div
      className={`mkt-surface relative overflow-hidden rounded-2xl border ${worldAccent[moment.world]} ${
        isExpanded ? "p-5 sm:p-7" : isCompact ? "p-4" : "p-5"
      } ${className}`}
    >
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/[0.04] to-transparent" />

      <div className="relative z-10">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="mb-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-white/40">
              {moment.purpose}
            </p>
            <h3
              className={`font-extrabold tracking-tight text-text-on-dark ${
                isExpanded
                  ? "text-2xl sm:text-3xl"
                  : isCompact
                    ? "text-lg"
                    : "text-xl sm:text-2xl"
              }`}
            >
              {moment.title}
            </h3>
          </div>
          <span className="shrink-0 rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wider text-white/55">
            {moment.world}
          </span>
        </div>

        <div
          className={`mb-4 grid gap-2 ${
            isExpanded
              ? "grid-cols-2 sm:grid-cols-4"
              : "grid-cols-2"
          }`}
        >
          {typeof moment.participants === "number" ? (
            <MetaChip
              icon={<Users size={12} />}
              label="Participants"
              value={String(moment.participants)}
            />
          ) : null}
          {moment.budgetLabel ? (
            <MetaChip
              icon={<Target size={12} />}
              label="Budget"
              value={moment.budgetLabel}
            />
          ) : null}
          <MetaChip
            icon={<Calendar size={12} />}
            label="Timeline"
            value={moment.timeline}
          />
          {moment.memoryLabel ? (
            <MetaChip
              icon={<Images size={12} />}
              label="Memory"
              value={moment.memoryLabel}
            />
          ) : null}
        </div>

        {(typeof moment.progress === "number") && (
          <div className="mb-4">
            <div className="mb-1.5 flex items-center justify-between gap-2 text-xs">
              <span className="text-white/55">
                {moment.savedLabel ?? "Progress"}
              </span>
              <span className="font-semibold text-text-on-dark">
                {moment.progress}%
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-white/10">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-ember-500 to-amber-400"
                initial={
                  animateProgress ? { width: 0 } : { width: `${moment.progress}%` }
                }
                animate={{ width: `${moment.progress}%` }}
                transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1] }}
              />
            </div>
          </div>
        )}

        {moment.metaLines?.length ? (
          <ul className="mb-4 space-y-1.5">
            {moment.metaLines.map((line) => (
              <li
                key={line}
                className="rounded-lg border border-white/8 bg-white/[0.03] px-3 py-2 text-xs text-white/75"
              >
                {line}
              </li>
            ))}
          </ul>
        ) : null}

        {moment.statuses?.length ? (
          <div className="mb-4 flex flex-wrap gap-2">
            {moment.statuses.map((s) => (
              <span
                key={s.label}
                className={`rounded-full border px-2.5 py-1 text-[11px] font-medium ${
                  statusTone[s.tone ?? "ok"]
                }`}
              >
                {s.label}
              </span>
            ))}
          </div>
        ) : null}

        <div className={`space-y-3 ${isExpanded ? "sm:space-y-4" : ""}`}>
          <MomentPulse
            health={moment.pulse.health}
            score={moment.pulse.score}
            line={moment.pulse.line}
            compact={isCompact}
          />
          <AIInsightLine insight={moment.aiInsight} />
        </div>
      </div>
    </div>
  );
}

function MetaChip({
  icon,
  label,
  value,
}: {
  icon: ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-xl border border-white/8 bg-white/[0.03] px-3 py-2">
      <div className="mb-0.5 flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-white/40">
        {icon}
        {label}
      </div>
      <p className="truncate text-sm font-semibold text-text-on-dark">{value}</p>
    </div>
  );
}

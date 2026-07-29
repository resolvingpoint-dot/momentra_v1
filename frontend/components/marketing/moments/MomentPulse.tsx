"use client";

import { motion } from "framer-motion";
import type { PulseHealth } from "@/lib/marketing/moments";

const healthStyles: Record<PulseHealth, string> = {
  Healthy: "border-teal-500/35 bg-teal-500/15 text-teal-200",
  "On Track": "border-indigo-300/35 bg-indigo-500/15 text-indigo-100",
  "Needs attention": "border-amber-500/35 bg-amber-500/15 text-amber-200",
  "At risk": "border-red-500/35 bg-red-500/15 text-red-200",
};

export default function MomentPulse({
  health,
  score,
  line,
  compact = false,
}: {
  health: PulseHealth;
  score?: number;
  line: string;
  compact?: boolean;
}) {
  return (
    <div
      className={`rounded-xl border border-white/10 bg-white/[0.04] ${
        compact ? "p-3" : "p-4"
      }`}
    >
      <div className="mb-2 flex items-center justify-between gap-3">
        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-white/45">
          Moment Pulse
        </p>
        <span
          className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[11px] font-semibold ${healthStyles[health]}`}
        >
          <motion.span
            className="h-1.5 w-1.5 rounded-full bg-current"
            animate={{ opacity: [1, 0.35, 1], scale: [1, 0.85, 1] }}
            transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
          />
          {health}
          {typeof score === "number" ? ` · ${score}%` : null}
        </span>
      </div>
      <p className={`leading-relaxed text-white/75 ${compact ? "text-xs" : "text-sm"}`}>
        {line}
      </p>
    </div>
  );
}

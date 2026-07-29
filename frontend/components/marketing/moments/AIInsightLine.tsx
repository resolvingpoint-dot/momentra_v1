"use client";

import { Sparkles } from "lucide-react";

export default function AIInsightLine({
  insight,
  label = "Moment Intelligence",
  className = "",
}: {
  insight: string;
  label?: string;
  className?: string;
}) {
  return (
    <div
      className={`rounded-xl border border-ember-500/25 bg-gradient-to-br from-ember-500/10 to-transparent p-3 sm:p-4 ${className}`}
    >
      <div className="mb-1.5 flex items-center gap-2">
        <span className="inline-flex h-6 w-6 items-center justify-center rounded-lg bg-ember-500/20 text-ember-300">
          <Sparkles size={13} />
        </span>
        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-ember-300/90">
          {label}
        </p>
      </div>
      <p className="text-sm leading-relaxed text-indigo-50/95">{insight}</p>
    </div>
  );
}

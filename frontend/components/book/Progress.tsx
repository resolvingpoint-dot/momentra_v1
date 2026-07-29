"use client";

interface ProgressProps {
  percent: number;
}

export function Progress({ percent }: ProgressProps) {
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <div className="px-2">
      <div
        className="h-1 w-full overflow-hidden rounded-full bg-white/10"
        role="progressbar"
        aria-valuenow={clamped}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Reading progress"
      >
        <div
          className="h-full rounded-full bg-ember-500 transition-[width] duration-300 ease-out"
          style={{ width: `${clamped}%` }}
        />
      </div>
      <p className="mt-1.5 text-center text-xs tabular-nums text-white/45">
        {clamped}%
      </p>
    </div>
  );
}

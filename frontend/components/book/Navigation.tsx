"use client";

interface NavigationProps {
  currentPage: number;
  totalPages: number;
  onPrev: () => void;
  onNext: () => void;
  canPrev: boolean;
  canNext: boolean;
}

export function Navigation({
  currentPage,
  totalPages,
  onPrev,
  onNext,
  canPrev,
  canNext,
}: NavigationProps) {
  return (
    <div className="flex items-center justify-between gap-4 px-2">
      <button
        type="button"
        onClick={onPrev}
        disabled={!canPrev}
        className="rounded-md px-3 py-2 text-sm text-white/80 transition hover:bg-white/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-30"
        aria-label="Previous page"
      >
        ← Previous
      </button>
      <p className="text-sm tabular-nums text-white/60">
        Page {currentPage} / {totalPages}
      </p>
      <button
        type="button"
        onClick={onNext}
        disabled={!canNext}
        className="rounded-md px-3 py-2 text-sm text-white/80 transition hover:bg-white/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-30"
        aria-label="Next page"
      >
        Next →
      </button>
    </div>
  );
}

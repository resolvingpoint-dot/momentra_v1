"use client";

import { Bookmark as BookmarkIcon } from "lucide-react";

interface BookmarkProps {
  active: boolean;
  onToggle: () => void;
}

export function Bookmark({ active, onToggle }: BookmarkProps) {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-sm text-white/70 transition hover:bg-white/10 hover:text-white"
      aria-pressed={active}
      aria-label={active ? "Remove bookmark" : "Bookmark this page"}
    >
      <BookmarkIcon
        className={`size-4 ${active ? "fill-ember-500 text-ember-500" : ""}`}
        aria-hidden
      />
      Bookmark
    </button>
  );
}

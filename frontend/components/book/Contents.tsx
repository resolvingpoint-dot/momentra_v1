"use client";

import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";
import type { BookContentsEntry } from "@/lib/book/types";

interface ContentsProps {
  open: boolean;
  onClose: () => void;
  entries: BookContentsEntry[];
  bookmarks: number[];
  currentPage: number;
  onSelectPage: (page: number) => void;
}

export function Contents({
  open,
  onClose,
  entries,
  bookmarks,
  currentPage,
  onSelectPage,
}: ContentsProps) {
  return (
    <AnimatePresence>
      {open ? (
        <>
          <motion.button
            type="button"
            aria-label="Close contents"
            className="fixed inset-0 z-40 bg-black/50"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <motion.aside
            role="dialog"
            aria-modal="true"
            aria-label="Table of contents"
            className="fixed inset-y-0 right-0 z-50 flex w-full max-w-sm flex-col border-l border-white/10 bg-[#0c0818] shadow-2xl"
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 28, stiffness: 280 }}
          >
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
              <h2 className="text-sm font-semibold tracking-wide text-white/90">
                Contents
              </h2>
              <button
                type="button"
                onClick={onClose}
                className="rounded-md p-1.5 text-white/60 hover:bg-white/10 hover:text-white"
                aria-label="Close"
              >
                <X className="size-5" />
              </button>
            </div>

            <nav className="flex-1 overflow-y-auto px-2 py-3">
              <ul className="space-y-0.5">
                {entries.map((entry) => {
                  const active = currentPage === entry.page;
                  return (
                    <li key={`${entry.title}-${entry.page}`}>
                      <button
                        type="button"
                        onClick={() => {
                          onSelectPage(entry.page);
                          onClose();
                        }}
                        className={`flex w-full items-baseline justify-between gap-3 rounded-md px-3 py-2.5 text-left text-sm transition ${
                          active
                            ? "bg-white/10 text-white"
                            : "text-white/70 hover:bg-white/5 hover:text-white"
                        }`}
                      >
                        <span>{entry.title}</span>
                        <span className="tabular-nums text-white/40">
                          {entry.page}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>

              {bookmarks.length > 0 ? (
                <div className="mt-6 border-t border-white/10 px-3 pt-4">
                  <p className="mb-2 text-xs font-medium uppercase tracking-wider text-white/40">
                    Bookmarks
                  </p>
                  <ul className="space-y-0.5">
                    {bookmarks.map((page) => (
                      <li key={page}>
                        <button
                          type="button"
                          onClick={() => {
                            onSelectPage(page);
                            onClose();
                          }}
                          className="flex w-full items-center justify-between rounded-md px-3 py-2 text-sm text-white/70 hover:bg-white/5 hover:text-white"
                        >
                          <span>Page {page}</span>
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </nav>
          </motion.aside>
        </>
      ) : null}
    </AnimatePresence>
  );
}

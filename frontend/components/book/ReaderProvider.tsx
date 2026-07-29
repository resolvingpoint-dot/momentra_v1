"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import type {
  BookManifest,
  BookMilestone,
  BookProgress,
  BookTransition,
} from "@/lib/book/types";
import {
  completionPercentForPage,
  createEmptyProgress,
  loadProgress,
  saveProgress,
  syncProgressLater,
} from "@/lib/book/progressStore";
import { pageSrc, preloadNeighbors } from "@/lib/book/preload";
import { BookAnalytics } from "@/components/book/Analytics";

interface ReaderContextValue {
  manifest: BookManifest;
  totalPages: number;
  /** 1-based */
  currentPage: number;
  completionPercent: number;
  progress: BookProgress;
  pageSrcFor: (page1Based: number) => string | null;
  goToPage: (page1Based: number) => void;
  nextPage: () => void;
  prevPage: () => void;
  toggleBookmark: () => void;
  isBookmarked: boolean;
  contentsOpen: boolean;
  setContentsOpen: (open: boolean) => void;
  activeTransition: BookTransition | null;
  dismissTransition: (action: "continue" | "open_app") => void;
  activeMilestone: BookMilestone | null;
  dismissMilestone: () => void;
  markCompleted: () => void;
}

const ReaderContext = createContext<ReaderContextValue | null>(null);

export function useReader(): ReaderContextValue {
  const ctx = useContext(ReaderContext);
  if (!ctx) throw new Error("useReader must be used within ReaderProvider");
  return ctx;
}

export function ReaderProvider({
  manifest,
  initialPage = 1,
  children,
}: {
  manifest: BookManifest;
  initialPage?: number;
  children: ReactNode;
}) {
  const totalPages = manifest.pages.length;
  const [progress, setProgress] = useState<BookProgress>(() =>
    createEmptyProgress(),
  );
  const [hydrated, setHydrated] = useState(false);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [contentsOpen, setContentsOpen] = useState(false);
  const [activeTransition, setActiveTransition] =
    useState<BookTransition | null>(null);
  const [activeMilestone, setActiveMilestone] = useState<BookMilestone | null>(
    null,
  );
  const [sessionSeenTransitions, setSessionSeenTransitions] = useState<
    Set<number>
  >(() => new Set());

  const pageEnteredAt = useRef<number>(Date.now());
  const sessionStartedAt = useRef<number>(Date.now());
  const readingTickRef = useRef<number | null>(null);

  useEffect(() => {
    const stored = loadProgress(manifest.id);
    const page = Math.max(
      1,
      Math.min(manifest.pages.length, initialPage),
    );
    const nextProgress = {
      ...stored,
      currentPage: page,
      completionPercent: completionPercentForPage(page, manifest.pages.length),
    };
    setProgress(nextProgress);
    saveProgress(manifest.id, nextProgress);
    setSessionSeenTransitions(new Set(stored.seenTransitions));
    setCurrentPage(page);
    setHydrated(true);
    void BookAnalytics.readingStarted(manifest.id, page);
  }, [manifest.id, manifest.pages.length, initialPage]);

  const persist = useCallback(
    (next: BookProgress) => {
      setProgress(next);
      saveProgress(manifest.id, next);
      void syncProgressLater(manifest.id, next);
    },
    [manifest.id],
  );

  // Accumulate reading time every 15s while tab visible
  useEffect(() => {
    if (!hydrated) return;
    const tick = () => {
      if (document.visibilityState !== "visible") return;
      setProgress((prev) => {
        const next = {
          ...prev,
          readingTimeMs: prev.readingTimeMs + 15_000,
          lastReadAt: new Date().toISOString(),
        };
        saveProgress(manifest.id, next);
        return next;
      });
    };
    readingTickRef.current = window.setInterval(tick, 15_000);
    return () => {
      if (readingTickRef.current) window.clearInterval(readingTickRef.current);
    };
  }, [hydrated, manifest.id]);

  // Session duration on unmount
  useEffect(() => {
    const started = sessionStartedAt.current;
    const bookId = manifest.id;
    return () => {
      void BookAnalytics.sessionDuration(bookId, Date.now() - started);
    };
  }, [manifest.id]);

  const checkMilestones = useCallback(
    (page: number, percent: number, prev: BookProgress): BookProgress => {
      let next = prev;
      for (const m of manifest.milestones) {
        if (next.milestones.includes(m.id)) continue;
        const byPage = m.atPage !== undefined && page >= m.atPage;
        const byPercent =
          m.atPercent !== undefined && percent >= m.atPercent;
        if (byPage || byPercent) {
          next = {
            ...next,
            milestones: [...next.milestones, m.id],
          };
          setActiveMilestone(m);
          void BookAnalytics.milestoneReached(manifest.id, m.id);
        }
      }
      return next;
    },
    [manifest.id, manifest.milestones],
  );

  const maybeShowTransition = useCallback(
    (fromPage: number, toPage: number, prev: BookProgress) => {
      if (toPage <= fromPage) return prev;
      for (const t of manifest.transitions) {
        if (fromPage <= t.afterPage && toPage > t.afterPage) {
          if (
            sessionSeenTransitions.has(t.afterPage) ||
            prev.seenTransitions.includes(t.afterPage)
          ) {
            continue;
          }
          setActiveTransition(t);
          setSessionSeenTransitions((s) => new Set(s).add(t.afterPage));
          void BookAnalytics.transitionShown(manifest.id, t.afterPage);
          return {
            ...prev,
            seenTransitions: [...prev.seenTransitions, t.afterPage],
          };
        }
      }
      return prev;
    },
    [manifest.id, manifest.transitions, sessionSeenTransitions],
  );

  const goToPage = useCallback(
    (page1Based: number) => {
      const clamped = Math.max(1, Math.min(totalPages, Math.round(page1Based)));
      const from = currentPage;
      const dwell = Date.now() - pageEnteredAt.current;
      void BookAnalytics.pageViewed(manifest.id, from, dwell);
      pageEnteredAt.current = Date.now();

      const percent = completionPercentForPage(clamped, totalPages);
      setCurrentPage(clamped);

      setProgress((prev) => {
        let next: BookProgress = {
          ...prev,
          currentPage: clamped,
          completionPercent: percent,
          lastReadAt: new Date().toISOString(),
        };
        next = maybeShowTransition(from, clamped, next);
        next = checkMilestones(clamped, percent, next);
        saveProgress(manifest.id, next);
        void syncProgressLater(manifest.id, next);
        return next;
      });

      const idx = clamped - 1;
      preloadNeighbors(manifest.assetBase, manifest.pages, idx);
    },
    [
      checkMilestones,
      currentPage,
      manifest.assetBase,
      manifest.id,
      manifest.pages,
      maybeShowTransition,
      totalPages,
    ],
  );

  const nextPage = useCallback(() => {
    if (currentPage >= totalPages) return;
    goToPage(currentPage + 1);
  }, [currentPage, goToPage, totalPages]);

  const prevPage = useCallback(() => {
    if (currentPage <= 1) return;
    goToPage(currentPage - 1);
  }, [currentPage, goToPage]);

  // Initial preload
  useEffect(() => {
    if (!hydrated) return;
    preloadNeighbors(manifest.assetBase, manifest.pages, currentPage - 1);
  }, [hydrated, manifest.assetBase, manifest.pages, currentPage]);

  const toggleBookmark = useCallback(() => {
    setProgress((prev) => {
      const has = prev.bookmarks.includes(currentPage);
      const bookmarks = has
        ? prev.bookmarks.filter((p) => p !== currentPage)
        : [...prev.bookmarks, currentPage].sort((a, b) => a - b);
      const next = { ...prev, bookmarks };
      saveProgress(manifest.id, next);
      return next;
    });
  }, [currentPage, manifest.id]);

  const dismissTransition = useCallback(
    (action: "continue" | "open_app") => {
      setActiveTransition(null);
      if (action === "open_app") {
        void BookAnalytics.openMomentraFromBook(manifest.id, "transition");
      }
    },
    [manifest.id],
  );

  const dismissMilestone = useCallback(() => {
    setActiveMilestone(null);
  }, []);

  const markCompleted = useCallback(() => {
    const percent = 100;
    persist({
      ...progress,
      currentPage: totalPages,
      completionPercent: percent,
      lastReadAt: new Date().toISOString(),
    });
    void BookAnalytics.bookCompleted(manifest.id, progress.readingTimeMs);
  }, [manifest.id, persist, progress, totalPages]);

  const pageSrcFor = useCallback(
    (page1Based: number) => {
      const idx = page1Based - 1;
      if (idx < 0 || idx >= manifest.pages.length) return null;
      return pageSrc(manifest.assetBase, manifest.pages[idx]!);
    },
    [manifest.assetBase, manifest.pages],
  );

  const value = useMemo<ReaderContextValue>(
    () => ({
      manifest,
      totalPages,
      currentPage,
      completionPercent: completionPercentForPage(currentPage, totalPages),
      progress,
      pageSrcFor,
      goToPage,
      nextPage,
      prevPage,
      toggleBookmark,
      isBookmarked: progress.bookmarks.includes(currentPage),
      contentsOpen,
      setContentsOpen,
      activeTransition,
      dismissTransition,
      activeMilestone,
      dismissMilestone,
      markCompleted,
    }),
    [
      activeMilestone,
      activeTransition,
      contentsOpen,
      currentPage,
      dismissMilestone,
      dismissTransition,
      goToPage,
      markCompleted,
      manifest,
      nextPage,
      pageSrcFor,
      prevPage,
      progress,
      toggleBookmark,
      totalPages,
    ],
  );

  return (
    <ReaderContext.Provider value={value}>{children}</ReaderContext.Provider>
  );
}

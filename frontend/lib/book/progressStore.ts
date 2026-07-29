import type { BookProgress } from "@/lib/book/types";

const STORAGE_PREFIX = "momentra.book.";

function storageKey(bookId: string): string {
  return `${STORAGE_PREFIX}${bookId}`;
}

export function createEmptyProgress(): BookProgress {
  return {
    currentPage: 1,
    completionPercent: 0,
    readingTimeMs: 0,
    lastReadAt: null,
    bookmarks: [],
    milestones: [],
    seenTransitions: [],
    version: 1,
  };
}

export function loadProgress(bookId: string): BookProgress {
  if (typeof window === "undefined") return createEmptyProgress();
  try {
    const raw = window.localStorage.getItem(storageKey(bookId));
    if (!raw) return createEmptyProgress();
    const parsed = JSON.parse(raw) as Partial<BookProgress>;
    return {
      ...createEmptyProgress(),
      ...parsed,
      bookmarks: Array.isArray(parsed.bookmarks) ? parsed.bookmarks : [],
      milestones: Array.isArray(parsed.milestones) ? parsed.milestones : [],
      seenTransitions: Array.isArray(parsed.seenTransitions)
        ? parsed.seenTransitions
        : [],
      version: 1,
    };
  } catch {
    return createEmptyProgress();
  }
}

export function saveProgress(bookId: string, progress: BookProgress): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(storageKey(bookId), JSON.stringify(progress));
  } catch {
    // Quota / private mode — ignore for v1
  }
}

export function completionPercentForPage(
  page: number,
  totalPages: number,
): number {
  if (totalPages <= 0) return 0;
  return Math.min(100, Math.round((page / totalPages) * 100));
}

/**
 * Sync-ready seam: later replace body with API upsert.
 * For now this is localStorage only.
 */
export async function syncProgressLater(
  _bookId: string,
  _progress: BookProgress,
): Promise<void> {
  // Intentionally empty — architecture hook for backend sync
}

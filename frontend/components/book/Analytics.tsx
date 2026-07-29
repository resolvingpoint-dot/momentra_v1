"use client";

import { MomentraAnalytics } from "@/lib/analytics";
import { trackMarketingCta } from "@/lib/marketing/track";

function strParams(
  params: Record<string, string | number | undefined>,
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined) continue;
    out[k] = String(v);
  }
  return out;
}

async function emit(
  name: string,
  params: Record<string, string | number | undefined> = {},
) {
  // trackMarketingCta also forwards to Firebase Analytics
  trackMarketingCta(name, { surface: "book", ...strParams(params) });
}

export const BookAnalytics = {
  bookOpened: (bookId: string) => {
    void MomentraAnalytics.logScreen("book");
    return emit("book_opened", { book_id: bookId });
  },

  readingStarted: (bookId: string, page: number) =>
    emit("reading_started", { book_id: bookId, page }),

  pageViewed: (bookId: string, page: number, dwellMs: number) =>
    emit("page_viewed", {
      book_id: bookId,
      page,
      dwell_ms: Math.round(dwellMs),
    }),

  sessionDuration: (bookId: string, durationMs: number) =>
    emit("session_duration", {
      book_id: bookId,
      duration_ms: Math.round(durationMs),
    }),

  resumeReading: (bookId: string, page: number) =>
    emit("resume_reading", { book_id: bookId, page }),

  bookCompleted: (bookId: string, readingTimeMs: number) =>
    emit("book_completed", {
      book_id: bookId,
      reading_time_ms: Math.round(readingTimeMs),
    }),

  milestoneReached: (bookId: string, milestoneId: string) =>
    emit("milestone_reached", {
      book_id: bookId,
      milestone_id: milestoneId,
    }),

  transitionShown: (bookId: string, afterPage: number) =>
    emit("transition_shown", { book_id: bookId, after_page: afterPage }),

  openMomentraFromBook: (bookId: string, source: string) =>
    emit("open_momentra_from_book", { book_id: bookId, source }),

  readerReturn: (bookId: string, completionPercent: number) =>
    emit("reader_return", {
      book_id: bookId,
      completion_percent: completionPercent,
    }),
};

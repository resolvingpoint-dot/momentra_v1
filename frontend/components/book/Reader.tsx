"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { List } from "lucide-react";
import { useReader } from "@/components/book/ReaderProvider";
import { Page } from "@/components/book/Page";
import { Navigation } from "@/components/book/Navigation";
import { Progress } from "@/components/book/Progress";
import { Bookmark } from "@/components/book/Bookmark";
import { Contents } from "@/components/book/Contents";
import { TransitionOverlay } from "@/components/book/TransitionOverlay";
import { MilestoneToast } from "@/components/book/MilestoneToast";

interface ReaderProps {
  onReachEnd: () => void;
  onExit: () => void;
}

export function Reader({ onReachEnd, onExit }: ReaderProps) {
  const router = useRouter();
  const {
    manifest,
    currentPage,
    totalPages,
    completionPercent,
    progress,
    pageSrcFor,
    goToPage,
    nextPage,
    prevPage,
    toggleBookmark,
    isBookmarked,
    contentsOpen,
    setContentsOpen,
    activeTransition,
    dismissTransition,
    activeMilestone,
    dismissMilestone,
  } = useReader();

  const src = pageSrcFor(currentPage);
  const tapLock = useRef(false);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (contentsOpen || activeTransition) return;
      if (e.key === "ArrowRight" || e.key === " ") {
        e.preventDefault();
        if (currentPage >= totalPages) {
          onReachEnd();
          return;
        }
        nextPage();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        prevPage();
      } else if (e.key === "Escape") {
        onExit();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [
    activeTransition,
    contentsOpen,
    currentPage,
    nextPage,
    onExit,
    onReachEnd,
    prevPage,
    totalPages,
  ]);

  function handleNext() {
    if (currentPage >= totalPages) {
      onReachEnd();
      return;
    }
    nextPage();
  }

  function handleTapNav(e: React.MouseEvent<HTMLDivElement>) {
    if (tapLock.current) return;
    const target = e.target as HTMLElement;
    if (target.closest("button, a, [role='dialog']")) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const third = rect.width / 3;
    tapLock.current = true;
    window.setTimeout(() => {
      tapLock.current = false;
    }, 280);

    if (x < third) {
      prevPage();
    } else if (x > third * 2) {
      handleNext();
    }
  }

  function handleOpenAppFromTransition() {
    dismissTransition("open_app");
    router.push("/app");
  }

  return (
    <div className="flex min-h-dvh flex-col bg-[#0a0614] text-white">
      <header className="sticky top-0 z-30 flex items-center justify-end gap-1 border-b border-white/5 bg-[#0a0614]/90 px-3 py-2 backdrop-blur-md sm:px-5">
        <button
          type="button"
          onClick={() => setContentsOpen(true)}
          className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-sm text-white/70 transition hover:bg-white/10 hover:text-white"
        >
          <List className="size-4" aria-hidden />
          Contents
        </button>
        <Bookmark active={isBookmarked} onToggle={toggleBookmark} />
        <button
          type="button"
          onClick={onExit}
          className="rounded-md px-2.5 py-1.5 text-sm text-white/70 transition hover:bg-white/10 hover:text-white"
        >
          Exit Reader
        </button>
      </header>

      <div
        className="relative flex-1 overflow-y-auto"
        onClick={handleTapNav}
        role="presentation"
      >
        <div className="mx-auto max-w-3xl px-0 pb-4 pt-2 sm:px-4 sm:pt-6">
          {src ? (
            <Page
              src={src}
              alt={`${manifest.title} — page ${currentPage}`}
              priority
            />
          ) : null}
        </div>

        {/* Invisible tap zones hint for mobile — left/right thirds */}
        <div className="pointer-events-none absolute inset-y-0 left-0 w-1/3 sm:hidden" />
        <div className="pointer-events-none absolute inset-y-0 right-0 w-1/3 sm:hidden" />
      </div>

      <footer className="sticky bottom-0 z-30 space-y-2 border-t border-white/5 bg-[#0a0614]/95 px-3 py-3 backdrop-blur-md sm:px-6">
        <Navigation
          currentPage={currentPage}
          totalPages={totalPages}
          onPrev={prevPage}
          onNext={handleNext}
          canPrev={currentPage > 1}
          canNext={true}
        />
        <Progress percent={completionPercent} />
      </footer>

      <Contents
        open={contentsOpen}
        onClose={() => setContentsOpen(false)}
        entries={manifest.contents}
        bookmarks={progress.bookmarks}
        currentPage={currentPage}
        onSelectPage={goToPage}
      />

      <TransitionOverlay
        transition={activeTransition}
        onContinue={() => dismissTransition("continue")}
        onOpenApp={handleOpenAppFromTransition}
      />

      <MilestoneToast
        milestone={activeMilestone}
        onDismiss={dismissMilestone}
      />
    </div>
  );
}

"use client";

import { useEffect } from "react";
import { X } from "lucide-react";
import { Life360Empty } from "@/components/life360/Life360Empty";
import { Life360Updated } from "@/components/life360/Life360Updated";
import { useAppContextState } from "@/components/theme/AppContextProvider";
import { openLifeTabFromLife360 } from "@/lib/life360ShellEvents";
import { openBusinessCreateOverlay } from "@/lib/businessShellEvents";
import { openGroupCreateOverlay } from "@/lib/groupShellEvents";
import { openPersonalCreateOverlay } from "@/lib/personalShellEvents";
import {
  ensureLife360,
  retryLife360,
  softRefreshLife360,
  useLife360Store,
} from "@/stores/life360Store";

type Life360OverlayProps = {
  open: boolean;
  onClose: () => void;
};

export function Life360Overlay({ open, onClose }: Life360OverlayProps) {
  const { context } = useAppContextState();
  const { viewState, snapshot, analytics, loading, error, refreshing } =
    useLife360Store();

  useEffect(() => {
    if (!open) return;
    void (async () => {
      await ensureLife360();
      void softRefreshLife360();
    })();
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  function handleCreateMoment() {
    onClose();
    if (context === "personal") openPersonalCreateOverlay();
    else if (context === "group") openGroupCreateOverlay();
    else if (context === "business") openBusinessCreateOverlay();
  }

  function handleExploreLife() {
    onClose();
    openLifeTabFromLife360();
  }

  const showSpinner = loading && viewState == null && !error;

  return (
    <div
      className="fixed inset-0 z-[80] flex flex-col bg-[#131313] text-[#e5e2e1]"
      role="dialog"
      aria-modal="true"
      aria-label="Life 360"
    >
      <button
        type="button"
        onClick={onClose}
        aria-label="Close Life 360"
        className="absolute right-3 top-3 z-10 flex h-10 w-10 items-center justify-center rounded-full text-[#d0c5af] hover:bg-white/5"
      >
        <X className="h-5 w-5" />
      </button>

      {refreshing && viewState != null ? (
        <div className="pointer-events-none absolute left-1/2 top-3 z-10 -translate-x-1/2 rounded-full border border-[#f2ca50]/20 bg-[#1c1b1b]/90 px-3 py-1 text-xs text-[#d0c5af]">
          Updating…
        </div>
      ) : null}

      <div className="min-h-0 flex-1 overflow-y-auto pt-2">
        {showSpinner ? (
          <div className="flex h-full min-h-[40vh] flex-col items-center justify-center gap-3 px-6">
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-[#f2ca50]/30 border-t-[#f2ca50]" />
            <p className="text-sm text-[#d0c5af]">Loading Life 360…</p>
          </div>
        ) : null}

        {error && viewState == null ? (
          <div className="flex h-full min-h-[40vh] flex-col items-center justify-center gap-4 px-6 text-center">
            <p className="text-base text-[#d0c5af]">{error}</p>
            <button
              type="button"
              onClick={() => void retryLife360()}
              className="rounded-xl bg-[#f2ca50] px-6 py-3 font-bold text-[#3c2f00]"
            >
              Retry
            </button>
          </div>
        ) : null}

        {viewState === "empty" ? (
          <Life360Empty
            onCreateMoment={handleCreateMoment}
            onExploreLifeModules={handleExploreLife}
          />
        ) : null}

        {viewState === "full" && snapshot ? (
          <Life360Updated
            snapshot={snapshot}
            analytics={analytics}
            onExploreLifeModules={handleExploreLife}
          />
        ) : null}
      </div>
    </div>
  );
}

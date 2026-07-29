"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { useAuth } from "@/components/auth/AuthProvider";
import type { BookManifest, BookPhase } from "@/lib/book/types";
import {
  completionPercentForPage,
  loadProgress,
  saveProgress,
} from "@/lib/book/progressStore";
import { BookAnalytics } from "@/components/book/Analytics";
import { Intro } from "@/components/book/Intro";
import { BookAuthGate } from "@/components/book/BookAuthGate";
import { ResumeCard } from "@/components/book/ResumeCard";
import { ReaderProvider } from "@/components/book/ReaderProvider";
import { Reader } from "@/components/book/Reader";
import { EndExperience } from "@/components/book/EndExperience";

interface BookExperienceProps {
  manifest: BookManifest;
}

export function BookExperience({ manifest }: BookExperienceProps) {
  const { user, isRestoring } = useAuth();
  const [phase, setPhase] = useState<BookPhase>("intro");
  const [resumePage, setResumePage] = useState(1);
  const [readerKey, setReaderKey] = useState(0);
  const [openedTracked, setOpenedTracked] = useState(false);

  useEffect(() => {
    if (openedTracked) return;
    setOpenedTracked(true);
    void BookAnalytics.bookOpened(manifest.id);
  }, [manifest.id, openedTracked]);

  // After successful auth while on auth phase, advance
  useEffect(() => {
    if (phase !== "auth" || isRestoring || !user) return;
    advancePastAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- intentional: only react to auth success
  }, [phase, user, isRestoring]);

  function advancePastAuth() {
    const stored = loadProgress(manifest.id);
    if (stored.currentPage > 1) {
      void BookAnalytics.readerReturn(manifest.id, stored.completionPercent);
      setResumePage(stored.currentPage);
      setPhase("resume");
    } else {
      setResumePage(1);
      setPhase("reading");
    }
  }

  function handleBegin() {
    if (isRestoring) return;
    if (!user) {
      setPhase("auth");
      return;
    }
    advancePastAuth();
  }

  function handleResume() {
    void BookAnalytics.resumeReading(manifest.id, resumePage);
    setReaderKey((k) => k + 1);
    setPhase("reading");
  }

  function handleStartOver() {
    const stored = loadProgress(manifest.id);
    saveProgress(manifest.id, {
      ...stored,
      currentPage: 1,
      completionPercent: 0,
      lastReadAt: new Date().toISOString(),
    });
    setResumePage(1);
    setReaderKey((k) => k + 1);
    setPhase("reading");
  }

  function handleReachEnd() {
    const stored = loadProgress(manifest.id);
    const next = {
      ...stored,
      currentPage: manifest.pages.length,
      completionPercent: completionPercentForPage(
        manifest.pages.length,
        manifest.pages.length,
      ),
      lastReadAt: new Date().toISOString(),
    };
    saveProgress(manifest.id, next);
    void BookAnalytics.bookCompleted(manifest.id, next.readingTimeMs);
    setPhase("end");
  }

  function handleExit() {
    setPhase("intro");
  }

  if (phase === "intro") {
    return (
      <Intro
        title={manifest.title}
        subtitle={manifest.subtitle}
        onBegin={handleBegin}
      />
    );
  }

  if (phase === "auth") {
    if (isRestoring) {
      return (
        <div className="flex min-h-dvh items-center justify-center bg-[#0a0614]">
          <Loader2 className="size-7 animate-spin text-white/60" aria-hidden />
        </div>
      );
    }
    return <BookAuthGate title={manifest.title} />;
  }

  if (phase === "resume") {
    return (
      <ResumeCard
        lastPage={resumePage}
        onResume={handleResume}
        onStartOver={handleStartOver}
      />
    );
  }

  if (phase === "end") {
    return (
      <EndExperience
        onLaunchApp={() => {
          void BookAnalytics.openMomentraFromBook(manifest.id, "end");
        }}
      />
    );
  }

  return (
    <ReaderProvider
      key={readerKey}
      manifest={manifest}
      initialPage={resumePage}
    >
      <Reader onReachEnd={handleReachEnd} onExit={handleExit} />
    </ReaderProvider>
  );
}

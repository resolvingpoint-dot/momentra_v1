"use client";
import React from "react";
import { MOTION_DURATION_MS } from "@/lib/motion/tokens";

const skeletonPulseStyle: React.CSSProperties = {
  animation: `momentraSkeletonPulse ${MOTION_DURATION_MS.skeleton}ms ease-in-out infinite`,
};

const skeletonKeyframes = `
  @keyframes momentraSkeletonPulse {
    0%, 100% { opacity: 0.45; }
    50% { opacity: 0.85; }
  }
  @media (prefers-reduced-motion: reduce) {
    .momentra-skeleton-pulse { animation: none !important; opacity: 0.6 !important; }
  }
`;

type SkeletonBlockProps = {
  className?: string;
  style?: React.CSSProperties;
  children?: React.ReactNode;
};

export function SkeletonLine({ className = "", style }: SkeletonBlockProps) {
  return (
    <>
      <style>{skeletonKeyframes}</style>
      <div
        className={`momentra-skeleton-pulse rounded bg-[#2a2a2a] ${className}`}
        style={{ ...skeletonPulseStyle, ...style }}
      />
    </>
  );
}

export function SkeletonCard({ className = "", style }: SkeletonBlockProps) {
  return (
    <div
      className={`rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] ${className}`}
      style={style}
    />
  );
}

export function SkeletonAvatar({ className = "", style }: SkeletonBlockProps) {
  return (
    <div
      className={`momentra-skeleton-pulse rounded-full bg-[#2a2a2a] ${className}`}
      style={{ ...skeletonPulseStyle, ...style }}
    />
  );
}

export function SkeletonHero() {
  return (
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <SkeletonLine className="mb-2 h-6 w-48" />
        <SkeletonLine className="h-4 w-32" />
      </div>
      <div className="flex items-center gap-3">
        <SkeletonLine className="h-8 w-20 rounded-full" />
        <SkeletonLine className="h-8 w-8 rounded-full" />
      </div>
    </div>
  );
}

export function SkeletonStatGrid({ cols = 4, count = 4 }: { cols?: number; count?: number }) {
  return (
    <div className="mb-8 grid gap-4" style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}>
      {[...Array(count)].map((_, i) => (
        <SkeletonCard key={i} className="p-4">
          <SkeletonLine className="mb-2 h-3 w-20" />
          <SkeletonLine className="mb-1 h-8 w-12" />
          <SkeletonLine className="h-3 w-16" />
        </SkeletonCard>
      ))}
    </div>
  );
}

export function SkeletonActivityFeed({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {[...Array(count)].map((_, i) => (
        <SkeletonCard key={i} className="flex gap-4 p-4">
          <SkeletonAvatar className="h-10 w-10" />
          <div className="flex-1 space-y-2">
            <SkeletonLine className="h-4 w-32" />
            <SkeletonLine className="h-3 w-24" />
          </div>
        </SkeletonCard>
      ))}
    </div>
  );
}

export function SkeletonOpportunityCard() {
  return (
    <SkeletonCard className="p-5">
      <SkeletonLine className="mb-3 h-3 w-28" />
      <SkeletonLine className="mb-2 h-6 w-48" />
      <SkeletonLine className="mb-4 h-4 w-full" />
      <SkeletonLine className="h-12 w-32 rounded-2xl" />
    </SkeletonCard>
  );
}

export function SkeletonIntelligenceCard() {
  return (
    <SkeletonCard className="flex gap-4 p-5">
      <SkeletonAvatar className="h-7 w-7" />
      <div className="flex-1 space-y-2">
        <SkeletonLine className="h-3 w-28" />
        <SkeletonLine className="h-4 w-full" />
      </div>
    </SkeletonCard>
  );
}

export function SkeletonQuickCapture() {
  return (
    <div className="grid grid-cols-3 gap-2">
      {[...Array(3)].map((_, i) => (
        <SkeletonLine key={i} className="h-12 rounded-full" />
      ))}
    </div>
  );
}

export function SkeletonSignalBar() {
  return (
    <SkeletonCard className="flex gap-4 p-3">
      {[...Array(3)].map((_, i) => (
        <SkeletonLine key={i} className="h-4 flex-1 rounded-full" />
      ))}
    </SkeletonCard>
  );
}

export function SkeletonChartCard() {
  return (
    <SkeletonCard className="p-5">
      <SkeletonLine className="mb-4 h-5 w-36" />
      <SkeletonLine className="mb-2 h-32 w-full rounded-xl" />
      <div className="flex gap-4">
        <SkeletonLine className="h-3 w-16" />
        <SkeletonLine className="h-3 w-16" />
      </div>
    </SkeletonCard>
  );
}

export function SkeletonGaugesRow({ count = 4 }: { count?: number }) {
  return (
    <div className="flex justify-between gap-4">
      {[...Array(count)].map((_, i) => (
        <div key={i} className="flex flex-col items-center gap-2">
          <SkeletonCard className="h-16 w-16 rounded-full" />
          <SkeletonLine className="h-3 w-12" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonJourneyHero() {
  return (
    <SkeletonCard className="p-6">
      <SkeletonLine className="mb-3 h-10 w-24" />
      <SkeletonLine className="mb-4 h-4 w-full" />
      <div className="flex gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex flex-col items-center">
            <SkeletonLine className="mb-1 h-5 w-16" />
            <SkeletonLine className="h-3 w-10" />
          </div>
        ))}
      </div>
    </SkeletonCard>
  );
}

export function SkeletonTimeline({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {[...Array(count)].map((_, i) => (
        <SkeletonCard key={i} className="flex gap-4 p-4">
          <SkeletonLine className="h-12 w-12 rounded-xl" />
          <div className="flex-1 space-y-2">
            <SkeletonLine className="h-4 w-40" />
            <SkeletonLine className="h-3 w-56" />
          </div>
        </SkeletonCard>
      ))}
    </div>
  );
}

export function SkeletonCarousel() {
  return (
    <div className="flex gap-4 overflow-hidden">
      {[...Array(3)].map((_, i) => (
        <SkeletonCard key={i} className="h-36 w-64 shrink-0 p-4">
          <SkeletonLine className="mb-2 h-4 w-32" />
          <SkeletonLine className="h-3 w-24" />
        </SkeletonCard>
      ))}
    </div>
  );
}

export function SkeletonMemorySection({ count = 2 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {[...Array(count)].map((_, i) => (
        <SkeletonCard key={i} className="p-5">
          <SkeletonLine className="mb-2 h-3 w-32" />
          <SkeletonLine className="mb-2 h-5 w-48" />
          <SkeletonLine className="h-4 w-full" />
        </SkeletonCard>
      ))}
    </div>
  );
}

export function SkeletonMemoryDetail() {
  return (
    <div className="space-y-5">
      <SkeletonCard className="p-5">
        <SkeletonLine className="mb-2 h-3 w-36" />
        <SkeletonLine className="mb-2 h-6 w-56" />
        <SkeletonLine className="mb-1 h-4 w-full" />
        <SkeletonLine className="h-4 w-3/4" />
      </SkeletonCard>
      <SkeletonCard className="p-5">
        <SkeletonLine className="mb-2 h-3 w-28" />
        <SkeletonLine className="mb-2 h-5 w-full" />
        <SkeletonLine className="h-4 w-full" />
      </SkeletonCard>
    </div>
  );
}

export function SkeletonQuickAddSheet() {
  return (
    <div className="animate-pulse space-y-5">
      <SkeletonLine className="h-6 w-48" />
      <div className="flex gap-4">
        <SkeletonLine className="h-8 w-20 rounded-lg" />
        <SkeletonLine className="h-8 w-24 rounded-lg" />
        <SkeletonLine className="h-8 w-16 rounded-lg" />
      </div>
      <div className="space-y-2">
        <SkeletonLine className="h-3 w-24" />
        <SkeletonLine className="h-12 w-full rounded-xl" />
      </div>
      <div className="space-y-2">
        <SkeletonLine className="h-3 w-32" />
        <SkeletonLine className="h-12 w-full rounded-xl" />
      </div>
      <SkeletonCard className="p-4">
        <SkeletonLine className="mb-2 h-3 w-28" />
        <SkeletonLine className="h-4 w-full" />
      </SkeletonCard>
      <SkeletonLine className="h-12 w-full rounded-2xl" />
    </div>
  );
}

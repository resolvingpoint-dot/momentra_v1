"use client";

import { MOTION_DURATION_MS } from "@/lib/motion/tokens";

const skeletonPulseStyle = {
  animation: `momentraSkeletonPulse ${MOTION_DURATION_MS.skeleton}ms ease-in-out infinite`,
} as const;

const skeletonKeyframes = `
  @keyframes momentraSkeletonPulse {
    0%, 100% { opacity: 0.45; }
    50% { opacity: 0.85; }
  }
  @media (prefers-reduced-motion: reduce) {
    .group-skeleton { animation: none !important; opacity: 0.6 !important; }
  }
`;

function SkeletonStyle() {
  return <style>{skeletonKeyframes}</style>;
}

type SkeletonProps = {
  className?: string;
};

export function GroupSkeletonLine({ className = "" }: SkeletonProps) {
  return (
    <>
      <SkeletonStyle />
      <div
        className={`group-skeleton group-skeleton-line rounded ${className}`}
        style={{
          background: "linear-gradient(90deg, #1C1B1B 25%, #2A2A2A 50%, #1C1B1B 75%)",
          backgroundSize: "200% 100%",
          ...skeletonPulseStyle,
        }}
      />
    </>
  );
}

export function GroupSkeletonCard({ className = "" }: SkeletonProps) {
  return (
    <>
      <SkeletonStyle />
      <div
        className={`group-skeleton group-skeleton-card rounded-2xl ${className}`}
        style={{
          background: "linear-gradient(90deg, #1C1B1B 25%, #2A2A2A 50%, #1C1B1B 75%)",
          backgroundSize: "200% 100%",
          ...skeletonPulseStyle,
        }}
      />
    </>
  );
}

export function GroupSkeletonAvatar({ className = "" }: SkeletonProps) {
  return (
    <>
      <SkeletonStyle />
      <div
        className={`group-skeleton group-skeleton-avatar rounded-full ${className}`}
        style={{
          background: "linear-gradient(90deg, #1C1B1B 25%, #2A2A2A 50%, #1C1B1B 75%)",
          backgroundSize: "200% 100%",
          ...skeletonPulseStyle,
        }}
      />
    </>
  );
}

export function GroupSkeletonStatGrid() {
  return (
    <div className="grid grid-cols-2 gap-3">
      <div className="p-3 rounded-xl" style={{ background: "rgba(255,255,255,0.05)" }}>
        <GroupSkeletonLine className="h-4 w-12 mb-2" />
        <GroupSkeletonLine className="h-6 w-20" />
      </div>
      <div className="p-3 rounded-xl" style={{ background: "rgba(255,255,255,0.05)" }}>
        <GroupSkeletonLine className="h-4 w-12 mb-2" />
        <GroupSkeletonLine className="h-6 w-20" />
      </div>
    </div>
  );
}

export function GroupSkeletonHero() {
  return (
    <div className="relative h-48 rounded-2xl overflow-hidden">
      <div className="absolute inset-0" style={{ background: "linear-gradient(135deg, #1C1B1B 0%, #2A2A2A 100%)" }} />
      <div className="absolute bottom-4 left-4 right-4">
        <GroupSkeletonLine className="h-6 w-3/4 mb-2" />
        <GroupSkeletonLine className="h-4 w-1/2" />
      </div>
    </div>
  );
}

export function GroupSkeletonForm() {
  return (
    <div className="space-y-4">
      <div>
        <GroupSkeletonLine className="h-3 w-24 mb-2" />
        <GroupSkeletonLine className="h-10 w-full" />
      </div>
      <div>
        <GroupSkeletonLine className="h-3 w-24 mb-2" />
        <GroupSkeletonLine className="h-10 w-full" />
      </div>
      <div>
        <GroupSkeletonLine className="h-3 w-24 mb-2" />
        <GroupSkeletonLine className="h-10 w-full" />
      </div>
    </div>
  );
}

export function GroupSkeletonQuickAddHub() {
  return (
    <div className="space-y-4">
      <GroupSkeletonHero />
      <div className="grid grid-cols-3 gap-3">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="p-3 rounded-xl" style={{ background: "rgba(255,255,255,0.05)" }}>
            <GroupSkeletonAvatar className="w-10 h-10 mx-auto mb-2" />
            <GroupSkeletonLine className="h-3 w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

export function GroupSkeletonMomentCard() {
  return (
    <div className="rounded-2xl overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
      <div className="h-40" style={{ background: "linear-gradient(135deg, #1C1B1B 0%, #2A2A2A 100%)" }} />
      <div className="p-4">
        <GroupSkeletonLine className="h-5 w-3/4 mb-2" />
        <GroupSkeletonLine className="h-4 w-full mb-3" />
        <div className="flex items-center gap-2">
          <GroupSkeletonAvatar className="w-8 h-8" />
          <GroupSkeletonAvatar className="w-8 h-8 -ml-2" />
          <GroupSkeletonAvatar className="w-8 h-8 -ml-2" />
        </div>
      </div>
    </div>
  );
}

export function GroupSkeletonPulseDashboard() {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <GroupSkeletonAvatar className="w-20 h-20" />
        <div className="flex-1">
          <GroupSkeletonLine className="h-6 w-32 mb-2" />
          <GroupSkeletonLine className="h-4 w-48" />
        </div>
      </div>
      <GroupSkeletonStatGrid />
      <div className="grid grid-cols-2 gap-3">
        <GroupSkeletonCard className="h-24" />
        <GroupSkeletonCard className="h-24" />
      </div>
    </div>
  );
}

export function GroupSkeletonSetupStep() {
  return (
    <div className="space-y-6">
      <GroupSkeletonHero />
      <div className="space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="p-4 rounded-xl" style={{ background: "rgba(255,255,255,0.05)" }}>
            <GroupSkeletonLine className="h-4 w-3/4 mb-2" />
            <GroupSkeletonLine className="h-3 w-1/2" />
          </div>
        ))}
      </div>
    </div>
  );
}

type GroupSkeletonBlocksProps = {
  variant: "pulse" | "moments" | "memory" | "life" | "hub";
};

export function GroupSkeletonBlocks({ variant }: GroupSkeletonBlocksProps) {
  switch (variant) {
    case "hub":
      return (
        <div className="space-y-6">
          <GroupSkeletonHero />
          <div className="space-y-3">
            <GroupSkeletonLine className="h-3 w-24" />
            <GroupSkeletonMomentCard />
            <GroupSkeletonMomentCard />
          </div>
          <div className="space-y-3">
            <GroupSkeletonLine className="h-3 w-28" />
            <GroupSkeletonMomentCard />
          </div>
        </div>
      );
    case "pulse":
      return <GroupSkeletonPulseDashboard />;
    case "moments":
      return (
        <div className="space-y-4">
          <GroupSkeletonHero />
          <GroupSkeletonStatGrid />
          <GroupSkeletonMomentCard />
        </div>
      );
    case "memory":
      return (
        <div className="space-y-4">
          <GroupSkeletonHero />
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-4 rounded-xl" style={{ background: "rgba(255,255,255,0.05)" }}>
                <GroupSkeletonLine className="h-4 w-3/4 mb-2" />
                <GroupSkeletonLine className="h-3 w-full" />
              </div>
            ))}
          </div>
        </div>
      );
    case "life":
      return (
        <div className="space-y-4">
          <GroupSkeletonHero />
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <GroupSkeletonMomentCard key={i} />
            ))}
          </div>
        </div>
      );
  }
}

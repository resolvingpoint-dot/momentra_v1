"use client";

import { SkeletonHero, SkeletonLine, SkeletonStatGrid } from "@/components/personal/shared/skeleton/SkeletonBlocks";

export function LifeOperationsPulseSkeleton() {
  return (
    <div className="relative min-h-0 flex-1 overflow-y-auto bg-[#14121b]" style={{ paddingBottom: 40 }}>
      <div className="flex min-h-0 flex-1 items-center justify-center px-6 py-8">
        <div className="w-full max-w-[1080px]">
          <SkeletonHero />
          <SkeletonStatGrid cols={4} count={4} />
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex gap-4 rounded-2xl border border-[#2a2a2a] bg-[#1e1e1e] p-4">
                <SkeletonLine className="h-10 w-10 rounded-full" />
                <div className="flex-1 space-y-2">
                  <SkeletonLine className="h-4 w-32" />
                  <SkeletonLine className="h-3 w-24" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

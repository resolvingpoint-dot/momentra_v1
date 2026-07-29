"use client";

import { SkeletonCard, SkeletonLine } from "@/components/personal/shared/skeleton/SkeletonBlocks";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

export function MasterExpenseSkeleton() {
  const tokens = useThemeTokens();

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div
        className="sticky top-0 z-10 flex items-center justify-between px-5 py-4"
        style={{ background: tokens.colors.background }}
      >
        <SkeletonLine className="h-8 w-40" />
        <SkeletonLine className="h-4 w-16" />
      </div>
      <div className="flex-1 space-y-6 overflow-y-auto px-5 pb-32">
        <SkeletonCard className="p-4" style={personalGlassCardStyle(tokens)}>
          <SkeletonLine className="mb-2 h-4 w-48" />
          <SkeletonLine className="h-3 w-full" />
        </SkeletonCard>
        <div className="grid grid-cols-2 gap-3">
          {[0, 1, 2, 3].map((i) => (
            <SkeletonCard key={i} className="p-3" style={personalGlassCardStyle(tokens)}>
              <SkeletonLine className="mb-2 h-2 w-16" />
              <SkeletonLine className="h-4 w-24" />
            </SkeletonCard>
          ))}
        </div>
        <SkeletonCard className="p-4" style={personalGlassCardStyle(tokens)}>
          <SkeletonLine className="mb-3 h-3 w-40" />
          <div className="grid grid-cols-5 gap-2">
            {[0, 1, 2, 3, 4].map((i) => (
              <SkeletonLine key={i} className="h-14 rounded-xl" />
            ))}
          </div>
        </SkeletonCard>
        <div className="flex gap-3">
          <SkeletonLine className="h-12 flex-1 rounded-2xl" />
          <SkeletonLine className="h-12 flex-[2] rounded-2xl" />
        </div>
      </div>
    </div>
  );
}

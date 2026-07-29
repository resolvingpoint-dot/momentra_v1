"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { scrollShellStyle } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";

export function PersonalLifeSkeleton({ bottomPadding = 0 }: { bottomPadding?: number }) {
  const tokens = useThemeTokens();
  return (
    <div
      className="flex min-h-0 flex-1 flex-col gap-4 px-5 py-6"
      style={{ ...scrollShellStyle(tokens, bottomPadding), color: tokens.colors.textPrimary }}
    >
      <div className="h-8 w-24 animate-pulse rounded-lg bg-white/10" />
      <div className="h-48 animate-pulse rounded-xl bg-white/5" />
      <div className="h-32 animate-pulse rounded-xl bg-white/5" />
      <div className="h-40 animate-pulse rounded-xl bg-white/5" />
      <p className="text-center text-sm opacity-60">{personalLifeCopy.loading}</p>
    </div>
  );
}

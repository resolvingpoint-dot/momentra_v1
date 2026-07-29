"use client";

import Image from "next/image";
import { Network } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type CircleEmptyProps = {
  onCreateGroupMoment: () => void;
  onCreateBusinessWorkspace: () => void;
};

const PREVIEW_CHIPS = [
  "Groups",
  "Business",
  "Recent",
  "Active",
  "Shared Moments",
] as const;

export function CircleEmpty({
  onCreateGroupMoment,
  onCreateBusinessWorkspace,
}: CircleEmptyProps) {
  const tokens = useThemeTokens();
  const accent = tokens.colors.brandPrimary;
  const accentEnd = tokens.colors.brandSecondary;

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col items-center px-5 pb-10 pt-2">
      <section className="relative mb-8 min-h-[320px] w-full overflow-hidden rounded-3xl sm:min-h-[40vh]">
        <Image
          src="/circle/hero.png"
          alt="Circle network"
          fill
          priority
          className="object-cover"
          sizes="(max-width: 672px) 100vw, 672px"
        />
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(to top, ${tokens.colors.background} 0%, transparent 45%, transparent 100%)`,
          }}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <div
            className="rounded-full px-6 py-2 text-sm font-bold backdrop-blur-md"
            style={{
              color: accent,
              background: `${tokens.colors.glassBackground}`,
              border: `1px solid ${accent}4D`,
              boxShadow: `0 0 20px ${tokens.shadows.glowColor}`,
            }}
          >
            0 Connections
          </div>
        </div>
      </section>

      <section className="mb-8 max-w-xl text-center">
        <h2
          className="mb-3 text-2xl font-semibold tracking-tight sm:text-3xl"
          style={{ color: tokens.colors.textPrimary }}
        >
          Your Circle is waiting to grow
        </h2>
        <p
          className="px-2 text-base leading-relaxed"
          style={{ color: tokens.colors.textSecondary }}
        >
          Every participant you add to a Group or Business moment becomes part of your
          Circle. Momentra automatically builds your people network as your shared
          moments grow.
        </p>
      </section>

      <section className="mb-8 flex max-w-md flex-wrap justify-center gap-3">
        {PREVIEW_CHIPS.map((chip) => (
          <div
            key={chip}
            className="rounded-full px-4 py-2 text-xs font-semibold"
            style={{
              color: accent,
              background: `${accent}0D`,
              border: `1px solid ${accent}33`,
            }}
          >
            {chip}
          </div>
        ))}
      </section>

      <section className="mb-8 flex w-full max-w-md flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onCreateGroupMoment}
          className="h-14 flex-1 rounded-2xl text-sm font-bold transition-transform active:scale-95"
          style={{
            background: `linear-gradient(135deg, ${accent} 0%, ${accentEnd} 100%)`,
            color: tokens.colors.brandOnPrimary,
            boxShadow: `0 8px 24px ${tokens.shadows.fabColor}`,
          }}
        >
          Create Group Moment
        </button>
        <button
          type="button"
          onClick={onCreateBusinessWorkspace}
          className="h-14 flex-1 rounded-2xl border text-sm font-semibold transition-transform active:scale-95"
          style={{
            borderColor: tokens.colors.border,
            color: tokens.colors.textPrimary,
            background: tokens.colors.glassBackground,
          }}
        >
          Create Business Workspace
        </button>
      </section>

      <section className="w-full max-w-md">
        <div
          className="flex items-center gap-4 rounded-2xl p-5"
          style={{
            background: tokens.colors.glassBackground,
            border: `1px solid ${accent}1A`,
            backdropFilter: "blur(20px)",
          }}
        >
          <div
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl"
            style={{
              background: `${accent}1A`,
              border: `1px solid ${accent}33`,
            }}
          >
            <Network className="h-7 w-7" style={{ color: accent }} />
          </div>
          <p
            className="text-sm leading-snug"
            style={{ color: tokens.colors.textSecondary }}
          >
            Circle grows automatically as you create shared moments.
          </p>
        </div>
      </section>
    </div>
  );
}

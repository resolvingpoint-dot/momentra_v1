"use client";

import Image from "next/image";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalGlowWrapperStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifeOpsIdentitySnapshot } from "@/lib/api/personal";

type Props = { snapshot: PersonalLifeOpsIdentitySnapshot };

export function LifestyleIdentitySnapshot({ snapshot }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={personalGlowWrapperStyle(tokens)}>
      <div className="relative overflow-hidden" style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
        <LifestyleSectionBadge index={1} label="Identity Snapshot" accent explainerId="MEMORY-001" />
        <h1 className="mb-1 text-[28px] font-bold leading-tight" style={{ color: colors.brandPrimary }}>
          {snapshot.title}
        </h1>
        <div className="mb-3 flex items-end gap-2">
          <span className="text-3xl font-bold" style={{ color: colors.brandPrimary }}>
            {snapshot.confidence_percent}%
          </span>
          <span className="mb-1 text-sm opacity-60">Confidence</span>
        </div>
        {snapshot.trend_label ? (
          <div className="mb-3 text-[10px] font-bold uppercase tracking-wider opacity-60">{snapshot.trend_label}</div>
        ) : null}
        <p className="max-w-[85%] text-sm leading-relaxed opacity-70">{snapshot.body}</p>
        {snapshot.image_url ? (
          <div className="pointer-events-none absolute -right-4 -top-4 size-48 opacity-40">
            <Image src={snapshot.image_url} alt="" fill className="rounded-full object-cover mix-blend-screen" unoptimized />
          </div>
        ) : null}
      </div>
    </section>
  );
}

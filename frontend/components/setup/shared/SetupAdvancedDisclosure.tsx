"use client";

import type { ReactNode } from "react";
import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type Props = {
  title: string;
  helper?: string;
  defaultOpen?: boolean;
  children: ReactNode;
};

export function SetupAdvancedDisclosure({
  title,
  helper,
  defaultOpen = false,
  children,
}: Props) {
  const { colors } = useThemeTokens();
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div
      className="rounded-2xl border"
      style={{ borderColor: `color-mix(in srgb, ${colors.border} 35%, transparent)` }}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left"
      >
        <div>
          <p className="text-sm font-semibold">{title}</p>
          {helper ? (
            <p className="mt-0.5 text-xs opacity-60" style={{ color: colors.textSecondary }}>
              {helper}
            </p>
          ) : null}
        </div>
        <ChevronDown
          className={`size-4 shrink-0 opacity-60 transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>
      {open ? <div className="space-y-4 border-t px-4 py-4"
        style={{ borderColor: `color-mix(in srgb, ${colors.border} 35%, transparent)` }}
      >{children}</div> : null}
    </div>
  );
}

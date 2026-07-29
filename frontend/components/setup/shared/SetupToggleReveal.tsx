"use client";

import type { ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

type Props = {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
  children?: ReactNode;
  disabled?: boolean;
};

export function SetupToggleReveal({ label, checked, onChange, children, disabled }: Props) {
  const { colors } = useThemeTokens();
  return (
    <div className="space-y-3">
      <label className="flex items-center justify-between gap-3 text-sm font-medium">
        <span>{label}</span>
        <button
          type="button"
          role="switch"
          aria-checked={checked}
          disabled={disabled}
          onClick={() => onChange(!checked)}
          className="relative h-7 w-12 shrink-0 rounded-full transition-colors disabled:opacity-50"
          style={{
            background: checked
              ? colors.primary
              : `color-mix(in srgb, ${colors.border} 55%, transparent)`,
          }}
        >
          <span
            className="absolute top-0.5 size-6 rounded-full bg-white shadow transition-transform"
            style={{ left: checked ? "1.35rem" : "0.15rem" }}
          />
        </button>
      </label>
      {checked && children ? <div className="space-y-3 pl-0 sm:pl-1">{children}</div> : null}
    </div>
  );
}

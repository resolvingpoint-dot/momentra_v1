"use client";

import type { ReactNode } from "react";
import { CreditCard, Heart, Shield } from "lucide-react";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalQuickAddFieldOption } from "@/lib/api/client";
import type { ContextThemeTokens } from "@/lib/contextTokens";

export function MasterExpenseFieldLabel({
  label,
  labelColor,
}: {
  label: string;
  labelColor: string;
}) {
  return (
    <span
      className="mb-1.5 block text-[11px] font-bold uppercase tracking-wide"
      style={{ ...personalTypography.labelSm, color: labelColor }}
    >
      {label}
    </span>
  );
}

/** Compact surface without heavy nested card chrome. */
export function MasterExpenseFieldSurface({
  label,
  children,
  className,
  labelColor,
  surfaceStyle,
}: {
  label: string;
  children: ReactNode;
  className?: string;
  labelColor: string;
  surfaceStyle?: React.CSSProperties;
}) {
  return (
    <label className={className ?? "block"}>
      <MasterExpenseFieldLabel label={label} labelColor={labelColor} />
      <div
        className="rounded-xl px-3.5 py-3"
        style={surfaceStyle ?? { background: "rgba(255,255,255,0.04)" }}
      >
        {children}
      </div>
    </label>
  );
}

/** @deprecated Prefer MasterExpenseFieldSurface — kept for any residual imports. */
export function MasterExpenseFieldCard({
  label,
  children,
  className,
  surfaceStyle,
  labelColor,
}: {
  label: string;
  children: ReactNode;
  className?: string;
  surfaceStyle: React.CSSProperties;
  labelColor: string;
}) {
  return (
    <MasterExpenseFieldSurface
      label={label}
      className={className}
      labelColor={labelColor}
      surfaceStyle={surfaceStyle}
    >
      {children}
    </MasterExpenseFieldSurface>
  );
}

export function SegmentedScaleControl({
  options,
  value,
  onChange,
  colors,
}: {
  options: PersonalQuickAddFieldOption[];
  value: string;
  onChange: (value: string) => void;
  colors: ContextThemeTokens["colors"];
}) {
  return (
    <div
      className="grid gap-1 rounded-lg p-1"
      style={{
        gridTemplateColumns: `repeat(${Math.max(options.length, 1)}, minmax(0, 1fr))`,
        background: "rgba(0,0,0,0.35)",
      }}
      role="radiogroup"
    >
      {options.map((opt) => {
        const selected = value === opt.value;
        return (
          <button
            key={opt.value}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onChange(opt.value)}
            className="pressable rounded-md py-1.5 text-xs font-medium transition-all active:scale-95"
            style={{
              background: selected ? colors.brandPrimary : "transparent",
              color: selected ? colors.onPrimary : colors.textSecondary,
              boxShadow: selected ? `0 2px 8px ${colors.brandPrimary}40` : undefined,
            }}
          >
            {opt.label}
          </button>
        );
      })}
    </div>
  );
}

const IMPACT_ICONS = {
  "Life Operations": CreditCard,
  Lifestyle: Shield,
  Relationships: Heart,
} as const;

export function MasterExpenseImpactTile({
  title,
  subtitle,
  active,
  surfaceStyle,
  colors,
}: {
  title: keyof typeof IMPACT_ICONS;
  subtitle: string;
  active: boolean;
  surfaceStyle: React.CSSProperties;
  colors: ContextThemeTokens["colors"];
}) {
  const Icon = IMPACT_ICONS[title];
  return (
    <div
      className="rounded-xl p-2.5 text-center"
      style={{ ...surfaceStyle, opacity: active ? 1 : 0.55 }}
    >
      <div
        className="mx-auto mb-1.5 flex size-8 items-center justify-center rounded-lg"
        style={{ background: `${colors.brandPrimary}18` }}
      >
        <Icon size={16} style={{ color: colors.brandPrimary }} aria-hidden />
      </div>
      <h4 className="text-[10px] font-bold">{title}</h4>
      <p className="mt-0.5 text-[9px] leading-tight" style={{ color: colors.textSecondary }}>
        {subtitle}
      </p>
    </div>
  );
}

export function MasterExpenseChip({
  label,
  selected,
  onClick,
  colors,
}: {
  label: string;
  selected: boolean;
  onClick: () => void;
  colors: ContextThemeTokens["colors"];
}) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      className="pressable min-h-11 rounded-xl px-3.5 py-2.5 text-xs font-medium transition-transform active:scale-95"
      style={{
        border: `1px solid ${selected ? colors.brandPrimary : colors.border}`,
        background: selected
          ? "linear-gradient(135deg, rgba(108, 78, 242, 0.35), rgba(108, 78, 242, 0.15))"
          : "rgba(255,255,255,0.03)",
        color: selected ? colors.brandPrimary : colors.textSecondary,
      }}
    >
      {label}
    </button>
  );
}

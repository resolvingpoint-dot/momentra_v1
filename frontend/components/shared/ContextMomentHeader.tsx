"use client";

import { useState } from "react";
import { ChevronDown, Settings, Trash2, UserPlus } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

export type ContextMomentSwitcherOption = {
  typeCode: string;
  label: string;
  momentId: string | null;
};

export type ContextAccentVariant = "personal" | "business" | "group";

type ContextMomentHeaderProps = {
  contextLabel: string;
  tabLabel: string;
  options: ContextMomentSwitcherOption[];
  selectedTypeCode: string;
  onSelect: (option: ContextMomentSwitcherOption) => void;
  onManageClick?: () => void;
  /** Group / Business only — Personal omits this. Acts on the selected moment. */
  onInviteMoment?: (option: ContextMomentSwitcherOption) => void;
  /** Acts on the selected moment. */
  onDeleteMoment?: (option: ContextMomentSwitcherOption) => void;
  accentVariant?: ContextAccentVariant;
};

export function ContextMomentHeader({
  contextLabel,
  tabLabel,
  options,
  selectedTypeCode,
  onSelect,
  onManageClick,
  onInviteMoment,
  onDeleteMoment,
  accentVariant = "business",
}: ContextMomentHeaderProps) {
  const [expanded, setExpanded] = useState(false);
  const tokens = useThemeTokens();
  const { colors } = tokens;

  if (options.length === 0) return null;

  const selected = options.find((o) => o.typeCode === selectedTypeCode) ?? options[0];
  const canExpand = options.length > 1;
  const isPersonal = accentVariant === "personal";
  const showInvite = accentVariant !== "personal" && Boolean(onInviteMoment);
  const hasMoment = Boolean(selected.momentId);
  const accentColor = isPersonal ? colors.brandTertiary : colors.brandPrimary;
  const avatarGradient = isPersonal
    ? `linear-gradient(135deg, ${colors.primaryContainer}, ${colors.brandTertiary})`
    : accentVariant === "group"
      ? `linear-gradient(135deg, ${colors.primaryContainer}, ${colors.brandPrimary})`
      : `linear-gradient(135deg, ${colors.brandPrimary}, ${colors.brandSecondary})`;

  const iconBtnClass =
    "flex size-10 shrink-0 items-center justify-center rounded-xl transition-colors disabled:opacity-40";

  return (
    <header
      className="sticky top-0 z-40 shrink-0 border-b backdrop-blur-xl"
      style={{
        background: `color-mix(in srgb, ${colors.surface} 85%, transparent)`,
        borderColor: `color-mix(in srgb, ${colors.border} 25%, transparent)`,
      }}
      data-momentra-context={contextLabel.toLowerCase()}
    >
      <div className="flex h-16 items-center justify-between gap-3 px-5">
        <div className="flex min-w-0 items-center gap-3">
          <div
            className="size-8 shrink-0 overflow-hidden rounded-full border"
            style={{ borderColor: `color-mix(in srgb, ${colors.brandPrimary} 30%, transparent)` }}
          >
            <div className="size-full" style={{ background: avatarGradient }} />
          </div>
          <div className="min-w-0">
            <p
              className="text-[10px] font-bold uppercase tracking-widest opacity-60"
              style={{ color: colors.textSecondary }}
            >
              {contextLabel} / {tabLabel}
            </p>
            <button
              type="button"
              disabled={!canExpand}
              onClick={() => canExpand && setExpanded((v) => !v)}
              className="flex max-w-full items-center gap-1 text-left disabled:cursor-default"
            >
              <span
                className="truncate text-lg font-bold leading-tight"
                style={{ color: colors.textPrimary }}
              >
                {selected.label}
              </span>
              {canExpand ? (
                <ChevronDown
                  className={`size-4 shrink-0 transition-transform ${expanded ? "rotate-180" : ""}`}
                  style={{ color: accentColor }}
                />
              ) : null}
            </button>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-1.5">
          {showInvite ? (
            <button
              type="button"
              aria-label="Invite"
              disabled={!hasMoment}
              className={iconBtnClass}
              style={{ background: colors.surfaceContainer }}
              onClick={() => {
                if (!hasMoment || !onInviteMoment) return;
                onInviteMoment(selected);
              }}
            >
              <UserPlus className="size-5" style={{ color: accentColor }} />
            </button>
          ) : null}
          {onDeleteMoment ? (
            <button
              type="button"
              aria-label="Delete"
              disabled={!hasMoment}
              className={iconBtnClass}
              style={{ background: colors.surfaceContainer }}
              onClick={() => {
                if (!hasMoment || !onDeleteMoment) return;
                onDeleteMoment(selected);
              }}
            >
              <Trash2
                className="size-5"
                style={{ color: hasMoment ? colors.error : colors.textSubtle }}
              />
            </button>
          ) : null}
          <button
            type="button"
            aria-label="Settings"
            disabled={!onManageClick}
            onClick={onManageClick}
            className={iconBtnClass}
            style={{ background: colors.surfaceContainer }}
          >
            <Settings className="size-5" style={{ color: accentColor }} />
          </button>
        </div>
      </div>

      {expanded && canExpand ? (
        <div
          className="flex gap-2 overflow-x-auto px-5 pb-3"
          style={{ scrollbarWidth: "none" }}
        >
          {options.map((option) => {
            const isSelected = option.typeCode === selectedTypeCode;
            return (
              <button
                key={`${option.typeCode}:${option.momentId ?? ""}`}
                type="button"
                onClick={() => {
                  onSelect(option);
                  setExpanded(false);
                }}
                className={`flex shrink-0 items-stretch overflow-hidden rounded-full border text-sm font-medium transition-colors ${isPersonal ? "" : "px-4 py-2"}`}
                style={{
                  color: isSelected ? accentColor : colors.textSecondary,
                  background: isSelected
                    ? `color-mix(in srgb, ${accentColor} 12%, transparent)`
                    : `color-mix(in srgb, ${colors.surfaceContainer} 60%, transparent)`,
                  borderColor: isSelected
                    ? `color-mix(in srgb, ${accentColor} 35%, transparent)`
                    : `color-mix(in srgb, ${colors.border} 20%, transparent)`,
                }}
              >
                {isPersonal && isSelected ? (
                  <span className="w-1 shrink-0" style={{ background: accentColor }} />
                ) : null}
                <span className={isPersonal ? "px-4 py-2" : undefined}>{option.label}</span>
              </button>
            );
          })}
        </div>
      ) : null}
    </header>
  );
}

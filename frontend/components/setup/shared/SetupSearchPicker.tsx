"use client";

import { useMemo, useState } from "react";
import { ChevronRight, Search, X } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { SetupChoice } from "@/components/setup/shared/setupControlTypes";
import { SetupField } from "@/components/setup/shared/SetupField";

type Props = {
  label: string;
  helper?: string;
  optionalLabel?: string;
  error?: string | null;
  value: string;
  options: SetupChoice[];
  onChange: (value: string) => void;
  suggestedValue?: string | null;
  recentValues?: string[];
  disabled?: boolean;
  placeholder?: string;
  /** When true (default), appends option value to the selected label if missing (currency codes). Member pickers pass false. */
  appendValueToLabel?: boolean;
  /** When false, hides the raw option value in the open list (member UUIDs). Default true. */
  showOptionValue?: boolean;
};

export function SetupSearchPicker({
  label,
  helper,
  optionalLabel,
  error,
  value,
  options,
  onChange,
  suggestedValue,
  recentValues = [],
  disabled,
  placeholder = "Search…",
  appendValueToLabel = true,
  showOptionValue = true,
}: Props) {
  const { colors } = useThemeTokens();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  const selected = options.find((o) => o.value === value);
  const display = selected
    ? appendValueToLabel && !selected.label.includes(selected.value)
      ? `${selected.label} — ${selected.value}`
      : selected.label
    : value || "Select…";

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return options;
    return options.filter(
      (o) =>
        o.label.toLowerCase().includes(q) ||
        o.value.toLowerCase().includes(q) ||
        (o.description ?? "").toLowerCase().includes(q),
    );
  }, [options, query]);

  const recent = recentValues
    .map((v) => options.find((o) => o.value === v))
    .filter(Boolean) as SetupChoice[];
  const suggested = suggestedValue
    ? options.find((o) => o.value === suggestedValue)
    : undefined;

  function pick(next: string) {
    onChange(next);
    setOpen(false);
    setQuery("");
  }

  return (
    <SetupField label={label} helper={helper} optionalLabel={optionalLabel} error={error}>
      <button
        type="button"
        disabled={disabled}
        onClick={() => setOpen(true)}
        className="flex w-full items-center justify-between gap-2 rounded-xl border px-3 py-2.5 text-left text-sm disabled:opacity-50"
        style={{
          borderColor: error
            ? colors.error
            : `color-mix(in srgb, ${colors.border} 40%, transparent)`,
          background: colors.background,
        }}
      >
        <span className="truncate font-medium">{display}</span>
        <ChevronRight className="size-4 shrink-0 opacity-50" />
      </button>

      {open ? (
        <div className="fixed inset-0 z-[60] flex items-end justify-center sm:items-center">
          <button
            type="button"
            className="absolute inset-0 bg-black/40"
            aria-label="Close picker"
            onClick={() => setOpen(false)}
          />
          <div
            className="relative z-10 flex max-h-[80vh] w-full max-w-md flex-col rounded-t-2xl sm:rounded-2xl"
            style={{ background: colors.background, color: colors.textPrimary }}
            role="dialog"
            aria-label={label}
          >
            <div className="flex items-center justify-between border-b px-4 py-3"
              style={{ borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)` }}
            >
              <p className="text-sm font-semibold">{label}</p>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-full p-2"
                style={{ background: colors.surfaceContainer }}
                aria-label="Close"
              >
                <X className="size-4" />
              </button>
            </div>
            <div className="px-4 py-3">
              <div
                className="flex items-center gap-2 rounded-xl border px-3 py-2"
                style={{ borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)` }}
              >
                <Search className="size-4 opacity-50" />
                <input
                  autoFocus
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={placeholder}
                  className="w-full bg-transparent text-sm outline-none"
                />
              </div>
            </div>
            <div className="flex-1 overflow-y-auto px-2 pb-4">
              {suggested && !query ? (
                <div className="mb-2 px-2">
                  <p className="mb-1 text-[10px] font-bold uppercase tracking-wide opacity-50">
                    Suggested
                  </p>
                  <button
                    type="button"
                    onClick={() => pick(suggested.value)}
                    className="w-full rounded-xl px-3 py-2.5 text-left text-sm font-medium"
                    style={{ background: colors.surfaceContainer }}
                  >
                    {suggested.label}
                  </button>
                </div>
              ) : null}
              {recent.length > 0 && !query ? (
                <div className="mb-2 px-2">
                  <p className="mb-1 text-[10px] font-bold uppercase tracking-wide opacity-50">
                    Recent
                  </p>
                  {recent.map((opt) => (
                    <button
                      key={`recent-${opt.value}`}
                      type="button"
                      onClick={() => pick(opt.value)}
                      className="w-full rounded-xl px-3 py-2.5 text-left text-sm"
                    >
                      {opt.label}
                    </button>
                  ))}
                </div>
              ) : null}
              <p className="mb-1 px-2 text-[10px] font-bold uppercase tracking-wide opacity-50">
                All
              </p>
              {filtered.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => pick(opt.value)}
                  className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm"
                  style={{
                    background:
                      opt.value === value
                        ? `color-mix(in srgb, ${colors.primary} 14%, transparent)`
                        : undefined,
                  }}
                >
                  <span>
                    <span className="font-medium">{opt.label}</span>
                    {opt.description ? (
                      <span className="mt-0.5 block text-xs opacity-60">{opt.description}</span>
                    ) : null}
                  </span>
                  {showOptionValue ? (
                    <span className="text-xs opacity-50">{opt.value}</span>
                  ) : null}
                </button>
              ))}
              {filtered.length === 0 ? (
                <p className="px-3 py-4 text-sm opacity-60">No matches</p>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}
    </SetupField>
  );
}

"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { SetupMoneyField } from "@/components/business/setup/shared/SetupMoneyField";
import { findCurrency, formatMinor } from "@/lib/reference_data/money";
import type { CurrencyReference } from "@/lib/reference_data/types";

export type BudgetAllocationDraft = {
  allocation_id: string;
  category_code: string;
  label: string;
  amount_minor: number;
  percentage?: number | null;
  owner_id?: string | null;
  notes?: string | null;
};

type Props = {
  allocations: BudgetAllocationDraft[];
  allocationMode: "FIXED_AMOUNT" | "PERCENTAGE";
  monthlyBudgetMinor: number;
  allowOverallocation: boolean;
  currencies: CurrencyReference[];
  currencyCode: string;
  locale?: string;
  onChange: (next: BudgetAllocationDraft[]) => void;
};

function fieldStyle(colors: { border: string; surfaceContainer: string }) {
  return {
    borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
    background: colors.surfaceContainer,
  } as const;
}

function newAllocationId() {
  return `a-${Math.random().toString(36).slice(2, 10)}`;
}

export function BudgetAllocationEditor({
  allocations,
  allocationMode,
  monthlyBudgetMinor,
  allowOverallocation,
  currencies,
  currencyCode,
  locale = "en-IN",
  onChange,
}: Props) {
  const { colors } = useThemeTokens();
  const style = fieldStyle(colors);

  const allocatedTotal = allocations.reduce((sum, a) => sum + (a.amount_minor || 0), 0);
  const percentTotal = allocations.reduce((sum, a) => sum + (Number(a.percentage) || 0), 0);
  const overBudget = !allowOverallocation && allocatedTotal > monthlyBudgetMinor;
  const percentInvalid = allocationMode === "PERCENTAGE" && allocations.length > 0 && percentTotal !== 100;
  const currency =
    findCurrency(currencies, currencyCode) ??
    ({ code: currencyCode, label: currencyCode, symbol: currencyCode, minor_unit: 2 } as CurrencyReference);
  const formatAmt = (minor: number) => formatMinor(minor, currency, locale);

  const addRow = () => {
    onChange([
      ...allocations,
      {
        allocation_id: newAllocationId(),
        category_code: "custom",
        label: "",
        amount_minor: 0,
        percentage: allocationMode === "PERCENTAGE" ? 0 : null,
        owner_id: null,
        notes: null,
      },
    ]);
  };

  const patch = (id: string, patch: Partial<BudgetAllocationDraft>) => {
    onChange(
      allocations.map((a) => {
        if (a.allocation_id !== id) return a;
        const next = { ...a, ...patch };
        if (patch.label != null && !patch.category_code) {
          const code = patch.label
            .trim()
            .toLowerCase()
            .replace(/\s+/g, "_")
            .replace(/[^a-z0-9_]/g, "");
          if (code) next.category_code = code;
        }
        return next;
      }),
    );
  };

  const remove = (id: string) => {
    onChange(allocations.filter((a) => a.allocation_id !== id));
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold tracking-wide opacity-70">Budget allocations</span>
        <button
          type="button"
          className="rounded-xl px-3 py-2 text-sm font-semibold text-white"
          style={{ background: colors.brandPrimary }}
          onClick={addRow}
        >
          Add allocation
        </button>
      </div>

      {allocations.length === 0 ? (
        <p className="rounded-xl px-3 py-2 text-xs opacity-60" style={{ background: colors.surfaceContainer }}>
          No allocations yet. Add categories to distribute the monthly budget.
        </p>
      ) : null}

      <div className="space-y-3">
        {allocations.map((a) => (
          <div
            key={a.allocation_id}
            className="space-y-2 rounded-2xl border p-3"
            style={{ borderColor: `color-mix(in srgb, ${colors.border} 35%, transparent)` }}
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-xs font-bold tracking-wide opacity-60">ALLOCATION</p>
              <button type="button" className="text-xs text-red-500" onClick={() => remove(a.allocation_id)}>
                Remove
              </button>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <label className="block space-y-1">
                <span className="text-xs font-semibold tracking-wide opacity-70">Label</span>
                <input
                  className="w-full rounded-xl border px-3 py-2 text-sm outline-none"
                  style={style}
                  value={a.label}
                  onChange={(e) => patch(a.allocation_id, { label: e.target.value })}
                  placeholder="e.g. Facilities"
                />
              </label>
              <label className="block space-y-1">
                <span className="text-xs font-semibold tracking-wide opacity-70">Category code</span>
                <input
                  className="w-full rounded-xl border px-3 py-2 text-sm outline-none"
                  style={style}
                  value={a.category_code}
                  onChange={(e) => patch(a.allocation_id, { category_code: e.target.value })}
                />
              </label>
            </div>

            {allocationMode === "PERCENTAGE" ? (
              <label className="block space-y-1">
                <span className="text-xs font-semibold tracking-wide opacity-70">Percentage</span>
                <input
                  className="w-full rounded-xl border px-3 py-2 text-sm outline-none"
                  style={style}
                  inputMode="numeric"
                  value={a.percentage == null ? "" : String(a.percentage)}
                  onChange={(e) => {
                    const pct = e.target.value === "" ? 0 : Number(e.target.value);
                    const amount =
                      monthlyBudgetMinor > 0 ? Math.floor((monthlyBudgetMinor * (pct || 0)) / 100) : 0;
                    patch(a.allocation_id, { percentage: pct, amount_minor: amount });
                  }}
                />
              </label>
            ) : (
              <SetupMoneyField
                label="Amount"
                amountMinor={a.amount_minor || 0}
                currencyCode={currencyCode}
                currencies={currencies}
                allowEmpty={false}
                onChange={(v) => patch(a.allocation_id, { amount_minor: v ?? 0 })}
              />
            )}

            <label className="block space-y-1">
              <span className="text-xs font-semibold tracking-wide opacity-70">Notes</span>
              <input
                className="w-full rounded-xl border px-3 py-2 text-sm outline-none"
                style={style}
                value={a.notes ?? ""}
                onChange={(e) => patch(a.allocation_id, { notes: e.target.value || null })}
              />
            </label>
          </div>
        ))}
      </div>

      <div
        className="rounded-xl px-3 py-2 text-xs space-y-1"
        style={{ background: colors.surfaceContainer }}
      >
        {allocationMode === "FIXED_AMOUNT" ? (
          <>
            <p>
              Allocated: {formatAmt(allocatedTotal)} / Budget: {formatAmt(monthlyBudgetMinor)}
              {monthlyBudgetMinor > 0
                ? ` (${Math.min(100, Math.floor((allocatedTotal * 100) / monthlyBudgetMinor))}%)`
                : ""}
            </p>
            <p>Unallocated: {formatAmt(Math.max(0, monthlyBudgetMinor - allocatedTotal))}</p>
            {overBudget ? (
              <p className="text-red-600">Total exceeds monthly budget. Enable overallocation or reduce amounts.</p>
            ) : null}
          </>
        ) : (
          <>
            <p>Percentage total: {percentTotal}% (must be 100)</p>
            <p>Resolved allocated: {formatAmt(allocatedTotal)}</p>
            {percentInvalid ? <p className="text-red-600">Percentages must total exactly 100.</p> : null}
          </>
        )}
      </div>
    </div>
  );
}

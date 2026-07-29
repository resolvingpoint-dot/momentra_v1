"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { BUSINESS_ACCENT } from "@/components/business/actioncenter/ui/BusinessActionDesignSystem";
import { getReferenceData } from "@/lib/reference_data/referenceDataStore";
import { findCurrency, parseUserInputToMinor } from "@/lib/reference_data/money";
import type { BusinessCatalogMember } from "@/repositories/BusinessActionRepository";

function useInputStyle() {
  const { colors } = useThemeTokens();
  return {
    background: colors.surfaceContainer,
    color: colors.textPrimary,
    border: `1px solid ${colors.textSecondary}22`,
  };
}

function FieldShell({
  label,
  required,
  children,
  error,
}: {
  label: string;
  required?: boolean;
  children: ReactNode;
  error?: string;
}) {
  const { colors } = useThemeTokens();
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-bold uppercase tracking-wide" style={{ color: colors.textSecondary }}>
        {label}
        {required ? " *" : ""}
      </label>
      {children}
      {error ? (
        <p className="text-xs" style={{ color: colors.error }}>
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function TextField(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  error?: string;
  placeholder?: string;
  type?: string;
}) {
  const style = useInputStyle();
  return (
    <FieldShell label={props.label} required={props.required} error={props.error}>
      <input
        type={props.type ?? "text"}
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        placeholder={props.placeholder}
        className="w-full rounded-xl px-3 py-2.5 text-sm"
        style={style}
      />
    </FieldShell>
  );
}

export function TextArea(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  error?: string;
  rows?: number;
}) {
  const style = useInputStyle();
  return (
    <FieldShell label={props.label} required={props.required} error={props.error}>
      <textarea
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        rows={props.rows ?? 3}
        className="w-full rounded-xl px-3 py-2.5 text-sm"
        style={style}
      />
    </FieldShell>
  );
}

export function MoneyInput(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  error?: string;
  currencyCode?: string;
}) {
  const style = useInputStyle();
  const { colors } = useThemeTokens();
  const symbol = props.currencyCode === "USD" ? "$" : props.currencyCode === "EUR" ? "€" : "₹";
  return (
    <FieldShell label={props.label} required={props.required} error={props.error}>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style={{ color: colors.textSecondary }}>
          {symbol}
        </span>
        <input
          type="number"
          inputMode="decimal"
          min={0}
          step="0.01"
          value={props.value}
          onChange={(e) => props.onChange(e.target.value)}
          className="w-full rounded-xl py-2.5 pl-8 pr-3 text-sm"
          style={style}
        />
      </div>
    </FieldShell>
  );
}

export function DateInput(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  error?: string;
}) {
  return (
    <TextField
      label={props.label}
      value={props.value}
      onChange={props.onChange}
      required={props.required}
      error={props.error}
      type="date"
    />
  );
}

export function MemberPicker(props: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  members: BusinessCatalogMember[];
  required?: boolean;
  error?: string;
}) {
  const style = useInputStyle();
  return (
    <FieldShell label={props.label ?? "Member"} required={props.required} error={props.error}>
      <select
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        className="w-full rounded-xl px-3 py-2.5 text-sm"
        style={style}
      >
        <option value="">Select member</option>
        {props.members.map((m) => {
          const id = m.member_id || m.id || "";
          const label = m.name || m.display_name || "Member";
          return (
            <option key={id} value={id}>
              {label}
              {m.role ? ` (${m.role})` : ""}
            </option>
          );
        })}
      </select>
    </FieldShell>
  );
}

export function MemberMultiPicker(props: {
  label?: string;
  value: string[];
  onChange: (ids: string[]) => void;
  members: BusinessCatalogMember[];
  required?: boolean;
  error?: string;
}) {
  const { colors } = useThemeTokens();
  const selected = new Set(props.value);
  function toggle(id: string) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    props.onChange(Array.from(next));
  }
  return (
    <FieldShell label={props.label ?? "Members"} required={props.required} error={props.error}>
      <div className="space-y-2">
        {props.members.map((m) => {
          const id = m.member_id || m.id || "";
          const label = m.name || m.display_name || "Member";
          const on = selected.has(id);
          return (
            <button
              key={id}
              type="button"
              onClick={() => toggle(id)}
              className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm"
              style={{
                background: on ? BUSINESS_ACCENT.teal : colors.surfaceContainer,
                color: on ? "#fff" : colors.textPrimary,
              }}
            >
              <span>{label}</span>
              <span className="text-xs font-semibold">{on ? "Selected" : "Add"}</span>
            </button>
          );
        })}
        {!props.members.length ? (
          <p className="text-xs" style={{ color: colors.textSecondary }}>
            No team members found
          </p>
        ) : null}
      </div>
    </FieldShell>
  );
}

export function CurrencyPicker(props: {
  value: string;
  onChange: (v: string) => void;
  label?: string;
}) {
  const { colors } = useThemeTokens();
  const style = useInputStyle();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  const catalog = useMemo(() => {
    const ref = getReferenceData()?.currencies ?? [];
    const active = ref.filter((c) => c.is_active !== false);
    if (active.length) {
      return active.map((c) => ({ code: c.code, label: c.label || c.code, symbol: c.symbol || c.code }));
    }
    return ["INR", "USD", "EUR", "GBP", "AED", "JPY"].map((code) => ({ code, label: code, symbol: code }));
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return catalog;
    return catalog.filter((c) => c.code.toLowerCase().includes(q) || c.label.toLowerCase().includes(q));
  }, [catalog, query]);

  return (
    <FieldShell label={props.label ?? "Currency"} required>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="w-full rounded-xl px-3 py-2.5 text-left text-sm"
        style={style}
      >
        {props.value || "Select currency"}
      </button>
      {open ? (
        <div
          className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 p-4 sm:items-center"
          role="dialog"
          aria-modal="true"
          aria-label="Select currency"
        >
          <div
            className="max-h-[70vh] w-full max-w-md overflow-hidden rounded-2xl p-4 shadow-xl"
            style={{ background: colors.surface }}
          >
            <div className="mb-3 flex items-center justify-between">
              <p className="text-sm font-semibold" style={{ color: colors.textPrimary }}>Currency</p>
              <button type="button" className="text-xs font-semibold" onClick={() => setOpen(false)}>Close</button>
            </div>
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search currencies…"
              className="mb-3 w-full rounded-xl px-3 py-2.5 text-sm"
              style={style}
            />
            <div className="max-h-[45vh] space-y-1 overflow-y-auto">
              {filtered.map((c) => (
                <button
                  key={c.code}
                  type="button"
                  className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm"
                  style={{
                    background: props.value === c.code ? BUSINESS_ACCENT.teal : colors.surfaceContainer,
                    color: props.value === c.code ? "#fff" : colors.textPrimary,
                  }}
                  onClick={() => { props.onChange(c.code); setOpen(false); setQuery(""); }}
                >
                  <span>{c.symbol} {c.code}</span>
                  <span className="text-xs" style={{ color: colors.textSecondary }}>{c.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </FieldShell>
  );
}

export function VendorPicker(props: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  error?: string;
}) {
  return (
    <TextField
      label={props.label ?? "Vendor"}
      value={props.value}
      onChange={props.onChange}
      required={props.required}
      error={props.error}
      placeholder="Vendor name"
    />
  );
}

export function ApprovalPicker(props: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  members: BusinessCatalogMember[];
  required?: boolean;
  error?: string;
}) {
  return (
    <MemberPicker
      label={props.label ?? "Approver"}
      value={props.value}
      onChange={props.onChange}
      members={props.members}
      required={props.required}
      error={props.error}
    />
  );
}

export function CategoryPicker(props: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  options: Array<{ value: string; label: string }>;
  required?: boolean;
  error?: string;
}) {
  const { colors } = useThemeTokens();
  return (
    <FieldShell label={props.label ?? "Category"} required={props.required} error={props.error}>
      <div className="flex flex-wrap gap-2">
        {props.options.map((opt) => {
          const sel = props.value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => props.onChange(opt.value)}
              className="rounded-full px-3 py-1.5 text-xs font-semibold"
              style={{
                background: sel ? BUSINESS_ACCENT.teal : colors.surfaceContainer,
                color: sel ? "#fff" : colors.textPrimary,
              }}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </FieldShell>
  );
}

export function ChipSelector(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: Array<{ value: string; label: string }>;
  required?: boolean;
  error?: string;
}) {
  const { colors } = useThemeTokens();
  return (
    <FieldShell label={props.label} required={props.required} error={props.error}>
      <div className="flex flex-wrap gap-2">
        {props.options.map((opt) => {
          const sel = props.value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => props.onChange(opt.value)}
              className="rounded-full px-3 py-1.5 text-xs font-semibold"
              style={{
                background: sel ? BUSINESS_ACCENT.teal : colors.surfaceContainer,
                color: sel ? "#fff" : colors.textPrimary,
              }}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </FieldShell>
  );
}

export function Toggle(props: { label: string; value: boolean; onChange: (v: boolean) => void }) {
  const { colors } = useThemeTokens();
  return (
    <FieldShell label={props.label}>
      <button
        type="button"
        onClick={() => props.onChange(!props.value)}
        className="rounded-full px-3 py-1.5 text-xs font-semibold"
        style={{
          background: props.value ? BUSINESS_ACCENT.teal : colors.surfaceContainer,
          color: props.value ? "#fff" : colors.textPrimary,
        }}
      >
        {props.value ? "On" : "Off"}
      </button>
    </FieldShell>
  );
}

export function PrioritySelector(props: { value: string; onChange: (v: string) => void }) {
  return (
    <ChipSelector
      label="Priority"
      value={props.value}
      onChange={props.onChange}
      options={[
        { value: "low", label: "Low" },
        { value: "medium", label: "Medium" },
        { value: "high", label: "High" },
        { value: "critical", label: "Critical" },
      ]}
    />
  );
}

export function StatusSelector(props: {
  value: string;
  onChange: (v: string) => void;
  options?: Array<{ value: string; label: string }>;
}) {
  return (
    <ChipSelector
      label="Status"
      value={props.value}
      onChange={props.onChange}
      options={
        props.options ?? [
          { value: "open", label: "Open" },
          { value: "in_progress", label: "In Progress" },
          { value: "resolved", label: "Resolved" },
          { value: "closed", label: "Closed" },
        ]
      }
    />
  );
}

export function NotesField(props: { value: string; onChange: (v: string) => void; label?: string }) {
  return <TextArea label={props.label ?? "Notes"} value={props.value} onChange={props.onChange} />;
}

export function parseAmountMinor(value: string, minorUnit = 2): number {
  const fallback = { minor_unit: minorUnit };
  return parseUserInputToMinor(value, fallback);
}

export function formatMoneyDisplay(major: string, currency = "INR"): string {
  if (!major) return "—";
  const ref = findCurrency(getReferenceData()?.currencies ?? [], currency);
  const symbol = ref?.symbol ?? (currency === "USD" ? "$" : currency === "EUR" ? "€" : "₹");
  return `${symbol}${major}`;
}

"use client";

import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { requestWithRetry } from "@/lib/api/client";
import { getReferenceData } from "@/lib/reference_data/referenceDataStore";
import { findCurrency, parseUserInputToMinor } from "@/lib/reference_data/money";

type FieldShellProps = { label: string; required?: boolean; children: ReactNode; error?: string };

function useInputStyle() {
  const { colors } = useThemeTokens();
  return {
    background: colors.surfaceContainer,
    color: colors.textPrimary,
    border: `1px solid ${colors.textSecondary}22`,
  };
}

function FieldShell({ label, required, children, error }: FieldShellProps) {
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

export function NotesField(props: { value: string; onChange: (v: string) => void; label?: string }) {
  return <TextArea label={props.label ?? "Notes"} value={props.value} onChange={props.onChange} />;
}

export function MoneyField(props: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  error?: string;
  currencyCode?: string;
}) {
  const style = useInputStyle();
  const { colors } = useThemeTokens();
  return (
    <FieldShell label={props.label} required={props.required} error={props.error}>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style={{ color: colors.textSecondary }}>
          {props.currencyCode === "USD" ? "$" : props.currencyCode === "EUR" ? "€" : "₹"}
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

export function CurrencyPicker(props: {
  value: string;
  onChange: (v: string) => void;
  options?: string[];
  /** When false, currency is locked to value (read-only). */
  locked?: boolean;
  label?: string;
}) {
  const { colors } = useThemeTokens();
  const style = useInputStyle();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  const catalog = useMemo(() => {
    if (props.options?.length) {
      return props.options.map((code) => ({ code, label: code, symbol: code }));
    }
    const ref = getReferenceData()?.currencies ?? [];
    const active = ref.filter((c) => c.is_active !== false);
    if (active.length) {
      return active.map((c) => ({
        code: c.code,
        label: c.label || c.code,
        symbol: c.symbol || c.code,
      }));
    }
    return ["INR", "USD", "EUR", "GBP", "AED", "JPY", "KWD"].map((code) => ({
      code,
      label: code,
      symbol: code,
    }));
  }, [props.options]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return catalog;
    return catalog.filter(
      (c) =>
        c.code.toLowerCase().includes(q) ||
        c.label.toLowerCase().includes(q) ||
        c.symbol.toLowerCase().includes(q),
    );
  }, [catalog, query]);

  if (props.locked) {
    return (
      <FieldShell label={props.label ?? "Currency"} required>
        <div className="rounded-xl px-3 py-2.5 text-sm" style={style}>
          {props.value || "—"}
        </div>
      </FieldShell>
    );
  }

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
              <p className="text-sm font-semibold" style={{ color: colors.textPrimary }}>
                Currency
              </p>
              <button type="button" className="text-xs font-semibold" onClick={() => setOpen(false)}>
                Close
              </button>
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
                    background:
                      props.value === c.code ? colors.primaryContainer : colors.surfaceContainer,
                    color: colors.textPrimary,
                  }}
                  onClick={() => {
                    props.onChange(c.code);
                    setOpen(false);
                    setQuery("");
                  }}
                >
                  <span>
                    {c.symbol} {c.code}
                  </span>
                  <span className="text-xs" style={{ color: colors.textSecondary }}>
                    {c.label}
                  </span>
                </button>
              ))}
              {!filtered.length ? (
                <p className="px-2 py-4 text-center text-xs" style={{ color: colors.textSecondary }}>
                  No currencies match
                </p>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}
    </FieldShell>
  );
}

export function DateField(props: {
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

export function TimeField(props: { label: string; value: string; onChange: (v: string) => void }) {
  return <TextField label={props.label} value={props.value} onChange={props.onChange} type="time" />;
}

export function PhoneField(props: { label?: string; value: string; onChange: (v: string) => void }) {
  return <TextField label={props.label ?? "Phone"} value={props.value} onChange={props.onChange} type="tel" />;
}

export function EmailField(props: { label?: string; value: string; onChange: (v: string) => void }) {
  return <TextField label={props.label ?? "Email"} value={props.value} onChange={props.onChange} type="email" />;
}

export function LocationField(props: { value: string; onChange: (v: string) => void; label?: string }) {
  return <TextField label={props.label ?? "Location"} value={props.value} onChange={props.onChange} />;
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
          const selected = props.value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => props.onChange(opt.value)}
              className="rounded-full px-3 py-1.5 text-xs font-semibold"
              style={{
                background: selected ? colors.primaryContainer : colors.surfaceContainer,
                color: selected ? colors.brandOnPrimary : colors.textPrimary,
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
          background: props.value ? colors.primaryContainer : colors.surfaceContainer,
          color: props.value ? colors.brandOnPrimary : colors.textPrimary,
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
          { value: "in_progress", label: "In progress" },
          { value: "done", label: "Done" },
        ]
      }
    />
  );
}

export function VisibilitySelector(props: { value: string; onChange: (v: string) => void }) {
  return (
    <ChipSelector
      label="Visibility"
      value={props.value}
      onChange={props.onChange}
      options={[
        { value: "everyone", label: "Everyone" },
        { value: "owners", label: "Owners only" },
      ]}
    />
  );
}

export function RatingSelector(props: { value: string; onChange: (v: string) => void }) {
  return (
    <ChipSelector
      label="Rating"
      value={props.value}
      onChange={props.onChange}
      options={["1", "2", "3", "4", "5"].map((n) => ({ value: n, label: `${n}★` }))}
    />
  );
}

export function TagPicker(props: { value: string; onChange: (v: string) => void; label?: string }) {
  return (
    <TextField
      label={props.label ?? "Tags"}
      value={props.value}
      onChange={props.onChange}
      placeholder="comma, separated, tags"
    />
  );
}

export function PhotoPlaceholder(props: { label?: string }) {
  const { colors } = useThemeTokens();
  return (
    <FieldShell label={props.label ?? "Attachment"}>
      <div
        className="flex h-24 items-center justify-center rounded-xl border border-dashed text-xs"
        style={{ borderColor: `${colors.textSecondary}40`, color: colors.textSecondary }}
      >
        Photo / receipt placeholder
      </div>
    </FieldShell>
  );
}

export type MemberPickerSurface = "trip" | "living" | "purchase";

function memberContextPath(momentId: string, surface: MemberPickerSurface = "trip"): string {
  if (surface === "living") {
    return `api/v1/group/shared-living/moments/${momentId}/quick-add/expenses/context`;
  }
  if (surface === "purchase") {
    return `api/v1/group/shared-purchase/moments/${momentId}/quick-add/expenses/context`;
  }
  return `api/v1/group/trips/${momentId}/quick-add/expense/context`;
}

export function ParticipantPicker(props: {
  label?: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  error?: string;
  hint?: string;
  momentId?: string;
  /** Which quick-add surface to load members from. Defaults to trip. */
  surface?: MemberPickerSurface;
  options?: Array<{ value: string; label: string }>;
  /** When true and only one option, show read-only. */
  readOnlyWhenSingle?: boolean;
  emptyMessage?: string;
  /** Opens dedicated Participant / Invite action — only used when roster is empty. */
  onInviteParticipant?: () => void;
}) {
  const style = useInputStyle();
  const { colors } = useThemeTokens();
  const [loaded, setLoaded] = useState<Array<{ value: string; label: string }>>([]);
  const [loading, setLoading] = useState(false);
  const surface = props.surface ?? "trip";

  useEffect(() => {
    if (props.options?.length || !props.momentId) return;
    let cancelled = false;
    setLoading(true);
    void (async () => {
      try {
        const ctx = await requestWithRetry<{
          payers?: Array<{ id: string; display_name: string }>;
          guests?: Array<{ id: string; full_name: string }>;
          members?: Array<{ id: string; display_name: string }>;
          participants?: Array<{ id?: string; user_id?: string; display_name: string }>;
          default_paid_by_participant_id?: string | null;
        }>(memberContextPath(props.momentId!, surface), { method: "GET" });
        if (cancelled) return;
        const rows = [
          ...(ctx.payers ?? []).map((p) => ({ value: p.id, label: p.display_name })),
          ...(ctx.members ?? []).map((m) => ({ value: m.id, label: m.display_name })),
          ...(ctx.guests ?? []).map((g) => ({ value: g.id, label: g.full_name })),
          ...(ctx.participants ?? []).map((p) => ({
            value: String(p.id || p.user_id || ""),
            label: p.display_name,
          })),
        ].filter((r) => r.value);
        const dedup = Array.from(new Map(rows.map((r) => [r.value, r])).values());
        setLoaded(dedup);
        if (!props.value && ctx.default_paid_by_participant_id) {
          props.onChange(String(ctx.default_paid_by_participant_id));
        } else if (!props.value && dedup.length === 1) {
          props.onChange(dedup[0].value);
        }
      } catch {
        if (!cancelled) setLoaded([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [props.momentId, props.options?.length, surface]);

  const options = props.options?.length ? props.options : loaded;
  const single = options.length === 1;
  const readOnly = Boolean(props.readOnlyWhenSingle && single);

  if (options.length > 0 || loading || props.momentId) {
    if (!loading && options.length === 0) {
      return (
        <FieldShell label={props.label ?? "Paid by"} required={props.required} error={props.error}>
          <div className="space-y-2 rounded-xl px-3 py-2.5 text-sm" style={style}>
            <p style={{ color: colors.textSecondary }}>
              {props.emptyMessage ?? "No participant found?"}
            </p>
            {props.onInviteParticipant ? (
              <button
                type="button"
                className="text-sm font-semibold underline-offset-2 hover:underline"
                style={{ color: colors.primaryContainer }}
                onClick={props.onInviteParticipant}
              >
                + Invite participant
              </button>
            ) : (
              <p style={{ color: colors.error }}>
                Activate the experience or invite people first.
              </p>
            )}
          </div>
        </FieldShell>
      );
    }
    if (readOnly) {
      return (
        <FieldShell label={props.label ?? "Paid by"} required={props.required} error={props.error}>
          <div className="rounded-xl px-3 py-2.5 text-sm" style={style}>
            {options[0]?.label ?? props.value}
          </div>
        </FieldShell>
      );
    }
    return (
      <FieldShell label={props.label ?? "Paid by"} required={props.required} error={props.error}>
        <select
          value={props.value}
          onChange={(e) => props.onChange(e.target.value)}
          disabled={loading || options.length === 0}
          className="w-full rounded-xl px-3 py-2.5 text-sm"
          style={style}
        >
          <option value="">{loading ? "Loading members…" : "Select member"}</option>
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </FieldShell>
    );
  }

  return (
    <TextField
      label={props.label ?? "Paid by"}
      value={props.value}
      onChange={props.onChange}
      required={props.required}
      error={props.error}
      placeholder={props.hint ?? "Select a group member"}
    />
  );
}

export function MemberMultiSelect(props: {
  label?: string;
  value: string[];
  onChange: (ids: string[]) => void;
  momentId?: string;
  surface?: MemberPickerSurface;
  options?: Array<{ value: string; label: string }>;
  required?: boolean;
  error?: string;
  onInviteParticipant?: () => void;
}) {
  const style = useInputStyle();
  const { colors } = useThemeTokens();
  const [loaded, setLoaded] = useState<Array<{ value: string; label: string }>>([]);
  const [loading, setLoading] = useState(false);
  const surface = props.surface ?? "trip";

  useEffect(() => {
    if (props.options?.length || !props.momentId) return;
    let cancelled = false;
    setLoading(true);
    void (async () => {
      try {
        const ctx = await requestWithRetry<{
          members?: Array<{ id: string; display_name: string }>;
          payers?: Array<{ id: string; display_name: string }>;
          participants?: Array<{ id?: string; user_id?: string; display_name: string }>;
        }>(memberContextPath(props.momentId!, surface), { method: "GET" });
        if (cancelled) return;
        const rows = [
          ...(ctx.members ?? []).map((m) => ({ value: m.id, label: m.display_name })),
          ...(ctx.payers ?? []).map((p) => ({ value: p.id, label: p.display_name })),
          ...(ctx.participants ?? []).map((p) => ({
            value: String(p.id || p.user_id || ""),
            label: p.display_name,
          })),
        ].filter((r) => r.value);
        const dedup = Array.from(new Map(rows.map((r) => [r.value, r])).values());
        setLoaded(dedup);
        if (!props.value.length && dedup.length) {
          props.onChange(dedup.map((d) => d.value));
        }
      } catch {
        if (!cancelled) setLoaded([]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [props.momentId, props.options?.length, surface]);

  const options = props.options?.length ? props.options : loaded;
  const selected = new Set(props.value);

  function toggle(id: string) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    props.onChange(Array.from(next));
  }

  return (
    <FieldShell label={props.label ?? "Participants"} required={props.required} error={props.error}>
      {loading ? (
        <p className="text-xs" style={{ color: colors.textSecondary }}>
          Loading members…
        </p>
      ) : null}
      {!loading && !options.length ? (
        <div className="space-y-2 rounded-xl px-3 py-2.5 text-sm" style={style}>
          <p style={{ color: colors.textSecondary }}>No participant found?</p>
          {props.onInviteParticipant ? (
            <button
              type="button"
              className="font-semibold underline-offset-2 hover:underline"
              style={{ color: colors.primaryContainer }}
              onClick={props.onInviteParticipant}
            >
              + Invite participant
            </button>
          ) : (
            <p style={{ color: colors.error }}>No members available for split.</p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {options.map((opt) => {
            const on = selected.has(opt.value);
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => toggle(opt.value)}
                className="flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm"
                style={{
                  background: on ? colors.primaryContainer : colors.surfaceContainer,
                  color: colors.textPrimary,
                }}
              >
                <span>{opt.label}</span>
                <span className="text-xs font-semibold">{on ? "Included" : "Add"}</span>
              </button>
            );
          })}
        </div>
      )}
    </FieldShell>
  );
}

export function ContactPicker(props: { value: string; onChange: (v: string) => void }) {
  return <TextField label="Contact" value={props.value} onChange={props.onChange} />;
}

export function SplitEditor(props: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <ChipSelector
      label="Split method"
      value={props.value}
      onChange={props.onChange}
      options={[
        { value: "EQUAL", label: "Equal" },
        { value: "EXACT", label: "Exact" },
        { value: "PERCENTAGE", label: "Percentage" },
        { value: "SHARES", label: "Shares" },
      ]}
    />
  );
}

export function SplitPreview(props: {
  amountMinor: number;
  currencyCode: string;
  participantIds: string[];
  participantLabels?: Record<string, string>;
  splitStyle: string;
}) {
  const { colors } = useThemeTokens();
  const n = Math.max(props.participantIds.length, 1);
  const style = String(props.splitStyle || "EQUAL").toUpperCase();
  const base = Math.floor(props.amountMinor / n);
  const rem = props.amountMinor - base * n;
  const rows = props.participantIds.map((id, i) => ({
    id,
    label: props.participantLabels?.[id] ?? id,
    amount: style === "EQUAL" ? base + (i === 0 ? rem : 0) : base + (i === 0 ? rem : 0),
  }));
  const currency = findCurrency(getReferenceData()?.currencies ?? [], props.currencyCode);
  const minorUnit = currency?.minor_unit ?? 2;
  const divisor = 10 ** minorUnit;
  return (
    <div className="space-y-1 rounded-xl px-3 py-2" style={{ background: `${colors.textSecondary}12` }}>
      <p className="text-xs font-bold uppercase tracking-wide" style={{ color: colors.textSecondary }}>
        Split preview
      </p>
      {rows.map((r) => (
        <div key={r.id} className="flex justify-between text-xs" style={{ color: colors.textPrimary }}>
          <span>{r.label}</span>
          <span>
            {props.currencyCode} {(r.amount / divisor).toFixed(minorUnit)}
          </span>
        </div>
      ))}
    </div>
  );
}

export function PercentageEditor(props: {
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
      type="number"
      placeholder="0–100"
    />
  );
}

export function parseAmountMinor(value: string, minorUnit = 2): number {
  const currencies = getReferenceData()?.currencies ?? [];
  const fallback = { minor_unit: minorUnit };
  return parseUserInputToMinor(value, fallback.minor_unit === minorUnit ? { minor_unit: minorUnit } : fallback);
}

export function formatMoneyDisplay(major: string, currency = "INR"): string {
  if (!major) return "—";
  const ref = findCurrency(getReferenceData()?.currencies ?? [], currency);
  const symbol = ref?.symbol ?? (currency === "USD" ? "$" : currency === "EUR" ? "€" : "₹");
  return `${symbol}${major}`;
}

export { PollComposer } from "./PollComposer";

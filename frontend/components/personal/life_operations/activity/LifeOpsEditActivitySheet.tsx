"use client";

import { useCallback, useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { lifeOpsActivityCopy } from "@/lib/personal/life_operations/activity/lifeOpsActivityCopy";
import type { PersonalQuickAddDetail } from "@/lib/api/personal";
import {
  getPersonalQuickAddEvent,
  getPersonalQuickAddOptions,
  patchPersonalQuickAddEvent,
} from "@/lib/api/client";
import { minorToDisplayInput, parseUserInputToMinor } from "@/lib/reference_data/money";

type LifeOpsEditActivitySheetProps = {
  eventId: string;
  eventType: string;
  onClose: () => void;
  onSuccess: () => void;
};

const MONEY_EDIT_TYPES = new Set([
  "EXPENSE",
  "CONTRIBUTION",
  "SAVINGS",
  "INVESTMENT",
  "INCOME",
]);

function isMoneyEditType(eventType: string): boolean {
  return MONEY_EDIT_TYPES.has(eventType.toUpperCase());
}

/** Prefer major `amount`; never treat raw `amount_minor` as the text-field value. */
function expenseAmountDisplay(expense: Record<string, unknown>): string {
  if (expense.amount != null && String(expense.amount).trim() !== "") {
    return String(expense.amount);
  }
  const minor = Number(expense.amount_minor);
  if (Number.isFinite(minor) && minor > 0) {
    return minorToDisplayInput(minor, 2);
  }
  return "";
}

export function LifeOpsEditActivitySheet({
  eventId,
  eventType,
  onClose,
  onSuccess,
}: LifeOpsEditActivitySheetProps) {
  const { colors } = useThemeTokens();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<PersonalQuickAddDetail | null>(null);
  const [title, setTitle] = useState("");
  const [note, setNote] = useState("");
  const [amount, setAmount] = useState("");
  const [currencyCode, setCurrencyCode] = useState("INR");
  const [accountId, setAccountId] = useState("");
  const [categoryName, setCategoryName] = useState("");
  const [feeling, setFeeling] = useState("BALANCED");
  const [recoveryType, setRecoveryType] = useState("QUIET_TIME");
  const [accounts, setAccounts] = useState<Array<{ account_id: string; account_name: string }>>([]);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [data, options] = await Promise.all([
        getPersonalQuickAddEvent(eventId),
        getPersonalQuickAddOptions(),
      ]);
      setDetail(data);
      setTitle(data.event_title);
      setNote(data.event_summary ?? "");
      setAccounts(options.accounts ?? []);
      const primary =
        options.accounts?.find((a) => a.is_primary)?.account_id ?? options.accounts?.[0]?.account_id ?? "";
      if (data.expense) {
        const expense = data.expense as Record<string, unknown>;
        setAmount(expenseAmountDisplay(expense));
        setCurrencyCode(String(expense.currency_code ?? "INR"));
        setAccountId(String(expense.account_id ?? primary));
        setCategoryName(String(expense.category_name ?? ""));
      } else {
        setAccountId(primary);
      }
      if (data.reflection) {
        setNote(String(data.reflection.reflection_note ?? ""));
        setFeeling(String(data.reflection.feeling_state ?? "BALANCED"));
      }
      if (data.recovery) {
        setRecoveryType(String(data.recovery.recovery_type ?? "QUIET_TIME"));
        setNote(String(data.recovery.notes ?? ""));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load activity.");
    } finally {
      setLoading(false);
    }
  }, [eventId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!detail) return;
    setSubmitting(true);
    setError(null);
    const type = eventType.toUpperCase();
    const body: Record<string, unknown> = {
      event_title: title.trim(),
      event_summary: note.trim() || null,
    };
    if (type === "EXPENSE" || (isMoneyEditType(type) && detail.expense)) {
      const amountMinor = parseUserInputToMinor(amount, { minor_unit: 2 });
      body.expense = {
        transaction_type: detail.expense?.transaction_type ?? type,
        amount_minor: amountMinor,
        currency_code: currencyCode,
        account_id: accountId,
        category_name: categoryName || undefined,
        description: note.trim() || undefined,
        transaction_date: detail.expense?.transaction_date,
      };
    } else if (type === "REFLECTION") {
      body.reflection = {
        feeling_state: feeling,
        reflection_note: note.trim(),
        reflection_tag: detail.reflection?.reflection_tag ?? null,
      };
    } else if (type === "RECOVERY") {
      body.recovery = {
        recovery_type: recoveryType,
        recovery_intensity: detail.recovery?.recovery_intensity ?? "MODERATE",
        duration_minutes: detail.recovery?.duration_minutes ?? null,
        notes: note.trim() || null,
      };
    } else if (type === "COMMITMENT" && detail.commitment) {
      body.commitment = { ...detail.commitment, commitment_name: title.trim(), notes: note.trim() || null };
    } else if (type === "RHYTHM" && detail.rhythm) {
      body.rhythm = detail.rhythm;
      body.event_title = title.trim();
    }
    try {
      await patchPersonalQuickAddEvent(eventId, body);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save changes.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-[60] flex items-end justify-center"
      style={{ background: "rgba(0,0,0,0.6)" }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-t-[32px] p-8"
        style={{ background: colors.surfaceContainerHigh, borderTop: "1px solid rgba(255,255,255,0.1)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-8 h-1.5 w-12 rounded-full" style={{ background: "rgba(255,255,255,0.1)" }} />
        <div className="mb-6">
          <h2 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
            {lifeOpsActivityCopy.editTitle}
          </h2>
          <p style={{ ...personalTypography.bodyMd, opacity: 0.6 }}>{lifeOpsActivityCopy.editSubtitle}</p>
        </div>

        {loading ? (
          <p style={{ opacity: 0.7 }}>Loading…</p>
        ) : (
          <form className="space-y-4" onSubmit={(e) => void handleSave(e)}>
            <label className="block">
              <span style={{ fontSize: 11, fontWeight: 700, opacity: 0.5, textTransform: "uppercase" }}>
                {lifeOpsActivityCopy.titleLabel}
              </span>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="mt-2 w-full rounded-xl border px-4 py-3"
                style={{ background: colors.surfaceContainerLowest, borderColor: "rgba(255,255,255,0.05)", color: colors.textPrimary }}
              />
            </label>

            {isMoneyEditType(eventType) && detail?.expense ? (
              <>
                <label className="block">
                  <span style={{ fontSize: 11, fontWeight: 700, opacity: 0.5, textTransform: "uppercase" }}>
                    {lifeOpsActivityCopy.amountLabel}
                  </span>
                  <input
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    className="mt-2 w-full rounded-xl border px-4 py-3"
                    style={{ background: colors.surfaceContainerLowest, borderColor: "rgba(255,255,255,0.05)", color: colors.textPrimary }}
                  />
                </label>
                <label className="block">
                  <span style={{ fontSize: 11, fontWeight: 700, opacity: 0.5, textTransform: "uppercase" }}>
                    {lifeOpsActivityCopy.accountLabel}
                  </span>
                  <select
                    value={accountId}
                    onChange={(e) => setAccountId(e.target.value)}
                    className="mt-2 w-full rounded-xl border px-4 py-3"
                    style={{ background: colors.surfaceContainerLowest, borderColor: "rgba(255,255,255,0.05)", color: colors.textPrimary }}
                  >
                    {accounts.map((a) => (
                      <option key={a.account_id} value={a.account_id}>
                        {a.account_name}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  <span style={{ fontSize: 11, fontWeight: 700, opacity: 0.5, textTransform: "uppercase" }}>
                    {lifeOpsActivityCopy.categoryLabel}
                  </span>
                  <input
                    value={categoryName}
                    onChange={(e) => setCategoryName(e.target.value)}
                    className="mt-2 w-full rounded-xl border px-4 py-3"
                    style={{ background: colors.surfaceContainerLowest, borderColor: "rgba(255,255,255,0.05)", color: colors.textPrimary }}
                  />
                </label>
              </>
            ) : null}

            <label className="block">
              <span style={{ fontSize: 11, fontWeight: 700, opacity: 0.5, textTransform: "uppercase" }}>
                {lifeOpsActivityCopy.noteLabel}
              </span>
              <textarea
                value={note}
                onChange={(e) => setNote(e.target.value)}
                rows={3}
                className="mt-2 w-full rounded-xl border px-4 py-3"
                style={{ background: colors.surfaceContainerLowest, borderColor: "rgba(255,255,255,0.05)", color: colors.textPrimary }}
              />
            </label>

            {error ? <p style={{ color: colors.error, fontSize: 13 }}>{error}</p> : null}

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 rounded-2xl py-4 font-bold"
                style={{ background: `${colors.surfaceVariant}4d`, color: colors.textSecondary, border: "none" }}
              >
                {lifeOpsActivityCopy.cancel}
              </button>
              <button
                type="submit"
                disabled={submitting}
                className="flex-[2] rounded-2xl py-4 font-bold"
                style={{ background: colors.brandPrimary, color: "#fff", border: "none" }}
              >
                {lifeOpsActivityCopy.saveChanges}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

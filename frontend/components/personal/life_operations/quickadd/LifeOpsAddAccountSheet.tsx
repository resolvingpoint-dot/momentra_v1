"use client";

import { useEffect, useMemo, useState } from "react";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import {
  createPersonalAccount,
  type PersonalAccountCreateRequest,
  type PersonalQuickAddAccount,
} from "@/lib/api/client";
import { MoneyInput } from "@/components/shared/MoneyInput";
import { getBootstrap } from "@/stores/bootstrapStore";
import type { CurrencyReference, ReferenceItem } from "@/lib/reference_data/types";

type LifeOpsAddAccountSheetProps = {
  onClose: () => void;
  onCreated: (account: PersonalQuickAddAccount) => void;
  accountTypes?: ReferenceItem[];
  currencies?: CurrencyReference[];
  defaultCurrencyCode?: string;
};

export function LifeOpsAddAccountSheet({
  onClose,
  onCreated,
  accountTypes = [],
  currencies = [],
  defaultCurrencyCode,
}: LifeOpsAddAccountSheetProps) {
  const { colors } = usePersonalDomainTokens();
  const bootstrap = getBootstrap();
  const locale = bootstrap?.preferences.locale ?? "en-IN";
  const defaultCurrency =
    defaultCurrencyCode ?? bootstrap?.preferences.default_currency_code ?? "INR";

  const typeOptions = useMemo(() => accountTypes, [accountTypes]);

  const [selectedTypeCode, setSelectedTypeCode] = useState(typeOptions[0]?.code ?? "SAVINGS");
  const [accountName, setAccountName] = useState("");
  const [openingBalanceMinor, setOpeningBalanceMinor] = useState(0);
  const [currencyCode, setCurrencyCode] = useState(defaultCurrency);
  const [isPrimary, setIsPrimary] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCurrencyCode(defaultCurrency);
  }, [defaultCurrency]);

  useEffect(() => {
    if (typeOptions.length > 0 && !typeOptions.some((t) => t.code === selectedTypeCode)) {
      setSelectedTypeCode(typeOptions[0].code);
    }
  }, [typeOptions, selectedTypeCode]);

  const canSubmit = accountName.trim().length > 0 && !submitting && typeOptions.length > 0;

  async function handleSubmit() {
    const trimmedName = accountName.trim();
    if (!trimmedName) return;
    setSubmitting(true);
    setError(null);
    const body: PersonalAccountCreateRequest = {
      account_name: trimmedName,
      account_type: selectedTypeCode,
      currency_code: currencyCode,
      opening_balance_minor: openingBalanceMinor > 0 ? openingBalanceMinor : null,
      is_primary: isPrimary,
    };
    try {
      const account = await createPersonalAccount(body);
      onCreated(account);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create account.");
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-[60] flex items-end justify-center bg-black/60 sm:items-center"
      onClick={onClose}
      role="presentation"
    >
      <div
        className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-t-2xl p-5 sm:rounded-2xl"
        style={{ background: colors.surface ?? "#14121b" }}
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-account-title"
      >
        <div className="mb-4 flex items-center justify-between">
          <button type="button" onClick={onClose} className="text-sm font-medium transition-transform duration-200 hover:scale-[1.02] active:scale-95" style={{ color: colors.brandPrimary }}>
            Back
          </button>
          <h2 id="add-account-title" style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
            Add Account
          </h2>
          <span className="w-10" />
        </div>

        <div className="space-y-5">
          <div className="space-y-2">
            <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>Account Type</label>
            <div className="flex flex-wrap gap-2">
              {typeOptions.map((opt) => {
                const selected = selectedTypeCode === opt.code;
                return (
                  <button
                    key={opt.code}
                    type="button"
                    onClick={() => setSelectedTypeCode(opt.code)}
                    className="rounded-lg px-3 py-2 text-xs font-medium transition-transform duration-200 hover:scale-[1.02] active:scale-95"
                    style={{
                      border: `1px solid ${selected ? opt.color || colors.brandPrimary : colors.border}`,
                      background: selected ? `${opt.color || colors.brandPrimary}22` : "transparent",
                      color: selected ? opt.color || colors.brandPrimary : colors.textSecondary,
                    }}
                  >
                    {opt.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="space-y-2">
            <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>Account Name</label>
            <input
              type="text"
              value={accountName}
              onChange={(e) => setAccountName(e.target.value)}
              placeholder="e.g. HDFC Savings"
              className="w-full rounded-xl border px-3 py-3"
              style={{
                borderColor: colors.border,
                background: colors.surfaceContainerLowest ?? "#0e0d16",
                color: colors.textPrimary,
              }}
            />
          </div>

          {currencies.length > 0 ? (
            <MoneyInput
              label="Opening Balance (optional)"
              currencies={currencies}
              defaultCurrencyCode={defaultCurrency}
              locale={locale}
              value={{ amount_minor: openingBalanceMinor, currency_code: currencyCode }}
              onChange={(v) => {
                setOpeningBalanceMinor(v.amount_minor);
                setCurrencyCode(v.currency_code);
              }}
            />
          ) : null}

          <label className="flex items-center gap-2 text-sm" style={{ color: colors.textSecondary }}>
            <input
              type="checkbox"
              checked={isPrimary}
              onChange={(e) => setIsPrimary(e.target.checked)}
            />
            Set as primary account
          </label>

          {error ? <p className="text-sm text-red-400">{error}</p> : null}

          <button
            type="button"
            disabled={!canSubmit}
            onClick={() => void handleSubmit()}
            className="w-full rounded-xl py-3 text-sm font-semibold transition-transform duration-200 hover:scale-[1.02] active:scale-95 disabled:opacity-50"
            style={{ background: colors.brandPrimary, color: "#fff" }}
          >
            {submitting ? "Creating…" : "Create Account"}
          </button>
        </div>
      </div>
    </div>
  );
}

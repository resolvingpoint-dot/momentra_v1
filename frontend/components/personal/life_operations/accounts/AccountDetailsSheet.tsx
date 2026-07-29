"use client";

import { useEffect, useState } from "react";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { MoneyInput } from "@/components/shared/MoneyInput";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import { getBootstrap } from "@/stores/bootstrapStore";
import type { PersonalAccountRecord } from "@/lib/metadata/money";
import type { CurrencyReference, ReferenceItem } from "@/lib/reference_data/types";

type AccountDetailsSheetProps = {
  account: PersonalAccountRecord;
  accountTypes: ReferenceItem[];
  currencies: CurrencyReference[];
  defaultCurrencyCode?: string;
  onClose: () => void;
  onUpdated: () => void;
};

export function AccountDetailsSheet({
  account,
  accountTypes,
  currencies,
  defaultCurrencyCode,
  onClose,
  onUpdated,
}: AccountDetailsSheetProps) {
  const { colors } = usePersonalDomainTokens();
  const bootstrap = getBootstrap();
  const locale = bootstrap?.preferences.locale ?? "en-IN";
  const defaultCurrency = defaultCurrencyCode ?? bootstrap?.preferences.default_currency_code ?? "INR";

  const [accountName, setAccountName] = useState(account.account_name);
  const [selectedTypeCode, setSelectedTypeCode] = useState(account.account_type);
  const [currencyCode, setCurrencyCode] = useState(account.currency_code);
  const [balanceMinor, setBalanceMinor] = useState(account.current_balance_minor ?? 0);
  const [isDefault, setIsDefault] = useState(account.is_primary ?? account.is_default ?? false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const txCount = account.transaction_count ?? 0;
  const canEditCurrency = txCount === 0;

  useEffect(() => {
    setAccountName(account.account_name);
    setSelectedTypeCode(account.account_type);
    setCurrencyCode(account.currency_code);
    setBalanceMinor(account.current_balance_minor ?? 0);
    setIsDefault(account.is_primary ?? account.is_default ?? false);
  }, [account]);

  async function handleSave() {
    setSubmitting(true);
    setError(null);
    try {
      await PersonalRepository.patchAccount(account.account_id, {
        account_name: accountName.trim(),
        account_type: selectedTypeCode,
        currency_code: canEditCurrency ? currencyCode : undefined,
        current_balance_minor: balanceMinor,
        is_default: isDefault,
      });
      onUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not update account.");
      setSubmitting(false);
    }
  }

  async function handleArchive() {
    setSubmitting(true);
    setError(null);
    try {
      await PersonalRepository.archiveAccount(account.account_id);
      onUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not archive account.");
      setSubmitting(false);
    }
  }

  async function handleDelete() {
    if (txCount > 0) return;
    setSubmitting(true);
    setError(null);
    try {
      await PersonalRepository.deleteAccount(account.account_id);
      onUpdated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete account.");
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
      >
        <div className="mb-4 flex items-center justify-between">
          <button type="button" onClick={onClose} style={{ color: colors.brandPrimary }}>Back</button>
          <h2 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>Account Details</h2>
          <span className="w-10" />
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>Account Name</label>
            <input
              value={accountName}
              onChange={(e) => setAccountName(e.target.value)}
              className="w-full rounded-xl border px-3 py-3"
              style={{ borderColor: colors.border, background: colors.surfaceContainerLowest, color: colors.textPrimary }}
            />
          </div>

          <div className="space-y-2">
            <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>Account Type</label>
            <div className="flex flex-wrap gap-2">
              {accountTypes.map((opt) => (
                <button
                  key={opt.code}
                  type="button"
                  onClick={() => setSelectedTypeCode(opt.code)}
                  className="rounded-lg px-3 py-2 text-xs font-medium"
                  style={{
                    border: `1px solid ${selectedTypeCode === opt.code ? colors.brandPrimary : colors.border}`,
                    color: selectedTypeCode === opt.code ? colors.brandPrimary : colors.textSecondary,
                  }}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          {currencies.length > 0 ? (
            <MoneyInput
              label="Current Balance"
              currencies={currencies}
              defaultCurrencyCode={defaultCurrency}
              locale={locale}
              value={{ amount_minor: balanceMinor, currency_code: canEditCurrency ? currencyCode : account.currency_code }}
              onChange={(v) => {
                setBalanceMinor(v.amount_minor);
                if (canEditCurrency) setCurrencyCode(v.currency_code);
              }}
            />
          ) : null}

          {!canEditCurrency ? (
            <p className="text-xs opacity-60" style={{ color: colors.textSecondary }}>
              Currency cannot be changed after transactions exist on this account.
            </p>
          ) : null}

          <label className="flex items-center gap-2 text-sm" style={{ color: colors.textSecondary }}>
            <input type="checkbox" checked={isDefault} onChange={(e) => setIsDefault(e.target.checked)} />
            Set as default account
          </label>

          {error ? <p className="text-sm text-red-400">{error}</p> : null}

          <button
            type="button"
            disabled={submitting || !accountName.trim()}
            onClick={() => void handleSave()}
            className="w-full rounded-xl py-3 text-sm font-semibold disabled:opacity-50"
            style={{ background: colors.brandPrimary, color: "#fff" }}
          >
            {submitting ? "Saving…" : "Save Changes"}
          </button>

          <button
            type="button"
            disabled={submitting}
            onClick={() => void handleArchive()}
            className="w-full rounded-xl border py-3 text-sm font-semibold"
            style={{ borderColor: colors.border, color: colors.textSecondary }}
          >
            Archive Account
          </button>

          {txCount === 0 ? (
            <button
              type="button"
              disabled={submitting}
              onClick={() => void handleDelete()}
              className="w-full rounded-xl py-3 text-sm font-semibold"
              style={{ color: colors.error }}
            >
              Delete Account
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

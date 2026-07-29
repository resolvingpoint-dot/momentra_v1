"use client";

import { useCallback, useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { LifeOpsAddAccountSheet } from "@/components/personal/life_operations/quickadd/LifeOpsAddAccountSheet";
import { AccountDetailsSheet } from "@/components/personal/life_operations/accounts/AccountDetailsSheet";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import { getQuickAddOptionsCache, prefetchQuickAddOptions } from "@/hooks/useQuickAddOptions";
import { formatAccountBalance } from "@/lib/metadata/money";
import { getBootstrap } from "@/stores/bootstrapStore";
import type { PersonalAccountRecord } from "@/lib/metadata/money";
import type { CurrencyReference, ReferenceItem } from "@/lib/reference_data/types";
import { Wallet } from "lucide-react";

type AccountsCardProps = {
  momentId?: string | null;
  /** Increment to force a background refresh (e.g. after account create). */
  refreshToken?: number;
};

export function AccountsCard({ momentId, refreshToken = 0 }: AccountsCardProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const bootstrap = getBootstrap();
  const locale = bootstrap?.preferences.locale ?? "en-IN";

  const cachedOptions = getQuickAddOptionsCache(momentId);
  const [accounts, setAccounts] = useState<PersonalAccountRecord[]>([]);
  const [currencies, setCurrencies] = useState<CurrencyReference[]>(
    (cachedOptions?.currencies ?? []) as CurrencyReference[],
  );
  const [accountTypes, setAccountTypes] = useState<ReferenceItem[]>(
    (cachedOptions?.account_types ?? []) as ReferenceItem[],
  );
  const [defaultCurrency, setDefaultCurrency] = useState(
    cachedOptions?.default_currency_code ?? bootstrap?.preferences.default_currency_code ?? "INR",
  );
  const [loading, setLoading] = useState(accounts.length === 0);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const load = useCallback(
    async (background = false) => {
      if (!background) {
        setLoading(accounts.length === 0);
      }
      setLoadError(null);
      try {
        const [accountRows, options] = await Promise.all([
          PersonalRepository.listAccounts(false),
          prefetchQuickAddOptions(momentId ?? undefined),
        ]);
        setAccounts(accountRows as PersonalAccountRecord[]);
        setCurrencies((options.currencies ?? []) as CurrencyReference[]);
        setAccountTypes((options.account_types ?? []) as ReferenceItem[]);
        setDefaultCurrency(
          options.default_currency_code ?? bootstrap?.preferences.default_currency_code ?? "INR",
        );
      } catch (err) {
        setLoadError(err instanceof Error ? err.message : "Could not load accounts.");
      } finally {
        setLoading(false);
      }
    },
    [momentId, bootstrap?.preferences.default_currency_code, accounts.length],
  );

  useEffect(() => {
    void load(accounts.length > 0);
  }, [momentId, refreshToken]); // eslint-disable-line react-hooks/exhaustive-deps -- refreshToken triggers background reload

  const selected = accounts.find((a) => a.account_id === selectedId || a.id === selectedId);

  return (
    <>
      <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
        <div className="mb-3 flex items-center justify-between">
          <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>Accounts</h3>
          <button
            type="button"
            onClick={() => setShowAdd(true)}
            className="text-xs font-semibold transition-transform duration-200 hover:scale-[1.02] active:scale-95"
            style={{ color: colors.brandPrimary, background: "none", border: "none" }}
          >
            + Add Account
          </button>
        </div>

        {loading ? (
          <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>Loading accounts…</p>
        ) : loadError ? (
          <div className="space-y-2">
            <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>{loadError}</p>
            <button
              type="button"
              onClick={() => void load()}
              className="text-xs font-semibold"
              style={{ color: colors.brandPrimary, background: "none", border: "none" }}
            >
              Retry
            </button>
          </div>
        ) : accounts.length === 0 ? (
          <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
            No accounts yet. Add one to track money flows.
          </p>
        ) : (
          <div className="space-y-2">
            {accounts.map((account) => (
              <button
                key={account.account_id}
                type="button"
                onClick={() => setSelectedId(account.account_id)}
                className="flex w-full items-center gap-3 rounded-xl border p-3 text-left transition-transform duration-200 hover:scale-[1.01] active:scale-[0.99]"
                style={{ borderColor: "rgba(255,255,255,0.08)", background: "rgba(255,255,255,0.03)" }}
              >
                <div
                  className="flex size-9 shrink-0 items-center justify-center rounded-lg"
                  style={{ background: `${colors.brandPrimary}22` }}
                >
                  <Wallet size={18} color={colors.brandPrimary} />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-semibold" style={{ color: colors.textPrimary }}>
                    {account.account_name}
                  </p>
                  <p className="text-xs opacity-60" style={{ color: colors.textSecondary }}>
                    {account.account_type_label ?? account.account_type}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold" style={{ color: colors.textPrimary }}>
                    {formatAccountBalance(account, currencies, locale)}
                  </p>
                  <p className="text-[10px] uppercase opacity-50">{account.currency_code}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </section>

      {showAdd ? (
        <LifeOpsAddAccountSheet
          accountTypes={accountTypes}
          currencies={currencies}
          defaultCurrencyCode={defaultCurrency}
          onClose={() => setShowAdd(false)}
          onCreated={(_account) => {
            void load(true);
          }}
        />
      ) : null}

      {selected ? (
        <AccountDetailsSheet
          account={selected}
          accountTypes={accountTypes}
          currencies={currencies}
          defaultCurrencyCode={defaultCurrency}
          onClose={() => setSelectedId(null)}
          onUpdated={() => {
            setSelectedId(null);
            void load(true);
          }}
        />
      ) : null}
    </>
  );
}

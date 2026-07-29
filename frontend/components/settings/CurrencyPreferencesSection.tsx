"use client";

import { useEffect, useMemo, useState } from "react";
import { patchAppPreferences } from "@/lib/api/client";
import type { BootstrapPreferences } from "@/lib/api/bootstrapTypes";
import { MoneyInput } from "@/components/shared/MoneyInput";
import { getReferenceData } from "@/lib/reference_data/referenceDataStore";
import { invalidateBootstrapAfterMutation } from "@/stores/bootstrapStore";
import type { CurrencyReference } from "@/lib/reference_data/types";

type CurrencyPreferencesSectionProps = {
  preferences: BootstrapPreferences;
  onPreferencesUpdated: (prefs: BootstrapPreferences) => void;
};

export function CurrencyPreferencesSection({
  preferences,
  onPreferencesUpdated,
}: CurrencyPreferencesSectionProps) {
  const referenceData = getReferenceData();
  const currencies = (referenceData?.currencies ?? []) as CurrencyReference[];
  const supportedCodes = useMemo(
    () => new Set(["INR", "USD", "EUR", "GBP", "AED", "SGD", "JPY"]),
    [],
  );
  const currencyOptions = currencies.filter((c) => supportedCodes.has(c.code));

  const [currencyCode, setCurrencyCode] = useState(preferences.default_currency_code);
  const [locale, setLocale] = useState(preferences.locale);
  const [previewMinor, setPreviewMinor] = useState(0);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    setCurrencyCode(preferences.default_currency_code);
    setLocale(preferences.locale);
  }, [preferences.default_currency_code, preferences.locale]);

  async function handleSave() {
    setSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const updated = await patchAppPreferences({
        default_currency_code: currencyCode,
        locale,
      });
      invalidateBootstrapAfterMutation();
      onPreferencesUpdated(updated);
      setSuccess("Currency preferences saved");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save preferences");
    } finally {
      setSaving(false);
    }
  }

  if (currencyOptions.length === 0) {
    return (
      <p className="text-sm text-white/60">
        Reference data is still loading. Currency settings will appear shortly.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <label className="text-sm text-white/70">Default currency</label>
        <select
          value={currencyCode}
          onChange={(e) => setCurrencyCode(e.target.value)}
          className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white"
        >
          {currencyOptions.map((c) => (
            <option key={c.code} value={c.code}>
              {c.code} — {c.label}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="text-sm text-white/70">Locale</label>
        <input
          type="text"
          value={locale}
          onChange={(e) => setLocale(e.target.value)}
          className="w-full rounded-lg border border-white/15 bg-black/30 px-3 py-2 text-sm text-white"
          placeholder="en-IN"
        />
      </div>

      <MoneyInput
        label="Preview amount"
        currencies={currencyOptions}
        defaultCurrencyCode={currencyCode}
        locale={locale}
        value={{ amount_minor: previewMinor, currency_code: currencyCode }}
        onChange={(v) => {
          setPreviewMinor(v.amount_minor);
          setCurrencyCode(v.currency_code);
        }}
      />

      {error ? <p className="text-sm text-red-400">{error}</p> : null}
      {success ? <p className="text-sm text-emerald-400">{success}</p> : null}

      <button
        type="button"
        disabled={saving}
        onClick={() => void handleSave()}
        className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        {saving ? "Saving…" : "Save currency preferences"}
      </button>
    </div>
  );
}

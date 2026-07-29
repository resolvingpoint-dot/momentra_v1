"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { BottomSheet } from "@/components/shared/BottomSheet";
import { AppToast } from "@/components/shared/AppToast";
import { successPulseVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { MOTION_DURATION_MS } from "@/lib/motion/tokens";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { SkeletonQuickAddSheet } from "@/components/personal/shared/skeleton/SkeletonBlocks";
import { useQuickAddOptions } from "@/hooks/useQuickAddOptions";
import { getQuickAddBundleByContext } from "@/lib/quick_add/registry";
import {
  buildLifeOpsQuickAddPayload,
  canSubmitLifeOpsTab,
  defaultLifeOpsFormState,
  isLifeOpsTabDirty,
  type LifeOpsQuickAddFormState,
  type RuntimeSignalDirection,
  type RuntimeSignalKey,
} from "@/lib/quick_add/payloadBuilders/lifeOperations";
import {
  accountLabelForEntryType,
  compactInsightBody,
  filterMoneyEntryTypes,
  humanizeEnumLabel,
  INTENTION_SIGNAL_PRESETS,
  LO_SELECTOR_HELPER,
  LO_SHEET_SUPPORTING,
  loSelectorBlurb,
  runtimeModeHint,
  runtimeModeLabel,
  signalDirectionLabel,
  tabSaveLabel,
  tabSuccessMessage,
} from "@/lib/quick_add/lifeOpsCopy";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import {
  deserializeQuickAddForm,
  hasQuickAddDraft,
  loadQuickAddDraft,
  saveQuickAddDraft,
  serializeQuickAddForm,
  subscribeOnlineRetry,
  createClientRequestId,
} from "@/lib/quick_add/draftStore";
import {
  ApiError,
  type PersonalQuickAddAccount,
  type PersonalQuickAddFieldOption,
  type PersonalQuickAddMetadata,
  type PersonalQuickAddOptionsResponse,
  type PersonalQuickAddTab,
} from "@/lib/api/client";
import { getPersonalPulseCache } from "@/hooks/usePersonalPulse";
import { applyOptimisticPatch, rollbackPatch } from "@/lib/telemetry/optimisticPulse";
import {
  buildLifeOpsOptimisticPatch,
  isOptimisticSafeEventType,
} from "@/lib/telemetry/lifeOpsOptimisticPatch";
import { endQuickAddSaveSpan, startQuickAddSaveSpan } from "@/lib/telemetry/performanceTelemetry";
import { resolveExpenseCategoryIcon } from "@/lib/personal/life_operations/expenseCategoryIcons";
import { LifeOpsAddAccountSheet } from "@/components/personal/life_operations/quickadd/LifeOpsAddAccountSheet";
import { MoneyInput } from "@/components/shared/MoneyInput";
import { resolveExpenseCategories } from "@/lib/quick_add/resolveOptions";
import type { CurrencyReference, ReferenceItem } from "@/lib/reference_data/types";
import { getBootstrap } from "@/stores/bootstrapStore";
import { nowISOTime, todayISODate } from "@/lib/quick_add/dateTimeDefaults";
import { MomentraAnalytics } from "@/lib/analytics";

type LifeOperationsQuickAddSheetProps = {
  initialEventType?: string | null;
  defaultMomentId?: string | null;
  open?: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  onBeginSetup?: () => void;
};

const LIFE_OPS_BUNDLE = getQuickAddBundleByContext("LIFE_OPERATIONS")!;
const LIFE_OPS_EVENT_TYPES = new Set((LIFE_OPS_BUNDLE?.actions ?? []).map((a) => a.action_id));

type ChipOptionSource = string | PersonalQuickAddFieldOption | Record<string, unknown>;
type FormState = LifeOpsQuickAddFormState;
type TabDraftMap = Partial<Record<string, FormState>>;

function normalizeChipOptions(items: ChipOptionSource[]): Array<{ value: string; label: string }> {
  return items.map((item) => {
    if (typeof item === "string") {
      return { value: item, label: humanizeEnumLabel(item) };
    }
    const record = item as Record<string, unknown>;
    const value = String(record.value ?? "");
    const label = String(record.label ?? humanizeEnumLabel(value));
    return { value, label };
  });
}

function optionsFromFieldOptions(items: PersonalQuickAddFieldOption[]) {
  return normalizeChipOptions(items);
}

function ChipSelect({
  label,
  options,
  value,
  onChange,
  multi = false,
  hint,
}: {
  label: string;
  options: Array<{ value: string; label: string }>;
  value: string | string[];
  onChange: (value: string) => void;
  multi?: boolean;
  hint?: string;
}) {
  const { colors } = usePersonalDomainTokens();
  const selected = multi ? new Set(Array.isArray(value) ? value : []) : value;

  return (
    <div className="space-y-2">
      <div className="space-y-0.5">
        <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>{label}</label>
        {hint ? (
          <p className="text-xs" style={{ color: colors.textSecondary, opacity: 0.75 }}>
            {hint}
          </p>
        ) : null}
      </div>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const isSelected = multi
            ? (selected as Set<string>).has(opt.value)
            : selected === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              aria-pressed={isSelected}
              onClick={() => onChange(opt.value)}
              className="min-h-11 rounded-lg px-3 py-2 text-xs font-medium transition-transform duration-200 hover:scale-[1.02] active:scale-95"
              style={{
                border: `1px solid ${isSelected ? colors.brandPrimary : colors.border}`,
                background: isSelected ? "rgba(108, 78, 242, 0.15)" : "transparent",
                color: isSelected ? colors.brandPrimary : colors.textSecondary,
              }}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function SegmentedControl({
  label,
  hint,
  options,
  value,
  onChange,
}: {
  label: string;
  hint?: string;
  options: Array<{ value: string; label: string }>;
  value: string;
  onChange: (value: string) => void;
}) {
  const { colors } = usePersonalDomainTokens();
  return (
    <div className="space-y-2">
      <div className="space-y-0.5">
        <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>{label}</label>
        {hint ? (
          <p className="text-xs" style={{ color: colors.textSecondary, opacity: 0.75 }}>
            {hint}
          </p>
        ) : null}
      </div>
      <div
        className="flex gap-1 rounded-full p-1"
        style={{ background: colors.surfaceContainer ?? "rgba(255,255,255,0.04)" }}
        role="radiogroup"
        aria-label={label}
      >
        {options.map((opt) => {
          const active = value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              role="radio"
              aria-checked={active}
              onClick={() => onChange(opt.value)}
              className="min-h-11 flex-1 rounded-full px-2 py-2 text-xs font-semibold"
              style={{
                background: active ? colors.brandPrimary : "transparent",
                color: active ? colors.brandOnPrimary ?? "#0e0d16" : colors.textSecondary,
              }}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function ReferenceCategoryChips({
  label,
  items,
  value,
  onChange,
  maxVisible = 5,
}: {
  label: string;
  items: ReferenceItem[];
  value: string;
  onChange: (code: string) => void;
  maxVisible?: number;
}) {
  const { colors } = usePersonalDomainTokens();
  const [showAll, setShowAll] = useState(false);
  const visible = showAll ? items : items.slice(0, maxVisible);
  const hasMore = items.length > maxVisible;

  return (
    <div className="space-y-2">
      <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>{label}</label>
      <div className="flex flex-wrap gap-2">
        {visible.map((item) => {
          const selected = value === item.code;
          const Icon = resolveExpenseCategoryIcon(
            item.icon,
            item.parent_code ?? item.code,
            item.parent_code ? item.code : undefined,
          );
          const accent = item.color || colors.brandPrimary;
          return (
            <button
              key={item.code}
              type="button"
              aria-pressed={selected}
              onClick={() => onChange(item.code)}
              className="inline-flex min-h-11 items-center gap-1.5 rounded-lg px-3 py-2 text-xs font-medium"
              style={{
                border: `1px solid ${selected ? accent : colors.border}`,
                background: selected ? `${accent}22` : "transparent",
                color: selected ? accent : colors.textSecondary,
              }}
            >
              <Icon size={14} aria-hidden />
              {item.label}
            </button>
          );
        })}
        {hasMore ? (
          <button
            type="button"
            onClick={() => setShowAll((v) => !v)}
            className="min-h-11 rounded-lg px-3 py-2 text-xs font-medium"
            style={{ border: `1px solid ${colors.border}`, color: colors.brandPrimary }}
          >
            {showAll ? "Less" : "More"}
          </button>
        ) : null}
      </div>
    </div>
  );
}

function CompactTextField({
  label,
  value,
  onChange,
  placeholder,
  multiline = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  multiline?: boolean;
}) {
  const { colors } = usePersonalDomainTokens();
  const style = {
    borderColor: colors.border,
    background: colors.surfaceContainerLowest ?? "#0e0d16",
    color: colors.textPrimary,
  };
  return (
    <div className="space-y-2">
      <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>{label}</label>
      {multiline ? (
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={2}
          placeholder={placeholder}
          className="w-full rounded-xl border p-3 input-focus-glow"
          style={style}
        />
      ) : (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full rounded-xl border px-3 py-3 input-focus-glow"
          style={style}
        />
      )}
    </div>
  );
}

function defaultFormState(): FormState {
  const bootstrap = getBootstrap();
  return defaultLifeOpsFormState(bootstrap?.preferences.default_currency_code ?? "INR");
}

function moodIcon(value: string): string {
  switch (value) {
    case "GREAT":
      return "◎";
    case "GOOD":
      return "○";
    case "OKAY":
      return "◌";
    case "LOW":
      return "◡";
    case "STRESSED":
      return "⚡";
    default:
      return "•";
  }
}

function ExpenseTab({
  meta,
  options,
  state,
  setState,
  colors,
  onAddAccount,
}: {
  meta: PersonalQuickAddMetadata;
  options: PersonalQuickAddOptionsResponse;
  state: FormState;
  setState: (patch: Partial<FormState>) => void;
  colors: ReturnType<typeof usePersonalDomainTokens>["colors"];
  onAddAccount: () => void;
}) {
  const bootstrap = getBootstrap();
  const currencies = (options.currencies ?? []) as CurrencyReference[];
  const defaultCurrency =
    options.default_currency_code ?? bootstrap?.preferences.default_currency_code ?? "INR";
  const locale = bootstrap?.preferences.locale ?? "en-IN";
  const expenseCategories = resolveExpenseCategories(options as unknown as Record<string, unknown>);
  const entryTypes = filterMoneyEntryTypes(
    meta.expense_entry_types?.length
      ? optionsFromFieldOptions(meta.expense_entry_types)
      : [],
  );
  const selectedAccount = options.accounts?.find((a) => a.account_id === state.accountId);
  const [showWhenPicker, setShowWhenPicker] = useState(false);

  const whenLabel = useMemo(() => {
    const today = todayISODate();
    const yesterday = (() => {
      const d = new Date();
      d.setDate(d.getDate() - 1);
      return d.toISOString().slice(0, 10);
    })();
    if (state.occurredDate === today) {
      const [h, m] = state.occurredTime.split(":").map(Number);
      const ampm = h >= 12 ? "PM" : "AM";
      const hr = ((h + 11) % 12) + 1;
      return `Today, ${hr}:${String(m).padStart(2, "0")} ${ampm}`;
    }
    if (state.occurredDate === yesterday) return "Yesterday";
    return `${state.occurredDate} ${state.occurredTime}`;
  }, [state.occurredDate, state.occurredTime]);

  return (
    <div className="space-y-6">
      <ChipSelect
        label="Entry type"
        options={entryTypes}
        value={state.transactionType}
        onChange={(v) => setState({ transactionType: v })}
      />

      <CompactTextField
        label="Title"
        value={state.expenseTitle}
        onChange={(v) => setState({ expenseTitle: v })}
        placeholder="Coffee, groceries, rent…"
      />

      <MoneyInput
        label="Amount"
        currencies={currencies}
        defaultCurrencyCode={defaultCurrency}
        locale={locale}
        value={{ amount_minor: state.amountMinor, currency_code: state.currencyCode }}
        onChange={(v) => setState({ amountMinor: v.amount_minor, currencyCode: v.currency_code })}
      />

      <div className="space-y-2">
        <div className="flex items-center justify-between gap-2">
          <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>
            {accountLabelForEntryType(state.transactionType)}
          </label>
          <button
            type="button"
            onClick={onAddAccount}
            className="text-xs font-medium"
            style={{ color: colors.brandPrimary }}
          >
            Add account ›
          </button>
        </div>
        {options.accounts?.length ? (
          <select
            value={state.accountId}
            onChange={(e) => setState({ accountId: e.target.value })}
            aria-label={accountLabelForEntryType(state.transactionType)}
            className="w-full rounded-xl border px-3 py-3"
            style={{
              borderColor: colors.border,
              background: colors.surfaceContainerLowest ?? "#0e0d16",
              color: colors.textPrimary,
            }}
          >
            {options.accounts.map((a) => (
              <option key={a.account_id} value={a.account_id}>
                {a.account_name}
                {a.account_type_label ? ` · ${a.account_type_label}` : ""}
              </option>
            ))}
          </select>
        ) : (
          <button
            type="button"
            onClick={onAddAccount}
            className="flex w-full items-center justify-between rounded-xl px-3 py-3 text-left text-sm"
            style={{ background: colors.surfaceContainerLowest ?? "#0e0d16", color: colors.textPrimary }}
          >
            <span>Add an account before recording this entry.</span>
            <span style={{ color: colors.brandPrimary }}>›</span>
          </button>
        )}
        {selectedAccount?.currency_code ? (
          <p className="text-xs" style={{ color: colors.textSecondary }}>
            {selectedAccount.currency_code}
          </p>
        ) : null}
      </div>

      {expenseCategories.length > 0 ? (
        <ReferenceCategoryChips
          label="Category"
          items={expenseCategories}
          value={state.categoryCode}
          onChange={(v) => setState({ categoryCode: v, subcategoryCode: "" })}
        />
      ) : null}

      {(() => {
        const selected = expenseCategories.find((c) => c.code === state.categoryCode);
        const children = (selected?.children ?? []).filter((c) => c.is_active !== false);
        if (!children.length) return null;
        return (
          <ReferenceCategoryChips
            label="Subcategory"
            items={children}
            value={state.subcategoryCode}
            onChange={(v) => setState({ subcategoryCode: v })}
          />
        );
      })()}

      {meta.pressure_impact_chips?.length ? (
        <ChipSelect
          label="Financial impact"
          options={normalizeChipOptions(meta.pressure_impact_chips)}
          value={state.pressureImpact}
          onChange={(v) => setState({ pressureImpact: v })}
        />
      ) : null}

      <div className="space-y-2">
        <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>When</label>
        <div className="flex items-center justify-between gap-3">
          <p style={{ ...personalTypography.bodyMd, color: colors.textPrimary }}>{whenLabel}</p>
          <button
            type="button"
            onClick={() => setShowWhenPicker((v) => !v)}
            className="text-xs font-semibold"
            style={{ color: colors.brandPrimary }}
          >
            Change
          </button>
        </div>
        {showWhenPicker ? (
          <div className="space-y-3">
            <div className="flex flex-wrap gap-2">
              {[
                {
                  label: "Now",
                  apply: () => setState({ occurredDate: todayISODate(), occurredTime: nowISOTime() }),
                },
                {
                  label: "Today",
                  apply: () => setState({ occurredDate: todayISODate() }),
                },
                {
                  label: "Yesterday",
                  apply: () => {
                    const d = new Date();
                    d.setDate(d.getDate() - 1);
                    setState({ occurredDate: d.toISOString().slice(0, 10) });
                  },
                },
              ].map((q) => (
                <button
                  key={q.label}
                  type="button"
                  onClick={q.apply}
                  className="min-h-10 rounded-lg px-3 py-2 text-xs font-medium"
                  style={{ border: `1px solid ${colors.border}`, color: colors.textSecondary }}
                >
                  {q.label}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-3">
              <input
                type="date"
                value={state.occurredDate}
                onChange={(e) => setState({ occurredDate: e.target.value })}
                className="w-full rounded-xl border px-3 py-3"
                style={{
                  borderColor: colors.border,
                  background: colors.surfaceContainerLowest ?? "#0e0d16",
                  color: colors.textPrimary,
                }}
              />
              <input
                type="time"
                value={state.occurredTime}
                onChange={(e) => setState({ occurredTime: e.target.value })}
                className="w-full rounded-xl border px-3 py-3"
                style={{
                  borderColor: colors.border,
                  background: colors.surfaceContainerLowest ?? "#0e0d16",
                  color: colors.textPrimary,
                }}
              />
            </div>
          </div>
        ) : null}
      </div>

      <div className="space-y-2">
        <button
          type="button"
          onClick={() => setState({ showMoreDetails: !state.showMoreDetails })}
          className="text-xs font-semibold"
          style={{ color: colors.brandPrimary }}
          aria-expanded={state.showMoreDetails}
        >
          {state.showMoreDetails ? "Hide details" : "More details"}
        </button>
        {state.showMoreDetails ? (
          <CompactTextField
            label="Notes — optional"
            value={state.expenseNotes}
            onChange={(v) => setState({ expenseNotes: v })}
            placeholder="Merchant, context, receipt note…"
            multiline
          />
        ) : null}
      </div>
    </div>
  );
}

function CommitmentTab({
  meta,
  state,
  setState,
  colors,
}: {
  meta: PersonalQuickAddMetadata;
  state: FormState;
  setState: (patch: Partial<FormState>) => void;
  colors: ReturnType<typeof usePersonalDomainTokens>["colors"];
}) {
  const intensityOptions = [
    { value: "LIGHT", label: "Light" },
    { value: "MODERATE", label: "Moderate" },
    { value: "HEAVY", label: "Heavy" },
  ];

  return (
    <div className="space-y-6">
      <CompactTextField
        label="What has your attention?"
        value={state.commitmentName}
        onChange={(v) => setState({ commitmentName: v })}
        placeholder="Finish client proposal"
      />
      {meta.attention_focus_areas?.length ? (
        <ChipSelect
          label="Category — optional"
          options={normalizeChipOptions(meta.attention_focus_areas)}
          value={state.focusArea}
          onChange={(v) => setState({ focusArea: v })}
        />
      ) : null}
      <SegmentedControl
        label="Attention load"
        hint="How demanding is it?"
        options={intensityOptions}
        value={state.intensity}
        onChange={(v) => setState({ intensity: v })}
      />
      {meta.commitment_status_options?.length ? (
        <ChipSelect
          label="Status"
          options={optionsFromFieldOptions(meta.commitment_status_options)}
          value={state.commitmentStatus}
          onChange={(v) => setState({ commitmentStatus: v })}
        />
      ) : null}

      {!state.showExpectedAmount ? (
        <button
          type="button"
          onClick={() => setState({ showExpectedAmount: true })}
          className="text-xs font-semibold"
          style={{ color: colors.brandPrimary }}
        >
          + Add expected amount
        </button>
      ) : (
        <div className="space-y-2">
          <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>
            Expected amount (₹)
          </label>
          <input
            type="number"
            inputMode="decimal"
            min={0}
            value={state.expectedAmountMinor > 0 ? state.expectedAmountMinor / 100 : ""}
            onChange={(e) => {
              const major = Number(e.target.value);
              setState({
                expectedAmountMinor: Number.isFinite(major) ? Math.round(major * 100) : 0,
              });
            }}
            placeholder="0.00"
            className="w-full rounded-xl border px-3 py-3"
            style={{
              borderColor: colors.border,
              background: colors.surfaceContainerLowest ?? "#0e0d16",
              color: colors.textPrimary,
            }}
          />
        </div>
      )}

      {!state.showCommitmentNotes ? (
        <button
          type="button"
          onClick={() => setState({ showCommitmentNotes: true })}
          className="text-xs font-semibold"
          style={{ color: colors.brandPrimary }}
        >
          Add context — optional
        </button>
      ) : (
        <CompactTextField
          label="Add context — optional"
          value={state.commitmentNotes}
          onChange={(v) => setState({ commitmentNotes: v })}
          placeholder="Anything to remember later"
          multiline
        />
      )}

      <p className="text-xs" style={{ color: colors.textSecondary, opacity: 0.8 }}>
        Add a name or category to make this easier to recognise later.
      </p>
    </div>
  );
}

function RecoveryTab({
  meta,
  state,
  setState,
  colors,
}: {
  meta: PersonalQuickAddMetadata;
  state: FormState;
  setState: (patch: Partial<FormState>) => void;
  colors: ReturnType<typeof usePersonalDomainTokens>["colors"];
}) {
  const durationOptions = meta.recovery_duration_options?.length
    ? optionsFromFieldOptions(meta.recovery_duration_options)
    : [
        { value: "15", label: "15 min" },
        { value: "30", label: "30 min" },
        { value: "60", label: "1 hour" },
        { value: "120", label: "2+ hours" },
      ];
  const levelOptions = (meta.energy_impact_options?.length
    ? normalizeChipOptions(meta.energy_impact_options)
    : [
        { value: "LOW", label: "Low" },
        { value: "MODERATE", label: "Moderate" },
        { value: "HIGH", label: "High" },
      ]
  ).slice(0, 3);

  return (
    <div className="space-y-6">
      {meta.recovery_types?.length ? (
        <ChipSelect
          label="What helped you recover?"
          options={optionsFromFieldOptions(meta.recovery_types)}
          value={state.recoveryType}
          onChange={(v) => setState({ recoveryType: v })}
        />
      ) : null}
      <SegmentedControl
        label="How restorative was it?"
        options={levelOptions}
        value={state.recoveryEnergyImpact}
        onChange={(v) => setState({ recoveryEnergyImpact: v })}
      />
      <ChipSelect
        label="Duration"
        options={durationOptions}
        value={state.recoveryDuration}
        onChange={(v) => setState({ recoveryDuration: v })}
      />
      {!state.showRecoveryNotes ? (
        <button
          type="button"
          onClick={() => setState({ showRecoveryNotes: true })}
          className="text-xs font-semibold"
          style={{ color: colors.brandPrimary }}
        >
          Add note — optional
        </button>
      ) : (
        <CompactTextField
          label="Notes — optional"
          value={state.recoveryNotes}
          onChange={(v) => setState({ recoveryNotes: v })}
          placeholder="What helped?"
          multiline
        />
      )}
    </div>
  );
}

function ReflectionTab({
  meta,
  state,
  setState,
  colors,
}: {
  meta: PersonalQuickAddMetadata;
  state: FormState;
  setState: (patch: Partial<FormState>) => void;
  colors: ReturnType<typeof usePersonalDomainTokens>["colors"];
}) {
  const moods = meta.mood_feeling_options?.length
    ? optionsFromFieldOptions(meta.mood_feeling_options)
    : [
        { value: "GREAT", label: "Great" },
        { value: "GOOD", label: "Good" },
        { value: "OKAY", label: "Okay" },
        { value: "LOW", label: "Low" },
        { value: "STRESSED", label: "Stressed" },
      ];

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>
          How do you feel?
        </label>
        <div className="grid grid-cols-3 gap-2 sm:grid-cols-5">
          {moods.map((m) => {
            const selected = state.feelingState === m.value;
            return (
              <button
                key={m.value}
                type="button"
                aria-pressed={selected}
                aria-label={m.label}
                onClick={() => setState({ feelingState: m.value })}
                className="flex min-h-[4.5rem] flex-col items-center justify-center gap-1 rounded-xl px-2 py-3 text-xs font-semibold"
                style={{
                  border: `1px solid ${selected ? colors.brandPrimary : colors.border}`,
                  background: selected ? "rgba(108, 78, 242, 0.18)" : "transparent",
                  color: selected ? colors.brandPrimary : colors.textSecondary,
                }}
              >
                <span aria-hidden className="text-lg">
                  {moodIcon(m.value)}
                </span>
                {m.label}
              </button>
            );
          })}
        </div>
      </div>

      {meta.reflection_tags?.length ? (
        <ChipSelect
          label="Anything else?"
          options={normalizeChipOptions(meta.reflection_tags)}
          value={state.reflectionTags}
          multi
          onChange={(v) => {
            const next = new Set(state.reflectionTags);
            if (next.has(v)) next.delete(v);
            else next.add(v);
            setState({ reflectionTags: Array.from(next) });
          }}
        />
      ) : null}

      {!state.showMoodNote ? (
        <button
          type="button"
          onClick={() => setState({ showMoodNote: true })}
          className="text-xs font-semibold"
          style={{ color: colors.brandPrimary }}
        >
          What shaped this mood?
        </button>
      ) : (
        <CompactTextField
          label="What shaped this mood?"
          value={state.reflectionNote}
          onChange={(v) => setState({ reflectionNote: v })}
          placeholder="A conversation, work, sleep, progress…"
          multiline
        />
      )}

      <p className="text-xs" style={{ color: colors.textSecondary, opacity: 0.8 }}>
        Recording it now helps Momentra understand your patterns.
      </p>
    </div>
  );
}

function RhythmTab({
  meta,
  state,
  setState,
}: {
  meta: PersonalQuickAddMetadata;
  state: FormState;
  setState: (patch: Partial<FormState>) => void;
}) {
  const { colors } = usePersonalDomainTokens();
  const rhythmOptions = meta.rhythm_actions?.length
    ? optionsFromFieldOptions(meta.rhythm_actions)
    : [];
  const modes = (meta.runtime_modes?.length ? meta.runtime_modes : ["FLOW_MODE", "RECOVERY_MODE", "BUILD_MODE"]).map(
    (m) => ({ value: m, label: runtimeModeLabel(m) }),
  );
  const dimensions =
    meta.runtime_signal_dimensions?.length
      ? meta.runtime_signal_dimensions
      : [
          { key: "pressure", label: "Pressure", description: "Load and stress" },
          { key: "recovery", label: "Recovery", description: "Rest and recharge" },
          { key: "focus", label: "Focus", description: "Attention quality" },
          { key: "momentum", label: "Momentum", description: "Forward motion" },
        ];
  const directions: Array<{ value: RuntimeSignalDirection; label: string }> = [
    { value: "DOWN", label: "Decrease" },
    { value: "STABLE", label: "Keep" },
    { value: "UP", label: "Increase" },
  ];

  return (
    <div className="space-y-6">
      {rhythmOptions.length > 0 ? (
        <ChipSelect
          label="Quick intention"
          options={rhythmOptions}
          value={Array.from(state.rhythmActions)}
          multi
          onChange={(v) => {
            const next = new Set(state.rhythmActions);
            if (next.has(v)) next.delete(v);
            else next.add(v);
            const preset = INTENTION_SIGNAL_PRESETS[v];
            const signals = { ...state.runtimeSignals };
            if (preset && next.has(v)) {
              Object.assign(signals, preset);
            }
            setState({ rhythmActions: next, runtimeSignals: signals });
          }}
        />
      ) : null}

      <div className="space-y-3">
        <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>
          Runtime signals
        </label>
        {dimensions.map((dim) => {
          const key = dim.key as RuntimeSignalKey;
          const selected = state.runtimeSignals[key] ?? "STABLE";
          return (
            <div key={dim.key} className="space-y-2">
              <div>
                <p style={{ ...personalTypography.bodyMd, color: colors.textPrimary }}>{dim.label}</p>
                <p className="text-xs" style={{ color: colors.textSecondary }}>
                  {dim.description}
                </p>
              </div>
              <div
                className="flex gap-1 rounded-full p-1"
                role="radiogroup"
                aria-label={`${dim.label} adjustment`}
                style={{ background: colors.surfaceContainer ?? "rgba(255,255,255,0.04)" }}
              >
                {directions.map((d) => {
                  const active = selected === d.value;
                  return (
                    <button
                      key={d.value}
                      type="button"
                      role="radio"
                      aria-checked={active}
                      aria-label={`${dim.label}: ${signalDirectionLabel(d.value)}`}
                      onClick={() =>
                        setState({
                          runtimeSignals: { ...state.runtimeSignals, [key]: d.value },
                        })
                      }
                      className="min-h-11 flex-1 rounded-full px-2 py-2 text-xs font-semibold"
                      style={{
                        background: active ? colors.brandPrimary : "transparent",
                        color: active ? colors.brandOnPrimary ?? "#0e0d16" : colors.textSecondary,
                      }}
                    >
                      {d.label}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="space-y-2">
        <ChipSelect
          label="Runtime mode"
          options={modes}
          value={state.runtimeMode}
          onChange={(v) => setState({ runtimeMode: v })}
        />
        {runtimeModeHint(state.runtimeMode) ? (
          <p className="text-xs" style={{ color: colors.textSecondary }}>
            {runtimeModeHint(state.runtimeMode)}
          </p>
        ) : null}
      </div>
    </div>
  );
}

export function LifeOperationsQuickAddSheet({
  initialEventType,
  defaultMomentId,
  open = true,
  onClose,
  onSuccess,
  onBeginSetup,
}: LifeOperationsQuickAddSheetProps) {
  const { colors } = usePersonalDomainTokens();
  const reducedMotion = useReducedMotion();
  const {
    options,
    loading,
    error: loadError,
    reload: reloadOptions,
  } = useQuickAddOptions({ momentId: defaultMomentId, enabled: open });

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [pendingDraft, setPendingDraft] = useState(false);
  const [selectedTab, setSelectedTab] = useState("EXPENSE");
  const [form, setForm] = useState<FormState>(defaultFormState);
  const [tabDrafts, setTabDrafts] = useState<TabDraftMap>({});
  const [showAddAccount, setShowAddAccount] = useState(false);
  const [successPulse, setSuccessPulse] = useState(false);
  const [toast, setToast] = useState<{ message: string; tone: "success" | "error" } | null>(null);
  const [confirmClose, setConfirmClose] = useState(false);
  const [selectorTouched, setSelectorTouched] = useState(false);
  const submitLatch = useRef(false);
  const openedTracked = useRef(false);

  const patchForm = (patch: Partial<FormState>) => setForm((prev) => ({ ...prev, ...patch }));

  useEffect(() => {
    if (!open || openedTracked.current) return;
    openedTracked.current = true;
    try {
      void MomentraAnalytics.logCustomEvent("intelligence_os_opened", {
        cached: options ? "true" : "false",
      });
    } catch {
      /* analytics best-effort */
    }
  }, [open, options]);

  useEffect(() => {
    if (!options) return;
    const initial = initialEventType?.toUpperCase();
    if (initial && LIFE_OPS_EVENT_TYPES.has(initial)) {
      setSelectedTab(initial);
    } else if (options.tabs?.[0]?.event_type) {
      setSelectedTab(options.tabs[0].event_type);
    }
    const primary =
      options.accounts?.find((a: PersonalQuickAddAccount) => a.is_primary)?.account_id ??
      options.accounts?.[0]?.account_id ??
      "";
    const firstCategory =
      (options.expense_categories?.[0] as ReferenceItem | undefined)?.code ?? "";
    setForm((prev) => ({
      ...prev,
      accountId: prev.accountId || primary,
      currencyCode: options.default_currency_code ?? prev.currencyCode,
      categoryCode: prev.categoryCode || firstCategory,
    }));
  }, [options, initialEventType]);

  useEffect(() => {
    const accounts = options?.accounts;
    if (!accounts?.length) return;
    setForm((prev) => {
      if (prev.accountId && accounts.some((a) => a.account_id === prev.accountId)) return prev;
      const primary =
        accounts.find((a) => a.is_primary)?.account_id ?? accounts[0]?.account_id ?? "";
      return { ...prev, accountId: primary };
    });
  }, [options?.accounts]);

  const selectTab = (next: string) => {
    if (next === selectedTab) return;
    setSelectorTouched(true);
    setTabDrafts((prev) => ({ ...prev, [selectedTab]: form }));
    const restored = tabDrafts[next];
    setSelectedTab(next);
    if (restored) {
      setForm(restored);
    } else {
      const base = defaultFormState();
      if (options?.accounts?.length) {
        base.accountId =
          options.accounts.find((a) => a.is_primary)?.account_id ??
          options.accounts[0]?.account_id ??
          "";
      }
      if (options?.default_currency_code) base.currencyCode = options.default_currency_code;
      setForm(base);
    }
    try {
      void MomentraAnalytics.logCustomEvent("intelligence_os_tab_selected", { tab: next });
    } catch {
      /* best-effort */
    }
  };

  const moment = useMemo(() => {
    if (!options?.moments.length) return null;
    if (defaultMomentId) {
      return options.moments.find((m) => m.moment_id === defaultMomentId) ?? options.moments[0];
    }
    return (
      options.moments.find((m) => m.moment_type_code === "LIFE_OPERATIONS") ?? options.moments[0]
    );
  }, [defaultMomentId, options]);

  const tabs: PersonalQuickAddTab[] = useMemo(() => {
    if (options?.tabs?.length) return options.tabs;
    return (LIFE_OPS_BUNDLE?.actions ?? []).map((action) => ({
      event_type: action.action_id,
      label: action.label,
      tab_code: action.tab_code ?? action.action_id,
      description: action.label,
      hero_title: action.label,
      hero_subtitle: action.impact_preview.summary_template,
      cta_label: action.cta_label,
    }));
  }, [options?.tabs]);

  const activeTab = tabs.find((t) => t.event_type === selectedTab);
  const meta = options?.metadata ?? {};
  const submitEnabled = Boolean(moment && canSubmitLifeOpsTab(selectedTab, form));
  const dirty =
    isLifeOpsTabDirty(selectedTab, form) ||
    Object.entries(tabDrafts).some(([k, v]) => v && isLifeOpsTabDirty(k, v));

  const statusLabel = useMemo(() => {
    if (selectedTab === "EXPENSE" || selectedTab === "COMMITMENT") {
      const n = options?.entries_today_count ?? 0;
      return `${n} Entries Today`;
    }
    return "Runtime learning";
  }, [options?.entries_today_count, selectedTab]);

  const ctaLabel = tabSaveLabel(selectedTab, form.transactionType);
  const insight = compactInsightBody(activeTab?.insight_title, activeTab?.insight_body);

  const requestClose = useCallback(() => {
    if (dirty && !successPulse) {
      setConfirmClose(true);
      return;
    }
    onClose();
  }, [dirty, onClose, successPulse]);

  const submitQuickAddEntry = useCallback(
    async (draftClientRequestId?: string) => {
      if (!moment || !submitEnabled || submitLatch.current) return;
      submitLatch.current = true;
      setSubmitting(true);
      setSubmitError(null);
      const title =
        selectedTab === "EXPENSE"
          ? form.expenseTitle.trim() || "Money entry"
          : activeTab?.label ?? selectedTab.replace(/_/g, " ");
      const payload = buildLifeOpsQuickAddPayload(selectedTab, moment.moment_id, title, form);
      const clientRequestId = draftClientRequestId ?? createClientRequestId();
      const currentPulse = getPersonalPulseCache("LIFE_OPERATIONS");
      let optimisticApplied = false;
      if (isOptimisticSafeEventType(selectedTab)) {
        const patch = buildLifeOpsOptimisticPatch(
          selectedTab,
          form,
          title,
          moment.moment_id,
          clientRequestId,
          currentPulse,
        );
        if (patch) {
          applyOptimisticPatch("LIFE_OPERATIONS", clientRequestId, currentPulse, patch);
          optimisticApplied = true;
        }
      }
      try {
        void MomentraAnalytics.logCustomEvent("intelligence_os_save_started", { tab: selectedTab });
      } catch {
        /* best-effort */
      }
      startQuickAddSaveSpan();
      try {
        await PersonalRepository.submitQuickAdd(payload, {
          clientRequestId,
          momentId: moment.moment_id,
          tab: selectedTab,
          form: serializeQuickAddForm(form),
          momentTypeCode: "LIFE_OPERATIONS",
        });
        endQuickAddSaveSpan();
        setPendingDraft(false);
        setSuccessPulse(true);
        const msg = tabSuccessMessage(selectedTab, form.transactionType);
        setToast({ message: msg, tone: "success" });
        try {
          void MomentraAnalytics.logCustomEvent("intelligence_os_save_succeeded", { tab: selectedTab });
        } catch {
          /* best-effort */
        }
        window.setTimeout(() => {
          setSuccessPulse(false);
          onSuccess?.();
          onClose();
          submitLatch.current = false;
        }, reducedMotion ? 0 : MOTION_DURATION_MS.slow);
      } catch (err) {
        endQuickAddSaveSpan();
        submitLatch.current = false;
        if (optimisticApplied) rollbackPatch(clientRequestId);
        const networkDraft = hasQuickAddDraft(moment.moment_id, selectedTab);
        setPendingDraft(networkDraft);
        let message = "Couldn't save. Try again.";
        if (typeof navigator !== "undefined" && !navigator.onLine) {
          message = "You're offline. Your entry wasn't saved.";
        } else if (err instanceof ApiError) {
          message = err.userMessage;
        } else if (err instanceof Error) {
          message =
            err.message === "Failed to fetch"
              ? "You're offline. Check your connection and try again."
              : err.message;
        }
        setSubmitError(message);
        setToast({ message, tone: "error" });
        setSubmitting(false);
        try {
          void MomentraAnalytics.logCustomEvent("intelligence_os_save_failed", { tab: selectedTab });
        } catch {
          /* best-effort */
        }
      }
    },
    [activeTab?.label, form, moment, onClose, onSuccess, reducedMotion, selectedTab, submitEnabled],
  );

  useEffect(() => {
    if (!moment) return;
    const draft = loadQuickAddDraft(moment.moment_id, selectedTab);
    if (!draft) {
      setPendingDraft(false);
      return;
    }
    setPendingDraft(true);
    setForm((prev) => deserializeQuickAddForm(draft.form, prev));
    setSubmitError("You have an unsaved entry. Tap Retry to submit.");
  }, [moment, selectedTab]);

  useEffect(() => {
    if (!moment || !submitEnabled) return;
    const draft = loadQuickAddDraft(moment.moment_id, selectedTab);
    if (!draft) return;
      const title =
        selectedTab === "EXPENSE"
          ? form.expenseTitle.trim() || "Money entry"
          : (activeTab?.label ?? selectedTab.replace(/_/g, " "));
      const payload = buildLifeOpsQuickAddPayload(selectedTab, moment.moment_id, title, form);
    saveQuickAddDraft({
      momentId: moment.moment_id,
      tab: selectedTab,
      form: serializeQuickAddForm(form),
      payload,
      clientRequestId: draft.clientRequestId,
      savedAt: new Date().toISOString(),
    });
  }, [activeTab?.label, form, moment, selectedTab, submitEnabled]);

  useEffect(() => {
    if (!moment || !pendingDraft) return undefined;
    return subscribeOnlineRetry(() => {
      const draft = loadQuickAddDraft(moment.moment_id, selectedTab);
      if (!draft) return;
      void submitQuickAddEntry(draft.clientRequestId);
    });
  }, [moment, pendingDraft, selectedTab, submitQuickAddEntry]);

  function renderTabContent() {
    if (!options) return null;
    switch (selectedTab) {
      case "EXPENSE":
        return (
          <ExpenseTab
            meta={meta}
            options={options}
            state={form}
            setState={patchForm}
            colors={colors}
            onAddAccount={() => setShowAddAccount(true)}
          />
        );
      case "COMMITMENT":
        return (
          <CommitmentTab meta={meta} state={form} setState={patchForm} colors={colors} />
        );
      case "REFLECTION":
        return (
          <ReflectionTab meta={meta} state={form} setState={patchForm} colors={colors} />
        );
      case "RECOVERY":
        return <RecoveryTab meta={meta} state={form} setState={patchForm} colors={colors} />;
      case "RHYTHM":
        return <RhythmTab meta={meta} state={form} setState={patchForm} />;
      default:
        return null;
    }
  }

  if (!open) return null;

  return (
    <>
      <BottomSheet
        open={open}
        onClose={requestClose}
        panelClassName="flex flex-col border"
        ariaLabelledBy="life-ops-quick-add-title"
      >
        <div
          className="relative flex max-h-[92dvh] w-full flex-col"
          style={{ borderColor: colors.border, background: colors.surface }}
        >
          <div className="shrink-0 px-5 pb-2 pt-4" style={{ borderColor: colors.border }}>
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-3">
                  <h2
                    id="life-ops-quick-add-title"
                    style={{ ...personalTypography.heroTitle, color: colors.brandPrimary, fontSize: "1.35rem" }}
                  >
                    Intelligence OS
                  </h2>
                  <span
                    className="inline-flex shrink-0 items-center gap-2 rounded-full px-3 py-1 text-[10px] font-semibold uppercase tracking-wide"
                    style={{
                      background: "rgba(108, 78, 242, 0.1)",
                      border: "1px solid rgba(108, 78, 242, 0.2)",
                      color: colors.textSecondary,
                    }}
                  >
                    <span
                      className="inline-block h-1.5 w-1.5 rounded-full"
                      style={{ background: colors.brandPrimary }}
                      aria-hidden
                    />
                    {statusLabel}
                  </span>
                </div>
                <p className="mt-1" style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
                  {LO_SHEET_SUPPORTING}
                </p>
              </div>
              <button
                type="button"
                onClick={requestClose}
                aria-label="Close Intelligence OS"
                className="min-h-11 min-w-11 rounded-full text-lg"
                style={{ color: colors.textSecondary }}
              >
                ✕
              </button>
            </div>
            <div
              className="mt-3 flex gap-2 overflow-x-auto pb-1"
              role="tablist"
              aria-label="Intelligence OS entry type"
            >
              {tabs.map((tab) => {
                const active = tab.event_type === selectedTab;
                const blurb = loSelectorBlurb(tab.event_type) || tab.description || tab.hero_subtitle || "";
                return (
                  <button
                    key={tab.event_type}
                    type="button"
                    role="tab"
                    aria-selected={active}
                    aria-label={`${tab.label}. ${blurb}.${active ? " Selected." : ""}`}
                    onClick={() => selectTab(tab.event_type)}
                    className="min-w-[9.5rem] shrink-0 rounded-2xl border px-3 py-3 text-left"
                    style={{
                      borderColor: active ? colors.brandPrimary : colors.border,
                      background: active ? `${colors.brandPrimary}18` : "transparent",
                      minHeight: 48,
                    }}
                  >
                    <span
                      className="block text-sm font-semibold"
                      style={{ color: active ? colors.brandPrimary : colors.textPrimary }}
                    >
                      {tab.label}
                    </span>
                    <span className="mt-0.5 block text-[11px] leading-snug" style={{ color: colors.textSecondary }}>
                      {blurb}
                    </span>
                  </button>
                );
              })}
            </div>
            {!selectorTouched ? (
              <p className="mt-2 text-xs" style={{ color: colors.textSecondary }}>
                {LO_SELECTOR_HELPER}
              </p>
            ) : null}
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4 pb-28">
            {loading && !options ? (
              <SkeletonQuickAddSheet />
            ) : loadError && !options ? (
              <div className="space-y-2">
                <p style={{ color: colors.error }}>{loadError}</p>
                <button type="button" onClick={() => void reloadOptions()} className="text-sm underline">
                  Retry
                </button>
              </div>
            ) : !moment ? (
              <div className="space-y-3">
                <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
                  Activate a Life Operations moment to use Quick Add.
                </p>
                {onBeginSetup ? (
                  <button
                    type="button"
                    onClick={onBeginSetup}
                    className="rounded-xl px-4 py-2 text-sm font-semibold"
                    style={{ background: colors.brandPrimary, color: colors.onPrimary }}
                  >
                    Set up Life Operations
                  </button>
                ) : null}
              </div>
            ) : (
              <div className="space-y-5">
                {activeTab ? (
                  <div className="space-y-1">
                    <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
                      {activeTab.hero_title ?? activeTab.label}
                    </h3>
                    <p className="text-sm" style={{ color: colors.textSecondary }}>
                      {activeTab.hero_subtitle ?? activeTab.description}
                    </p>
                  </div>
                ) : null}

                <div>{renderTabContent()}</div>

                {insight ? (
                  <p className="text-xs" style={{ color: colors.textSecondary, opacity: 0.85 }}>
                    {insight}
                  </p>
                ) : null}

                {submitError ? (
                  <div className="space-y-2">
                    <p style={{ color: colors.error }}>{submitError}</p>
                    {pendingDraft ? (
                      <button
                        type="button"
                        disabled={submitting || !submitEnabled}
                        onClick={() => void submitQuickAddEntry(loadQuickAddDraft(moment.moment_id, selectedTab)?.clientRequestId)}
                        className="w-full rounded-xl border py-2 text-sm font-semibold"
                        style={{ borderColor: colors.brandPrimary, color: colors.brandPrimary }}
                      >
                        {submitting ? "Retrying…" : "Try again"}
                      </button>
                    ) : null}
                  </div>
                ) : null}
              </div>
            )}
          </div>

          {moment ? (
            <div
              className="absolute inset-x-0 bottom-0 border-t px-5 py-3"
              style={{
                borderColor: colors.border,
                background: colors.surface,
                paddingBottom: "max(0.75rem, env(safe-area-inset-bottom))",
              }}
            >
              <motion.button
                type="button"
                disabled={!submitEnabled || submitting}
                onClick={() => void submitQuickAddEntry()}
                aria-label={ctaLabel}
                className="w-full rounded-2xl py-3 font-semibold"
                style={{
                  background: colors.brandPrimaryContainer ?? colors.brandPrimary,
                  color: colors.brandOnPrimary,
                  opacity: !submitEnabled || submitting ? 0.55 : 1,
                }}
                variants={successPulseVariants(reducedMotion)}
                animate={successPulse ? "pulse" : "idle"}
              >
                {submitting
                  ? selectedTab === "RHYTHM"
                    ? "Updating…"
                    : "Saving…"
                  : successPulse
                    ? "Saved!"
                    : ctaLabel}
              </motion.button>
            </div>
          ) : null}
        </div>
      </BottomSheet>

      {confirmClose ? (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/50 px-6">
          <div
            className="w-full max-w-sm space-y-4 rounded-2xl p-5"
            style={{ background: colors.surface, border: `1px solid ${colors.border}` }}
            role="alertdialog"
            aria-labelledby="discard-title"
          >
            <h3 id="discard-title" style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
              Discard changes?
            </h3>
            <p className="text-sm" style={{ color: colors.textSecondary }}>
              You have unsaved entries in this sheet.
            </p>
            <div className="flex gap-3">
              <button
                type="button"
                className="flex-1 rounded-xl border py-2 text-sm"
                style={{ borderColor: colors.border, color: colors.textSecondary }}
                onClick={() => setConfirmClose(false)}
              >
                Keep editing
              </button>
              <button
                type="button"
                className="flex-1 rounded-xl py-2 text-sm font-semibold"
                style={{ background: colors.brandPrimary, color: colors.brandOnPrimary }}
                onClick={() => {
                  setConfirmClose(false);
                  try {
                    void MomentraAnalytics.logCustomEvent("intelligence_os_discard_confirmed", {
                      tab: selectedTab,
                    });
                  } catch {
                    /* best-effort */
                  }
                  onClose();
                }}
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      ) : null}

      <AppToast
        open={Boolean(toast)}
        message={toast?.message ?? ""}
        tone={toast?.tone ?? "success"}
        onDismiss={() => setToast(null)}
      />

      {showAddAccount ? (
        <LifeOpsAddAccountSheet
          accountTypes={(options?.account_types ?? []) as ReferenceItem[]}
          currencies={(options?.currencies ?? []) as CurrencyReference[]}
          defaultCurrencyCode={options?.default_currency_code}
          onClose={() => setShowAddAccount(false)}
          onCreated={async (account) => {
            setForm((prev) => ({ ...prev, accountId: account.account_id }));
            await reloadOptions();
            setForm((prev) => ({ ...prev, accountId: account.account_id }));
          }}
        />
      ) : null}
    </>
  );
}

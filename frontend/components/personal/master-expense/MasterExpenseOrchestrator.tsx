"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  Info,
  Lock,
  Sparkles,
  Wallet,
} from "lucide-react";
import { resolveExpenseCategoryIcon } from "@/lib/personal/life_operations/expenseCategoryIcons";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { MasterExpenseSkeleton } from "@/components/personal/master_expense/MasterExpenseSkeleton";
import { MoneyInput } from "@/components/shared/MoneyInput";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import {
  PersonalRepository,
  invalidateAfterMasterExpense,
} from "@/repositories/PersonalRepository";
import type { PersonalMasterExpenseOptionsResponse, PersonalQuickAddFieldOption } from "@/lib/api/client";
import { buildMasterExpensePayload } from "@/lib/master_expense/payloadBuilder";
import {
  MASTER_EXPENSE_CONTEXT_REASONS,
  MASTER_EXPENSE_FEELINGS,
  MASTER_EXPENSE_RELATIONSHIP_IMPACTS,
  MASTER_EXPENSE_SCALE_LEVELS,
  MASTER_EXPENSE_SHARED_WITH,
} from "@/lib/master_expense/defaultOptions";
import {
  MasterExpenseChip,
  MasterExpenseFieldLabel,
  MasterExpenseImpactTile,
  SegmentedScaleControl,
} from "@/lib/master_expense/masterExpenseUi";
import {
  MASTER_EXPENSE_DESCRIPTION_PLACEHOLDERS,
  MASTER_EXPENSE_VISIBLE_CHIP_LIMIT,
  canSaveMasterExpense,
  formatWhenLabel,
  isMasterExpenseFormDirty,
  resolveSubcategoryForCategory,
  visibleCategoryChips,
  whenPresetValue,
} from "@/lib/master_expense/formHelpers";
import { getReferenceData } from "@/lib/reference_data/referenceDataStore";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { MoneyValue } from "@/lib/reference_data/types";
import { createClientRequestId } from "@/lib/quick_add/draftStore";
import { defaultOccurredAt } from "@/lib/quick_add/dateTimeDefaults";

export type MasterExpenseOrchestratorProps = {
  onBack: () => void;
  onSuccess?: () => void;
};

const FEELING_EMOJI: Record<string, string> = {
  VERY_BAD: "😡",
  BAD: "😕",
  NEUTRAL: "😐",
  GOOD: "😊",
  GREAT: "😍",
};

type PickerKind = "category" | "subcategory" | "account" | "when" | null;

function ChipRow({
  label,
  options,
  value,
  onChange,
  multi = false,
}: {
  label: string;
  options: PersonalQuickAddFieldOption[];
  value: string | string[];
  onChange: (value: string) => void;
  multi?: boolean;
}) {
  const { colors } = usePersonalDomainTokens();
  const selected = multi ? new Set(Array.isArray(value) ? value : []) : value;

  return (
    <div className="space-y-2">
      {label ? (
        <p style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>{label}</p>
      ) : null}
      <div className="flex flex-wrap gap-2" role={multi ? "group" : "radiogroup"} aria-label={label || undefined}>
        {options.map((opt) => {
          const isSelected = multi
            ? (selected as Set<string>).has(opt.value)
            : selected === opt.value;
          return (
            <MasterExpenseChip
              key={opt.value}
              label={opt.label}
              selected={isSelected}
              onClick={() => onChange(opt.value)}
              colors={colors}
            />
          );
        })}
      </div>
    </div>
  );
}

function CompactSelectRow({
  label,
  value,
  onClick,
  icon,
}: {
  label: string;
  value: string;
  onClick: () => void;
  icon?: React.ReactNode;
}) {
  const { colors } = usePersonalDomainTokens();
  return (
    <div>
      <MasterExpenseFieldLabel label={label} labelColor={colors.textSecondary} />
      <button
        type="button"
        onClick={onClick}
        className="pressable flex min-h-12 w-full items-center gap-2.5 rounded-xl px-3.5 py-3 text-left"
        style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${colors.border}` }}
      >
        {icon}
        <span className="flex-1 text-sm font-medium" style={{ color: colors.textPrimary }}>
          {value}
        </span>
        <span className="text-sm font-semibold" style={{ color: colors.brandPrimary }}>
          Change
        </span>
      </button>
    </div>
  );
}

function PickerSheet({
  title,
  options,
  selected,
  onSelect,
  onClose,
  searchable = true,
}: {
  title: string;
  options: Array<{ id: string; label: string }>;
  selected: string;
  onSelect: (id: string) => void;
  onClose: () => void;
  searchable?: boolean;
}) {
  const tokens = useThemeTokens();
  const { colors } = usePersonalDomainTokens();
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => {
    if (!query.trim()) return options;
    const q = query.toLowerCase();
    return options.filter((o) => o.label.toLowerCase().includes(q) || o.id.toLowerCase().includes(q));
  }, [options, query]);

  return (
    <div
      className="fixed inset-0 z-[140] flex items-end justify-center bg-black/50"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onClick={onClose}
    >
      <div
        className="max-h-[70vh] w-full max-w-lg overflow-hidden rounded-t-2xl p-5"
        style={{ background: tokens.colors.surface }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-3 flex items-center justify-between">
          <h2 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>{title}</h2>
          <button type="button" onClick={onClose} className="text-sm font-semibold" style={{ color: colors.brandPrimary }}>
            Close
          </button>
        </div>
        {searchable && options.length > 8 ? (
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search"
            className="mb-3 w-full rounded-xl border bg-transparent px-3 py-2 text-sm outline-none"
            style={{ borderColor: colors.border, color: colors.textPrimary }}
          />
        ) : null}
        <div className="max-h-[50vh] space-y-2 overflow-y-auto">
          {filtered.map((opt) => {
            const isSelected = selected === opt.id;
            return (
              <button
                key={opt.id}
                type="button"
                onClick={() => {
                  onSelect(opt.id);
                  onClose();
                }}
                className="flex min-h-12 w-full items-center rounded-xl px-3.5 py-3 text-left text-sm"
                style={{
                  background: isSelected ? `${colors.brandPrimary}22` : "rgba(255,255,255,0.04)",
                  color: colors.textPrimary,
                }}
                aria-pressed={isSelected}
              >
                <span className="flex-1 font-medium">{opt.label}</span>
                {isSelected ? (
                  <span className="text-xs font-semibold" style={{ color: colors.brandPrimary }}>
                    Selected
                  </span>
                ) : null}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export function MasterExpenseOrchestrator({ onBack, onSuccess }: MasterExpenseOrchestratorProps) {
  const tokens = useThemeTokens();
  const { colors } = usePersonalDomainTokens();
  const referenceData = getReferenceData();
  const currencies = referenceData?.currencies ?? [];
  const titleRef = useRef<HTMLInputElement>(null);
  const savingRef = useRef(false);

  const [options, setOptions] = useState<PersonalMasterExpenseOptionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [moreDetailsOpen, setMoreDetailsOpen] = useState(false);
  const [picker, setPicker] = useState<PickerKind>(null);
  const [confirmClear, setConfirmClear] = useState(false);
  const [confirmCancel, setConfirmCancel] = useState(false);

  const [title, setTitle] = useState("");
  const [money, setMoney] = useState<MoneyValue>({ amount_minor: 0, currency_code: "INR" });
  const [accountId, setAccountId] = useState("");
  const [categoryCode, setCategoryCode] = useState("");
  const [subcategoryCode, setSubcategoryCode] = useState("");
  const [occurredAt, setOccurredAt] = useState(defaultOccurredAt);
  const [feeling, setFeeling] = useState("");
  const [meaningfulness, setMeaningfulness] = useState("");
  const [memorability, setMemorability] = useState("");
  const [sharedEnabled, setSharedEnabled] = useState(true);
  const [sharedWith, setSharedWith] = useState<string[]>([]);
  const [relationshipImpact, setRelationshipImpact] = useState<string[]>([]);
  const [contextReason, setContextReason] = useState("");
  const [notes, setNotes] = useState("");

  const descriptionPlaceholder = MASTER_EXPENSE_DESCRIPTION_PLACEHOLDERS[0];

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await PersonalRepository.getMasterExpenseOptions();
      setOptions(data);
      if (data.accounts[0]) setAccountId(data.accounts[0].account_id);
      // Do not auto-select category.
      const accountCurrency = data.accounts[0]?.currency_code;
      if (accountCurrency) {
        setMoney((prev) => ({ ...prev, currency_code: accountCurrency }));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load options.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const resolvedOptions = useMemo(() => {
    if (!options) return null;
    return {
      ...options,
      feelings: options.feelings?.length ? options.feelings : MASTER_EXPENSE_FEELINGS,
      scale_levels: options.scale_levels?.length ? options.scale_levels : MASTER_EXPENSE_SCALE_LEVELS,
      shared_with: options.shared_with?.length ? options.shared_with : MASTER_EXPENSE_SHARED_WITH,
      relationship_impacts: options.relationship_impacts?.length
        ? options.relationship_impacts
        : MASTER_EXPENSE_RELATIONSHIP_IMPACTS,
      context_reasons: options.context_reasons?.length
        ? options.context_reasons
        : MASTER_EXPENSE_CONTEXT_REASONS,
    };
  }, [options]);

  const fieldSurface = { background: "rgba(255,255,255,0.04)" } as const;

  const canSave = useMemo(
    () =>
      canSaveMasterExpense({
        lifeOperationsMomentId: resolvedOptions?.life_operations_moment_id,
        lifestyleMomentId: resolvedOptions?.lifestyle_moment_id,
        title,
        amountMinor: money.amount_minor,
        accountId,
        categoryCode,
      }),
    [resolvedOptions, title, money.amount_minor, accountId, categoryCode],
  );

  const dirty = useMemo(
    () =>
      isMasterExpenseFormDirty({
        title,
        amountMinor: money.amount_minor,
        subcategoryCode,
        feeling,
        meaningfulness,
        memorability,
        sharedWith,
        relationshipImpact,
        contextReason,
        notes,
      }),
    [
      title,
      money.amount_minor,
      subcategoryCode,
      feeling,
      meaningfulness,
      memorability,
      sharedWith,
      relationshipImpact,
      contextReason,
      notes,
    ],
  );

  const selectedCategory = resolvedOptions?.categories.find((c) => c.category_id === categoryCode);
  const subcategoryChildren = selectedCategory?.children ?? [];
  const selectedAccount = resolvedOptions?.accounts.find((a) => a.account_id === accountId);

  const impactPreview = useMemo(
    () => [
      {
        title: "Life Operations" as const,
        subtitle: "Will refresh Pulse & Activity",
        active: Boolean(resolvedOptions?.life_operations_moment_id),
      },
      {
        title: "Lifestyle" as const,
        subtitle: "Will refresh Pulse & Moments",
        active: Boolean(resolvedOptions?.lifestyle_moment_id),
      },
      {
        title: "Relationships" as const,
        subtitle: sharedEnabled ? "Will refresh Pulse & Moments" : "Skipped (not shared)",
        active: sharedEnabled && Boolean(resolvedOptions?.emotional_security_moment_id),
      },
    ],
    [sharedEnabled, resolvedOptions],
  );

  const showImpact =
    Boolean(title.trim()) && money.amount_minor > 0 && Boolean(categoryCode) && Boolean(accountId);

  function clearAll() {
    setTitle("");
    setMoney((prev) => ({ ...prev, amount_minor: 0 }));
    setCategoryCode("");
    setSubcategoryCode("");
    setOccurredAt(defaultOccurredAt());
    setFeeling("");
    setMeaningfulness("");
    setMemorability("");
    setSharedWith([]);
    setRelationshipImpact([]);
    setContextReason("");
    setNotes("");
  }

  function requestClear() {
    if (dirty) setConfirmClear(true);
    else clearAll();
  }

  function requestBack() {
    if (dirty) setConfirmCancel(true);
    else onBack();
  }

  function selectCategory(code: string) {
    setCategoryCode(code);
    setSubcategoryCode(
      resolveSubcategoryForCategory(resolvedOptions?.categories ?? [], code, subcategoryCode),
    );
  }

  function toggleSharedWith(value: string) {
    setSharedWith((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value],
    );
  }

  function toggleRelationshipImpact(value: string) {
    setRelationshipImpact((prev) =>
      prev.includes(value) ? prev.filter((v) => v !== value) : [...prev, value],
    );
  }

  async function handleSave() {
    if (!canSave || savingRef.current) {
      if (!title.trim()) titleRef.current?.focus();
      return;
    }
    savingRef.current = true;
    setSaving(true);
    setError(null);
    const safeSub = resolveSubcategoryForCategory(
      resolvedOptions?.categories ?? [],
      categoryCode,
      subcategoryCode,
    );
    const payload = buildMasterExpensePayload(
      {
        title,
        amountMinor: money.amount_minor,
        currencyCode: money.currency_code,
        accountId,
        categoryCode,
        subcategoryCode: safeSub,
        occurredAt,
        feeling,
        meaningfulness,
        memorability,
        sharedEnabled,
        sharedWith,
        relationshipImpact,
        contextReason,
        notes,
      },
      createClientRequestId(),
    );

    try {
      await PersonalRepository.createMasterExpense(payload);
      invalidateAfterMasterExpense(sharedEnabled);
      setSaved(true);
      onSuccess?.();
      setTimeout(() => onBack(), 600);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save expense.");
    } finally {
      setSaving(false);
      savingRef.current = false;
    }
  }

  if (loading && !resolvedOptions) {
    return (
      <div
        className="fixed inset-0 z-[120] flex flex-col"
        style={{ background: tokens.colors.background }}
      >
        <MasterExpenseSkeleton />
      </div>
    );
  }

  const visibleCategories = visibleCategoryChips(resolvedOptions?.categories ?? []);

  return (
    <div
      className="fixed inset-0 z-[120] flex flex-col"
      style={{ background: tokens.colors.background, color: colors.textPrimary }}
      data-testid="master-expense-orchestrator"
    >
      <PersonalAtmosphericOrbs />
      <header
        className="sticky top-0 z-10 flex items-center justify-between px-5 py-3 backdrop-blur-md"
        style={{ background: `${tokens.colors.background}e6` }}
      >
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={requestBack}
            className="pressable rounded-lg p-2 transition-opacity hover:opacity-80"
            aria-label="Back"
          >
            <ArrowLeft size={22} />
          </button>
          <div className="flex items-center gap-2">
            <div
              className="flex size-9 items-center justify-center rounded-xl"
              style={{ background: colors.brandPrimary, boxShadow: `0 4px 12px ${colors.brandPrimary}40` }}
            >
              <Wallet size={16} color={colors.onPrimary} aria-hidden />
            </div>
            <div>
              <h1 className="flex items-center gap-1" style={personalTypography.screenTitle}>
                Master Expense
                <Sparkles size={14} style={{ color: colors.brandTertiary }} aria-hidden />
              </h1>
              <p className="text-[11px]" style={{ color: colors.textSecondary }}>
                One expense. Impact across your life.
              </p>
            </div>
          </div>
        </div>
        <button
          type="button"
          onClick={requestClear}
          className="text-sm font-semibold"
          style={{ color: colors.brandPrimary }}
          aria-label="Clear all fields"
        >
          Clear All
        </button>
      </header>

      <main
        className="relative flex-1 space-y-5 overflow-y-auto px-5 pb-36 pt-2"
        data-testid="master-expense-form"
      >
        {error ? (
          <p
            className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300"
            role="alert"
          >
            {error}
            <button type="button" className="ml-3 underline" onClick={() => void load()}>
              Retry
            </button>
          </p>
        ) : null}

        {saved ? (
          <p
            className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-200"
            aria-live="polite"
          >
            Expense saved across your life templates.
          </p>
        ) : null}

        {!resolvedOptions?.life_operations_moment_id ? (
          <div className="rounded-2xl p-4 text-sm" style={personalGlassCardStyle(tokens)}>
            Activate Life Operations, Lifestyle, and Relationships moments to use Master Expense.
          </div>
        ) : null}

        <div
          className="flex items-center gap-2 rounded-xl px-3 py-2.5 text-xs"
          style={{ background: `${colors.brandPrimary}14`, color: colors.textSecondary }}
          data-testid="master-expense-info-banner"
        >
          <Info size={14} style={{ color: colors.brandPrimary }} aria-hidden />
          This entry can update Life, Lifestyle and Relationships.
        </div>

        <div data-field="description">
          <MasterExpenseFieldLabel label="What did you spend on?" labelColor={colors.textSecondary} />
          <input
            ref={titleRef}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded-xl px-3.5 py-3.5 text-sm font-medium outline-none"
            style={{ ...fieldSurface, color: colors.textPrimary, border: `1px solid ${colors.border}` }}
            placeholder={descriptionPlaceholder}
            aria-required
          />
        </div>

        <div data-field="amount">
          <MasterExpenseFieldLabel label="Amount" labelColor={colors.textSecondary} />
          <div
            className="rounded-xl px-3 py-2"
            style={{ ...fieldSurface, border: `1px solid ${colors.border}` }}
          >
            <MoneyInput
              label=""
              value={money}
              onChange={setMoney}
              currencies={currencies}
              defaultCurrencyCode={money.currency_code}
              className="!space-y-0"
            />
          </div>
        </div>

        <div data-field="category">
          <MasterExpenseFieldLabel label="Category" labelColor={colors.textSecondary} />
          {selectedCategory && (resolvedOptions?.categories.length ?? 0) > MASTER_EXPENSE_VISIBLE_CHIP_LIMIT ? (
            <button
              type="button"
              onClick={() => setPicker("category")}
              className="flex min-h-12 w-full items-center gap-2 rounded-xl px-3.5 py-3"
              style={{
                background: `${colors.brandPrimary}22`,
                border: `1px solid ${colors.brandPrimary}66`,
              }}
            >
              {(() => {
                const CatIcon = resolveExpenseCategoryIcon(null, categoryCode);
                return <CatIcon size={16} className="shrink-0 opacity-80" aria-hidden />;
              })()}
              <span className="flex-1 text-left text-sm font-semibold">{selectedCategory.category_name}</span>
              <span className="text-sm font-semibold" style={{ color: colors.brandPrimary }}>
                Change
              </span>
            </button>
          ) : (
            <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Category">
              {visibleCategories.map((c) => (
                <MasterExpenseChip
                  key={c.category_id}
                  label={c.category_name}
                  selected={categoryCode === c.category_id}
                  onClick={() => selectCategory(c.category_id)}
                  colors={colors}
                />
              ))}
              {(resolvedOptions?.categories.length ?? 0) > MASTER_EXPENSE_VISIBLE_CHIP_LIMIT ? (
                <MasterExpenseChip
                  label="More"
                  selected={false}
                  onClick={() => setPicker("category")}
                  colors={colors}
                />
              ) : null}
            </div>
          )}
        </div>

        {categoryCode && subcategoryChildren.length > 0 ? (
          <div data-field="subcategory">
            <MasterExpenseFieldLabel label="Subcategory" labelColor={colors.textSecondary} />
            <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Subcategory">
              {visibleCategoryChips(subcategoryChildren).map((c) => (
                <MasterExpenseChip
                  key={c.category_id}
                  label={c.category_name}
                  selected={subcategoryCode === c.category_id}
                  onClick={() => setSubcategoryCode(c.category_id)}
                  colors={colors}
                />
              ))}
              {subcategoryChildren.length > MASTER_EXPENSE_VISIBLE_CHIP_LIMIT ? (
                <MasterExpenseChip
                  label="More"
                  selected={false}
                  onClick={() => setPicker("subcategory")}
                  colors={colors}
                />
              ) : null}
            </div>
          </div>
        ) : null}

        <div data-field="paid_from">
          <CompactSelectRow
            label="Paid from"
            value={
              selectedAccount?.account_name ??
              (resolvedOptions?.accounts.length ? "Select account" : "No accounts")
            }
            icon={<Wallet size={16} style={{ color: colors.brandPrimary }} aria-hidden />}
            onClick={() => {
              if (resolvedOptions?.accounts.length) setPicker("account");
            }}
          />
        </div>

        <div data-field="when">
          <CompactSelectRow
            label="When"
            value={formatWhenLabel(occurredAt)}
            onClick={() => setPicker("when")}
          />
        </div>

        {showImpact ? (
          <section data-field="impact" className="border-t border-white/5 pt-4">
            <p
              className="mb-3 text-center text-[10px] font-bold uppercase tracking-[0.2em]"
              style={{ color: colors.textSecondary }}
            >
              Impact
            </p>
            <div className="grid grid-cols-3 gap-2">
              {impactPreview.map((card) => (
                <MasterExpenseImpactTile
                  key={card.title}
                  title={card.title}
                  subtitle={card.subtitle}
                  active={card.active}
                  surfaceStyle={fieldSurface}
                  colors={colors}
                />
              ))}
            </div>
          </section>
        ) : null}

        <section data-field="more_details">
          <button
            type="button"
            onClick={() => setMoreDetailsOpen((v) => !v)}
            className="flex min-h-11 w-full items-center justify-between py-2"
            aria-expanded={moreDetailsOpen}
            data-testid="more-details-toggle"
          >
            <span style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
              More details
            </span>
            {moreDetailsOpen ? (
              <ChevronUp size={18} style={{ color: colors.textSecondary }} aria-hidden />
            ) : (
              <ChevronDown size={18} style={{ color: colors.textSecondary }} aria-hidden />
            )}
          </button>
          {moreDetailsOpen ? (
            <div className="space-y-5 pt-2" data-testid="more-details-content">
              <div>
                <p style={{ ...personalTypography.labelSm, color: colors.textSecondary, marginBottom: 12 }}>
                  How did this make you feel?
                </p>
                <div className="grid grid-cols-5 gap-2">
                  {(resolvedOptions?.feelings ?? []).map((opt) => {
                    const isSelected = feeling === opt.value;
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => setFeeling(opt.value)}
                        aria-pressed={isSelected}
                        className="pressable flex flex-col items-center gap-1 rounded-xl border p-2 transition-transform active:scale-95"
                        style={{
                          borderColor: isSelected ? "transparent" : colors.border,
                          background: isSelected
                            ? `linear-gradient(135deg, ${colors.brandPrimary} 0%, ${colors.brandPrimary}cc 100%)`
                            : "transparent",
                          color: isSelected ? colors.onPrimary : undefined,
                        }}
                      >
                        <span className="text-xl">{FEELING_EMOJI[opt.value] ?? "😐"}</span>
                        <span
                          className="text-[9px] font-bold uppercase"
                          style={{ color: isSelected ? colors.onPrimary : colors.textSecondary }}
                        >
                          {opt.label}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
              <div>
                <p style={{ ...personalTypography.labelSm, color: colors.textSecondary, marginBottom: 8 }}>
                  How meaningful was this experience?
                </p>
                <SegmentedScaleControl
                  options={resolvedOptions?.scale_levels ?? []}
                  value={meaningfulness}
                  onChange={setMeaningfulness}
                  colors={colors}
                />
              </div>
              <div>
                <p style={{ ...personalTypography.labelSm, color: colors.textSecondary, marginBottom: 8 }}>
                  How memorable was this?
                </p>
                <SegmentedScaleControl
                  options={resolvedOptions?.scale_levels ?? []}
                  value={memorability}
                  onChange={setMemorability}
                  colors={colors}
                />
              </div>
              <div className="flex items-center justify-between">
                <p style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
                  Shared experience
                </p>
                <label className="relative inline-flex min-h-11 cursor-pointer items-center">
                  <input
                    type="checkbox"
                    checked={sharedEnabled}
                    onChange={(e) => setSharedEnabled(e.target.checked)}
                    className="peer sr-only"
                    aria-label="Shared experience"
                  />
                  <div className="peer h-6 w-11 rounded-full bg-gray-700 after:absolute after:left-[2px] after:top-[2px] after:size-5 after:rounded-full after:bg-white after:transition-all peer-checked:bg-[#6c4ef2] peer-checked:after:translate-x-full" />
                </label>
              </div>
              {sharedEnabled ? (
                <div className="space-y-5">
                  <ChipRow
                    label="Shared With"
                    options={resolvedOptions?.shared_with ?? []}
                    value={sharedWith}
                    onChange={toggleSharedWith}
                    multi
                  />
                  <ChipRow
                    label="What was the impact on this relationship?"
                    options={resolvedOptions?.relationship_impacts ?? []}
                    value={relationshipImpact}
                    onChange={toggleRelationshipImpact}
                    multi
                  />
                </div>
              ) : null}
              <div>
                <p style={{ ...personalTypography.labelSm, color: colors.textSecondary, marginBottom: 12 }}>
                  Why did this happen?
                </p>
                <ChipRow
                  label=""
                  options={resolvedOptions?.context_reasons ?? []}
                  value={contextReason}
                  onChange={setContextReason}
                />
              </div>
              <div>
                <MasterExpenseFieldLabel label="Notes" labelColor={colors.textSecondary} />
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value.slice(0, 200))}
                  placeholder="Add any additional notes..."
                  className="min-h-[60px] w-full resize-none rounded-xl px-3 py-3 text-xs outline-none"
                  style={{ ...fieldSurface, color: colors.textSecondary, border: `1px solid ${colors.border}` }}
                />
                <div className="text-right text-[10px]" style={{ color: colors.textSecondary, opacity: 0.6 }}>
                  {notes.length}/200
                </div>
              </div>
            </div>
          ) : null}
        </section>
      </main>

      <footer
        className="sticky bottom-0 space-y-3 px-5 py-5 backdrop-blur-lg"
        style={{ background: `${tokens.colors.background}f2` }}
      >
        {saving ? (
          <p className="text-center text-xs" style={{ color: colors.textSecondary }} aria-live="polite">
            Saving…
          </p>
        ) : null}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={requestBack}
            className="pressable flex-1 rounded-2xl border py-4 text-sm font-bold tracking-wide transition-transform active:scale-95"
            style={{ borderColor: colors.border, background: "rgba(255,255,255,0.05)" }}
            aria-label="Cancel expense"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => void handleSave()}
            disabled={!canSave || saving}
            className="pressable flex-[2] rounded-2xl py-4 text-sm font-bold tracking-wide transition-transform active:scale-95 disabled:opacity-50"
            style={{
              background: colors.brandPrimary,
              color: colors.onPrimary,
              boxShadow: `0 8px 24px ${colors.brandPrimary}40`,
            }}
            data-testid="save-expense"
          >
            {saving ? "Saving…" : "Save Expense"}
          </button>
        </div>
        <div
          className="flex items-center justify-center gap-1.5 text-[10px]"
          style={{ color: colors.textSecondary, opacity: 0.6 }}
        >
          <Lock size={12} aria-hidden />
          Your data is private and secure
        </div>
      </footer>

      {picker === "category" ? (
        <PickerSheet
          title="Category"
          options={(resolvedOptions?.categories ?? []).map((c) => ({
            id: c.category_id,
            label: c.category_name,
          }))}
          selected={categoryCode}
          onSelect={selectCategory}
          onClose={() => setPicker(null)}
        />
      ) : null}
      {picker === "subcategory" ? (
        <PickerSheet
          title="Subcategory"
          options={subcategoryChildren.map((c) => ({
            id: c.category_id,
            label: c.category_name,
          }))}
          selected={subcategoryCode}
          onSelect={setSubcategoryCode}
          onClose={() => setPicker(null)}
        />
      ) : null}
      {picker === "account" ? (
        <PickerSheet
          title="Paid from"
          options={(resolvedOptions?.accounts ?? []).map((a) => ({
            id: a.account_id,
            label: a.account_name,
          }))}
          selected={accountId}
          searchable={(resolvedOptions?.accounts.length ?? 0) > 8}
          onSelect={(id) => {
            setAccountId(id);
            const account = resolvedOptions?.accounts.find((a) => a.account_id === id);
            if (account?.currency_code) {
              setMoney((prev) => ({ ...prev, currency_code: account.currency_code }));
            }
          }}
          onClose={() => setPicker(null)}
        />
      ) : null}
      {picker === "when" ? (
        <PickerSheet
          title="When"
          options={[
            { id: "now", label: "Now" },
            { id: "today", label: "Today" },
            { id: "yesterday", label: "Yesterday" },
            { id: "choose", label: "Choose date and time" },
          ]}
          selected=""
          searchable={false}
          onSelect={(id) => {
            if (id === "choose") {
              const el = document.createElement("input");
              el.type = "datetime-local";
              el.value = occurredAt;
              el.style.position = "fixed";
              el.style.opacity = "0";
              document.body.appendChild(el);
              el.addEventListener("change", () => {
                if (el.value) setOccurredAt(el.value);
                el.remove();
              });
              el.showPicker?.();
              el.click();
              return;
            }
            if (id === "now" || id === "today" || id === "yesterday") {
              setOccurredAt(whenPresetValue(id));
            }
          }}
          onClose={() => setPicker(null)}
        />
      ) : null}

      {confirmClear ? (
        <div className="fixed inset-0 z-[150] flex items-center justify-center bg-black/50 p-6" role="alertdialog">
          <div className="w-full max-w-sm rounded-2xl p-5" style={{ background: tokens.colors.surface }}>
            <h2 className="text-base font-semibold">Clear all fields?</h2>
            <p className="mt-2 text-sm" style={{ color: colors.textSecondary }}>
              Entered details will be discarded.
            </p>
            <div className="mt-4 flex gap-2">
              <button type="button" className="flex-1 rounded-xl border py-3 text-sm" style={{ borderColor: colors.border }} onClick={() => setConfirmClear(false)}>
                Keep editing
              </button>
              <button
                type="button"
                className="flex-1 rounded-xl py-3 text-sm font-semibold"
                style={{ background: colors.brandPrimary, color: colors.onPrimary }}
                onClick={() => {
                  setConfirmClear(false);
                  clearAll();
                }}
              >
                Clear All
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {confirmCancel ? (
        <div className="fixed inset-0 z-[150] flex items-center justify-center bg-black/50 p-6" role="alertdialog">
          <div className="w-full max-w-sm rounded-2xl p-5" style={{ background: tokens.colors.surface }}>
            <h2 className="text-base font-semibold">Discard expense?</h2>
            <p className="mt-2 text-sm" style={{ color: colors.textSecondary }}>
              You have unsaved changes.
            </p>
            <div className="mt-4 flex gap-2">
              <button type="button" className="flex-1 rounded-xl border py-3 text-sm" style={{ borderColor: colors.border }} onClick={() => setConfirmCancel(false)}>
                Keep editing
              </button>
              <button
                type="button"
                className="flex-1 rounded-xl py-3 text-sm font-semibold"
                style={{ background: colors.brandPrimary, color: colors.onPrimary }}
                onClick={() => {
                  setConfirmCancel(false);
                  onBack();
                }}
              >
                Discard
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

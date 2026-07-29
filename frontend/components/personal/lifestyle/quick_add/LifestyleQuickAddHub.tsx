"use client";

import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { SkeletonQuickAddSheet } from "@/components/personal/shared/skeleton/SkeletonBlocks";
import { AppToast } from "@/components/shared/AppToast";
import { useQuickAddOptions } from "@/hooks/useQuickAddOptions";
import {
  createPersonalQuickAdd,
  type PersonalFutureBuildingQuickAddFieldGroup,
  type PersonalQuickAddOptionsResponse,
  type PersonalQuickAddTab,
} from "@/lib/api/client";
import { createClientRequestId } from "@/lib/quick_add/draftStore";
import {
  LS_SELECTOR_HELPER,
  LS_SHEET_SUPPORTING,
  lsErrorMessage,
  lsSavingLabel,
  lsSelectorFallback,
  lsSuccessMessage,
  lsTitlePlaceholder,
  normalizeLifestyleEventType,
} from "@/lib/quick_add/lifestyleCopy";
import {
  buildLifestylePayload,
  canSubmitLifestyle,
  resolveLsFieldOptions,
} from "@/lib/quick_add/lifestyleOptions";
import { invalidateAfterLifestyleQuickAdd } from "@/repositories/PersonalRepository";

type FieldState = Record<string, string>;
type MultiFieldState = Record<string, Set<string>>;
type Draft = { values: FieldState; multi: MultiFieldState };
type DraftMap = Record<string, Draft>;

type LifestyleQuickAddHubProps = {
  initialEventType?: string | null;
  momentId?: string | null;
  open?: boolean;
  onClose: () => void;
  onSuccess?: () => void;
};

export function LifestyleQuickAddHub({
  initialEventType,
  momentId,
  open = true,
  onClose,
  onSuccess,
}: LifestyleQuickAddHubProps) {
  const { colors } = useThemeTokens();
  const titleId = useId();
  const { options, loading, error, reload: reloadOptions } = useQuickAddOptions({
    momentId,
    enabled: open,
  });

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; tone: "success" | "error" } | null>(null);
  const [selectedTab, setSelectedTab] = useState(
    normalizeLifestyleEventType(initialEventType),
  );
  const [drafts, setDrafts] = useState<DraftMap>({});
  const [notesExpanded, setNotesExpanded] = useState(false);
  const [selectorTouched, setSelectorTouched] = useState(false);
  const saveLatch = useRef(false);
  const clientRequestId = useRef(createClientRequestId());

  useEffect(() => {
    if (!options) return;
    if (initialEventType) {
      setSelectedTab(normalizeLifestyleEventType(initialEventType));
    } else if (options.tabs?.[0]?.event_type) {
      setSelectedTab(normalizeLifestyleEventType(options.tabs[0].event_type));
    }
  }, [options, initialEventType]);

  useEffect(() => {
    if (!open) {
      saveLatch.current = false;
      clientRequestId.current = createClientRequestId();
      setDrafts({});
      setNotesExpanded(false);
      setSelectorTouched(false);
      setSubmitError(null);
      setSubmitting(false);
    }
  }, [open]);

  const draft = drafts[selectedTab] ?? { values: {}, multi: {} };
  const values = draft.values;
  const multi = draft.multi;
  const eventTitle = values.event_title ?? "";

  function patchDraft(patch: Partial<Draft>) {
    setDrafts((prev) => ({
      ...prev,
      [selectedTab]: {
        values: patch.values ?? prev[selectedTab]?.values ?? {},
        multi: patch.multi ?? prev[selectedTab]?.multi ?? {},
      },
    }));
  }

  function setValue(key: string, value: string) {
    patchDraft({ values: { ...values, [key]: value }, multi });
  }

  function toggleMulti(key: string, value: string) {
    const current = new Set(multi[key] ?? []);
    if (current.has(value)) current.delete(value);
    else current.add(value);
    patchDraft({ values, multi: { ...multi, [key]: current } });
  }

  function selectTab(eventType: string) {
    const normalized = normalizeLifestyleEventType(eventType);
    setSelectedTab(normalized);
    setSelectorTouched(true);
    const next = drafts[normalized];
    setNotesExpanded(Boolean(next?.values.notes?.trim()));
    setSubmitError(null);
  }

  const tabs = options?.tabs ?? [];
  const activeTab: PersonalQuickAddTab | undefined = tabs.find(
    (t) => normalizeLifestyleEventType(t.event_type) === selectedTab,
  );
  const groups =
    options?.metadata?.lifestyle_tabs?.find(
      (t) => normalizeLifestyleEventType(t.event_type) === selectedTab,
    )?.field_groups ?? [];

  const visibleGroups = groups.filter((g) => g.group_key !== "notes");

  const lifestyleMoment =
    options?.moments.find((m) => m.moment_type_code === "LIFESTYLE") ??
    options?.moments.find((m) => m.moment_id === momentId) ??
    options?.moments[0] ??
    null;

  const submitEnabled =
    Boolean(lifestyleMoment) &&
    canSubmitLifestyle(selectedTab, values, multi, eventTitle) &&
    !submitting;

  async function handleSubmit() {
    if (!lifestyleMoment || !submitEnabled || saveLatch.current) return;
    saveLatch.current = true;
    setSubmitting(true);
    setSubmitError(null);
    try {
      await createPersonalQuickAdd(
        {
          moment_id: lifestyleMoment.moment_id,
          event_type: selectedTab,
          event_title: eventTitle.trim(),
          lifestyle: buildLifestylePayload(values, multi),
        },
        { clientRequestId: clientRequestId.current },
      );
      invalidateAfterLifestyleQuickAdd();
      setToast({ message: lsSuccessMessage(selectedTab), tone: "success" });
      onSuccess?.();
      onClose();
    } catch (err) {
      const msg =
        err instanceof Error && err.message.toLowerCase().includes("offline")
          ? "You're offline. Check your connection and try again."
          : err instanceof Error && err.message.toLowerCase().includes("timeout")
            ? "Saving is taking longer than expected. Try again."
            : lsErrorMessage(selectedTab);
      setSubmitError(msg);
      setToast({ message: msg, tone: "error" });
      setSubmitting(false);
      saveLatch.current = false;
    }
  }

  const onKeyDownSelector = useCallback(
    (e: React.KeyboardEvent<HTMLButtonElement>, index: number) => {
      if (!tabs.length) return;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") {
        e.preventDefault();
        selectTab(tabs[(index + 1) % tabs.length].event_type);
      } else if (e.key === "ArrowLeft" || e.key === "ArrowUp") {
        e.preventDefault();
        selectTab(tabs[(index - 1 + tabs.length) % tabs.length].event_type);
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [tabs],
  );

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) {
    return (
      <AppToast
        open={Boolean(toast)}
        message={toast?.message ?? ""}
        tone={toast?.tone ?? "success"}
        onDismiss={() => setToast(null)}
      />
    );
  }

  return (
    <>
      <div
        className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 sm:items-center"
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={onClose}
      >
        <div
          className="flex max-h-[92dvh] w-full max-w-lg flex-col rounded-t-2xl border sm:rounded-2xl"
          style={{ borderColor: colors.border, background: colors.surface }}
          onClick={(e) => e.stopPropagation()}
        >
          <div className="shrink-0 border-b px-5 pb-3 pt-5" style={{ borderColor: colors.border }}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2 id={titleId} style={{ ...personalTypography.heroTitle, color: colors.brandPrimary, fontSize: 22 }}>
                  Capture Lifestyle
                </h2>
                <p className="mt-1" style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
                  {LS_SHEET_SUPPORTING}
                </p>
              </div>
              <button
                type="button"
                onClick={onClose}
                aria-label="Close Capture Lifestyle"
                className="rounded-lg px-2 py-1 text-lg leading-none"
                style={{ color: colors.textSecondary }}
              >
                ×
              </button>
            </div>

            <div role="tablist" aria-label="Lifestyle entry type" className="mt-4 flex gap-2 overflow-x-auto pb-1">
              {tabs.map((tab, index) => {
                const normalized = normalizeLifestyleEventType(tab.event_type);
                const active = normalized === selectedTab;
                const fallback = lsSelectorFallback(normalized);
                const blurb = tab.description?.trim() || fallback.blurb;
                return (
                  <button
                    key={tab.event_type}
                    type="button"
                    role="tab"
                    aria-selected={active}
                    aria-label={`${tab.label}. ${blurb}.${active ? " Selected." : ""}`}
                    tabIndex={active ? 0 : -1}
                    onClick={() => selectTab(tab.event_type)}
                    onKeyDown={(e) => onKeyDownSelector(e, index)}
                    className="min-w-[9.5rem] shrink-0 rounded-2xl border px-3 py-3 text-left"
                    style={{
                      borderColor: active ? colors.brandPrimary : colors.border,
                      background: active ? `${colors.brandPrimary}18` : "transparent",
                      minHeight: 48,
                    }}
                  >
                    <span className="block text-sm font-semibold" style={{ color: active ? colors.brandPrimary : colors.textPrimary }}>
                      {tab.label || fallback.title}
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
                {LS_SELECTOR_HELPER}
              </p>
            ) : null}
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5">
            {loading && !options ? (
              <SkeletonQuickAddSheet />
            ) : error && !options ? (
              <div className="space-y-2">
                <p style={{ color: colors.error }}>{error}</p>
                <button type="button" onClick={() => void reloadOptions()} className="text-sm underline">
                  Retry
                </button>
              </div>
            ) : !lifestyleMoment ? (
              <p style={{ color: colors.textSecondary }}>Activate a lifestyle moment first.</p>
            ) : (
              <div className="space-y-4 pb-4">
                {activeTab ? (
                  <div className="space-y-1">
                    <h3 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
                      {activeTab.hero_title ?? activeTab.label}
                    </h3>
                    <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
                      {activeTab.hero_subtitle ?? activeTab.description}
                    </p>
                  </div>
                ) : null}

                <div className="space-y-2">
                  <label htmlFor="ls-event-title" style={{ ...personalTypography.labelSm, color: colors.textSecondary }}>
                    {activeTab?.hero_subtitle ?? "What do you want to capture?"}
                  </label>
                  <input
                    id="ls-event-title"
                    type="text"
                    value={eventTitle}
                    onChange={(e) => setValue("event_title", e.target.value)}
                    placeholder={lsTitlePlaceholder(selectedTab)}
                    className="w-full rounded-xl border px-3 py-3 outline-none"
                    style={{
                      borderColor: colors.border,
                      background: colors.surfaceContainer ?? "transparent",
                      color: colors.textPrimary,
                    }}
                  />
                </div>

                {selectedTab === "LIFESTYLE_EXPENSE" ? (
                  <p className="text-xs" style={{ color: colors.textSecondary }}>
                    Saves a lifestyle spend to your money timeline — not a Master Expense bookkeeping entry.
                  </p>
                ) : null}

                {options
                  ? visibleGroups.map((group) => (
                      <FieldGroupView
                        key={group.group_key}
                        group={group}
                        values={values}
                        multi={multi}
                        options={resolveLsFieldOptions(group, options)}
                        onValue={setValue}
                        onToggle={toggleMulti}
                        colors={colors}
                      />
                    ))
                  : null}

                {!notesExpanded ? (
                  <button
                    type="button"
                    onClick={() => setNotesExpanded(true)}
                    className="text-sm font-medium"
                    style={{ color: colors.textSecondary }}
                  >
                    Add note — optional
                  </button>
                ) : (
                  <label className="block">
                    <span style={{ ...personalTypography.labelSm, color: colors.textSecondary }}>
                      Note — optional
                    </span>
                    <textarea
                      value={values.notes ?? ""}
                      onChange={(e) => setValue("notes", e.target.value)}
                      rows={2}
                      className="mt-2 w-full rounded-xl border px-3 py-2 outline-none"
                      style={{
                        borderColor: colors.border,
                        background: colors.surfaceContainer ?? "transparent",
                        color: colors.textPrimary,
                      }}
                    />
                  </label>
                )}

                {activeTab?.teaches_items?.length ? (
                  <section className="rounded-2xl border p-3" style={{ borderColor: colors.border }}>
                    <p className="mb-2 text-xs font-semibold" style={{ color: colors.brandPrimary }}>
                      Possible impact
                    </p>
                    <ul className="space-y-1">
                      {activeTab.teaches_items.map((item) => (
                        <li key={item} style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </section>
                ) : null}

                {submitError ? (
                  <p className="text-sm" role="alert" style={{ color: colors.error }}>
                    {submitError}
                  </p>
                ) : null}
              </div>
            )}
          </div>

          <div
            className="shrink-0 border-t px-5 py-4"
            style={{
              borderColor: colors.border,
              paddingBottom: "max(1rem, env(safe-area-inset-bottom))",
            }}
          >
            <button
              type="button"
              disabled={!submitEnabled}
              onClick={() => void handleSubmit()}
              aria-busy={submitting}
              className="w-full rounded-xl py-3 font-semibold disabled:opacity-55"
              style={{
                background: colors.brandPrimary,
                color: colors.brandOnPrimary,
                minHeight: 48,
              }}
            >
              {submitting ? lsSavingLabel(selectedTab) : activeTab?.cta_label ?? "Save Entry"}
            </button>
          </div>
        </div>
      </div>

      <AppToast
        open={Boolean(toast)}
        message={toast?.message ?? ""}
        tone={toast?.tone ?? "success"}
        onDismiss={() => setToast(null)}
      />
    </>
  );
}

function FieldGroupView({
  group,
  values,
  multi,
  options,
  onValue,
  onToggle,
  colors,
}: {
  group: PersonalFutureBuildingQuickAddFieldGroup;
  values: FieldState;
  multi: MultiFieldState;
  options: { value: string; label: string }[];
  onValue: (key: string, value: string) => void;
  onToggle: (key: string, value: string) => void;
  colors: ReturnType<typeof useThemeTokens>["colors"];
}) {
  if (group.field_type === "amount") {
    return (
      <label className="block">
        <span style={{ ...personalTypography.labelSm, color: colors.textSecondary }}>{group.label}</span>
        <div className="relative mt-2">
          <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-xl font-bold" style={{ color: colors.brandPrimary }}>
            ₹
          </span>
          <input
            type="number"
            inputMode="decimal"
            value={values[group.group_key] ?? ""}
            onChange={(e) => onValue(group.group_key, e.target.value)}
            className="w-full rounded-xl border bg-transparent py-4 pl-12 pr-4 text-2xl font-bold outline-none"
            style={{ borderColor: colors.border, color: colors.textPrimary }}
            placeholder="0.00"
          />
        </div>
      </label>
    );
  }

  if (group.field_type === "textarea") {
    return (
      <label className="block">
        <span style={{ ...personalTypography.labelSm, color: colors.textSecondary }}>{group.label}</span>
        <textarea
          value={values[group.group_key] ?? ""}
          onChange={(e) => onValue(group.group_key, e.target.value)}
          rows={2}
          className="mt-2 w-full rounded-xl border px-3 py-2 outline-none"
          style={{ borderColor: colors.border, color: colors.textPrimary }}
        />
      </label>
    );
  }

  if (
    group.field_type === "single_select" ||
    group.field_type === "chip_grid" ||
    group.field_type === "multi_select" ||
    group.field_type === "slider"
  ) {
    const isMulti = group.field_type === "multi_select" || group.group_key === "wellbeing_areas" || group.group_key === "contributors";
    const opts = options.length ? options : group.options ?? [];
    return (
      <div>
        <p style={{ ...personalTypography.labelSm, color: colors.textSecondary }}>{group.label}</p>
        <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label={group.label}>
          {opts.map((option) => {
            const active = isMulti
              ? multi[group.group_key]?.has(option.value)
              : values[group.group_key] === option.value;
            return (
              <button
                key={option.value}
                type="button"
                aria-pressed={Boolean(active)}
                onClick={() =>
                  isMulti ? onToggle(group.group_key, option.value) : onValue(group.group_key, option.value)
                }
                className="rounded-lg border px-3 py-2 text-xs font-medium"
                style={{
                  borderColor: active ? colors.brandPrimary : colors.border,
                  background: active ? `${colors.brandPrimary}22` : "transparent",
                  color: active ? colors.brandPrimary : colors.textSecondary,
                  minHeight: 40,
                }}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <label className="block">
      <span style={{ ...personalTypography.labelSm, color: colors.textSecondary }}>{group.label}</span>
      <input
        type="text"
        value={values[group.group_key] ?? ""}
        onChange={(e) => onValue(group.group_key, e.target.value)}
        className="mt-2 w-full rounded-xl border px-3 py-2.5 outline-none"
        style={{ borderColor: colors.border, color: colors.textPrimary }}
      />
    </label>
  );
}

// Keep type for consumers that imported it previously
export type { PersonalQuickAddOptionsResponse };

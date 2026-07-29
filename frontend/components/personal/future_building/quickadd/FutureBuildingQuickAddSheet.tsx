"use client";

import {
  useCallback,
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
} from "react";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import type { ContextThemeTokens } from "@/lib/contextTokens";
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
  FB_EVENT_TYPES,
  FB_SELECTOR_HELPER,
  FB_SHEET_SUPPORTING,
  fbCtaLabel,
  fbErrorMessage,
  fbSavingLabel,
  fbSelectorFallback,
  fbSuccessMessage,
  fbTitlePlaceholder,
} from "@/lib/quick_add/futureBuildingCopy";
import {
  buildFutureBuildingPayload,
  canSubmitFb,
  missingFbRequiredHint,
  resolveFbFieldOptions,
} from "@/lib/quick_add/futureBuildingOptions";
import { invalidateAfterFutureBuildingQuickAdd } from "@/repositories/PersonalRepository";

type DraftMap = Record<string, Record<string, string>>;

type FutureBuildingQuickAddSheetProps = {
  initialEventType?: string | null;
  defaultMomentId?: string | null;
  open?: boolean;
  onClose: () => void;
  onSuccess?: () => void;
};

export function FutureBuildingQuickAddSheet({
  initialEventType,
  defaultMomentId,
  open = true,
  onClose,
  onSuccess,
}: FutureBuildingQuickAddSheetProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const titleId = useId();
  const closeRef = useRef<HTMLButtonElement>(null);

  const { options, loading, error } = useQuickAddOptions({
    momentId: defaultMomentId,
    enabled: open,
  });

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; tone: "success" | "error" } | null>(
    null,
  );
  const [selectedTab, setSelectedTab] = useState("CONTRIBUTION");
  const [drafts, setDrafts] = useState<DraftMap>({});
  const [notesExpanded, setNotesExpanded] = useState(false);
  const [outcomeExpanded, setOutcomeExpanded] = useState(false);
  const [selectorTouched, setSelectorTouched] = useState(false);
  const saveLatch = useRef(false);
  const clientRequestId = useRef(createClientRequestId());

  useEffect(() => {
    if (!options) return;
    const initial = initialEventType?.toUpperCase();
    if (initial && FB_EVENT_TYPES.has(initial)) {
      setSelectedTab(initial);
      if (initial === "PIVOT") setNotesExpanded(true);
    } else if (options.tabs?.[0]?.event_type) {
      const first = options.tabs[0].event_type;
      setSelectedTab(first);
      if (first === "PIVOT") setNotesExpanded(true);
    }
  }, [options, initialEventType]);

  useEffect(() => {
    if (!open) {
      saveLatch.current = false;
      clientRequestId.current = createClientRequestId();
      setDrafts({});
      setNotesExpanded(false);
      setOutcomeExpanded(false);
      setSelectorTouched(false);
      setSubmitError(null);
      setSubmitting(false);
    }
  }, [open]);

  const fieldValues = drafts[selectedTab] ?? {};
  const eventTitle = fieldValues.event_title ?? "";

  function setField(key: string, value: string) {
    setDrafts((prev) => ({
      ...prev,
      [selectedTab]: { ...(prev[selectedTab] ?? {}), [key]: value },
    }));
  }

  function selectTab(eventType: string) {
    setSelectedTab(eventType);
    setSelectorTouched(true);
    setNotesExpanded(
      eventType === "PIVOT" || Boolean(drafts[eventType]?.notes?.trim()),
    );
    setOutcomeExpanded(Boolean(drafts[eventType]?.outcome_value?.trim()));
    setSubmitError(null);
  }

  const moment = useMemo(() => {
    if (!options?.moments.length) return null;
    if (defaultMomentId) {
      return options.moments.find((m) => m.moment_id === defaultMomentId) ?? options.moments[0];
    }
    return (
      options.moments.find((m) => m.moment_type_code === "FUTURE_BUILDING") ?? options.moments[0]
    );
  }, [defaultMomentId, options]);

  const tabs = options?.tabs ?? [];
  const activeTab: PersonalQuickAddTab | undefined = tabs.find((t) => t.event_type === selectedTab);
  const tabFields =
    options?.metadata?.future_building_tabs?.find((t) => t.event_type === selectedTab) ??
    { event_type: selectedTab, field_groups: [] };

  const visibleGroups = tabFields.field_groups.filter((g) => {
    if (g.group_key === "notes") return false;
    if (g.group_key === "outcome_value" && !outcomeExpanded) return false;
    return true;
  });

  const submitEnabled =
    Boolean(moment) &&
    canSubmitFb(selectedTab, tabFields.field_groups, fieldValues, eventTitle) &&
    !submitting;

  const requiredHint = missingFbRequiredHint(
    selectedTab,
    tabFields.field_groups,
    fieldValues,
    eventTitle,
  );

  async function handleSubmit() {
    if (!moment || !submitEnabled || saveLatch.current) return;
    saveLatch.current = true;
    setSubmitting(true);
    setSubmitError(null);
    try {
      await createPersonalQuickAdd(
        {
          moment_id: moment.moment_id,
          event_type: selectedTab,
          event_title: eventTitle.trim(),
          future_building: buildFutureBuildingPayload(fieldValues),
        },
        { clientRequestId: clientRequestId.current },
      );
      invalidateAfterFutureBuildingQuickAdd();
      setToast({ message: fbSuccessMessage(selectedTab), tone: "success" });
      onSuccess?.();
      window.setTimeout(() => {
        onClose();
      }, 650);
    } catch (err) {
      const msg =
        err instanceof Error && err.message.toLowerCase().includes("offline")
          ? "You're offline. Check your connection and try again."
          : err instanceof Error && err.message.toLowerCase().includes("timeout")
            ? "Saving is taking longer than expected. Try again."
            : fbErrorMessage(selectedTab);
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
    // selectTab closes over drafts intentionally for notes expansion state
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

  if (!open) return null;

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
          <div
            className="shrink-0 border-b px-5 pb-3 pt-5"
            style={{ borderColor: colors.border }}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <h2
                  id={titleId}
                  style={{ ...personalTypography.heroTitle, color: colors.brandPrimary }}
                >
                  Build Momentum
                </h2>
                <p
                  className="mt-1"
                  style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}
                >
                  {FB_SHEET_SUPPORTING}
                </p>
              </div>
              <button
                ref={closeRef}
                type="button"
                onClick={onClose}
                aria-label="Close Build Momentum"
                className="rounded-lg px-2 py-1 text-lg leading-none"
                style={{ color: colors.textSecondary }}
              >
                ×
              </button>
            </div>

            <div
              role="tablist"
              aria-label="Momentum entry type"
              className="mt-4 flex gap-2 overflow-x-auto pb-1"
            >
              {tabs.map((tab, index) => {
                const active = tab.event_type === selectedTab;
                const fallback = fbSelectorFallback(tab.event_type);
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
                    className="min-w-[9.5rem] shrink-0 rounded-2xl border px-3 py-3 text-left transition-transform duration-200 hover:scale-[1.01] active:scale-95"
                    style={{
                      borderColor: active ? colors.brandPrimary : colors.border,
                      background: active ? "rgba(108, 78, 242, 0.12)" : "transparent",
                      minHeight: 48,
                    }}
                  >
                    <span
                      className="block text-sm font-semibold"
                      style={{ color: active ? colors.brandPrimary : colors.textPrimary }}
                    >
                      {tab.label || fallback.title}
                    </span>
                    <span
                      className="mt-0.5 block text-[11px] leading-snug"
                      style={{ color: colors.textSecondary }}
                    >
                      {blurb}
                    </span>
                  </button>
                );
              })}
            </div>
            {!selectorTouched ? (
              <p
                className="mt-2 text-xs"
                style={{ color: colors.textSecondary }}
              >
                {FB_SELECTOR_HELPER}
              </p>
            ) : null}
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-5">
            {loading && !options ? (
              <SkeletonQuickAddSheet />
            ) : error && !options ? (
              <p style={{ color: colors.error }}>{error}</p>
            ) : !moment ? (
              <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
                Activate a Future Building moment to use Quick Add.
              </p>
            ) : (
              <div className="space-y-4 pb-4">
                {activeTab ? (
                  <div className="space-y-1">
                    <h3
                      style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}
                    >
                      {activeTab.hero_title ?? activeTab.label}
                    </h3>
                    <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
                      {activeTab.hero_subtitle ?? activeTab.description}
                    </p>
                  </div>
                ) : null}

                <div className="space-y-2">
                  <label
                    htmlFor="fb-event-title"
                    style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}
                  >
                    {activeTab?.hero_subtitle ?? "What moved you forward?"}
                  </label>
                  <input
                    id="fb-event-title"
                    type="text"
                    value={eventTitle}
                    onChange={(e) => setField("event_title", e.target.value)}
                    placeholder={fbTitlePlaceholder(selectedTab)}
                    className="w-full rounded-xl border px-3 py-3 input-focus-glow"
                    style={{
                      borderColor: colors.border,
                      background: colors.surfaceContainerLowest ?? "#0e0d16",
                      color: colors.textPrimary,
                    }}
                  />
                </div>

                {options
                  ? visibleGroups.map((group) => (
                      <FieldGroup
                        key={group.group_key}
                        group={group}
                        value={fieldValues[group.group_key] ?? ""}
                        onChange={(value) => setField(group.group_key, value)}
                        colors={colors}
                        resolvedOptions={resolveFbFieldOptions(group, options, selectedTab)}
                      />
                    ))
                  : null}

                {selectedTab === "MILESTONE" && !outcomeExpanded ? (
                  <button
                    type="button"
                    onClick={() => setOutcomeExpanded(true)}
                    className="text-sm font-medium"
                    style={{ color: colors.brandPrimary }}
                  >
                    + Add measurable outcome
                  </button>
                ) : null}

                {selectedTab === "PIVOT" || notesExpanded ? (
                  <FieldGroup
                    group={{
                      group_key: "notes",
                      label: selectedTab === "PIVOT" ? "Notes (required)" : "Note — optional",
                      field_type: "textarea",
                    }}
                    value={fieldValues.notes ?? ""}
                    onChange={(value) => setField("notes", value)}
                    colors={colors}
                    resolvedOptions={[]}
                    compact
                    placeholder={
                      selectedTab === "PIVOT"
                        ? "Why did this change matter?"
                        : undefined
                    }
                  />
                ) : (
                  <button
                    type="button"
                    onClick={() => setNotesExpanded(true)}
                    className="text-sm font-medium"
                    style={{ color: colors.textSecondary }}
                  >
                    Add note — optional
                  </button>
                )}

                {activeTab?.teaches_items?.length &&
                !(selectedTab === "PIVOT" && requiredHint) ? (
                  <section
                    className="rounded-2xl border p-3"
                    style={{
                      borderColor: "rgba(108, 78, 242, 0.2)",
                      background: "rgba(108, 78, 242, 0.08)",
                    }}
                  >
                    <p
                      className="mb-2 text-xs font-semibold"
                      style={{ color: colors.brandPrimary }}
                    >
                      Possible impact
                    </p>
                    <ul className="space-y-1">
                      {activeTab.teaches_items.map((item) => (
                        <li
                          key={item}
                          style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}
                        >
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
            {requiredHint && !submitError ? (
              <p className="mb-2 text-sm" style={{ color: colors.textSecondary }}>
                {requiredHint}
              </p>
            ) : null}
            <button
              type="button"
              disabled={!submitEnabled}
              onClick={() => void handleSubmit()}
              aria-busy={submitting}
              className="w-full rounded-2xl py-3 font-semibold transition-transform duration-200 hover:scale-[1.02] active:scale-95"
              style={{
                background: colors.brandPrimaryContainer ?? colors.brandPrimary,
                color: colors.brandOnPrimary,
                opacity: !submitEnabled ? 0.55 : 1,
                minHeight: 48,
              }}
            >
              {submitting
                ? fbSavingLabel(selectedTab)
                : fbCtaLabel(selectedTab, activeTab?.cta_label)}
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

function FieldGroup({
  group,
  value,
  onChange,
  colors,
  resolvedOptions,
  compact,
  placeholder,
}: {
  group: PersonalFutureBuildingQuickAddFieldGroup;
  value: string;
  onChange: (value: string) => void;
  colors: ContextThemeTokens["colors"];
  resolvedOptions: { value: string; label: string }[];
  compact?: boolean;
  placeholder?: string;
}) {
  const labelStyle = { ...personalTypography.sectionHeader, color: colors.textSecondary };

  if (group.field_type === "amount") {
    return (
      <div className="space-y-2">
        <label style={labelStyle}>{group.label}</label>
        <div className="relative">
          <span
            className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-xl font-bold"
            style={{ color: colors.brandPrimary }}
          >
            ₹
          </span>
          <input
            type="number"
            inputMode="decimal"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="0.00"
            className="w-full rounded-2xl border-none py-4 pl-12 pr-4 text-2xl font-bold input-focus-glow"
            style={{
              background: colors.surfaceContainerLowest ?? "#0e0d16",
              color: colors.textPrimary,
            }}
          />
        </div>
      </div>
    );
  }

  if (
    group.field_type === "slider" ||
    group.field_type === "single_select" ||
    group.field_type === "chip_grid"
  ) {
    const opts = resolvedOptions.length ? resolvedOptions : group.options ?? [];
    if (!opts.length && group.group_key === "category_name") {
      return (
        <div className="space-y-2">
          <label style={labelStyle}>{group.label}</label>
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Category"
            className="w-full rounded-xl border px-3 py-2.5"
            style={{
              borderColor: colors.border,
              background: colors.surfaceContainerLowest ?? "#0e0d16",
              color: colors.textPrimary,
            }}
          />
        </div>
      );
    }
    return (
      <div className="space-y-2">
        <label style={labelStyle}>{group.label}</label>
        <div className="flex flex-wrap gap-2" role="group" aria-label={group.label}>
          {opts.map((opt) => {
            const selected = value === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                aria-pressed={selected}
                onClick={() => onChange(opt.value)}
                className="rounded-lg px-3 py-2 text-xs font-medium transition-transform duration-200 hover:scale-[1.02] active:scale-95"
                style={{
                  border: `1px solid ${selected ? colors.brandPrimary : colors.border}`,
                  background: selected ? "rgba(108, 78, 242, 0.15)" : "transparent",
                  color: selected ? colors.brandPrimary : colors.textSecondary,
                  minHeight: 40,
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

  if (group.field_type === "textarea") {
    return (
      <div className="space-y-2">
        <label style={labelStyle}>{group.label}</label>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={compact ? 2 : 3}
          placeholder={placeholder}
          className="w-full rounded-xl border p-3 input-focus-glow"
          style={{
            borderColor: colors.border,
            background: colors.surfaceContainerLowest ?? "#0e0d16",
            color: colors.textPrimary,
          }}
        />
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <label style={labelStyle}>{group.label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border px-3 py-2.5"
        style={{
          borderColor: colors.border,
          background: colors.surfaceContainerLowest ?? "#0e0d16",
          color: colors.textPrimary,
        }}
      />
    </div>
  );
}

export function isFutureBuildingQuickAddEventType(eventType?: string | null): boolean {
  return Boolean(eventType && FB_EVENT_TYPES.has(eventType.toUpperCase()));
}

export function shouldUseFutureBuildingQuickAdd(
  options: PersonalQuickAddOptionsResponse,
  initialEventType?: string | null,
): boolean {
  if (isFutureBuildingQuickAddEventType(initialEventType)) return true;
  if (options.metadata?.future_building_tabs?.length) return true;
  if (options.tabs?.[0]?.event_type === "CONTRIBUTION") {
    const onlyFb =
      options.moments.length > 0 &&
      options.moments.every((m) => m.moment_type_code === "FUTURE_BUILDING");
    if (onlyFb) return true;
  }
  return false;
}

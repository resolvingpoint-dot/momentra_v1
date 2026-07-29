"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import type { ContextThemeTokens } from "@/lib/contextTokens";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { SkeletonQuickAddSheet } from "@/components/personal/shared/skeleton/SkeletonBlocks";
import { AppToast } from "@/components/shared/AppToast";
import { useQuickAddOptions } from "@/hooks/useQuickAddOptions";
import {
  type PersonalEmotionalSecurityQuickAddFieldGroup,
  type PersonalQuickAddOptionsResponse,
  type PersonalQuickAddTab,
} from "@/lib/api/client";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import {
  RS_EVENT_TYPES,
  buildEmotionalSecurityPayload,
  canSubmitRelationships,
  normalizeRelationshipsEventType,
  rsErrorMessage,
  rsGuidingQuestion,
  rsSelectorBlurb,
  rsSuccessMessage,
  rsTitlePlaceholder,
} from "@/lib/personal/relationships/relationshipsQuickAddHelpers";

type Draft = {
  eventTitle: string;
  fields: Record<string, string>;
  spendingExpanded: boolean;
  notesExpanded: boolean;
};

const emptyDraft = (): Draft => ({
  eventTitle: "",
  fields: {},
  spendingExpanded: false,
  notesExpanded: false,
});

function isDraftDirty(draft: Draft): boolean {
  return (
    Boolean(draft.eventTitle.trim()) ||
    Object.values(draft.fields).some((v) => Boolean(v?.trim())) ||
    draft.spendingExpanded ||
    draft.notesExpanded
  );
}

type RelationshipsQuickAddSheetProps = {
  initialEventType?: string | null;
  defaultMomentId?: string | null;
  open?: boolean;
  onClose: () => void;
  onSuccess?: () => void;
};

export function RelationshipsQuickAddSheet({
  initialEventType,
  defaultMomentId,
  open = true,
  onClose,
  onSuccess,
}: RelationshipsQuickAddSheetProps) {
  const tokens = usePersonalDomainTokens();
  const { colors } = tokens;
  const { options, loading, error } = useQuickAddOptions({ momentId: defaultMomentId, enabled: open });

  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; tone: "success" | "error" } | null>(null);
  const [selectedTab, setSelectedTab] = useState("CONNECTION");
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [confirmClose, setConfirmClose] = useState(false);
  const savingRef = useRef(false);

  const dirty = useMemo(
    () => Object.values(drafts).some(isDraftDirty),
    [drafts],
  );

  function requestClose() {
    if (dirty && !submitting) {
      setConfirmClose(true);
      return;
    }
    onClose();
  }

  useEffect(() => {
    if (!options) return;
    const initial = initialEventType?.toUpperCase();
    if (initial && RS_EVENT_TYPES.has(initial)) {
      setSelectedTab(normalizeRelationshipsEventType(initial));
    } else if (options.tabs?.[0]?.event_type) {
      setSelectedTab(normalizeRelationshipsEventType(options.tabs[0].event_type));
    }
  }, [options, initialEventType]);

  const moment = useMemo(() => {
    if (!options?.moments.length) return null;
    if (defaultMomentId) {
      return options.moments.find((m) => m.moment_id === defaultMomentId) ?? options.moments[0];
    }
    return (
      options.moments.find(
        (m) => m.moment_type_code === "RELATIONSHIPS" || m.moment_type_code === "EMOTIONAL_SECURITY",
      ) ?? options.moments[0]
    );
  }, [defaultMomentId, options]);

  const tabs = options?.tabs ?? [];
  const activeTab: PersonalQuickAddTab | undefined = tabs.find(
    (t) => normalizeRelationshipsEventType(t.event_type) === selectedTab,
  );
  const tabFields =
    options?.metadata?.emotional_security_tabs?.find(
      (t) => normalizeRelationshipsEventType(t.event_type) === selectedTab,
    ) ?? { event_type: selectedTab, field_groups: [] };

  const draft = drafts[selectedTab] ?? emptyDraft();
  const submitEnabled =
    Boolean(moment) && canSubmitRelationships(selectedTab, draft.fields, draft.eventTitle);

  function updateDraft(patch: Partial<Draft>) {
    setDrafts((prev) => ({
      ...prev,
      [selectedTab]: { ...(prev[selectedTab] ?? emptyDraft()), ...patch },
    }));
  }

  function setField(key: string, value: string) {
    updateDraft({ fields: { ...draft.fields, [key]: value } });
  }

  async function handleSubmit() {
    if (!moment || !submitEnabled || savingRef.current) return;
    savingRef.current = true;
    setSubmitting(true);
    setSubmitError(null);
    const title = draft.eventTitle.trim();
    const fields = { ...draft.fields };
    if (!fields.notes?.trim()) fields.notes = title;
    try {
      await PersonalRepository.submitQuickAdd(
        {
          moment_id: moment.moment_id,
          event_type: selectedTab,
          event_title: title,
          emotional_security: buildEmotionalSecurityPayload(fields),
        },
        { momentTypeCode: "RELATIONSHIPS", momentId: moment.moment_id, tab: selectedTab },
      );
      setToast({ message: rsSuccessMessage(selectedTab), tone: "success" });
      onSuccess?.();
      setTimeout(() => onClose(), 350);
    } catch (err) {
      const message = err instanceof Error ? err.message : rsErrorMessage(selectedTab);
      setSubmitError(message);
      setToast({ message: rsErrorMessage(selectedTab), tone: "error" });
      setSubmitting(false);
      savingRef.current = false;
    }
  }

  const spendingKeys = new Set(["amount", "spend_category"]);
  const showSpending = selectedTab === "SHARED_EXPERIENCE" || selectedTab === "RELATIONSHIP_INVESTMENT";
  const coreGroups = tabFields.field_groups.filter(
    (g) => !spendingKeys.has(g.group_key) && g.group_key !== "notes",
  );
  const notesGroup = tabFields.field_groups.find((g) => g.group_key === "notes");

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 sm:items-center"
      role="dialog"
      aria-modal="true"
      onClick={requestClose}
    >
      <div
        className="flex max-h-[92dvh] w-full max-w-lg flex-col rounded-t-2xl border sm:rounded-2xl"
        style={{ borderColor: colors.border, background: colors.surface }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="shrink-0 border-b px-5 pb-3 pt-5" style={{ borderColor: colors.border }}>
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 style={{ ...personalTypography.heroTitle, color: colors.brandPrimary }}>
                Capture Relationships
              </h2>
              <p className="mt-1 text-xs" style={{ color: colors.textSecondary }}>
                Record the moments and actions that shape your connections.
              </p>
            </div>
            <button type="button" onClick={requestClose} aria-label="Close" className="min-h-11 px-2 text-lg">
              ×
            </button>
          </div>
          <p className="mt-3 text-xs font-medium" style={{ color: colors.textSecondary }}>
            Choose what you want to record.
          </p>
          <div className="mt-2 flex gap-2 overflow-x-auto pb-1">
            {tabs.map((tab) => {
              const code = normalizeRelationshipsEventType(tab.event_type);
              const active = code === selectedTab;
              return (
                <button
                  key={tab.event_type}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setSelectedTab(code)}
                  className="min-w-[148px] shrink-0 rounded-2xl border px-3 py-3 text-left"
                  style={{
                    borderColor: active ? colors.brandPrimary : colors.border,
                    background: active ? "rgba(108, 78, 242, 0.16)" : "rgba(255,255,255,0.03)",
                  }}
                >
                  <p className="text-sm font-semibold" style={{ color: active ? colors.textPrimary : colors.textSecondary }}>
                    {tab.label}
                  </p>
                  <p className="mt-1 text-[11px] leading-snug" style={{ color: colors.textSecondary }}>
                    {tab.description || rsSelectorBlurb(code)}
                  </p>
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto px-5 py-4">
          {loading ? <SkeletonQuickAddSheet /> : null}
          {error ? <p className="text-sm text-red-300">{error}</p> : null}
          {!loading && options ? (
            <>
              <div>
                <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
                  {activeTab?.hero_title ?? activeTab?.label ?? selectedTab}
                </h3>
                <p className="mt-1 text-sm font-medium" style={{ color: colors.brandPrimary }}>
                  {(activeTab as { guiding_question?: string } | undefined)?.guiding_question ??
                    rsGuidingQuestion(selectedTab)}
                </p>
                <p className="mt-1 text-xs" style={{ color: colors.textSecondary }}>
                  {activeTab?.hero_subtitle ?? activeTab?.description ?? rsSelectorBlurb(selectedTab)}
                </p>
              </div>

              <div className="space-y-2">
                <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>
                  {rsGuidingQuestion(selectedTab)}
                </label>
                <input
                  value={draft.eventTitle}
                  onChange={(e) => updateDraft({ eventTitle: e.target.value })}
                  placeholder={rsTitlePlaceholder(selectedTab)}
                  className="w-full rounded-xl border px-3 py-3 text-sm"
                  style={{
                    borderColor: colors.border,
                    background: colors.surfaceContainerLowest ?? "#0e0d16",
                    color: colors.textPrimary,
                  }}
                />
              </div>

              {coreGroups.map((group) => (
                <FieldGroup
                  key={group.group_key}
                  group={group}
                  value={draft.fields[group.group_key] ?? ""}
                  onChange={(v) => setField(group.group_key, v)}
                  colors={colors}
                />
              ))}

              {showSpending ? (
                <div className="space-y-3">
                  <button
                    type="button"
                    className="text-sm font-semibold"
                    style={{ color: colors.brandPrimary }}
                    onClick={() => updateDraft({ spendingExpanded: !draft.spendingExpanded })}
                  >
                    {draft.spendingExpanded ? "Hide spending details" : "+ Add spending details"}
                  </button>
                  {draft.spendingExpanded ? (
                    <>
                      <p className="text-xs" style={{ color: colors.textSecondary }}>
                        If you enter an amount, Momentra also logs a personal money event.
                      </p>
                      {tabFields.field_groups
                        .filter((g) => spendingKeys.has(g.group_key))
                        .map((group) => (
                          <FieldGroup
                            key={group.group_key}
                            group={group}
                            value={draft.fields[group.group_key] ?? ""}
                            onChange={(v) => setField(group.group_key, v)}
                            colors={colors}
                          />
                        ))}
                    </>
                  ) : null}
                </div>
              ) : null}

              {notesGroup ? (
                draft.notesExpanded || draft.fields.notes ? (
                  <FieldGroup
                    group={notesGroup}
                    value={draft.fields.notes ?? ""}
                    onChange={(v) => setField("notes", v)}
                    colors={colors}
                  />
                ) : (
                  <button
                    type="button"
                    className="text-sm font-semibold"
                    style={{ color: colors.brandPrimary }}
                    onClick={() => updateDraft({ notesExpanded: true })}
                  >
                    Add note — optional
                  </button>
                )
              ) : null}

              {activeTab?.teaches_items?.length ? (
                <section className="rounded-2xl border p-4" style={{ borderColor: colors.border }}>
                  <p className="text-[10px] font-bold uppercase tracking-wider" style={{ color: colors.textSecondary }}>
                    What Momentra may learn
                  </p>
                  <ul className="mt-2 space-y-1 text-xs" style={{ color: colors.textSecondary }}>
                    {activeTab.teaches_items.map((item) => (
                      <li key={item}>• {item}</li>
                    ))}
                  </ul>
                </section>
              ) : null}

              {submitError ? <p className="text-sm text-red-300">{submitError}</p> : null}
            </>
          ) : null}
        </div>

        <div className="shrink-0 border-t px-5 py-4" style={{ borderColor: colors.border }}>
          <button
            type="button"
            disabled={!submitEnabled || submitting}
            onClick={() => void handleSubmit()}
            className="w-full rounded-2xl py-4 text-sm font-bold disabled:opacity-50"
            style={{ background: colors.brandPrimary, color: colors.onPrimary }}
          >
            {submitting ? "Saving…" : activeTab?.cta_label ?? "Save Entry"}
          </button>
        </div>
      </div>

      <AppToast
        open={Boolean(toast)}
        message={toast?.message ?? ""}
        tone={toast?.tone ?? "success"}
        onDismiss={() => setToast(null)}
      />

      {confirmClose ? (
        <div
          className="absolute inset-0 z-10 flex items-center justify-center bg-black/40 px-6"
          role="alertdialog"
          aria-modal="true"
          aria-labelledby="rs-discard-title"
          onClick={(e) => e.stopPropagation()}
        >
          <div
            className="w-full max-w-sm rounded-2xl border p-5"
            style={{ borderColor: colors.border, background: colors.surface }}
          >
            <h3 id="rs-discard-title" style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
              Discard changes?
            </h3>
            <p className="mt-2 text-sm" style={{ color: colors.textSecondary }}>
              You have unsaved changes that will be lost.
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                className="min-h-11 rounded-xl px-3 text-sm"
                onClick={() => setConfirmClose(false)}
              >
                Keep editing
              </button>
              <button
                type="button"
                className="min-h-11 rounded-xl px-3 text-sm font-semibold"
                style={{ background: colors.brandPrimary, color: colors.onPrimary }}
                onClick={() => {
                  setConfirmClose(false);
                  onClose();
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

function FieldGroup({
  group,
  value,
  onChange,
  colors,
}: {
  group: PersonalEmotionalSecurityQuickAddFieldGroup;
  value: string;
  onChange: (value: string) => void;
  colors: ContextThemeTokens["colors"];
}) {
  const labelStyle = { ...personalTypography.sectionHeader, color: colors.textSecondary };

  if (group.field_type === "amount") {
    return (
      <div className="space-y-2">
        <label style={labelStyle}>{group.label}</label>
        <div className="relative">
          <span
            className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-2xl font-bold"
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
            className="w-full rounded-2xl border-none py-6 pl-12 pr-4 text-3xl font-bold"
            style={{ background: colors.surfaceContainerLowest ?? "#0e0d16", color: colors.textPrimary }}
          />
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
          rows={3}
          className="w-full rounded-xl border p-3"
          style={{
            borderColor: colors.border,
            background: colors.surfaceContainerLowest ?? "#0e0d16",
            color: colors.textPrimary,
          }}
        />
      </div>
    );
  }

  if (
    group.field_type === "slider" ||
    group.field_type === "single_select" ||
    group.field_type === "panel_select" ||
    group.field_type === "chip_grid" ||
    group.field_type === "icon_grid" ||
    group.field_type === "value_card"
  ) {
    const options = group.options ?? [];
    if (options.length === 0) {
      return (
        <div className="space-y-2">
          <label style={labelStyle}>{group.label}</label>
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full rounded-xl border px-3 py-3"
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
        <div className="flex flex-wrap gap-2" role="radiogroup" aria-label={group.label}>
          {options.map((opt) => {
            const selected = value === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                aria-pressed={selected}
                onClick={() => onChange(opt.value)}
                className="min-h-11 rounded-xl px-3 py-2 text-xs font-medium"
                style={{
                  border: `1px solid ${selected ? colors.brandPrimary : colors.border}`,
                  background: selected ? "rgba(108, 78, 242, 0.15)" : "transparent",
                  color: selected ? colors.brandPrimary : colors.textSecondary,
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

  return (
    <div className="space-y-2">
      <label style={labelStyle}>{group.label}</label>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-xl border px-3 py-3"
        style={{
          borderColor: colors.border,
          background: colors.surfaceContainerLowest ?? "#0e0d16",
          color: colors.textPrimary,
        }}
      />
    </div>
  );
}

export function isRelationshipsQuickAddEventType(eventType?: string | null): boolean {
  return Boolean(eventType && RS_EVENT_TYPES.has(eventType.toUpperCase()));
}

export function shouldUseRelationshipsQuickAdd(
  options: PersonalQuickAddOptionsResponse,
  initialEventType?: string | null,
): boolean {
  if (isRelationshipsQuickAddEventType(initialEventType)) return true;
  if (options.metadata?.emotional_security_tabs?.length) return true;
  if (options.tabs?.[0]?.event_type === "SHARED_EXPERIENCE") {
    const onlyRs =
      options.moments.length > 0 &&
      options.moments.every(
        (m) => m.moment_type_code === "RELATIONSHIPS" || m.moment_type_code === "EMOTIONAL_SECURITY",
      );
    if (onlyRs) return true;
  }
  return false;
}

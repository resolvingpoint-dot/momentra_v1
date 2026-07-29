"use client";

/**
 * Phase 2D — quarantined generic Group guided adapter.
 * Production routing uses SharedExperienceSetup / SharedPurchaseSetup / SharedLivingSetup.
 * Do not import from Group home or production setup modules.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { Loader2, Users } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { glassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { InviteMethodsPanel } from "@/components/group/invite/InviteMethodsPanel";
import { GuidedSetupShell } from "@/components/setup/GuidedSetupShell";
import { emitGuidedSetupAnalytics } from "@/components/setup/guidedSetupAnalytics";
import { useSetupFlow } from "@/hooks/useSetupFlow";
import type { PersonalSetupField } from "@/lib/api/personal";
import type { InviteDraft } from "@/lib/api/group";
import { MomentraAnalytics } from "@/lib/analytics";
import { GroupRepository } from "@/repositories/GroupRepository";
import { buildGroupLiveSummaryModel } from "@/lib/group/buildGroupLiveSummary";
import {
  GROUP_SETUP_COPY,
  groupGuidedSteps,
  groupSetupTemplate,
  groupTemplateForMomentType,
} from "@/lib/group/setupCatalog";

type GroupMomentSetupProps = {
  momentId: string;
  onClose: () => void;
  onActivated: () => void;
};

const EXPERIENCE_NAME_PLACEHOLDERS: Record<string, string> = {
  TRIP: "Goa Trip",
  TRIP_VACATION: "Goa Trip",
  EVENT: "Birthday Dinner",
  WEDDING: "Rahul & Priya Wedding",
  CELEBRATION: "Birthday Dinner",
  ACTIVITY: "Team Offsite",
  OFFICE_OUTING: "Team Offsite",
  CUSTOM: "Our shared experience",
};

const NAME_KEYS = new Set([
  "moment_name",
  "experience_name",
  "trip_name",
  "purchase_name",
  "home_name",
  "living_name",
]);

function answerString(
  answers: Record<string, string | string[]>,
  ...keys: string[]
): string {
  for (const key of keys) {
    const value = answers[key];
    if (typeof value === "string" && value.length > 0) return value;
  }
  return "";
}

function isEndBeforeStart(start: string, end: string): boolean {
  if (!start || !end) return false;
  return end < start;
}

function leftoverStepId(
  field: PersonalSetupField,
  peopleStepId: string | undefined,
  detailsStepId: string | undefined,
): string {
  const key = field.field_key.toLowerCase();
  if (
    peopleStepId &&
    (key.includes("participant") ||
      key.includes("member") ||
      key.includes("invite") ||
      key === "contributors")
  ) {
    return peopleStepId;
  }
  return detailsStepId ?? peopleStepId ?? "basics";
}

const CURRENCY_KEYS = new Set(["budget_currency", "currency_code", "operating_currency_code"]);
const BUDGET_KEYS = new Set([
  "estimated_budget",
  "budget_minor",
  "monthly_budget",
  "monthly_budget_minor",
  "expected_amount",
  "target_amount_minor",
]);
const SPLIT_KEYS = new Set(["split_style", "split_method", "payment_plan", "rent_split_style"]);

function catalogKeyMatches(catalogKey: string, fieldKey: string): boolean {
  if (catalogKey === fieldKey) return true;
  if (NAME_KEYS.has(catalogKey) && NAME_KEYS.has(fieldKey)) return true;
  if (CURRENCY_KEYS.has(catalogKey) && CURRENCY_KEYS.has(fieldKey)) return true;
  if (BUDGET_KEYS.has(catalogKey) && BUDGET_KEYS.has(fieldKey)) return true;
  if (SPLIT_KEYS.has(catalogKey) && SPLIT_KEYS.has(fieldKey)) return true;
  if (catalogKey === "experience_type" && ["experience_type", "experience_profile", "trip_style"].includes(fieldKey)) {
    return true;
  }
  if (catalogKey === "item_or_goal" && ["item_or_goal", "item_description"].includes(fieldKey)) {
    return true;
  }
  if (catalogKey === "decision_deadline" && ["decision_deadline", "target_date"].includes(fieldKey)) {
    return true;
  }
  if (catalogKey === "living_type" && ["living_type", "living_profile"].includes(fieldKey)) {
    return true;
  }
  if (catalogKey === "rules_or_notes" && ["rules_or_notes", "address_label", "description"].includes(fieldKey)) {
    return true;
  }
  return false;
}

function partitionFields(
  fields: PersonalSetupField[],
  catalogFieldKeys: string[][],
  stepIds: string[],
): PersonalSetupField[][] {
  const used = new Set<string>();
  const buckets: PersonalSetupField[][] = catalogFieldKeys.map((keys) => {
    const matched = fields.filter((f) => keys.some((k) => catalogKeyMatches(k, f.field_key)));
    matched.forEach((f) => used.add(f.field_key));
    return matched;
  });
  const leftover = fields.filter((f) => !used.has(f.field_key));
  if (leftover.length === 0) return buckets;

  const peopleStepId = stepIds.find((id) => id === "participants" || id === "members");
  const detailsStepId = stepIds.find(
    (id) =>
      id === "dates_money" ||
      id === "goal_rules" ||
      id === "budget_prefs" ||
      id === "details",
  );
  const basicsIdx = stepIds.indexOf("basics");

  for (const field of leftover) {
    const targetId = leftoverStepId(field, peopleStepId, detailsStepId);
    let idx = stepIds.indexOf(targetId);
    if (idx < 0) idx = detailsStepId ? stepIds.indexOf(detailsStepId) : 1;
    // Never dump unmatched API fields onto Basics — that bloats step 1 vs catalog.
    if (idx === basicsIdx || idx < 0) {
      idx = detailsStepId ? stepIds.indexOf(detailsStepId) : Math.min(1, buckets.length - 1);
    }
    if (idx < 0 || idx >= buckets.length) idx = Math.min(1, buckets.length - 1);
    buckets[idx] = [...buckets[idx], field];
  }
  return buckets;
}

export function GroupMomentSetup({ momentId, onClose, onActivated }: GroupMomentSetupProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const {
    setup,
    template,
    preview,
    answers,
    loading,
    submitting,
    error,
    canSubmit,
    saveStatus,
    updateAnswer,
    toggleMulti,
    flushPendingSave,
    requestPreview,
    submit,
  } = useSetupFlow(momentId);

  const templateId = groupTemplateForMomentType(setup?.moment_type_code);
  const catalog = groupSetupTemplate(templateId);
  const steps = useMemo(() => groupGuidedSteps(templateId), [templateId]);
  const [step, setStep] = useState(1);

  const experienceType = answerString(answers, "experience_type", "experience_profile", "trip_style");
  const startDate = answerString(answers, "start_date");
  const endDate = answerString(answers, "end_date");
  const dateRangeInvalid = isEndBeforeStart(startDate, endDate);
  const dateError = dateRangeInvalid ? "End date must be on or after start date." : null;
  const activateEnabled = canSubmit && !submitting && !dateRangeInvalid;
  const namePlaceholder =
    EXPERIENCE_NAME_PLACEHOLDERS[experienceType] ?? "Shared experience name";

  const fieldBuckets = useMemo(() => {
    if (!setup) return [[], [], [], []] as PersonalSetupField[][];
    const keys = catalog.steps.map((s) => ((s as { fields?: { key: string }[] }).fields ?? []).map((f) => f.key));
    const stepIds = catalog.steps.map((s) => s.id);
    return partitionFields(setup.fields, keys, stepIds);
  }, [setup, catalog.steps]);

  const liveSummary = useMemo(() => {
    return buildGroupLiveSummaryModel({
      templateId,
      answers,
      currentStep: step,
      totalSteps: steps.length,
      estimatedMinutes: GROUP_SETUP_COPY.estimated_minutes,
      memberCount: 0,
    });
  }, [answers, step, steps.length, templateId]);

  const onAnalytics = useCallback(
    (event: Parameters<typeof emitGuidedSetupAnalytics>[0]) => {
      emitGuidedSetupAnalytics(event, MomentraAnalytics);
    },
    [],
  );

  useEffect(() => {
    if (step === steps.length) void requestPreview();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- preview only when entering Review
  }, [step, steps.length]);

  async function handleSubmit() {
    if (dateRangeInvalid) return;
    const flushed = await flushPendingSave();
    if (!flushed) return;
    const ok = await submit();
    if (ok) onActivated();
  }

  async function go(next: number) {
    if (next > step && dateRangeInvalid && step === 2) return;
    const flushed = await flushPendingSave();
    if (!flushed) return;
    setStep(next);
  }

  if (loading || !setup) {
    return (
      <div
        className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-4 px-6"
        style={{ background: colors.background, color: colors.textPrimary }}
      >
        {loading ? (
          <Loader2 className="size-8 animate-spin opacity-70" />
        ) : (
          <>
            <p className="text-center text-sm" style={{ color: colors.error }}>
              {error ?? "Failed to load setup"}
            </p>
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl px-6 py-3 text-sm font-semibold"
              style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
            >
              Back
            </button>
          </>
        )}
      </div>
    );
  }

  const isReview = step >= steps.length;
  const stepFields = fieldBuckets[step - 1] ?? [];

  return (
    <GuidedSetupShell
      contextType="group"
      templateId={templateId}
      momentTypeCode={setup.moment_type_code}
      momentId={momentId}
      title={catalog.title}
      estimatedDuration={GROUP_SETUP_COPY.estimated_minutes}
      currentStep={step}
      steps={steps}
      saveState={saveStatus}
      canGoBack={step > 1}
      canContinue={!isReview}
      canPreview={isReview}
      liveSummary={liveSummary}
      contextHelp={steps[step - 1]?.description}
      footerPrimaryLabel={isReview ? (setup.cta_label ?? catalog.activate_cta) : "Continue"}
      error={error ?? dateError}
      submitting={submitting}
      canActivate={activateEnabled}
      onRetrySave={() => void flushPendingSave()}
      onBack={() => void go(step - 1)}
      onContinue={() => void go(step + 1)}
      onClose={onClose}
      onPreview={() => void requestPreview()}
      onActivate={() => void handleSubmit()}
      onAnalytics={onAnalytics}
    >
      <div className="space-y-6">
        <div className="flex items-center gap-2 text-[10px] font-bold tracking-widest opacity-60">
          <Users className="size-3" />
          {template?.hero.badge_label ?? "GROUP SETUP"}
        </div>

        {stepFields.map((field) => (
          <GroupFieldSection
            key={field.field_key}
            field={field}
            value={answers[field.field_key]}
            placeholder={
              field.field_key === "experience_name" || field.field_key === "trip_name"
                ? namePlaceholder
                : undefined
            }
            onChange={(value) => updateAnswer(field.field_key, value)}
            onToggle={(value) => toggleMulti(field.field_key, value)}
          />
        ))}

        {steps[step - 1]?.id === "participants" &&
        (setup.moment_type_code ?? "").toUpperCase() === "SHARED_EXPERIENCE" ? (
          <ParticipantsInviteSection momentId={momentId} />
        ) : null}

        {isReview && preview ? (
          <div className="rounded-2xl p-5" style={glassCardStyle(tokens)}>
            <h3 className="mb-2 text-lg font-semibold">Preview</h3>
            <p className="mb-3 text-sm opacity-80" style={{ color: colors.textSecondary }}>
              {preview.narrative}
            </p>
            <div className="flex flex-wrap gap-2">
              {preview.identity_chips.map((chip) => (
                <span
                  key={chip}
                  className="rounded-full px-3 py-1 text-xs"
                  style={{
                    background: `color-mix(in srgb, ${colors.primaryContainer} 30%, transparent)`,
                  }}
                >
                  {chip}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </GuidedSetupShell>
  );
}

function inputSurfaceStyle(colors: ReturnType<typeof useThemeTokens>["colors"]) {
  return {
    background: colors.surfaceContainer,
    color: colors.textPrimary,
    border: `1px solid color-mix(in srgb, ${colors.textSecondary} 35%, transparent)`,
  };
}

function GroupFieldSection({
  field,
  value,
  placeholder,
  onChange,
  onToggle,
}: {
  field: PersonalSetupField;
  value: string | string[] | undefined;
  placeholder?: string;
  onChange: (value: string) => void;
  onToggle: (value: string) => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const selected = typeof value === "string" ? value : "";
  const selectedMulti = Array.isArray(value) ? value : [];
  const fieldType = field.field_type;

  return (
    <section>
      <h3 className="mb-2 text-base font-semibold">
        {field.label}
        {field.required ? " *" : ""}
      </h3>
      {field.helper_text ? (
        <p className="mb-2 text-sm opacity-70" style={{ color: colors.textSecondary }}>
          {field.helper_text}
        </p>
      ) : null}

      {fieldType === "text" ||
      fieldType === "location" ||
      fieldType === "number" ||
      fieldType === "money" ||
      fieldType === "date" ? (
        <input
          type={
            fieldType === "date"
              ? "date"
              : fieldType === "number" || fieldType === "money"
                ? "number"
                : "text"
          }
          inputMode={fieldType === "number" || fieldType === "money" ? "decimal" : undefined}
          value={selected}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          className="w-full rounded-xl px-4 py-3 text-sm outline-none"
          style={inputSurfaceStyle(colors)}
        />
      ) : null}

      {fieldType === "single_select" ? (
        <div className="grid grid-cols-2 gap-2">
          {field.options?.map((option) => {
            const active = selected === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => onChange(option.value)}
                className="rounded-xl px-3 py-3 text-left text-sm font-medium"
                style={{
                  background: active
                    ? `color-mix(in srgb, ${colors.primaryContainer} 45%, transparent)`
                    : colors.surfaceContainer,
                  color: active ? colors.brandPrimary : colors.textPrimary,
                  border: active
                    ? `1px solid ${colors.brandPrimary}`
                    : `1px solid transparent`,
                }}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      ) : null}

      {fieldType === "multi_select" ? (
        <div className="flex flex-wrap gap-2">
          {field.options?.map((option) => {
            const active = selectedMulti.includes(option.value);
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => onToggle(option.value)}
                className="rounded-full px-3 py-2 text-sm"
                style={{
                  background: active
                    ? `color-mix(in srgb, ${colors.primaryContainer} 45%, transparent)`
                    : colors.surfaceContainer,
                  color: active ? colors.brandPrimary : colors.textSecondary,
                }}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      ) : null}
    </section>
  );
}

function ParticipantsInviteSection({ momentId }: { momentId: string }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [draft, setDraft] = useState<InviteDraft | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setLoadError(null);
    void GroupRepository.getInviteDraft(momentId)
      .then((result) => {
        if (!cancelled) {
          setDraft(result);
          setLoading(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setLoadError(err instanceof Error ? err.message : "Failed to load invite");
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [momentId]);

  return (
    <section className="rounded-2xl p-5" style={glassCardStyle(tokens)}>
      <h3 className="mb-1 text-base font-semibold">Invite participants</h3>
      <p className="mb-4 text-sm opacity-70" style={{ color: colors.textSecondary }}>
        Share a QR code or invite link — WhatsApp, Messages, and email are shortcuts.
      </p>

      {loading ? (
        <div className="flex items-center gap-2 text-sm opacity-70">
          <Loader2 className="size-4 animate-spin" />
          Loading invite…
        </div>
      ) : null}

      {loadError ? (
        <p className="text-sm" style={{ color: colors.error }}>
          {loadError}
        </p>
      ) : null}

      {draft ? (
        <InviteMethodsPanel momentId={momentId} draft={draft} onDraftChange={setDraft} />
      ) : null}
    </section>
  );
}


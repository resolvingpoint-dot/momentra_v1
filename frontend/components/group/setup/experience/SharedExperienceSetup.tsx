"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Loader2 } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { glassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { GroupSetupInviteSection } from "@/components/group/setup/shared/GroupSetupInviteSection";
import { GuidedSetupShell } from "@/components/setup/GuidedSetupShell";
import { SetupFieldRenderer } from "@/components/setup/SetupFieldRenderer";
import { SetupSectionCard } from "@/components/setup/shared/SetupSectionCard";
import { emitGuidedSetupAnalytics } from "@/components/setup/guidedSetupAnalytics";
import type { SetupControlType } from "@/components/setup/shared/setupControlTypes";
import { MomentraAnalytics } from "@/lib/analytics";
import { useSetupFlow } from "@/hooks/useSetupFlow";
import { buildGroupLiveSummaryModel } from "@/lib/group/buildGroupLiveSummary";
import {
  GROUP_SETUP_COPY,
  groupChoices,
  groupGuidedSteps,
  groupSetupTemplate,
} from "@/lib/group/setupCatalog";
import {
  GUIDED_CURRENCY_OPTIONS,
  GUIDED_CURRENCY_SUGGESTED,
} from "@/lib/setup/guidedIdentityOptions";

type Props = {
  momentId: string;
  onClose: () => void;
  onActivated: () => void;
};

const TEMPLATE_ID = "shared_experience" as const;
/** estimated_budget / target_amount_major are major units; SetupMoneyField uses minor. */
const MONEY_EXPONENT = 2;

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

function resolveFieldKey(
  catalogKey: string,
  available: Set<string>,
): string | null {
  if (available.has(catalogKey)) return catalogKey;
  const aliases: Record<string, string[]> = {
    experience_type: ["experience_type", "experience_profile", "trip_style"],
    experience_name: ["experience_name", "trip_name", "moment_name"],
    budget_currency: ["budget_currency", "currency_code", "operating_currency_code"],
    estimated_budget: ["estimated_budget", "budget_minor", "target_amount_minor"],
    split_style: ["split_style", "split_method"],
    participants: ["participants", "member_count"],
  };
  for (const alt of aliases[catalogKey] ?? []) {
    if (available.has(alt)) return alt;
  }
  return catalogKey;
}

function majorToMinor(major: string | number | null | undefined): number | null {
  if (major == null || major === "") return null;
  const n = typeof major === "number" ? major : Number(major);
  if (!Number.isFinite(n)) return null;
  return Math.round(n * 10 ** MONEY_EXPONENT);
}

function minorToMajorString(minor: number | null): string {
  if (minor == null) return "";
  const major = minor / 10 ** MONEY_EXPONENT;
  return String(major);
}

/**
 * Phase 2A — Shared Experience on GuidedSetupShell.
 * Catalog-driven presentation over useSetupFlow / SetupRepository (no new engine).
 */
export function SharedExperienceSetup({ momentId, onClose, onActivated }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const {
    setup,
    preview,
    answers,
    loading,
    submitting,
    error,
    canSubmit,
    saveStatus,
    updateAnswer,
    flushPendingSave,
    requestPreview,
    submit,
  } = useSetupFlow(momentId);

  const catalog = groupSetupTemplate(TEMPLATE_ID);
  const steps = useMemo(() => groupGuidedSteps(TEMPLATE_ID), []);
  const [step, setStep] = useState(1);
  const [activationSuccess, setActivationSuccess] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const availableKeys = useMemo(
    () => new Set((setup?.fields ?? []).map((f) => f.field_key)),
    [setup?.fields],
  );

  const experienceType = answerString(
    answers,
    "experience_type",
    "experience_profile",
    "trip_style",
  );
  const startDate = answerString(answers, "start_date");
  const endDate = answerString(answers, "end_date");
  const dateRangeInvalid = isEndBeforeStart(startDate, endDate);
  const dateError = dateRangeInvalid ? "End date must be on or after start date." : null;
  const currency = answerString(
    answers,
    "budget_currency",
    "currency_code",
    "operating_currency_code",
  ) || "INR";
  const namePlaceholder =
    EXPERIENCE_NAME_PLACEHOLDERS[experienceType] ?? "Shared experience name";

  const participantCount = useMemo(() => {
    const raw = answers.participants;
    if (typeof raw === "string" && raw.trim()) {
      const n = Number(raw);
      return Number.isFinite(n) ? n : 0;
    }
    return 0;
  }, [answers.participants]);

  const liveSummary = useMemo(
    () =>
      buildGroupLiveSummaryModel({
        templateId: TEMPLATE_ID,
        answers,
        currentStep: step,
        totalSteps: steps.length,
        estimatedMinutes: GROUP_SETUP_COPY.estimated_minutes,
        memberCount: participantCount,
      }),
    [answers, step, steps.length, participantCount],
  );

  const onAnalytics = useCallback(
    (event: Parameters<typeof emitGuidedSetupAnalytics>[0]) => {
      emitGuidedSetupAnalytics(event, MomentraAnalytics);
    },
    [],
  );

  useEffect(() => {
    if (step === steps.length) void requestPreview();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- preview only on Review
  }, [step, steps.length]);

  function validateStep(current: number): boolean {
    const errs: Record<string, string> = {};
    if (current === 1) {
      const name = answerString(answers, "experience_name", "trip_name", "moment_name");
      if (!name.trim()) errs.experience_name = "Required";
      if (!experienceType) errs.experience_type = "Required";
    }
    if (current === 2 && dateRangeInvalid) {
      errs.end_date = "End date must be on or after start date.";
    }
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function go(next: number) {
    const flushed = await flushPendingSave();
    if (!flushed) return;
    if (next > step && !validateStep(step)) return;
    setStep(next);
    setFieldErrors({});
  }

  async function handleActivate() {
    if (dateRangeInvalid) return;
    const flushed = await flushPendingSave();
    if (!flushed) return;
    const ok = await submit();
    if (ok) setActivationSuccess(true);
  }

  function setAnswer(catalogKey: string, value: string) {
    const key = resolveFieldKey(catalogKey, availableKeys) ?? catalogKey;
    updateAnswer(key, value);
    if (catalogKey === "experience_name" || catalogKey === "trip_name") {
      if (!answerString(answers, "moment_name")) updateAnswer("moment_name", value);
    }
    if (catalogKey === "estimated_budget") {
      updateAnswer("target_amount_major", value);
    }
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
  const activateEnabled = canSubmit && !submitting && !dateRangeInvalid;
  const stepMeta = catalog.steps[step - 1];
  const catalogFields =
    ((stepMeta as { fields?: Array<Record<string, unknown>> } | undefined)?.fields ??
      []) as Array<{
      key: string;
      label: string;
      control: string;
      choices?: string;
      suggested?: string[];
      maxLength?: number;
      optional?: boolean;
      helper?: string;
    }>;

  return (
    <GuidedSetupShell
      contextType="group"
      templateId={TEMPLATE_ID}
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
      tip={
        step === 1
          ? "Pick the experience type first — the name placeholder updates to match."
          : step === 3
            ? "Invite now or later. Owner stays on the moment after activation."
            : null
      }
      footerPrimaryLabel={isReview ? catalog.activate_cta : "Continue"}
      error={error ?? dateError}
      submitting={submitting}
      canActivate={activateEnabled}
      activationSuccess={activationSuccess}
      activationSuccessMessage={catalog.activation_success}
      onActivationSuccessDone={onActivated}
      onRetrySave={() => void flushPendingSave()}
      onBack={() => void go(step - 1)}
      onContinue={() => void go(step + 1)}
      onClose={onClose}
      onPreview={() => void requestPreview()}
      onActivate={() => void handleActivate()}
      onAnalytics={onAnalytics}
    >
      <div className="space-y-4">
        {step === 1 ? (
          <SetupSectionCard>
            <SetupFieldRenderer
              control="cards"
              label="What kind of experience is this?"
              value={experienceType}
              options={groupChoices("experience_type")}
              error={fieldErrors.experience_type}
              onChange={(v) => setAnswer("experience_type", v)}
            />
            <SetupFieldRenderer
              control="text"
              label="What should we call this experience?"
              value={answerString(answers, "experience_name", "trip_name", "moment_name")}
              placeholder={namePlaceholder}
              maxLength={60}
              examples={[namePlaceholder]}
              error={fieldErrors.experience_name}
              onChange={(v) => setAnswer("experience_name", v)}
            />
          </SetupSectionCard>
        ) : null}

        {step === 2 ? (
          <SetupSectionCard>
            {(() => {
              const dateFields = catalogFields.filter((f) => f.control === "date");
              const otherFields = catalogFields.filter((f) => f.control !== "date");
              return (
                <>
                  {dateFields.length > 0 ? (
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                      {dateFields.map((field) => {
                        const key = resolveFieldKey(field.key, availableKeys) ?? field.key;
                        const raw = answers[key];
                        const stringValue = typeof raw === "string" ? raw : "";
                        return (
                          <SetupFieldRenderer
                            key={field.key}
                            control="date"
                            label={field.label}
                            optionalLabel={field.optional ? "Optional" : undefined}
                            value={stringValue}
                            error={field.key === "end_date" ? fieldErrors.end_date : null}
                            onChange={(v) => setAnswer(field.key, v)}
                          />
                        );
                      })}
                    </div>
                  ) : null}
                  {otherFields.map((field) => {
              const control = (field.control === "chips" && field.key === "experience_type"
                ? "cards"
                : field.control) as SetupControlType;
              const key = resolveFieldKey(field.key, availableKeys) ?? field.key;
              const raw = answers[key];
              const stringValue = typeof raw === "string" ? raw : "";

              if (control === "money") {
                return (
                  <SetupFieldRenderer
                    key={field.key}
                    control="money"
                    label={field.label}
                    optionalLabel={field.optional ? "Optional" : undefined}
                    helper={field.helper}
                    amountMinor={majorToMinor(stringValue)}
                    currencyCode={currency}
                    onChangeAmount={(minor) =>
                      setAnswer(field.key, minorToMajorString(minor))
                    }
                  />
                );
              }

              if (control === "suggested_picker") {
                return (
                  <SetupFieldRenderer
                    key={field.key}
                    control="suggested_picker"
                    label={field.label}
                    value={stringValue || currency}
                    options={GUIDED_CURRENCY_OPTIONS}
                    suggested={[...GUIDED_CURRENCY_SUGGESTED]}
                    onChange={(v) => setAnswer(field.key, v)}
                  />
                );
              }

              if (control === "chips" || control === "cards") {
                const choiceKey = (field.choices ?? field.key) as keyof typeof GROUP_SETUP_COPY.choices;
                const options = groupChoices(choiceKey);
                return (
                  <SetupFieldRenderer
                    key={field.key}
                    control={control === "cards" ? "cards" : "chips"}
                    label={field.label}
                    optionalLabel={field.optional ? "Optional" : undefined}
                    value={stringValue}
                    options={options}
                    onChange={(v) => setAnswer(field.key, v)}
                  />
                );
              }

              return (
                <SetupFieldRenderer
                  key={field.key}
                  control="text"
                  label={field.label}
                  optionalLabel={field.optional ? "Optional" : undefined}
                  value={stringValue}
                  maxLength={field.maxLength}
                  onChange={(v) => setAnswer(field.key, v)}
                />
              );
                  })}
                </>
              );
            })()}
          </SetupSectionCard>
        ) : null}

        {step === 3 ? (
          <>
            <SetupSectionCard>
              <SetupFieldRenderer
                control="text"
                label="How many people are joining?"
                optionalLabel="Optional"
                value={answerString(answers, "participants")}
                placeholder="e.g. 6"
                onChange={(v) => setAnswer("participants", v)}
              />
            </SetupSectionCard>
            <GroupSetupInviteSection
              momentId={momentId}
              title="Invite participants"
              helper="Share a QR code or invite link — WhatsApp, Messages, and email are shortcuts."
            />
          </>
        ) : null}

        {isReview ? (
          <div className="space-y-4">
            {preview ? (
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
            ) : (
              <p className="text-sm opacity-60">Loading preview…</p>
            )}
          </div>
        ) : null}
      </div>
    </GuidedSetupShell>
  );
}

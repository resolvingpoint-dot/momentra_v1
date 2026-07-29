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
import { MomentraAnalytics } from "@/lib/analytics";
import { useSetupFlow } from "@/hooks/useSetupFlow";
import { buildGroupLiveSummaryModel } from "@/lib/group/buildGroupLiveSummary";
import {
  GROUP_SETUP_COPY,
  groupChoices,
  groupChoiceLabel,
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

const TEMPLATE_ID = "shared_living" as const;
const MONEY_EXPONENT = 2;

const NAME_PLACEHOLDERS: Record<string, string> = {
  FLATMATES: "Jubilee Hills Flatmates",
  FAMILY_HOUSEHOLD: "Malla Family Home",
  COLIVING: "Apartment 504",
  CUSTOM_LIVING: "Shared House",
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

function resolveFieldKey(catalogKey: string, available: Set<string>): string {
  if (available.has(catalogKey)) return catalogKey;
  const aliases: Record<string, string[]> = {
    living_type: ["living_type", "living_profile"],
    home_name: ["home_name", "living_name", "moment_name"],
    monthly_budget: ["monthly_budget", "monthly_budget_major"],
    currency_code: ["currency_code", "budget_currency"],
    rent_split_style: ["rent_split_style", "management"],
    rules_or_notes: ["rules_or_notes", "description"],
    members: ["members", "expected_residents"],
  };
  for (const alt of aliases[catalogKey] ?? []) {
    if (available.has(alt)) return alt;
  }
  return catalogKey;
}

/** monthly_budget / monthly_budget_major are major units; SetupMoneyField uses minor. */
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
 * Phase 2C — Shared Living on GuidedSetupShell.
 * Catalog-driven presentation over useSetupFlow / SetupRepository (no new engine).
 */
export function SharedLivingSetup({ momentId, onClose, onActivated }: Props) {
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

  const livingType = answerString(answers, "living_type", "living_profile");
  const currency =
    answerString(answers, "currency_code", "budget_currency") || "INR";
  const namePlaceholder =
    NAME_PLACEHOLDERS[livingType] ?? "What should we call this home?";

  const residentCount = useMemo(() => {
    const raw = answerString(answers, "members", "expected_residents");
    if (!raw.trim()) return 0;
    const n = Number(raw);
    return Number.isFinite(n) ? n : 0;
  }, [answers]);

  const liveSummary = useMemo(
    () =>
      buildGroupLiveSummaryModel({
        templateId: TEMPLATE_ID,
        answers,
        currentStep: step,
        totalSteps: steps.length,
        estimatedMinutes: GROUP_SETUP_COPY.estimated_minutes,
        memberCount: residentCount,
      }),
    [answers, step, steps.length, residentCount],
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

  function setAnswer(catalogKey: string, value: string) {
    const key = resolveFieldKey(catalogKey, availableKeys);
    updateAnswer(key, value);
    if (catalogKey === "living_type") {
      updateAnswer("living_profile", value);
    }
    if (catalogKey === "home_name") {
      updateAnswer("living_name", value);
      updateAnswer("moment_name", value);
    }
    if (catalogKey === "monthly_budget") {
      updateAnswer("monthly_budget_major", value);
    }
    if (catalogKey === "rent_split_style") {
      updateAnswer("management", value);
    }
    if (catalogKey === "rules_or_notes") {
      updateAnswer("description", value);
    }
    if (catalogKey === "members") {
      updateAnswer("expected_residents", value);
    }
  }

  function validateStep(current: number): boolean {
    const errs: Record<string, string> = {};
    if (current === 1) {
      if (!livingType) errs.living_type = "Required";
      const name = answerString(answers, "home_name", "living_name", "moment_name");
      if (!name.trim()) errs.home_name = "Required";
    }
    if (current === 2) {
      if (!answerString(answers, "rent_split_style", "management")) {
        errs.rent_split_style = "Required";
      }
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
    const flushed = await flushPendingSave();
    if (!flushed) return;
    const ok = await submit();
    if (ok) setActivationSuccess(true);
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
  const activateEnabled = canSubmit && !submitting;

  const homeName = answerString(answers, "home_name", "living_name", "moment_name");
  const rentSplit = answerString(answers, "rent_split_style", "management");
  const chores = answerString(answers, "chores_style");
  const budgetMajor = answerString(answers, "monthly_budget", "monthly_budget_major");
  const rules = answerString(answers, "rules_or_notes", "description");

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
          ? "Pick the living type first — the name placeholder updates to match."
          : step === 2
            ? "Budget is optional planning context — it does not lock residents into fixed amounts."
            : step === 3
              ? "Invite housemates now or later. You remain the household admin after activation."
              : null
      }
      footerPrimaryLabel={isReview ? catalog.activate_cta : "Continue"}
      error={error}
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
              label="What kind of shared home is this?"
              value={livingType}
              options={groupChoices("living_type")}
              error={fieldErrors.living_type}
              onChange={(v) => setAnswer("living_type", v)}
            />
            <SetupFieldRenderer
              control="text"
              label="What should we call this home?"
              helper="How this home appears in Momentra."
              value={homeName}
              placeholder={namePlaceholder}
              maxLength={60}
              examples={[
                "Apartment 504",
                "Malla Family Home",
                "Jubilee Hills Flatmates",
              ]}
              error={fieldErrors.home_name}
              onChange={(v) => setAnswer("home_name", v)}
            />
          </SetupSectionCard>
        ) : null}

        {step === 2 ? (
          <SetupSectionCard>
            <SetupFieldRenderer
              control="money"
              label="About how much is the monthly household budget?"
              helper="Enter the monthly target in normal currency units."
              optionalLabel="Optional"
              amountMinor={majorToMinor(budgetMajor)}
              currencyCode={currency}
              explainer={{
                title: "Monthly household budget",
                body: "An optional planning amount for shared living costs. It does not automatically charge residents.",
              }}
              onChangeAmount={(minor) =>
                setAnswer("monthly_budget", minorToMajorString(minor))
              }
            />
            <SetupFieldRenderer
              control="suggested_picker"
              label="What currency should we use by default?"
              value={currency}
              options={GUIDED_CURRENCY_OPTIONS}
              suggested={[...GUIDED_CURRENCY_SUGGESTED]}
              onChange={(v) => setAnswer("currency_code", v)}
            />
            <SetupFieldRenderer
              control="chips"
              label="Can members log expenses in other currencies?"
              optionalLabel="Optional"
              value={answerString(answers, "allow_multi_currency") || "true"}
              options={groupChoices("allow_multi_currency")}
              explainer={{
                title: "Multi-currency",
                body: "Use this when household expenses may be recorded in more than one currency.",
              }}
              onChange={(v) => setAnswer("allow_multi_currency", v)}
            />
            <SetupFieldRenderer
              control="cards"
              label="How should rent and shared costs be split?"
              value={rentSplit}
              options={groupChoices("rent_split_style")}
              error={fieldErrors.rent_split_style}
              explainer={{
                title: "Rent cycle / cost split",
                body: "How rent and recurring shared costs are divided or managed among residents.",
              }}
              onChange={(v) => setAnswer("rent_split_style", v)}
            />
            <SetupFieldRenderer
              control="chips"
              label="How do you want to handle chores?"
              optionalLabel="Optional"
              value={chores}
              options={groupChoices("chores_style")}
              explainer={{
                title: "House responsibilities",
                body: "How chores and household responsibilities are shared, rotated, or assigned.",
              }}
              onChange={(v) => setAnswer("chores_style", v)}
            />
            <SetupFieldRenderer
              control="text"
              label="Any house rules or notes?"
              optionalLabel="Optional"
              helper="Optional house rules residents can see later."
              value={rules}
              placeholder="Quiet hours after 10pm, shared kitchen cleaning…"
              onChange={(v) => setAnswer("rules_or_notes", v)}
            />
          </SetupSectionCard>
        ) : null}

        {step === 3 ? (
          <>
            <SetupSectionCard>
              <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
                You remain the household admin. Invite housemates now or later — the creator
                stays on the home after activation.
              </p>
              <SetupFieldRenderer
                control="text"
                label="How many people live here?"
                optionalLabel="Optional"
                helper="Optional count. Invite people with the panel below."
                value={answerString(answers, "members", "expected_residents")}
                placeholder="e.g. 3"
                onChange={(v) => setAnswer("members", v)}
              />
              {rentSplit ? (
                <p className="text-xs opacity-60">
                  Cost split: {groupChoiceLabel("rent_split_style", rentSplit)}
                </p>
              ) : null}
            </SetupSectionCard>
            <GroupSetupInviteSection
              momentId={momentId}
              title="Invite housemates"
              helper="Share a QR code or invite link — WhatsApp, Messages, and email are shortcuts."
            />
          </>
        ) : null}

        {isReview ? (
          <div className="space-y-4">
            <div className="rounded-2xl p-5" style={glassCardStyle(tokens)}>
              <h3 className="mb-3 text-lg font-semibold">Review your shared living</h3>
              <dl className="space-y-2 text-sm">
                {[
                  {
                    label: "Home",
                    value: groupChoiceLabel("living_type", livingType),
                  },
                  { label: "Name", value: homeName },
                  {
                    label: "Budget",
                    value: budgetMajor ? `${currency} ${budgetMajor}` : "",
                  },
                  { label: "Currency", value: currency },
                  {
                    label: "Cost split",
                    value: groupChoiceLabel("rent_split_style", rentSplit),
                  },
                  {
                    label: "Chores",
                    value: groupChoiceLabel("chores_style", chores),
                  },
                  { label: "Rules", value: rules },
                  {
                    label: "Residents",
                    value: answerString(answers, "members", "expected_residents"),
                  },
                ]
                  .filter((r) => r.value)
                  .map((row) => (
                    <div key={row.label} className="flex justify-between gap-3">
                      <dt className="opacity-60">{row.label}</dt>
                      <dd className="max-w-[60%] truncate text-right font-medium">{row.value}</dd>
                    </div>
                  ))}
              </dl>
            </div>
            {preview ? (
              <div className="rounded-2xl p-5" style={glassCardStyle(tokens)}>
                <h3 className="mb-2 text-lg font-semibold">Server preview</h3>
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

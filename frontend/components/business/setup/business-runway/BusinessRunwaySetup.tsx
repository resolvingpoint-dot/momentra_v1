"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { BusinessSetupShell } from "@/components/business/setup/BusinessSetupShell";
import { BusinessSetupSkeleton } from "@/components/business/setup/BusinessSetupSkeleton";
import { SetupAdvancedDisclosure } from "@/components/business/setup/shared/SetupAdvancedDisclosure";
import { SetupChoiceCards } from "@/components/business/setup/shared/SetupChoiceCards";
import { SetupChoiceChips } from "@/components/business/setup/shared/SetupChoiceChips";
import { SetupInviteButton } from "@/components/business/setup/shared/SetupInviteSheet";
import { SetupLiveSummary } from "@/components/business/setup/shared/SetupLiveSummary";
import { SetupMoneyField } from "@/components/business/setup/shared/SetupMoneyField";
import { SetupMultiCards } from "@/components/business/setup/shared/SetupMultiCards";
import { SetupMultiChips } from "@/components/business/setup/shared/SetupMultiChips";
import { SetupPercentField } from "@/components/business/setup/shared/SetupPercentField";
import { SetupReviewSummary } from "@/components/business/setup/shared/SetupReviewSummary";
import { SetupSearchPicker } from "@/components/business/setup/shared/SetupSearchPicker";
import { SetupSectionCard } from "@/components/business/setup/shared/SetupSectionCard";
import { SetupTextInput } from "@/components/business/setup/shared/SetupTextInput";
import { SetupToggleReveal } from "@/components/business/setup/shared/SetupToggleReveal";
import { useBusinessSetupFlow } from "@/hooks/useBusinessSetupFlow";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { buildBusinessLiveSummary } from "@/lib/business/buildBusinessLiveSummary";
import { setupExplainer } from "@/lib/business/setupExplainers";
import {
  BUSINESS_SETUP_COPY,
  choiceLabel,
  roleDescription,
  setupChoices,
  setupStepMeta,
  setupTemplate,
  SETUP_COUNTRY_FALLBACK,
  SETUP_CURRENCY_FALLBACK,
  SETUP_LOCALE_FALLBACK,
  SETUP_TIMEZONE_FALLBACK,
  SETUP_ESTIMATED_MINUTES,
  businessGuidedSteps,
} from "@/lib/business/setupCatalog";
import {
  estimateRunwayMonths,
  formatRunwayEstimatePrimary,
} from "@/lib/business/runwayEstimate";
import type { BusinessSetupState } from "@/lib/api/business";
import { markBusinessSetupFirstPaint } from "@/lib/telemetry/businessSetupTelemetry";
import { SuggestedChipsPicker } from "@/components/setup/shared/SuggestedChipsPicker";

export type RunwayMemberDraft = {
  local_id: string;
  user_id?: string | null;
  name: string;
  email?: string | null;
  phone?: string | null;
  role: string;
  permission_profile: string;
  permission_version: number;
  invite_method: string;
  invite_status: string;
  is_finance_lead: boolean;
  is_operations_lead: boolean;
  is_advisor: boolean;
  is_observer: boolean;
};

type Props = {
  momentId: string;
  onClose: () => void;
  onActivated: () => void;
  onSetupReady?: () => void;
  initialSetup?: BusinessSetupState | null;
};

const META = setupTemplate("business_runway");
const GOAL_PRESETS = setupChoices("runway_goal_presets").map((c) => c.value);
const ALERT_PRESETS = setupChoices("alert_threshold_presets").map((c) => c.value);

function newLocalId() {
  return `m-${Math.random().toString(36).slice(2, 10)}`;
}

function roleFlags(role: string) {
  return {
    is_finance_lead: role === "FINANCE_LEAD",
    is_operations_lead: role === "OPERATIONS_LEAD",
    is_advisor: role === "ADVISOR",
    is_observer: role === "OBSERVER",
  };
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((v) => String(v)).filter(Boolean);
}

function asInt(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

function memberOptionValue(m: RunwayMemberDraft) {
  return m.user_id || m.local_id;
}

function memberDisplayName(m: RunwayMemberDraft) {
  const name = (m.name || "").trim();
  if (!name || name === "Owner" || name === "Team owner") {
    return m.role === "OWNER" ? "You" : m.email || "Member";
  }
  return name;
}

function memberPickerLabel(m: RunwayMemberDraft) {
  return `${memberDisplayName(m)} · ${choiceLabel("runway_roles", m.role)}`;
}

function monthsChipValue(months: unknown, presets: string[]): string {
  if (months == null || months === "") return "";
  const s = String(months);
  if (presets.includes(s) && s !== "CUSTOM") return s;
  return "CUSTOM";
}

function formatMoneyDisplay(amountMinor: unknown, currencyCode: string): string {
  const n = asInt(amountMinor);
  if (n == null) return "";
  const major = n / 100;
  return `${currencyCode} ${major.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  })}`;
}

export function BusinessRunwaySetup({
  momentId,
  onClose,
  onActivated,
  onSetupReady,
  initialSetup,
}: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const {
    setup,
    preview,
    answers,
    loading,
    saveStatus,
    submitting,
    error,
    updateAnswer,
    updateAnswers,
    setProgress,
    flushPendingSave,
    requestPreview,
    activate,
  } = useBusinessSetupFlow(momentId, { initialSetup });

  const guidedSteps = useMemo(() => businessGuidedSteps("business_runway"), []);
  const [step, setStep] = useState(setup?.progress?.current_step ?? 1);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [activationSuccess, setActivationSuccess] = useState(false);
  const paintedRef = useRef(false);
  const readyNotifiedRef = useRef(false);

  const members = useMemo((): RunwayMemberDraft[] => {
    const raw = (answers.members as RunwayMemberDraft[] | undefined) ?? [];
    return Array.isArray(raw) ? raw : [];
  }, [answers.members]);

  const owner = members.find((m) => m.role === "OWNER");
  const ready = Boolean(setup) && !loading;
  const interactionsDisabled = !ready;
  const stepMeta = setupStepMeta("business_runway", step);
  const currency = String(answers.operating_currency_code ?? "INR");
  const fundingSources = asStringList(answers.funding_sources);
  const burnCategories = asStringList(answers.burn_categories);
  const revenueStatus = String(answers.revenue_status ?? "");
  const hideRevenueAmounts = revenueStatus === "NO_REVENUE";

  const goalChip = monthsChipValue(answers.runway_goal_months, GOAL_PRESETS);
  const alertChip = monthsChipValue(answers.runway_alert_threshold_months, ALERT_PRESETS);

  const runwayEstimate = useMemo(
    () =>
      estimateRunwayMonths({
        currentCashMinor: asInt(answers.current_cash_minor),
        monthlyBurnMinor: asInt(answers.monthly_burn_minor),
        estimatedMonthlyRevenueMinor: asInt(answers.estimated_monthly_revenue_minor),
        collectionRatePercent: asInt(answers.collection_rate_percent),
        revenueStatus,
      }),
    [
      answers.current_cash_minor,
      answers.monthly_burn_minor,
      answers.estimated_monthly_revenue_minor,
      answers.collection_rate_percent,
      revenueStatus,
    ],
  );

  const anyRunwayApproval =
    Boolean(answers.approval_required_for_funding_changes) ||
    Boolean(answers.approval_required_for_cash_adjustments) ||
    Boolean(answers.approval_required_for_large_expenses) ||
    Boolean(answers.approval_required_for_threshold_changes);

  const memberValues = useMemo(
    () => new Set(members.map((m) => memberOptionValue(m)).filter(Boolean)),
    [members],
  );

  useEffect(() => {
    if (!anyRunwayApproval) return;
    const ownerMember = members.find((m) => m.role === "OWNER");
    const ownerValue = ownerMember ? memberOptionValue(ownerMember) : null;
    if (!ownerValue) return;
    const current = String(answers.approval_owner_id ?? "").trim();
    if (!current || !memberValues.has(current)) {
      updateAnswer("approval_owner_id", ownerValue);
    }
  }, [
    anyRunwayApproval,
    members,
    memberValues,
    answers.approval_owner_id,
    updateAnswer,
  ]);

  useEffect(() => {
    if (paintedRef.current) return;
    paintedRef.current = true;
    markBusinessSetupFirstPaint();
  }, []);

  useEffect(() => {
    if (!setup || readyNotifiedRef.current) return;
    readyNotifiedRef.current = true;
    onSetupReady?.();
  }, [setup, onSetupReady]);

  useEffect(() => {
    if (!setup || (setup.progress?.current_step ?? 1) !== 4) return;
    void requestPreview();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- seed/resume path only
  }, [setup?.moment_id]);

  useEffect(() => {
    if (!setup?.progress?.current_step) return;
    setStep(setup.progress.current_step);
  }, [setup?.moment_id, setup?.progress?.current_step]);

  if (error && !setup) {
    return (
      <div
        className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-3 px-6"
        style={{ background: colors.background, color: colors.textPrimary }}
      >
        <p className="text-center text-sm" style={{ color: colors.error }} role="alert">
          {error}
        </p>
        <button
          type="button"
          className="rounded-xl px-4 py-2.5 text-sm font-semibold"
          style={{ background: colors.surfaceContainer }}
          onClick={onClose}
        >
          Close
        </button>
      </div>
    );
  }

  function validateStep(current: number): boolean {
    const errs: Record<string, string> = {};
    if (current === 1) {
      if (!String(answers.moment_name ?? "").trim()) errs.moment_name = "Required";
      if (!String(answers.runway_name ?? "").trim()) errs.runway_name = "Required";
      if (!answers.business_stage) errs.business_stage = "Required";
      if (!answers.operating_currency_code) errs.operating_currency_code = "Required";
      if (asInt(answers.runway_goal_months) == null || (asInt(answers.runway_goal_months) ?? 0) <= 0) {
        errs.runway_goal_months = "Required";
      }
      if (!String(answers.timezone ?? "").trim()) errs.timezone = "Required";
    } else if (current === 2) {
      if (answers.current_cash_minor == null || Number(answers.current_cash_minor) < 0) {
        errs.current_cash_minor = "Enter available cash (0 or more)";
      }
      if (answers.monthly_burn_minor == null || Number(answers.monthly_burn_minor) < 0) {
        errs.monthly_burn_minor = "Enter monthly spending (0 or more)";
      }
      if (!answers.revenue_status) errs.revenue_status = "Required";
      if (
        answers.runway_alert_threshold_months == null ||
        Number(answers.runway_alert_threshold_months) <= 0
      ) {
        errs.runway_alert_threshold_months = "Required";
      }
    } else if (current === 3) {
      for (const m of members) {
        if (m.role === "OWNER") continue;
        if (!String(m.name ?? "").trim()) {
          errs[`member_name_${m.local_id}`] = "Name required";
        }
      }
    }
    setFieldErrors(errs);
    if (Object.keys(errs).length > 0) {
      window.requestAnimationFrame(() => {
        document.querySelector('[role="alert"]')?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      });
      return false;
    }
    return true;
  }

  const go = async (next: number) => {
    if (interactionsDisabled) return;
    const flushed = await flushPendingSave();
    if (!flushed) return;
    if (next > step && !validateStep(step)) return;
    const completed = Array.from({ length: Math.max(0, next - 1) }, (_, i) => i + 1);
    setStep(next);
    setFieldErrors({});
    await setProgress(next, completed);
    if (next === 4) await requestPreview();
  };

  const addMember = () => {
    if (interactionsDisabled) return;
    const next: RunwayMemberDraft = {
      local_id: newLocalId(),
      user_id: null,
      name: "",
      email: "",
      phone: "",
      role: "FOUNDER",
      permission_profile: "FOUNDER_V1",
      permission_version: 1,
      invite_method: "EMAIL",
      invite_status: "DRAFT",
      ...roleFlags("FOUNDER"),
    };
    updateAnswers({ members: [...members, next] });
  };

  const patchMember = (localId: string, patch: Partial<RunwayMemberDraft>) => {
    if (interactionsDisabled) return;
    updateAnswers({
      members: members.map((m) => {
        if (m.local_id !== localId) return m;
        const next = { ...m, ...patch };
        if (patch.role) {
          Object.assign(next, roleFlags(patch.role), {
            permission_profile: `${patch.role}_V1`,
          });
        }
        return next;
      }),
    });
  };

  const removeMember = (localId: string) => {
    if (interactionsDisabled) return;
    const target = members.find((m) => m.local_id === localId);
    if (target?.role === "OWNER") return;
    updateAnswers({ members: members.filter((m) => m.local_id !== localId) });
  };

  const reviewBlocks = [
    {
      title: "Runway basics",
      rows: [
        { label: "Moment", value: String(answers.moment_name ?? "") },
        { label: "Runway", value: String(answers.runway_name ?? "") },
        {
          label: "Stage",
          value: choiceLabel("business_stage", String(answers.business_stage ?? "")),
        },
        { label: "Currency", value: currency },
        {
          label: "Goal",
          value:
            asInt(answers.runway_goal_months) == null
              ? ""
              : `${answers.runway_goal_months} months`,
        },
      ],
    },
    {
      title: "Financial picture",
      rows: [
        {
          label: "Available cash",
          value: formatMoneyDisplay(answers.current_cash_minor, currency),
        },
        {
          label: "Monthly spending",
          value: formatMoneyDisplay(answers.monthly_burn_minor, currency),
        },
        {
          label: "Revenue stage",
          value: choiceLabel("revenue_status", revenueStatus),
        },
        ...(hideRevenueAmounts
          ? []
          : [
              {
                label: "Expected revenue",
                value: formatMoneyDisplay(answers.estimated_monthly_revenue_minor, currency),
              },
              {
                label: "Collection rate",
                value:
                  asInt(answers.collection_rate_percent) == null
                    ? ""
                    : `${answers.collection_rate_percent}%`,
              },
            ]),
        {
          label: "Revenue model",
          value: choiceLabel("revenue_model", String(answers.revenue_model ?? "")),
        },
        {
          label: "Alert below",
          value:
            asInt(answers.runway_alert_threshold_months) == null
              ? ""
              : `${answers.runway_alert_threshold_months} months`,
        },
        {
          label: "Funding",
          value: fundingSources
            .map((s) => choiceLabel("funding_sources", s))
            .filter(Boolean)
            .join(", "),
        },
        {
          label: "Burn categories",
          value: burnCategories
            .map((s) => choiceLabel("burn_categories", s))
            .filter(Boolean)
            .join(", "),
        },
        {
          label: "Estimated runway",
          value: formatRunwayEstimatePrimary(runwayEstimate),
        },
      ],
    },
    {
      title: "People",
      rows: members.map((m) => ({
        label: m.name || "Member",
        value: `${choiceLabel("runway_roles", m.role)}${m.role === "OWNER" ? " · Full access" : ""}`,
      })),
    },
  ];

  const warnings = [...(preview?.warnings ?? [])];

  const liveSummary = [
    ...buildBusinessLiveSummary({
      templateId: "business_runway",
      answers,
      currentStep: step,
      totalSteps: guidedSteps.length,
      estimatedMinutes: SETUP_ESTIMATED_MINUTES,
      memberCount: members.length,
    }),
    {
      label: "Runway estimate",
      value: formatRunwayEstimatePrimary(runwayEstimate),
    },
  ].filter((r) => r.value);

  return (
    <BusinessSetupShell
      contextType="business"
      templateId="business_runway"
      momentTypeCode={setup?.moment_type_code}
      momentId={momentId}
      title={META.title}
      steps={guidedSteps}
      currentStep={step}
      totalSteps={guidedSteps.length}
      saveStatus={saveStatus}
      liveSummary={liveSummary}
      contextHelp={stepMeta?.intro}
      tip={
        step === 2
          ? "Your runway estimate updates locally as you enter cash, burn, and collection rate."
          : null
      }
      error={error}
      submitting={submitting}
      canActivate={preview?.activation_ready === true}
      interactionsDisabled={interactionsDisabled}
      activationSuccess={activationSuccess}
      activationSuccessMessage={META.activation_success}
      activateLabel={META.activate_cta}
      onActivationSuccessDone={onActivated}
      onClose={onClose}
      onRetrySave={() => void flushPendingSave()}
      onBack={step > 1 && ready ? () => void go(step - 1) : undefined}
      onNext={step < 4 && ready ? () => void go(step + 1) : undefined}
      onPreview={step === 4 && ready ? () => void requestPreview() : undefined}
      onActivate={
        step === 4 && ready
          ? async () => {
              const flushed = await flushPendingSave();
              if (!flushed) return;
              const ok = await activate();
              if (ok) setActivationSuccess(true);
            }
          : undefined
      }
    >
      {!ready ? (
        <BusinessSetupSkeleton rows={5} />
      ) : (
        <div className="space-y-8">
          {step === 1 ? (
            <>
              <SetupSectionCard title="Runway basics">
                <SetupTextInput
                  label="What should we call this moment?"
                  helper="How this runway chapter appears in Momentra."
                  placeholder="Acme Runway"
                  maxLength={60}
                  value={String(answers.moment_name ?? "")}
                  error={fieldErrors.moment_name}
                  onChange={(v) => updateAnswer("moment_name", v)}
                />
                <SetupTextInput
                  label="Runway name"
                  helper="The business or venture this runway tracks."
                  maxLength={60}
                  value={String(answers.runway_name ?? "")}
                  error={fieldErrors.runway_name}
                  onChange={(v) => {
                    updateAnswer("runway_name", v);
                    if (!answers.moment_name) updateAnswer("moment_name", v);
                  }}
                />
                <SetupChoiceCards
                  label="Where is the business today?"
                  value={String(answers.business_stage ?? "")}
                  options={setupChoices("business_stage").filter((c) => c.value !== "CUSTOM")}
                  error={fieldErrors.business_stage}
                  onChange={(v) => updateAnswer("business_stage", v)}
                />
                <SuggestedChipsPicker
                  label="Operating currency"
                  value={currency}
                  options={SETUP_CURRENCY_FALLBACK.map((c) => ({
                    value: c.value,
                    label: c.label,
                  }))}
                  suggested={["INR", "USD", "EUR", "GBP"]}
                  error={fieldErrors.operating_currency_code}
                  onChange={(v) => updateAnswer("operating_currency_code", v)}
                />
                <SetupChoiceChips
                  label="How many months of runway do you want?"
                  value={goalChip}
                  options={setupChoices("runway_goal_presets")}
                  error={fieldErrors.runway_goal_months}
                  onChange={(v) => {
                    if (v === "CUSTOM") {
                      if (goalChip !== "CUSTOM") updateAnswer("runway_goal_months", null);
                      return;
                    }
                    updateAnswer("runway_goal_months", Number(v));
                  }}
                />
                {goalChip === "CUSTOM" ? (
                  <SetupTextInput
                    label="Custom runway goal (months)"
                    inputMode="numeric"
                    value={
                      answers.runway_goal_months == null
                        ? ""
                        : String(answers.runway_goal_months)
                    }
                    error={fieldErrors.runway_goal_months}
                    onChange={(v) =>
                      updateAnswer("runway_goal_months", v.trim() === "" ? null : Number(v))
                    }
                  />
                ) : null}
              </SetupSectionCard>
              <SetupAdvancedDisclosure
                title={BUSINESS_SETUP_COPY.shared.regional_section.title}
                helper={BUSINESS_SETUP_COPY.shared.regional_section.helper}
              >
                <SetupSearchPicker
                  label="Country"
                  value={String(answers.country_code ?? "")}
                  options={SETUP_COUNTRY_FALLBACK}
                  onChange={(v) => updateAnswer("country_code", v)}
                />
                <SetupSearchPicker
                  label="Language and format"
                  value={String(answers.locale ?? "")}
                  options={SETUP_LOCALE_FALLBACK}
                  onChange={(v) => updateAnswer("locale", v)}
                />
                <SetupSearchPicker
                  label="Timezone"
                  value={String(answers.timezone ?? "")}
                  options={SETUP_TIMEZONE_FALLBACK}
                  error={fieldErrors.timezone}
                  onChange={(v) => updateAnswer("timezone", v)}
                />
                <SetupToggleReveal
                  label="Allow multi-currency tracking"
                  checked={Boolean(answers.allow_multi_currency)}
                  onChange={(v) => updateAnswer("allow_multi_currency", v)}
                />
              </SetupAdvancedDisclosure>
              {owner ? (
                <p
                  className="rounded-xl px-3 py-2 text-xs opacity-70"
                  style={{ background: colors.surfaceContainer }}
                >
                  {owner.name || "You"} · Owner · Full access
                </p>
              ) : null}
            </>
          ) : null}

          {step === 2 ? (
            <>
              <SetupSectionCard title="Cash today">
                <SetupMoneyField
                  label="Available operating cash"
                  helper="Include cash that is currently available to operate the business."
                  amountMinor={
                    answers.current_cash_minor == null
                      ? null
                      : Number(answers.current_cash_minor)
                  }
                  currencyCode={currency}
                  error={fieldErrors.current_cash_minor}
                  onChange={(v) => updateAnswer("current_cash_minor", v)}
                />
                <SetupMoneyField
                  label="Typical monthly spending"
                  helper="Enter the typical amount the business spends each month."
                  amountMinor={
                    answers.monthly_burn_minor == null
                      ? null
                      : Number(answers.monthly_burn_minor)
                  }
                  currencyCode={currency}
                  error={fieldErrors.monthly_burn_minor}
                  onChange={(v) => updateAnswer("monthly_burn_minor", v)}
                />
              </SetupSectionCard>

              <SetupSectionCard title="Revenue">
                <SetupChoiceChips
                  label="Current revenue stage"
                  value={revenueStatus}
                  options={setupChoices("revenue_status").filter((c) => c.value !== "CUSTOM")}
                  error={fieldErrors.revenue_status}
                  onChange={(v) => updateAnswer("revenue_status", v)}
                />
                {!hideRevenueAmounts ? (
                  <>
                    <SetupMoneyField
                      label="Expected monthly revenue"
                      amountMinor={
                        answers.estimated_monthly_revenue_minor == null
                          ? null
                          : Number(answers.estimated_monthly_revenue_minor)
                      }
                      currencyCode={currency}
                      onChange={(v) => updateAnswer("estimated_monthly_revenue_minor", v)}
                    />
                    <SetupPercentField
                      label="Payment collection rate"
                      helper="What percentage of expected revenue actually reaches your account?"
                      value={asInt(answers.collection_rate_percent)}
                      explainer={setupExplainer("collection_rate_percent")}
                      onChange={(v) => updateAnswer("collection_rate_percent", v)}
                    />
                  </>
                ) : null}
                <SetupChoiceCards
                  label="Revenue model"
                  value={String(answers.revenue_model ?? "")}
                  options={setupChoices("revenue_model").filter((c) => c.value !== "CUSTOM")}
                  explainer={setupExplainer("revenue_model")}
                  onChange={(v) => updateAnswer("revenue_model", v)}
                />
              </SetupSectionCard>

              <SetupSectionCard title="Risk and funding">
                <SetupChoiceChips
                  label="Warn me when runway falls below"
                  helper="Get alerted before cash runway gets critically short."
                  value={alertChip}
                  options={setupChoices("alert_threshold_presets")}
                  explainer={setupExplainer("runway_alert_threshold_months")}
                  error={fieldErrors.runway_alert_threshold_months}
                  onChange={(v) => {
                    if (v === "CUSTOM") {
                      if (alertChip !== "CUSTOM") {
                        updateAnswer("runway_alert_threshold_months", null);
                      }
                      return;
                    }
                    updateAnswer("runway_alert_threshold_months", Number(v));
                  }}
                />
                {alertChip === "CUSTOM" ? (
                  <SetupTextInput
                    label="Custom alert threshold (months)"
                    inputMode="numeric"
                    error={fieldErrors.runway_alert_threshold_months}
                    value={
                      answers.runway_alert_threshold_months == null
                        ? ""
                        : String(answers.runway_alert_threshold_months)
                    }
                    onChange={(v) =>
                      updateAnswer(
                        "runway_alert_threshold_months",
                        v.trim() === "" ? null : Number(v),
                      )
                    }
                  />
                ) : null}
                <SetupMultiCards
                  label="How is the business funded?"
                  values={fundingSources}
                  options={setupChoices("funding_sources")}
                  explainer={setupExplainer("funding_sources")}
                  onChange={(v) => updateAnswer("funding_sources", v)}
                />
                <SetupMultiChips
                  label="Where does spending go?"
                  values={burnCategories}
                  options={setupChoices("burn_categories")}
                  onChange={(v) => updateAnswer("burn_categories", v)}
                />
              </SetupSectionCard>

              <SetupLiveSummary
                title="Estimated runway"
                primary={formatRunwayEstimatePrimary(runwayEstimate)}
                detail={runwayEstimate.detail}
              />
            </>
          ) : null}

          {step === 3 ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="text-sm opacity-70">
                  Owner is locked. Add people who own cash, burn, and approvals.
                </p>
                <button
                  type="button"
                  className="rounded-xl px-3 py-2 text-sm font-semibold"
                  style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
                  onClick={addMember}
                >
                  Add member
                </button>
              </div>
              {members.map((m) => {
                const locked = m.role === "OWNER";
                const roleDesc = roleDescription("runway_roles", m.role);
                return (
                  <div
                    key={m.local_id}
                    className="space-y-3 rounded-2xl border p-4"
                    style={{
                      borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
                      background: colors.surfaceContainer,
                    }}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-semibold">
                          {m.name || (locked ? "You" : "New member")}
                        </p>
                        <p className="text-xs opacity-60">
                          {choiceLabel("runway_roles", m.role)}
                          {roleDesc ? ` · ${roleDesc}` : ""}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        {!locked ? (
                          <SetupInviteButton
                            memberName={m.name}
                            method={m.invite_method}
                            momentId={momentId}
                            localId={m.local_id}
                            memberEmail={m.email}
                            memberPhone={m.phone}
                            onBeforeInvite={flushPendingSave}
                            onEmailRequired={() =>
                              setFieldErrors((prev) => ({
                                ...prev,
                                [`member_email_${m.local_id}`]: "Email required to invite",
                              }))
                            }
                            onSelect={(method) =>
                              patchMember(m.local_id, { invite_method: method })
                            }
                          />
                        ) : null}
                        {!locked ? (
                          <button
                            type="button"
                            className="text-xs"
                            style={{ color: colors.error }}
                            onClick={() => removeMember(m.local_id)}
                          >
                            Remove
                          </button>
                        ) : null}
                      </div>
                    </div>
                    {!locked ? (
                      <>
                        <SetupTextInput
                          label="Name"
                          value={m.name}
                          error={fieldErrors[`member_name_${m.local_id}`]}
                          onChange={(v) => patchMember(m.local_id, { name: v })}
                        />
                        <SetupTextInput
                          label="Email"
                          optionalLabel="Optional"
                          value={m.email ?? ""}
                          error={fieldErrors[`member_email_${m.local_id}`]}
                          onChange={(v) => {
                            setFieldErrors((prev) => {
                              const next = { ...prev };
                              delete next[`member_email_${m.local_id}`];
                              return next;
                            });
                            patchMember(m.local_id, { email: v });
                          }}
                        />
                        <SetupChoiceChips
                          label="Role"
                          value={m.role}
                          options={setupChoices("runway_roles").filter(
                            (r) => r.value !== "OWNER",
                          )}
                          onChange={(v) => patchMember(m.local_id, { role: v })}
                        />
                      </>
                    ) : null}
                  </div>
                );
              })}
              <SetupSectionCard title="Visibility">
                <SetupChoiceChips
                  label="Visibility"
                  value={String(answers.visibility ?? "TEAM")}
                  options={setupChoices("visibility_leadership")}
                  onChange={(v) => updateAnswer("visibility", v)}
                />
              </SetupSectionCard>
            </div>
          ) : null}

          {step === 4 ? (
            <>
              {preview?.blocking_errors?.length ? (
                <ul
                  className="rounded-xl px-3 py-2 text-sm"
                  style={{ background: "rgba(239,68,68,0.12)", color: colors.error }}
                >
                  {preview.blocking_errors.map((e) => (
                    <li key={e}>{e}</li>
                  ))}
                </ul>
              ) : null}
              <SetupReviewSummary blocks={reviewBlocks} warnings={warnings} />
              <SetupSectionCard title="Governance">
                <SetupToggleReveal
                  label="Approval for funding changes"
                  checked={Boolean(answers.approval_required_for_funding_changes)}
                  onChange={(v) => updateAnswer("approval_required_for_funding_changes", v)}
                />
                <SetupToggleReveal
                  label="Approval for cash adjustments"
                  checked={Boolean(answers.approval_required_for_cash_adjustments)}
                  onChange={(v) => updateAnswer("approval_required_for_cash_adjustments", v)}
                />
                <SetupToggleReveal
                  label="Approval for large expenses"
                  checked={Boolean(answers.approval_required_for_large_expenses)}
                  onChange={(v) => updateAnswer("approval_required_for_large_expenses", v)}
                >
                  <SetupMoneyField
                    label="Large expense threshold"
                    amountMinor={
                      answers.large_expense_threshold_minor == null
                        ? null
                        : Number(answers.large_expense_threshold_minor)
                    }
                    currencyCode={currency}
                    onChange={(v) => updateAnswer("large_expense_threshold_minor", v)}
                  />
                </SetupToggleReveal>
                <SetupToggleReveal
                  label="Approval for threshold changes"
                  checked={Boolean(answers.approval_required_for_threshold_changes)}
                  onChange={(v) => updateAnswer("approval_required_for_threshold_changes", v)}
                />
                {anyRunwayApproval ? (
                  <SetupSearchPicker
                    label="Approval owner"
                    value={String(answers.approval_owner_id ?? "")}
                    options={members.map((m) => ({
                      value: memberOptionValue(m),
                      label: memberPickerLabel(m),
                    }))}
                    appendValueToLabel={false}
                    showOptionValue={false}
                    onChange={(v) => updateAnswer("approval_owner_id", v || null)}
                  />
                ) : null}
              </SetupSectionCard>
              <div className="space-y-3">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={Boolean(answers.invite_on_activation ?? true)}
                    onChange={(e) => updateAnswer("invite_on_activation", e.target.checked)}
                  />
                  Send invites on activation
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={Boolean(answers.notify_members ?? true)}
                    onChange={(e) => updateAnswer("notify_members", e.target.checked)}
                  />
                  Notify members
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={Boolean(answers.confirm_financial_inputs ?? true)}
                    onChange={(e) =>
                      updateAnswer("confirm_financial_inputs", e.target.checked)
                    }
                  />
                  Confirm financial inputs
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={Boolean(answers.confirm_governance ?? true)}
                    onChange={(e) => updateAnswer("confirm_governance", e.target.checked)}
                  />
                  Confirm governance
                </label>
              </div>
            </>
          ) : null}
        </div>
      )}
    </BusinessSetupShell>
  );
}

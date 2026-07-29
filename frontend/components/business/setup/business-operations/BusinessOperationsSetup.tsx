"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { BusinessSetupShell } from "@/components/business/setup/BusinessSetupShell";
import { BusinessSetupSkeleton } from "@/components/business/setup/BusinessSetupSkeleton";
import {
  BudgetAllocationEditor,
  type BudgetAllocationDraft,
} from "@/components/business/setup/business-operations/BudgetAllocationEditor";
import { SetupAdvancedDisclosure } from "@/components/business/setup/shared/SetupAdvancedDisclosure";
import { SetupChoiceCards } from "@/components/business/setup/shared/SetupChoiceCards";
import { SetupChoiceChips } from "@/components/business/setup/shared/SetupChoiceChips";
import { SetupInviteButton } from "@/components/business/setup/shared/SetupInviteSheet";
import { SetupMoneyField } from "@/components/business/setup/shared/SetupMoneyField";
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
import { formatMinor } from "@/lib/reference_data/money";
import { getReferenceData, loadReferenceData } from "@/lib/reference_data/referenceDataStore";
import type { CurrencyReference } from "@/lib/reference_data/types";
import type { BusinessSetupState } from "@/lib/api/business";
import { markBusinessSetupFirstPaint } from "@/lib/telemetry/businessSetupTelemetry";
import { SuggestedChipsPicker } from "@/components/setup/shared/SuggestedChipsPicker";

export type OperationsMemberDraft = {
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
  is_approver: boolean;
  is_budget_controller: boolean;
  is_operations_lead: boolean;
  is_vendor_manager: boolean;
  is_observer: boolean;
};

type Props = {
  momentId: string;
  onClose: () => void;
  onActivated: () => void;
  onSetupReady?: () => void;
  initialSetup?: BusinessSetupState | null;
};

const META = setupTemplate("business_operations");

const APPROVAL_MODELS_NEEDING_OWNER = new Set([
  "OWNER_ONLY",
  "SINGLE_APPROVER",
  "MULTI_APPROVER",
  "THRESHOLD_BASED",
  "ROLE_BASED",
]);

const APPROVAL_MODELS_NEEDING_THRESHOLD = new Set(["THRESHOLD_BASED"]);

function newLocalId() {
  return `m-${Math.random().toString(36).slice(2, 10)}`;
}

function roleFlags(role: string) {
  return {
    is_approver: role === "APPROVER",
    is_budget_controller: role === "BUDGET_CONTROLLER" || role === "FINANCE_LEAD",
    is_operations_lead: role === "OPERATIONS_LEAD",
    is_vendor_manager: role === "VENDOR_MANAGER",
    is_observer: role === "OBSERVER",
  };
}

function asInt(value: unknown): number | null {
  if (value === null || value === undefined || value === "") return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((v) => String(v)).filter(Boolean);
}

function memberOptionValue(m: OperationsMemberDraft) {
  return m.user_id || m.local_id;
}

function memberDisplayName(m: OperationsMemberDraft) {
  const name = (m.name || "").trim();
  if (!name || name === "Owner" || name === "Team owner") {
    return m.role === "OWNER" ? "You" : m.email || "Member";
  }
  return name;
}

function memberPickerLabel(m: OperationsMemberDraft) {
  return `${memberDisplayName(m)} · ${choiceLabel("ops_roles", m.role)}`;
}

function formatBudgetDisplay(amountMinor: number | null, currencyCode: string): string {
  if (amountMinor == null) return "";
  return formatMinor(
    amountMinor,
    { code: currencyCode, minor_unit: 2, symbol: currencyCode },
    "en-IN",
  );
}

export function BusinessOperationsSetup({
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

  const guidedSteps = useMemo(() => businessGuidedSteps("business_operations"), []);
  const [step, setStep] = useState(setup?.progress?.current_step ?? 1);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [activationSuccess, setActivationSuccess] = useState(false);
  const paintedRef = useRef(false);
  const readyNotifiedRef = useRef(false);
  const defaultsSeededRef = useRef(false);
  const [currencies, setCurrencies] = useState<CurrencyReference[]>(
    () => getReferenceData()?.currencies ?? [],
  );

  const members = useMemo((): OperationsMemberDraft[] => {
    const raw = (answers.members as OperationsMemberDraft[] | undefined) ?? [];
    return Array.isArray(raw) ? raw : [];
  }, [answers.members]);

  const allocations = useMemo((): BudgetAllocationDraft[] => {
    const raw = (answers.budget_allocations as BudgetAllocationDraft[] | undefined) ?? [];
    return Array.isArray(raw) ? raw : [];
  }, [answers.budget_allocations]);

  const owner = members.find((m) => m.role === "OWNER");
  const ready = Boolean(setup) && !loading;
  const interactionsDisabled = !ready;
  const stepMeta = setupStepMeta("business_operations", step);
  const currency = String(
    answers.operating_currency_code ?? answers.default_currency_code ?? "INR",
  );
  const allocationMode =
    String(answers.allocation_mode ?? "FIXED_AMOUNT").toUpperCase() === "PERCENTAGE"
      ? "PERCENTAGE"
      : "FIXED_AMOUNT";
  const monthlyBudget = asInt(answers.monthly_budget_minor) ?? 0;
  const approvalModel = String(answers.approval_model ?? "NONE");
  const needsApprovalOwner = APPROVAL_MODELS_NEEDING_OWNER.has(approvalModel);
  const needsThreshold = APPROVAL_MODELS_NEEDING_THRESHOLD.has(approvalModel);
  const secondaryApproverIds = asStringList(answers.secondary_approver_ids);
  const memberValues = useMemo(
    () => new Set(members.map((m) => memberOptionValue(m)).filter(Boolean)),
    [members],
  );

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

  useEffect(() => {
    void loadReferenceData()
      .then((data) => {
        setCurrencies(data.currencies ?? []);
      })
      .catch(() => {
        setCurrencies(getReferenceData()?.currencies ?? []);
      });
  }, []);

  useEffect(() => {
    if (!setup || defaultsSeededRef.current) return;
    defaultsSeededRef.current = true;
    const patch: Record<string, unknown> = {};
    for (const key of [
      "confirm_budget",
      "confirm_allocations",
      "confirm_governance",
      "confirm_members",
      "confirm_alerts",
      "invite_on_activation",
      "notify_members",
    ] as const) {
      if (answers[key] === undefined) patch[key] = true;
    }
    if (answers.allocation_mode === undefined) patch.allocation_mode = "FIXED_AMOUNT";
    if (answers.approval_model === undefined) patch.approval_model = "NONE";
    if (answers.monitoring_level === undefined) patch.monitoring_level = "STANDARD";
    if (Object.keys(patch).length) updateAnswers(patch);
  }, [setup, answers, updateAnswers]);

  useEffect(() => {
    const ownerMember = members.find((m) => m.role === "OWNER");
    const ownerValue = ownerMember ? memberOptionValue(ownerMember) : null;
    if (!ownerValue) return;
    const patch: Record<string, unknown> = {};
    if (needsApprovalOwner) {
      const current = String(answers.approval_owner_id ?? "").trim();
      if (!current || !memberValues.has(current)) {
        patch.approval_owner_id = ownerValue;
      }
    }
    const escalation = String(answers.escalation_contact_id ?? "").trim();
    if (!escalation || !memberValues.has(escalation)) {
      patch.escalation_contact_id = ownerValue;
    }
    if (Object.keys(patch).length === 0) return;
    updateAnswers(patch);
  }, [
    needsApprovalOwner,
    members,
    memberValues,
    answers.approval_owner_id,
    answers.escalation_contact_id,
    updateAnswers,
  ]);

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
      if (!String(answers.operations_name ?? "").trim()) errs.operations_name = "Required";
      if (!answers.operations_scope) errs.operations_scope = "Required";
      if (!answers.operating_model) errs.operating_model = "Required";
      if (!answers.operating_currency_code && !answers.default_currency_code) {
        errs.operating_currency_code = "Required";
      }
      if (!answers.review_cycle) errs.review_cycle = "Required";
      if (!String(answers.timezone ?? "").trim()) errs.timezone = "Required";
    } else if (current === 2) {
      if (answers.monthly_budget_minor == null || Number(answers.monthly_budget_minor) < 0) {
        errs.monthly_budget_minor = "Enter a monthly budget (0 or more)";
      }
      if (!answers.allocation_mode) errs.allocation_mode = "Required";
      if (!answers.approval_model) errs.approval_model = "Required";
    } else if (current === 3) {
      if (!String(answers.operational_visibility ?? answers.visibility ?? "").trim()) {
        errs.operational_visibility = "Required";
      }
      if (!String(answers.escalation_contact_id ?? "").trim()) {
        errs.escalation_contact_id = "Required";
      }
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
    const next: OperationsMemberDraft = {
      local_id: newLocalId(),
      user_id: null,
      name: "",
      email: "",
      phone: "",
      role: "MEMBER",
      permission_profile: "MEMBER_V1",
      permission_version: 1,
      invite_method: "EMAIL",
      invite_status: "DRAFT",
      ...roleFlags("MEMBER"),
    };
    updateAnswers({ members: [...members, next] });
  };

  const patchMember = (localId: string, patch: Partial<OperationsMemberDraft>) => {
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

  const toggleSecondaryApprover = (id: string) => {
    if (interactionsDisabled) return;
    const next = secondaryApproverIds.includes(id)
      ? secondaryApproverIds.filter((x) => x !== id)
      : [...secondaryApproverIds, id];
    updateAnswer("secondary_approver_ids", next);
  };

  const reviewBlocks = [
    {
      title: "Operations identity",
      rows: [
        { label: "Moment", value: String(answers.moment_name ?? "") },
        { label: "Operations", value: String(answers.operations_name ?? "") },
        {
          label: "Scope",
          value: choiceLabel("operations_scope", String(answers.operations_scope ?? "")),
        },
        {
          label: "Operating model",
          value: choiceLabel("operating_model", String(answers.operating_model ?? "")),
        },
        { label: "Currency", value: currency },
        {
          label: "Review cycle",
          value: choiceLabel("review_cycle", String(answers.review_cycle ?? "")),
        },
      ],
    },
    {
      title: "Budget and monitoring",
      rows: [
        {
          label: "Monthly budget",
          value: formatBudgetDisplay(asInt(answers.monthly_budget_minor), currency),
        },
        {
          label: "Allocation method",
          value: choiceLabel("allocation_mode", allocationMode),
        },
        {
          label: "Vendor dependency",
          value: choiceLabel(
            "vendor_dependency_level",
            String(answers.vendor_dependency_level ?? ""),
          ),
        },
        {
          label: "Issue sensitivity",
          value: choiceLabel("issue_sensitivity", String(answers.issue_sensitivity ?? "")),
        },
        {
          label: "Monitoring",
          value: choiceLabel("ops_monitoring_level", String(answers.monitoring_level ?? "")),
        },
        {
          label: "Approval model",
          value: choiceLabel("approval_model", approvalModel),
        },
        ...(needsThreshold
          ? [
              {
                label: "Approval required above",
                value: formatBudgetDisplay(asInt(answers.approval_threshold_minor), currency),
              },
            ]
          : []),
      ],
    },
    {
      title: "People and governance",
      rows: [
        {
          label: "Visibility",
          value: choiceLabel(
            "visibility_leadership",
            String(answers.operational_visibility ?? answers.visibility ?? ""),
          ),
        },
        {
          label: "Escalation contact",
          value:
            members.find((m) => memberOptionValue(m) === answers.escalation_contact_id)?.name ||
            "",
        },
      ],
    },
    {
      title: "Members",
      rows: members.map((m) => ({
        label: m.name || "Member",
        value: `${choiceLabel("ops_roles", m.role)}${m.role === "OWNER" ? " · Full access" : ""}`,
      })),
    },
  ];

  const warnings = [
    ...(preview?.warnings ?? []),
    ...(!answers.escalation_contact_id
      ? ["Add an escalation contact so urgent issues have an owner."]
      : []),
  ];

  const liveSummary = buildBusinessLiveSummary({
    templateId: "business_operations",
    answers,
    currentStep: step,
    totalSteps: guidedSteps.length,
    estimatedMinutes: SETUP_ESTIMATED_MINUTES,
    memberCount: members.length,
  });

  return (
    <BusinessSetupShell
      contextType="business"
      templateId="business_operations"
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
        step === 1
          ? "Country and timezone use suggested defaults plus a searchable picker — never a long chip wall."
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
              <SetupSectionCard title="Operations basics">
                <SetupTextInput
                  label="What should we call this moment?"
                  helper="How this operating chapter appears in Momentra."
                  placeholder="Retail Operations"
                  maxLength={60}
                  value={String(answers.moment_name ?? "")}
                  error={fieldErrors.moment_name}
                  onChange={(v) => updateAnswer("moment_name", v)}
                />
                <SetupTextInput
                  label="Operations name"
                  helper="The function, department, or portfolio being managed."
                  maxLength={60}
                  value={String(answers.operations_name ?? "")}
                  error={fieldErrors.operations_name}
                  onChange={(v) => {
                    updateAnswer("operations_name", v);
                    if (!answers.moment_name) updateAnswer("moment_name", v);
                  }}
                />
                <SetupChoiceCards
                  label="What part of the business is this?"
                  helper="Choose the part of the business this moment will monitor."
                  value={String(answers.operations_scope ?? "")}
                  options={setupChoices("operations_scope").filter((c) => c.value !== "CUSTOM")}
                  error={fieldErrors.operations_scope}
                  onChange={(v) => updateAnswer("operations_scope", v)}
                />
                <SetupChoiceCards
                  label="How is work organized?"
                  helper="How are operating decisions and responsibilities organized?"
                  value={String(answers.operating_model ?? "")}
                  options={setupChoices("operating_model").filter((c) => c.value !== "CUSTOM")}
                  error={fieldErrors.operating_model}
                  explainer={setupExplainer("operating_model")}
                  onChange={(v) => updateAnswer("operating_model", v)}
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
                  onChange={(v) =>
                    updateAnswers({
                      operating_currency_code: v,
                      default_currency_code: v,
                    })
                  }
                />
                <SetupChoiceChips
                  label="Review cycle"
                  value={String(answers.review_cycle ?? "")}
                  options={setupChoices("review_cycle").filter((c) => c.value !== "CUSTOM")}
                  error={fieldErrors.review_cycle}
                  explainer={setupExplainer("review_cycle")}
                  onChange={(v) => updateAnswer("review_cycle", v)}
                />
              </SetupSectionCard>
              <SetupAdvancedDisclosure
                title={BUSINESS_SETUP_COPY.shared.regional_section.title}
                helper={BUSINESS_SETUP_COPY.shared.regional_section.helper}
              >
                <SuggestedChipsPicker
                  label="Country"
                  value={String(answers.country_code ?? "")}
                  options={SETUP_COUNTRY_FALLBACK}
                  suggested={["IN", "US", "GB", "AE"]}
                  onChange={(v) => updateAnswer("country_code", v)}
                />
                <SetupSearchPicker
                  label="Language and format"
                  value={String(answers.locale ?? "")}
                  options={SETUP_LOCALE_FALLBACK}
                  onChange={(v) => updateAnswer("locale", v)}
                />
                <SuggestedChipsPicker
                  label="Timezone"
                  value={String(answers.timezone ?? "")}
                  options={SETUP_TIMEZONE_FALLBACK}
                  suggested={[
                    "Asia/Kolkata",
                    "America/New_York",
                    "Europe/London",
                    "Asia/Dubai",
                  ]}
                  error={fieldErrors.timezone}
                  onChange={(v) => updateAnswer("timezone", v)}
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
              <SetupSectionCard title="Operating budget">
                <SetupMoneyField
                  label="Monthly operating budget"
                  amountMinor={
                    answers.monthly_budget_minor == null
                      ? null
                      : Number(answers.monthly_budget_minor)
                  }
                  currencyCode={currency}
                  currencies={currencies}
                  error={fieldErrors.monthly_budget_minor}
                  onChange={(v) => updateAnswer("monthly_budget_minor", v)}
                />
                <SetupChoiceChips
                  label="Allocation method"
                  value={allocationMode}
                  options={setupChoices("allocation_mode")}
                  error={fieldErrors.allocation_mode}
                  onChange={(v) => updateAnswer("allocation_mode", v)}
                />
                <SetupToggleReveal
                  label="Allow overallocation?"
                  checked={Boolean(answers.allow_overallocation)}
                  onChange={(v) => updateAnswer("allow_overallocation", v)}
                />
                <BudgetAllocationEditor
                  allocations={allocations}
                  allocationMode={allocationMode}
                  monthlyBudgetMinor={monthlyBudget}
                  allowOverallocation={Boolean(answers.allow_overallocation)}
                  currencies={currencies}
                  currencyCode={currency}
                  locale={String(answers.locale ?? "en-IN")}
                  onChange={(next) => updateAnswer("budget_allocations", next)}
                />
              </SetupSectionCard>
              <SetupSectionCard title="Vendor and risk profile">
                <SetupChoiceChips
                  label="How dependent are you on vendors?"
                  helper="Vendor dependency describes how severely operations would be affected if a key vendor stopped delivering."
                  value={String(answers.vendor_dependency_level ?? "")}
                  options={setupChoices("vendor_dependency_level")}
                  explainer={setupExplainer("vendor_dependency_level")}
                  onChange={(v) => updateAnswer("vendor_dependency_level", v)}
                />
                <SetupChoiceChips
                  label="Issue sensitivity"
                  helper="Issue sensitivity controls how quickly Momentra highlights operational problems."
                  value={String(answers.issue_sensitivity ?? "")}
                  options={setupChoices("issue_sensitivity")}
                  explainer={setupExplainer("issue_sensitivity")}
                  onChange={(v) => updateAnswer("issue_sensitivity", v)}
                />
              </SetupSectionCard>
              <SetupSectionCard title="Monitoring and approvals">
                <SetupChoiceChips
                  label="How closely should Momentra monitor this?"
                  value={String(answers.monitoring_level ?? "STANDARD")}
                  options={setupChoices("ops_monitoring_level")}
                  explainer={setupExplainer("monitoring_level")}
                  onChange={(v) => updateAnswer("monitoring_level", v)}
                />
                <SetupChoiceChips
                  label="Approval model"
                  value={approvalModel}
                  options={setupChoices("approval_model")}
                  error={fieldErrors.approval_model}
                  onChange={(v) => updateAnswer("approval_model", v)}
                />
                {needsThreshold ? (
                  <SetupMoneyField
                    label="Approval required above"
                    helper="Enter the amount in normal currency units (not minor units)."
                    amountMinor={
                      answers.approval_threshold_minor == null
                        ? null
                        : Number(answers.approval_threshold_minor)
                    }
                    currencyCode={currency}
                    currencies={currencies}
                    explainer={setupExplainer("approval_threshold_minor")}
                    onChange={(v) => updateAnswer("approval_threshold_minor", v)}
                  />
                ) : null}
              </SetupSectionCard>
            </>
          ) : null}

          {step === 3 ? (
            <div className="space-y-8">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-sm opacity-70">Owner is locked. Add teammates when ready.</p>
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
                  const roleDesc = roleDescription("ops_roles", m.role);
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
                            {choiceLabel("ops_roles", m.role)}
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
                            options={setupChoices("ops_roles").filter((r) => r.value !== "OWNER")}
                            onChange={(v) => patchMember(m.local_id, { role: v })}
                          />
                        </>
                      ) : null}
                    </div>
                  );
                })}
              </div>

              <SetupSectionCard title="Visibility and governance">
                <SetupChoiceChips
                  label="Visibility"
                  value={String(
                    answers.operational_visibility ?? answers.visibility ?? "TEAM",
                  )}
                  options={setupChoices("visibility_leadership")}
                  error={fieldErrors.operational_visibility}
                  onChange={(v) =>
                    updateAnswers({
                      operational_visibility: v,
                      visibility: v,
                    })
                  }
                />
                {needsApprovalOwner ? (
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
                {approvalModel === "MULTI_APPROVER" ? (
                  <div className="space-y-2">
                    <p className="text-xs font-semibold tracking-wide opacity-70">
                      Secondary approvers
                    </p>
                    {members
                      .filter((m) => m.role !== "OWNER")
                      .map((m) => {
                        const id = memberOptionValue(m);
                        return (
                          <label key={m.local_id} className="flex items-center gap-2 text-sm">
                            <input
                              type="checkbox"
                              checked={secondaryApproverIds.includes(id)}
                              onChange={() => toggleSecondaryApprover(id)}
                            />
                            {m.name || m.email || "Member"}
                          </label>
                        );
                      })}
                  </div>
                ) : null}
                <SetupSearchPicker
                  label="Escalation contact"
                  value={String(answers.escalation_contact_id ?? "")}
                  options={members.map((m) => ({
                    value: memberOptionValue(m),
                    label: memberPickerLabel(m),
                  }))}
                  appendValueToLabel={false}
                  showOptionValue={false}
                  error={fieldErrors.escalation_contact_id}
                  onChange={(v) => updateAnswer("escalation_contact_id", v || null)}
                />
                <div className="space-y-2">
                  <p className="text-xs font-semibold tracking-wide opacity-70">
                    Alert recipients
                  </p>
                  {members.map((m) => {
                    const id = memberOptionValue(m);
                    const selected = asStringList(answers.alert_recipient_ids).includes(id);
                    return (
                      <label key={m.local_id} className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={() => {
                            const current = asStringList(answers.alert_recipient_ids);
                            const next = selected
                              ? current.filter((x) => x !== id)
                              : [...current, id];
                            updateAnswer("alert_recipient_ids", next);
                          }}
                        />
                        {memberDisplayName(m)}
                      </label>
                    );
                  })}
                </div>
                <SetupToggleReveal
                  label="Require approval for spending?"
                  checked={Boolean(answers.approval_required_for_spend)}
                  onChange={(v) => updateAnswer("approval_required_for_spend", v)}
                />
                <SetupToggleReveal
                  label="Require approval for vendor changes?"
                  checked={Boolean(answers.approval_required_for_vendor_changes)}
                  onChange={(v) => updateAnswer("approval_required_for_vendor_changes", v)}
                />
                <SetupToggleReveal
                  label="Require approval for budget changes?"
                  checked={Boolean(answers.approval_required_for_budget_changes)}
                  onChange={(v) => updateAnswer("approval_required_for_budget_changes", v)}
                />
                <SetupToggleReveal
                  label="Require approval for issue closure?"
                  checked={Boolean(answers.approval_required_for_issue_closure)}
                  onChange={(v) => updateAnswer("approval_required_for_issue_closure", v)}
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
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={Boolean(answers.invite_on_activation ?? true)}
                  onChange={(e) => updateAnswer("invite_on_activation", e.target.checked)}
                />
                Send invites on activation
              </label>
            </>
          ) : null}
        </div>
      )}
    </BusinessSetupShell>
  );
}

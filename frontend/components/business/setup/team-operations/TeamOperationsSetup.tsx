"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { BusinessSetupShell } from "@/components/business/setup/BusinessSetupShell";
import { BusinessSetupSkeleton } from "@/components/business/setup/BusinessSetupSkeleton";
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
import type { BusinessSetupState } from "@/lib/api/business";
import { markBusinessSetupFirstPaint } from "@/lib/telemetry/businessSetupTelemetry";
import { SuggestedChipsPicker } from "@/components/setup/shared/SuggestedChipsPicker";

export type TeamMemberDraft = {
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
  is_budget_owner: boolean;
};

type Props = {
  momentId: string;
  onClose: () => void;
  onActivated: () => void;
  onSetupReady?: () => void;
  initialSetup?: BusinessSetupState | null;
};

function newLocalId() {
  return `m-${Math.random().toString(36).slice(2, 10)}`;
}

const META = setupTemplate("team_ops");

export function TeamOperationsSetup({
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

  const guidedSteps = useMemo(() => businessGuidedSteps("team_ops"), []);
  const [step, setStep] = useState(setup?.progress?.current_step ?? 1);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [activationSuccess, setActivationSuccess] = useState(false);
  const paintedRef = useRef(false);
  const readyNotifiedRef = useRef(false);
  const members = useMemo((): TeamMemberDraft[] => {
    const raw = (answers.members as TeamMemberDraft[] | undefined) ?? [];
    return Array.isArray(raw) ? raw : [];
  }, [answers.members]);

  const owner = members.find((m) => m.role === "OWNER");
  const ready = Boolean(setup) && !loading;
  const interactionsDisabled = !ready;
  const stepMeta = setupStepMeta("team_ops", step);
  const currency = String(answers.operating_currency_code ?? "INR");

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
      if (!String(answers.team_name ?? "").trim()) errs.team_name = "Required";
      if (!String(answers.team_purpose ?? "").trim()) errs.team_purpose = "Required";
      if (!answers.team_size) errs.team_size = "Required";
      if (!answers.work_style) errs.work_style = "Required";
      if (!answers.operating_currency_code) errs.operating_currency_code = "Required";
    } else if (current === 2) {
      if (!String(answers.visibility ?? "").trim()) errs.visibility = "Required";
      if (!answers.coordination_style) errs.coordination_style = "Required";
      if (!answers.review_cycle) errs.review_cycle = "Required";
      if (
        answers.monthly_team_budget_minor != null &&
        Number(answers.monthly_team_budget_minor) < 0
      ) {
        errs.monthly_team_budget_minor = "Budget cannot be negative";
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
    // Continue: cancel debounce → flush → validate → advance
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
    const next: TeamMemberDraft = {
      local_id: newLocalId(),
      user_id: null,
      name: "",
      email: "",
      phone: "",
      role: "MEMBER",
      permission_profile: "TEAM_MEMBER_V1",
      permission_version: 1,
      invite_method: "EMAIL",
      invite_status: "DRAFT",
      is_approver: false,
      is_budget_owner: false,
    };
    updateAnswers({ members: [...members, next] });
  };

  const patchMember = (localId: string, patch: Partial<TeamMemberDraft>) => {
    if (interactionsDisabled) return;
    updateAnswers({
      members: members.map((m) => (m.local_id === localId ? { ...m, ...patch } : m)),
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
      title: "Team identity",
      rows: [
        { label: "Moment", value: String(answers.moment_name ?? "") },
        { label: "Team", value: String(answers.team_name ?? "") },
        { label: "Purpose", value: String(answers.team_purpose ?? "") },
        { label: "Size", value: choiceLabel("team_size", String(answers.team_size ?? "")) },
        { label: "Work style", value: choiceLabel("work_style", String(answers.work_style ?? "")) },
        { label: "Currency", value: currency },
      ],
    },
    {
      title: "Team structure",
      rows: [
        {
          label: "Coordination",
          value: choiceLabel("coordination_style", String(answers.coordination_style ?? "")),
        },
        {
          label: "Review cycle",
          value: choiceLabel("review_cycle", String(answers.review_cycle ?? "")),
        },
        {
          label: "Monitoring",
          value: choiceLabel("team_monitoring_level", String(answers.monitoring_level ?? "")),
        },
      ],
    },
    {
      title: "Budget and approvals",
      rows: [
        {
          label: "Approvals for spend",
          value: answers.approval_required_for_spend ? "On" : "Off",
        },
        {
          label: "Visibility",
          value: choiceLabel("visibility_team", String(answers.visibility ?? "")),
        },
      ],
    },
    {
      title: "Members",
      rows: members.map((m) => ({
        label: m.name || "Member",
        value: `${choiceLabel("team_roles", m.role)}${m.role === "OWNER" ? " · Full access" : ""}`,
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
    templateId: "team_ops",
    answers,
    currentStep: step,
    totalSteps: guidedSteps.length,
    estimatedMinutes: SETUP_ESTIMATED_MINUTES,
    memberCount: members.length,
  });

  return (
    <BusinessSetupShell
      contextType="business"
      templateId="team_ops"
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
          ? "Choosing Hybrid allows both remote and office employees."
          : step === 3
            ? "Owner is locked. Invite teammates by QR, WhatsApp, email, or link."
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
              <SetupSectionCard title="Team basics">
                <SetupTextInput
                  label="What should we call this moment?"
                  helper="How this operating chapter appears in Momentra."
                  placeholder="Engineering Team"
                  examples={["Product Team Operations", "Engineering Team"]}
                  maxLength={60}
                  value={String(answers.moment_name ?? "")}
                  error={fieldErrors.moment_name}
                  onChange={(v) => updateAnswer("moment_name", v)}
                />
                <SetupTextInput
                  label="Team name"
                  helper="The real team or function being managed."
                  placeholder="Product"
                  maxLength={60}
                  value={String(answers.team_name ?? "")}
                  error={fieldErrors.team_name}
                  onChange={(v) => {
                    updateAnswer("team_name", v);
                    if (!answers.moment_name) updateAnswer("moment_name", v);
                  }}
                />
                <SetupTextInput
                  label="What is this team for?"
                  placeholder="Plan releases, coordinate work and track approvals"
                  examples={["Plan releases, coordinate work and track approvals"]}
                  multiline
                  value={String(answers.team_purpose ?? "")}
                  error={fieldErrors.team_purpose}
                  onChange={(v) => updateAnswer("team_purpose", v)}
                />
                <SetupChoiceCards
                  label="How big is your team?"
                  value={String(answers.team_size ?? "")}
                  options={setupChoices("team_size")}
                  error={fieldErrors.team_size}
                  onChange={(v) => updateAnswer("team_size", v)}
                />
                <SetupChoiceCards
                  label="How does the team usually work?"
                  helper="Choosing Hybrid allows both remote and office employees."
                  value={String(answers.work_style ?? "")}
                  options={setupChoices("work_style")}
                  error={fieldErrors.work_style}
                  onChange={(v) => updateAnswer("work_style", v)}
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
                <SetupMoneyField
                  label="Approximate monthly operating budget"
                  helper="This helps build cash flow insights. You can change this later."
                  optionalLabel="Optional"
                  amountMinor={
                    answers.monthly_team_budget_minor == null
                      ? null
                      : Number(answers.monthly_team_budget_minor)
                  }
                  currencyCode={currency}
                  onChange={(v) => updateAnswer("monthly_team_budget_minor", v)}
                />
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
              <SetupSectionCard title="Governance">
                <SetupChoiceChips
                  label="Coordination style"
                  value={String(answers.coordination_style ?? "SHARED_OWNERSHIP")}
                  options={setupChoices("coordination_style")}
                  error={fieldErrors.coordination_style}
                  onChange={(v) => updateAnswer("coordination_style", v)}
                />
                <SetupChoiceChips
                  label="Review cycle"
                  value={String(answers.review_cycle ?? "MONTHLY")}
                  options={setupChoices("review_cycle").filter((c) => c.value !== "CUSTOM")}
                  explainer={setupExplainer("review_cycle")}
                  error={fieldErrors.review_cycle}
                  onChange={(v) => updateAnswer("review_cycle", v)}
                />
                <SetupChoiceChips
                  label="How closely should Momentra monitor this?"
                  value={String(answers.monitoring_level ?? "STANDARD")}
                  options={setupChoices("team_monitoring_level")}
                  explainer={setupExplainer("monitoring_level")}
                  onChange={(v) => updateAnswer("monitoring_level", v)}
                />
              </SetupSectionCard>
              <SetupSectionCard title="Approvals">
                <SetupToggleReveal
                  label="Require approval for spending?"
                  checked={Boolean(answers.approval_required_for_spend)}
                  onChange={(v) => updateAnswer("approval_required_for_spend", v)}
                >
                  <SetupMoneyField
                    label="Approval required above"
                    amountMinor={
                      answers.approval_threshold_minor == null
                        ? null
                        : Number(answers.approval_threshold_minor)
                    }
                    currencyCode={currency}
                    explainer={setupExplainer("approval_threshold_minor")}
                    onChange={(v) => updateAnswer("approval_threshold_minor", v)}
                  />
                </SetupToggleReveal>
                <SetupToggleReveal
                  label="Require approval for member changes?"
                  checked={Boolean(answers.approval_required_for_member_changes)}
                  onChange={(v) => updateAnswer("approval_required_for_member_changes", v)}
                />
              </SetupSectionCard>
              <SetupSectionCard title="Visibility and notifications">
                <SetupChoiceChips
                  label="Visibility"
                  value={String(answers.visibility ?? "TEAM")}
                  options={setupChoices("visibility_team")}
                  error={fieldErrors.visibility}
                  onChange={(v) => updateAnswer("visibility", v)}
                />
                <SetupChoiceChips
                  label="Notifications"
                  value={answers.notify_members === false ? "OFF" : "ON"}
                  options={[
                    { value: "ON", label: "Notify members" },
                    { value: "OFF", label: "Quiet for now" },
                  ]}
                  onChange={(v) => updateAnswer("notify_members", v === "ON")}
                />
              </SetupSectionCard>
            </>
          ) : null}

          {step === 3 ? (
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
                const roleDesc = roleDescription("team_roles", m.role);
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
                        <p className="font-semibold">{m.name || (locked ? "You" : "New member")}</p>
                        <p className="text-xs opacity-60">
                          {choiceLabel("team_roles", m.role)}
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
                          options={setupChoices("team_roles").filter((r) => r.value !== "OWNER")}
                          onChange={(v) =>
                            patchMember(m.local_id, {
                              role: v,
                              permission_profile: `${v === "MEMBER" ? "TEAM_MEMBER" : v}_V1`,
                              is_approver: v === "APPROVER",
                              is_budget_owner: v === "BUDGET_OWNER",
                            })
                          }
                        />
                      </>
                    ) : null}
                  </div>
                );
              })}
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

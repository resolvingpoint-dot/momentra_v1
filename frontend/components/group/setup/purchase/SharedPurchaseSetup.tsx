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

const TEMPLATE_ID = "shared_purchase" as const;
const MONEY_EXPONENT = 2;

const NAME_PLACEHOLDERS: Record<string, string> = {
  GIFT_POOL: "Birthday gift for Rahul",
  GROUP_PURCHASE: "New apartment refrigerator",
  SHARED_ASSET: "Shared camera",
  CUSTOM_PURCHASE: "Team equipment fund",
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
    purchase_name: ["purchase_name", "moment_name"],
    item_or_goal: ["item_or_goal", "description"],
    expected_amount: ["expected_amount", "target_amount_major"],
    currency_code: ["currency_code", "budget_currency", "operating_currency_code"],
    payment_plan: ["payment_plan", "funding_style"],
    decision_deadline: ["decision_deadline", "target_date"],
    contributors: ["contributors", "expected_contributors"],
  };
  for (const alt of aliases[catalogKey] ?? []) {
    if (available.has(alt)) return alt;
  }
  return catalogKey;
}

/** expected_amount / target_amount_major are major units; SetupMoneyField uses minor. */
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
 * Phase 2B — Shared Purchase on GuidedSetupShell.
 * Catalog-driven presentation over useSetupFlow / SetupRepository (no new engine).
 */
export function SharedPurchaseSetup({ momentId, onClose, onActivated }: Props) {
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

  const purchaseProfile = answerString(answers, "purchase_profile");
  const currency =
    answerString(answers, "currency_code", "budget_currency", "operating_currency_code") ||
    "INR";
  const namePlaceholder =
    NAME_PLACEHOLDERS[purchaseProfile] ?? "What are you buying or saving for?";

  const contributorCount = useMemo(() => {
    const raw = answerString(answers, "contributors", "expected_contributors");
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
        memberCount: contributorCount,
      }),
    [answers, step, steps.length, contributorCount],
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
    // Keep dual keys in sync when both exist in the contract surface.
    if (catalogKey === "purchase_name") {
      updateAnswer("moment_name", value);
    }
    if (catalogKey === "item_or_goal") {
      updateAnswer("description", value);
    }
    if (catalogKey === "expected_amount") {
      updateAnswer("target_amount_major", value);
    }
    if (catalogKey === "payment_plan") {
      updateAnswer("funding_style", value);
    }
    if (catalogKey === "decision_deadline") {
      updateAnswer("target_date", value);
    }
    if (catalogKey === "contributors") {
      updateAnswer("expected_contributors", value);
    }
  }

  function validateStep(current: number): boolean {
    const errs: Record<string, string> = {};
    if (current === 1) {
      if (!purchaseProfile) errs.purchase_profile = "Required";
      const name = answerString(answers, "purchase_name", "moment_name");
      if (!name.trim()) errs.purchase_name = "Required";
    }
    if (current === 2) {
      const amount = answerString(answers, "expected_amount", "target_amount_major");
      if (!amount.trim()) errs.expected_amount = "Required";
      if (!answerString(answers, "currency_code", "budget_currency")) {
        errs.currency_code = "Required";
      }
      if (!answerString(answers, "payment_plan", "funding_style")) {
        errs.payment_plan = "Required";
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

  const purchaseName = answerString(answers, "purchase_name", "moment_name");
  const paymentPlan = answerString(answers, "payment_plan", "funding_style");
  const ownership = answerString(answers, "ownership_style");
  const deadline = answerString(answers, "decision_deadline", "target_date");
  const amountMajor = answerString(answers, "expected_amount", "target_amount_major");

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
          ? "Pick the purchase type first — the name placeholder updates to match."
          : step === 2
            ? "Flexible contributions let members give different amounts without a fixed equal split."
            : step === 3
              ? "Invite contributors now or later. You remain on the purchase after activation."
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
              label="What kind of purchase is this?"
              value={purchaseProfile}
              options={groupChoices("purchase_profile")}
              error={fieldErrors.purchase_profile}
              onChange={(v) => setAnswer("purchase_profile", v)}
            />
            <SetupFieldRenderer
              control="text"
              label="What are you buying or saving for?"
              helper="How this purchase appears in Momentra."
              value={purchaseName}
              placeholder={namePlaceholder}
              maxLength={60}
              examples={[
                "New apartment refrigerator",
                "Birthday gift for Rahul",
                "Shared camera",
                "Wedding decorations",
                "Team equipment fund",
              ]}
              error={fieldErrors.purchase_name}
              onChange={(v) => setAnswer("purchase_name", v)}
            />
            <SetupFieldRenderer
              control="text"
              label="What is the item or goal?"
              helper="Optional detail about the item or savings goal."
              optionalLabel="Optional"
              value={answerString(answers, "item_or_goal", "description")}
              placeholder="New apartment refrigerator"
              onChange={(v) => setAnswer("item_or_goal", v)}
            />
          </SetupSectionCard>
        ) : null}

        {step === 2 ? (
          <SetupSectionCard>
            <SetupFieldRenderer
              control="money"
              label="How much do you expect to spend?"
              helper="Enter the group target in normal currency units."
              amountMinor={majorToMinor(amountMajor)}
              currencyCode={currency}
              error={fieldErrors.expected_amount}
              onChangeAmount={(minor) => setAnswer("expected_amount", minorToMajorString(minor))}
            />
            <SetupFieldRenderer
              control="suggested_picker"
              label="What currency should we use by default?"
              value={currency}
              options={GUIDED_CURRENCY_OPTIONS}
              suggested={[...GUIDED_CURRENCY_SUGGESTED]}
              error={fieldErrors.currency_code}
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
                body: "Use this when contributions may be recorded in more than one currency.",
              }}
              onChange={(v) => setAnswer("allow_multi_currency", v)}
            />
            <SetupFieldRenderer
              control="cards"
              label="How should contributions work?"
              value={paymentPlan}
              options={groupChoices("payment_plan")}
              error={fieldErrors.payment_plan}
              explainer={{
                title: "Contribution model",
                body: "How the target is divided or collected from members.",
              }}
              onChange={(v) => setAnswer("payment_plan", v)}
            />
            <SetupFieldRenderer
              control="cards"
              label="How should ownership work?"
              optionalLabel="Optional"
              value={ownership}
              options={groupChoices("ownership_style")}
              onChange={(v) => setAnswer("ownership_style", v)}
            />
            <SetupFieldRenderer
              control="date"
              label="When do you need to decide by?"
              optionalLabel="Optional"
              value={deadline}
              explainer={{
                title: "Target date",
                body: "An optional planning date. It does not automatically close the purchase.",
              }}
              onChange={(v) => setAnswer("decision_deadline", v)}
            />
          </SetupSectionCard>
        ) : null}

        {step === 3 ? (
          <>
            <SetupSectionCard>
              <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
                You remain the purchase admin. Invite contributors now or later — the creator
                stays on the moment after activation.
              </p>
              <SetupFieldRenderer
                control="text"
                label="How many people are contributing?"
                optionalLabel="Optional"
                helper="Optional count. Invite people with the panel below."
                value={answerString(answers, "contributors", "expected_contributors")}
                placeholder="e.g. 4"
                onChange={(v) => setAnswer("contributors", v)}
              />
              {ownership ? (
                <p className="text-xs opacity-60">
                  Ownership: {groupChoiceLabel("ownership_style", ownership)}
                </p>
              ) : null}
            </SetupSectionCard>
            <GroupSetupInviteSection
              momentId={momentId}
              title="Invite contributors"
              helper="Share a QR code or invite link — WhatsApp, Messages, and email are shortcuts."
            />
          </>
        ) : null}

        {isReview ? (
          <div className="space-y-4">
            <div className="rounded-2xl p-5" style={glassCardStyle(tokens)}>
              <h3 className="mb-3 text-lg font-semibold">Review your shared purchase</h3>
              <dl className="space-y-2 text-sm">
                {[
                  {
                    label: "Purchase",
                    value: groupChoiceLabel("purchase_profile", purchaseProfile),
                  },
                  { label: "Name", value: purchaseName },
                  {
                    label: "Item / goal",
                    value: answerString(answers, "item_or_goal", "description"),
                  },
                  {
                    label: "Target amount",
                    value: amountMajor ? `${currency} ${amountMajor}` : "",
                  },
                  { label: "Currency", value: currency },
                  {
                    label: "Contribution",
                    value: groupChoiceLabel("payment_plan", paymentPlan),
                  },
                  {
                    label: "Ownership",
                    value: groupChoiceLabel("ownership_style", ownership),
                  },
                  { label: "Target date", value: deadline },
                  {
                    label: "Contributors",
                    value: answerString(answers, "contributors", "expected_contributors"),
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

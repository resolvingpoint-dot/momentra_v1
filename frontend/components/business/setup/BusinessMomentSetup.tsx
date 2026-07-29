"use client";

import { useState } from "react";
import { BusinessSetupShell } from "@/components/business/setup/BusinessSetupShell";
import { BusinessOperationsSetup } from "@/components/business/setup/business-operations/BusinessOperationsSetup";
import { BusinessRunwaySetup } from "@/components/business/setup/business-runway/BusinessRunwaySetup";
import { TeamOperationsSetup } from "@/components/business/setup/team-operations/TeamOperationsSetup";
import { useBusinessSetupFlow } from "@/hooks/useBusinessSetupFlow";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { BusinessSetupState } from "@/lib/api/business";

type Props = {
  momentId: string;
  title: string;
  subtitle: string;
  onClose: () => void;
  onActivated: () => void;
  initialSetup?: BusinessSetupState | null;
};

/**
 * @deprecated Placeholder path for unknown Business types.
 * Team Ops / Runway / Ops use dedicated guided templates via GuidedSetupShell.
 */
function PlaceholderFields({
  momentId,
  title,
  subtitle,
  onClose,
  onActivated,
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
    activate,
  } = useBusinessSetupFlow(momentId, { initialSetup });
  const [activationSuccess, setActivationSuccess] = useState(false);

  if (loading && !setup) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: colors.background }}>
        <p className="text-sm opacity-70">Loading setup…</p>
      </div>
    );
  }

  return (
    <BusinessSetupShell
      title={title}
      subtitle={subtitle}
      currentStep={setup?.progress?.current_step ?? 1}
      totalSteps={2}
      saveStatus={saveStatus}
      error={error}
      submitting={submitting}
      canActivate={preview?.activation_ready !== false}
      activationSuccess={activationSuccess}
      activationSuccessMessage="Moment activated"
      onActivationSuccessDone={onActivated}
      onClose={onClose}
      onActivate={async () => {
        const ok = await activate();
        if (ok) setActivationSuccess(true);
      }}
    >
      <section className="space-y-4">
        <p className="text-sm opacity-70">
          Shared setup plumbing placeholder — full fields land in Runs 3–5.
        </p>
        <label className="block space-y-1">
          <span className="text-xs font-semibold tracking-wide opacity-70">Moment name</span>
          <input
            className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none"
            style={{
              borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
              background: colors.surfaceContainer,
            }}
            value={String(answers.moment_name ?? "")}
            onChange={(e) => updateAnswer("moment_name", e.target.value)}
            placeholder="Working title"
          />
        </label>
        <div className="grid gap-3 sm:grid-cols-2">
          {(
            [
              ["country_code", "Country code"],
              ["locale", "Locale"],
              ["timezone", "Timezone"],
              ["default_currency_code", "Currency (ISO)"],
              ["financial_year_start", "Financial year start"],
            ] as const
          ).map(([key, label]) => (
            <label key={key} className="block space-y-1">
              <span className="text-xs font-semibold tracking-wide opacity-70">{label}</span>
              <input
                className="w-full rounded-xl border px-3 py-2.5 text-sm outline-none"
                style={{
                  borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)`,
                  background: colors.surfaceContainer,
                }}
                value={String(answers[key] ?? "")}
                onChange={(e) => updateAnswer(key, e.target.value || null)}
              />
            </label>
          ))}
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={Boolean(answers.allow_multi_currency)}
            onChange={(e) => updateAnswer("allow_multi_currency", e.target.checked)}
          />
          Allow multi-currency
        </label>
        {preview?.summary_blocks?.length ? (
          <div className="rounded-xl p-4" style={{ background: colors.surfaceContainer }}>
            <p className="text-sm font-semibold">Preview</p>
            <ul className="mt-2 space-y-1 text-xs opacity-80">
              {preview.summary_blocks.map((b) => (
                <li key={b.block_id}>
                  <strong>{b.title}:</strong> {b.body}
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </section>
    </BusinessSetupShell>
  );
}

export function TeamOperationsSetupPlaceholder(props: Omit<Props, "title" | "subtitle">) {
  return <TeamOperationsSetup {...props} />;
}

export function BusinessRunwaySetupPlaceholder(props: Omit<Props, "title" | "subtitle">) {
  return <BusinessRunwaySetup {...props} />;
}

export function BusinessOperationsSetupPlaceholder(props: Omit<Props, "title" | "subtitle">) {
  return <BusinessOperationsSetup {...props} />;
}

export function BusinessMomentSetup({
  momentId,
  momentTypeCode,
  onClose,
  onActivated,
  onSetupReady,
  initialSetup,
}: {
  momentId: string;
  momentTypeCode: string;
  onClose: () => void;
  onActivated: () => void;
  onSetupReady?: () => void;
  /** From createDraft — skips GET /setup when present for this moment. */
  initialSetup?: BusinessSetupState | null;
}) {
  const code = momentTypeCode.toUpperCase();
  if (code === "BUSINESS_RUNWAY") {
    return (
      <BusinessRunwaySetup
        momentId={momentId}
        onClose={onClose}
        onActivated={onActivated}
        onSetupReady={onSetupReady}
        initialSetup={initialSetup}
      />
    );
  }
  if (code === "BUSINESS_OPERATIONS") {
    return (
      <BusinessOperationsSetup
        momentId={momentId}
        onClose={onClose}
        onActivated={onActivated}
        onSetupReady={onSetupReady}
        initialSetup={initialSetup}
      />
    );
  }
  return (
    <TeamOperationsSetup
      momentId={momentId}
      onClose={onClose}
      onActivated={onActivated}
      onSetupReady={onSetupReady}
      initialSetup={initialSetup}
    />
  );
}

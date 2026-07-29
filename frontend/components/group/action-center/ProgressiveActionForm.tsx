"use client";

import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import {
  ActionFooter,
  ActionHeader,
  ActionContextChips,
  ActionHeroBanner,
  ActionSection,
  ActionSuccessOverlay,
  ActionValidationBanner,
} from "@/components/group/action-center/ui/ActionDesignSystem";
import {
  clearQuickAddDraft,
  loadQuickAddDraft,
  saveQuickAddDraft,
  createClientRequestId,
} from "@/lib/quick_add/draftStore";
import type { QuickAddActionTemplate } from "@/lib/quick_add/types";
import { emitActionAnalytics, pushRecentAction } from "@/lib/action-center/actionCenterPrefs";

export type FormState = Record<string, string | boolean | string[]>;

export type ProgressiveStep = {
  id: string;
  title: string;
  render: (ctx: {
    state: FormState;
    set: (key: string, value: FormState[string]) => void;
    errors: Record<string, string>;
  }) => ReactNode;
  validate?: (state: FormState) => Record<string, string>;
};

type ProgressiveActionFormProps = {
  action: QuickAddActionTemplate;
  momentId: string;
  userId?: string;
  templateId: string;
  steps: ProgressiveStep[];
  /** @deprecated Unused after Review removal; kept optional for call-site compatibility. */
  buildReviewRows?: (state: FormState) => Array<{ label: string; value: string }>;
  /** @deprecated Unused after Summary removal. */
  buildSummaryRows?: (state: FormState) => Array<{ label: string; value: string }>;
  buildPayload: (state: FormState) => Record<string, unknown>;
  onSubmit: (payload: Record<string, unknown>) => Promise<void>;
  onClose: () => void;
  onSuccess?: () => void;
  draftTitleKey?: string;
  /** Seeded defaults (e.g. expense context). Draft restore still wins if user continues. */
  initialState?: FormState;
  contextChips?: string[];
  heroImageUrl?: string | null;
  /** Overrides the final-step primary button label (default: Save). */
  saveLabel?: string;
  successMessage?: string;
  successSubtitle?: string;
};

export function ProgressiveActionForm({
  action,
  momentId,
  userId = "local",
  templateId,
  steps,
  buildPayload,
  onSubmit,
  onClose,
  onSuccess,
  draftTitleKey = "title",
  initialState,
  contextChips,
  heroImageUrl,
  saveLabel = "Save",
  successMessage,
  successSubtitle,
}: ProgressiveActionFormProps) {
  const startedAt = useRef(Date.now());
  const completed = useRef(false);
  const [stepIndex, setStepIndex] = useState(0);
  const [state, setState] = useState<FormState>(() => ({ ...(initialState ?? {}) }));
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [banner, setBanner] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [success, setSuccess] = useState(false);
  const [draftPrompt, setDraftPrompt] = useState<{ title: string; form: FormState } | null>(null);
  const seededRef = useRef(false);

  const set = useCallback((key: string, value: FormState[string]) => {
    setState((prev) => ({ ...prev, [key]: value }));
  }, []);

  useEffect(() => {
    if (seededRef.current || !initialState || Object.keys(initialState).length === 0) return;
    if (draftPrompt) return;
    seededRef.current = true;
    setState((prev) => ({ ...initialState, ...prev }));
  }, [initialState, draftPrompt]);

  useEffect(() => {
    emitActionAnalytics({
      analytics_id: action.analytics_id ?? action.action_id,
      event: "started",
      action_id: action.action_id,
      template_id: templateId,
    });
    const draft = loadQuickAddDraft(momentId, action.action_id);
    if (draft?.form && Object.keys(draft.form).length) {
      const form = draft.form as FormState;
      const title = String(form[draftTitleKey] ?? form.title ?? form.item_name ?? form.full_name ?? action.label);
      setDraftPrompt({ title, form });
    }
    return () => {
      if (!completed.current) {
        emitActionAnalytics({
          analytics_id: action.analytics_id ?? action.action_id,
          event: "abandoned",
          action_id: action.action_id,
          template_id: templateId,
          duration_ms: Date.now() - startedAt.current,
        });
      }
    };
  }, [action, momentId, templateId, draftTitleKey]);

  // Auto-save draft (debounced)
  useEffect(() => {
    if (!action.supports?.drafts && action.supports?.drafts !== undefined) return;
    if (!Object.keys(state).length) return;
    const t = window.setTimeout(() => {
      saveQuickAddDraft({
        momentId,
        tab: action.action_id,
        form: state as Record<string, unknown>,
        payload: {},
        clientRequestId: createClientRequestId(),
        savedAt: new Date().toISOString(),
      });
    }, 400);
    return () => window.clearTimeout(t);
  }, [state, momentId, action]);

  const totalSteps = steps.length;
  const isLastStep = stepIndex >= totalSteps - 1;
  const current = steps[stepIndex];
  const singleScreen = totalSteps <= 1;

  async function handleSave() {
    if (busy) return;
    const allErrors: Record<string, string> = {};
    for (const s of steps) Object.assign(allErrors, s.validate?.(state) ?? {});
    if (Object.keys(allErrors).length) {
      setErrors(allErrors);
      setBanner(Object.values(allErrors));
      emitActionAnalytics({
        analytics_id: action.analytics_id ?? action.action_id,
        event: "validation_failed",
        action_id: action.action_id,
        template_id: templateId,
      });
      return;
    }
    try {
      setBusy(true);
      await onSubmit(buildPayload(state));
      clearQuickAddDraft(momentId, action.action_id);
      pushRecentAction(userId, templateId, action.action_id);
      completed.current = true;
      emitActionAnalytics({
        analytics_id: action.analytics_id ?? action.action_id,
        event: "completed",
        action_id: action.action_id,
        template_id: templateId,
        duration_ms: Date.now() - startedAt.current,
      });
      setSuccess(true);
    } catch (e) {
      setBanner([e instanceof Error ? e.message : "Failed to save"]);
    } finally {
      setBusy(false);
    }
  }

  function goNextOrSave() {
    const stepErrors = current?.validate?.(state) ?? {};
    setErrors(stepErrors);
    if (Object.keys(stepErrors).length) {
      setBanner(Object.values(stepErrors));
      emitActionAnalytics({
        analytics_id: action.analytics_id ?? action.action_id,
        event: "validation_failed",
        action_id: action.action_id,
        template_id: templateId,
      });
      return;
    }
    setBanner([]);
    if (isLastStep) {
      void handleSave();
    } else {
      setStepIndex((i) => i + 1);
    }
  }

  if (draftPrompt) {
    return (
      <div className="space-y-6 py-4">
        <ActionHeader title="Continue editing?" subtitle={`You have a draft for ${draftPrompt.title}.`} />
        <ActionFooter
          primaryLabel="Continue"
          onPrimary={() => {
            setState(draftPrompt.form);
            setDraftPrompt(null);
            emitActionAnalytics({
              analytics_id: action.analytics_id ?? action.action_id,
              event: "draft_restored",
              action_id: action.action_id,
              template_id: templateId,
            });
          }}
          secondaryLabel="Start fresh"
          onSecondary={() => {
            clearQuickAddDraft(momentId, action.action_id);
            setDraftPrompt(null);
          }}
        />
      </div>
    );
  }

  return (
    <div className="relative space-y-5 pb-2">
      <ActionHeader
        title={action.label}
        subtitle={action.subtitle}
        estimatedTimeSec={action.estimated_time_sec}
      />
      {contextChips?.length ? <ActionContextChips chips={contextChips} /> : null}
      {heroImageUrl !== undefined ? <ActionHeroBanner imageUrl={heroImageUrl} /> : null}
      <ActionValidationBanner messages={banner} />

      <ActionSection
        title={singleScreen ? undefined : current?.title}
        step={singleScreen ? undefined : stepIndex + 1}
        totalSteps={singleScreen ? undefined : totalSteps}
      >
        {current?.render({ state, set, errors })}
      </ActionSection>
      <ActionFooter
        primaryLabel={isLastStep ? (busy ? "Saving…" : saveLabel) : "Continue"}
        onPrimary={goNextOrSave}
        secondaryLabel={stepIndex > 0 ? "Back" : "Cancel"}
        onSecondary={() => {
          if (stepIndex > 0) setStepIndex((i) => i - 1);
          else onClose();
        }}
        busy={busy}
      />

      <ActionSuccessOverlay
        open={success}
        message={successMessage ?? `${action.label} saved`}
        subtitle={successSubtitle ?? "Synced with your trip."}
        onDone={() => {
          onSuccess?.();
          onClose();
        }}
      />
    </div>
  );
}

"use client";

import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";
import {
  BusinessActionHeader,
  BusinessContextChips,
  BusinessFooter,
  BusinessSection,
  BusinessSuccessOverlay,
  BusinessValidationBanner,
  BusinessReviewCard,
} from "@/components/business/actioncenter/ui/BusinessActionDesignSystem";
import {
  clearQuickAddDraft,
  loadQuickAddDraft,
  saveQuickAddDraft,
  createClientRequestId,
} from "@/lib/quick_add/draftStore";
import { emitActionAnalytics, pushRecentAction } from "@/lib/action-center/actionCenterPrefs";
import type { BusinessCatalogAction } from "@/repositories/BusinessActionRepository";

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
  action: BusinessCatalogAction;
  momentId: string;
  userId?: string;
  templateId: string;
  steps: ProgressiveStep[];
  buildPayload: (state: FormState) => Record<string, unknown>;
  buildReviewRows?: (state: FormState) => Array<{ label: string; value: string }>;
  onSubmit: (payload: Record<string, unknown>) => Promise<unknown>;
  onClose: () => void;
  onSuccess?: (result?: {
    action_type: string;
    title: string;
    mutationResponse?: unknown;
  }) => void;
  draftTitleKey?: string;
  initialState?: FormState;
  contextChips?: string[];
  saveLabel?: string;
  reviewEnabled?: boolean;
};

export function ProgressiveActionForm({
  action,
  momentId,
  userId = "local",
  templateId,
  steps,
  buildPayload,
  buildReviewRows,
  onSubmit,
  onClose,
  onSuccess,
  draftTitleKey = "title",
  initialState,
  contextChips,
  saveLabel = "Save",
  reviewEnabled = false,
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
  const [showReview, setShowReview] = useState(false);
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
      analytics_id: action.action_id,
      event: "started",
      action_id: action.action_id,
      template_id: templateId,
    });
    const draft = loadQuickAddDraft(momentId, action.action_id);
    if (draft?.form && Object.keys(draft.form).length) {
      const form = draft.form as FormState;
      const title = String(form[draftTitleKey] ?? form.title ?? action.label);
      setDraftPrompt({ title, form });
    }
    return () => {
      if (!completed.current) {
        emitActionAnalytics({
          analytics_id: action.action_id,
          event: "abandoned",
          action_id: action.action_id,
          template_id: templateId,
          duration_ms: Date.now() - startedAt.current,
        });
      }
    };
  }, [action, momentId, templateId, draftTitleKey]);

  useEffect(() => {
    if (action.supports?.drafts === false) return;
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

  const [mutationResponse, setMutationResponse] = useState<unknown>(null);

  async function handleSave() {
    const allErrors: Record<string, string> = {};
    for (const s of steps) Object.assign(allErrors, s.validate?.(state) ?? {});
    if (Object.keys(allErrors).length) {
      setErrors(allErrors);
      setBanner(Object.values(allErrors));
      return;
    }
    try {
      setBusy(true);
      const res = await onSubmit(buildPayload(state));
      setMutationResponse(res ?? null);
      clearQuickAddDraft(momentId, action.action_id);
      pushRecentAction(userId, templateId, action.action_id);
      completed.current = true;
      emitActionAnalytics({
        analytics_id: action.action_id,
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
      return;
    }
    setBanner([]);
    if (isLastStep) {
      if (reviewEnabled && !showReview) {
        setShowReview(true);
      } else {
        void handleSave();
      }
    } else {
      setStepIndex((i) => i + 1);
    }
  }

  if (draftPrompt) {
    return (
      <div className="space-y-6 py-4">
        <BusinessActionHeader title="Continue editing?" subtitle={`You have a draft for ${draftPrompt.title}.`} />
        <BusinessFooter
          primaryLabel="Continue"
          onPrimary={() => {
            setState(draftPrompt.form);
            setDraftPrompt(null);
            emitActionAnalytics({
              analytics_id: action.action_id,
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

  if (showReview && buildReviewRows) {
    const rows = buildReviewRows(state);
    return (
      <div className="relative space-y-5 pb-2">
        <BusinessActionHeader title="Review" subtitle={`Confirm ${action.label} details before saving.`} />
        <BusinessReviewCard title={action.label} rows={rows} />
        <BusinessFooter
          primaryLabel={busy ? "Saving…" : "Confirm & Save"}
          onPrimary={() => void handleSave()}
          secondaryLabel="Edit"
          onSecondary={() => setShowReview(false)}
          busy={busy}
        />
        <BusinessSuccessOverlay
          open={success}
          onDone={() => {
            onSuccess?.({
              action_type: action.action_type,
              title: String(state.title ?? action.label),
              mutationResponse,
            });
            onClose();
          }}
        />
      </div>
    );
  }

  return (
    <div className="relative space-y-5 pb-2">
      <BusinessActionHeader
        title={action.label}
        subtitle={action.subtitle}
        estimatedTimeSec={action.estimated_time_sec}
      />
      {contextChips?.length ? <BusinessContextChips chips={contextChips} /> : null}
      <BusinessValidationBanner messages={banner} />

      <BusinessSection
        title={singleScreen ? undefined : current?.title}
        step={singleScreen ? undefined : stepIndex + 1}
        totalSteps={singleScreen ? undefined : totalSteps}
      >
        {current?.render({ state, set, errors })}
      </BusinessSection>
      <BusinessFooter
        primaryLabel={isLastStep ? (busy ? "Saving…" : saveLabel) : "Continue"}
        onPrimary={goNextOrSave}
        secondaryLabel={stepIndex > 0 ? "Back" : "Cancel"}
        onSecondary={() => {
          if (stepIndex > 0) setStepIndex((i) => i - 1);
          else onClose();
        }}
        busy={busy}
      />

      <BusinessSuccessOverlay
        open={success}
        onDone={() => {
          onSuccess?.({
            action_type: action.action_type,
            title: String(state.title ?? action.label),
            mutationResponse,
          });
          onClose();
        }}
      />
    </div>
  );
}

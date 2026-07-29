"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api/client";
import type { BusinessSetupPreview, BusinessSetupState } from "@/lib/api/business";
import { BusinessSetupRepository } from "@/repositories/BusinessSetupRepository";
import { markBusinessSetupGetDone } from "@/lib/telemetry/businessSetupTelemetry";

export type UseBusinessSetupFlowOptions = {
  /** From createDraft — skip GET /setup on first paint for this moment. */
  initialSetup?: BusinessSetupState | null;
};

const ACTIVATED_DRAFT_ERROR = "Cannot save draft for an activated moment";

function isActiveStatus(status?: string | null): boolean {
  return (status ?? "").toUpperCase() === "ACTIVE";
}

function isActivatedDraftError(err: unknown): boolean {
  return err instanceof ApiError && err.message.includes(ACTIVATED_DRAFT_ERROR);
}

/**
 * Business setup ViewModel — UI must use this, never API client directly.
 * Draft autosave: 400ms debounce. Preview: on-demand only (Review / Activate).
 */
export function useBusinessSetupFlow(
  momentId: string | null,
  options?: UseBusinessSetupFlowOptions,
) {
  const initialSetup = options?.initialSetup ?? null;
  const seed =
    initialSetup && momentId && initialSetup.moment_id === momentId ? initialSetup : null;

  const [setup, setSetup] = useState<BusinessSetupState | null>(seed);
  const [preview, setPreview] = useState<BusinessSetupPreview | null>(null);
  const [answers, setAnswers] = useState<Record<string, unknown>>(
    () => (seed ? { ...(seed.answers ?? {}) } : {}),
  );
  const [loading, setLoading] = useState(() => Boolean(momentId) && !seed);
  const [saving, setSaving] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<"idle" | "dirty" | "saving" | "saved" | "error">(
    "idle",
  );
  const draftTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingAnswersRef = useRef<Record<string, unknown> | null>(null);
  const requestSeq = useRef(0);
  const loadedMomentIdRef = useRef<string | null>(seed ? momentId : null);
  const seededRef = useRef(Boolean(seed));
  const statusRef = useRef<string>(seed?.status ?? "DRAFT");

  const applySetup = useCallback((state: BusinessSetupState) => {
    loadedMomentIdRef.current = state.moment_id;
    statusRef.current = state.status;
    setSetup(state);
    setAnswers({ ...(state.answers ?? {}) });
    setLoading(false);
  }, []);

  const markLocalActive = useCallback(() => {
    statusRef.current = "ACTIVE";
    setSetup((prev) => (prev ? { ...prev, status: "ACTIVE" } : prev));
  }, []);

  const load = useCallback(
    async (id: string, force = false) => {
      if (!force && loadedMomentIdRef.current === id) return;
      // Create-seeded open: skip GET unless force reload.
      if (!force && seededRef.current && id === seed?.moment_id) {
        loadedMomentIdRef.current = id;
        setLoading(false);
        markBusinessSetupGetDone({ cache: "create_seed" });
        return;
      }
      setLoading(true);
      setError(null);
      const seq = ++requestSeq.current;
      try {
        const state = await BusinessSetupRepository.getSetupState(id);
        if (seq !== requestSeq.current) return;
        applySetup(state);
        markBusinessSetupGetDone();
      } catch (err) {
        if (seq !== requestSeq.current) return;
        loadedMomentIdRef.current = null;
        setError(err instanceof ApiError ? err.message : "Failed to load setup");
        setLoading(false);
      }
    },
    [applySetup, seed?.moment_id],
  );

  useEffect(() => {
    if (!momentId) {
      loadedMomentIdRef.current = null;
      seededRef.current = false;
      setSetup(null);
      setPreview(null);
      setAnswers({});
      setLoading(false);
      return;
    }
    if (seed && seed.moment_id === momentId) {
      seededRef.current = true;
      applySetup(seed);
      markBusinessSetupGetDone({ cache: "create_seed" });
      return;
    }
    seededRef.current = false;
    void load(momentId);
  }, [momentId, seed, load, applySetup]);

  useEffect(() => {
    return () => {
      if (draftTimer.current) clearTimeout(draftTimer.current);
    };
  }, []);

  const persistDraft = useCallback(
    async (nextAnswers: Record<string, unknown>) => {
      if (!momentId) return false;
      if (isActiveStatus(statusRef.current)) return true;
      setSaving(true);
      setSaveStatus("saving");
      try {
        const state = await BusinessSetupRepository.saveDraft(momentId, nextAnswers);
        statusRef.current = state.status;
        setSetup(state);
        pendingAnswersRef.current = null;
        setSaveStatus("saved");
        return true;
      } catch (err) {
        if (isActivatedDraftError(err)) {
          markLocalActive();
          pendingAnswersRef.current = null;
          setSaveStatus("idle");
          return true;
        }
        setSaveStatus("error");
        return false;
      } finally {
        setSaving(false);
      }
    },
    [momentId, markLocalActive],
  );

  const scheduleDraftSave = useCallback(
    (nextAnswers: Record<string, unknown>) => {
      if (!momentId) return;
      if (isActiveStatus(statusRef.current)) return;
      pendingAnswersRef.current = nextAnswers;
      setSaveStatus("dirty");
      if (draftTimer.current) clearTimeout(draftTimer.current);

      draftTimer.current = setTimeout(() => {
        draftTimer.current = null;
        if (isActiveStatus(statusRef.current)) return;
        void persistDraft(nextAnswers);
      }, 400);
    },
    [momentId, persistDraft],
  );

  /** Cancel debounce and save immediately — required before Continue / Review. */
  const flushPendingSave = useCallback(async () => {
    if (draftTimer.current) {
      clearTimeout(draftTimer.current);
      draftTimer.current = null;
    }
    const pending = pendingAnswersRef.current;
    if (!pending) {
      if (saveStatus === "dirty") {
        return persistDraft(answers);
      }
      return saveStatus !== "error";
    }
    return persistDraft(pending);
  }, [answers, persistDraft, saveStatus]);

  const updateAnswer = useCallback(
    (fieldKey: string, value: unknown) => {
      setAnswers((prev) => {
        const next = { ...prev, [fieldKey]: value };
        scheduleDraftSave(next);
        return next;
      });
    },
    [scheduleDraftSave],
  );

  const updateAnswers = useCallback(
    (patch: Record<string, unknown>) => {
      setAnswers((prev) => {
        const next = { ...prev, ...patch };
        scheduleDraftSave(next);
        return next;
      });
    },
    [scheduleDraftSave],
  );

  const setProgress = useCallback(
    async (currentStep: number, completedSteps?: number[]) => {
      if (!momentId) return;
      if (isActiveStatus(statusRef.current)) return;
      setAnswers((prev) => {
        void BusinessSetupRepository.saveDraft(momentId, prev, {
          current_step: currentStep,
          completed_steps: completedSteps ?? [],
        })
          .then((state) => {
            statusRef.current = state.status;
            setSetup(state);
          })
          .catch((err) => {
            if (isActivatedDraftError(err)) markLocalActive();
          });
        return prev;
      });
    },
    [momentId, markLocalActive],
  );

  /** Preview on Review / Activate only — not on every keystroke. */
  const requestPreview = useCallback(async () => {
    if (!momentId) return null;
    try {
      const p = await BusinessSetupRepository.preview(momentId, answers);
      setPreview(p);
      return p;
    } catch {
      setPreview(null);
      return null;
    }
  }, [momentId, answers]);

  const activate = useCallback(async () => {
    if (!momentId) return false;
    if (draftTimer.current) {
      clearTimeout(draftTimer.current);
      draftTimer.current = null;
    }
    setSubmitting(true);
    setError(null);
    try {
      // Backend rejects draft writes once ACTIVE. Skip (or tolerate) so reopen /
      // double-submit / post-activate races still complete activate successfully.
      if (!isActiveStatus(statusRef.current)) {
        try {
          const state = await BusinessSetupRepository.saveDraft(momentId, answers);
          statusRef.current = state.status;
          setSetup(state);
        } catch (err) {
          if (!isActivatedDraftError(err)) throw err;
          markLocalActive();
        }
      }
      const p = await BusinessSetupRepository.preview(momentId, answers);
      setPreview(p);
      if (p && p.activation_ready === false && !isActiveStatus(statusRef.current)) {
        const detail = p.blocking_errors?.join("; ") || "Setup is not ready to activate";
        setError(detail);
        setSubmitting(false);
        return false;
      }
      await BusinessSetupRepository.activate(momentId);
      markLocalActive();
      setSubmitting(false);
      return true;
    } catch (err) {
      // First activate can race past the client timeout after the server already
      // committed ACTIVE. Retry once — the ACTIVE fast path returns quickly.
      const timedOut =
        err instanceof ApiError &&
        (err.status === 408 || /timed out/i.test(err.message));
      if (timedOut && momentId) {
        try {
          await BusinessSetupRepository.activate(momentId);
          markLocalActive();
          setSubmitting(false);
          return true;
        } catch (retryErr) {
          // Fall through: check status via setup GET
          try {
            const state = await BusinessSetupRepository.getSetupState(momentId);
            if (isActiveStatus(state.status)) {
              applySetup(state);
              markLocalActive();
              setSubmitting(false);
              return true;
            }
          } catch {
            /* ignore */
          }
          setError(retryErr instanceof ApiError ? retryErr.message : "Failed to activate");
          setSubmitting(false);
          return false;
        }
      }
      setError(err instanceof ApiError ? err.message : "Failed to activate");
      setSubmitting(false);
      return false;
    }
  }, [momentId, answers, markLocalActive, applySetup]);

  return {
    setup,
    preview,
    answers,
    loading,
    saving,
    saveStatus,
    submitting,
    error,
    updateAnswer,
    updateAnswers,
    setProgress,
    flushPendingSave,
    requestPreview,
    activate,
    reload: () => (momentId ? load(momentId, true) : Promise.resolve()),
  };
}

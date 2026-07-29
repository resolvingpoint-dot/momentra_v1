"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "@/lib/api/client";
import type {
  PersonalSetupAnswers,
  PersonalSetupPreview,
  PersonalSetupResponse,
} from "@/lib/api/personal";
import {
  enrichAnswersWithTemplateMeta,
  mergeSetupWithTemplate,
  normalizeAnswerKeys,
  resolveTemplateForSetup,
} from "@/lib/setup/templates/templateResolver";
import type { MomentSetupTemplate } from "@/lib/setup/templates/types";
import { TEMPLATE_META_KEYS } from "@/lib/setup/templates/types";
import { SetupRepository } from "@/repositories/SetupRepository";

export type SetupFlowSaveState = "idle" | "dirty" | "saving" | "saved" | "error";

function parseSavedAnswers(
  saved: PersonalSetupAnswers | null | undefined,
): PersonalSetupAnswers {
  if (!saved) return {};
  return normalizeAnswerKeys(saved);
}

function stripTemplateMeta(answers: PersonalSetupAnswers): PersonalSetupAnswers {
  const { [TEMPLATE_META_KEYS.templateId]: _id, [TEMPLATE_META_KEYS.templateVersion]: _ver, ...rest } =
    answers;
  return rest;
}

/**
 * Shared setup ViewModel hook — setup UI must use this, never API client directly.
 * Draft autosave is debounced. Preview is on-demand (Review) only — never on keystroke.
 */
export function useSetupFlow(momentId: string | null) {
  const [setup, setSetup] = useState<PersonalSetupResponse | null>(null);
  const [template, setTemplate] = useState<MomentSetupTemplate | null>(null);
  const [preview, setPreview] = useState<PersonalSetupPreview | null>(null);
  const [answers, setAnswers] = useState<PersonalSetupAnswers>({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<SetupFlowSaveState>("idle");
  const draftTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingAnswersRef = useRef<PersonalSetupAnswers | null>(null);
  const templateRef = useRef<MomentSetupTemplate | null>(null);
  const loadedMomentIdRef = useRef<string | null>(null);

  const load = useCallback(async (id: string, force = false) => {
    if (!force && loadedMomentIdRef.current === id) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await SetupRepository.getSetupState(id);
      const resolvedTemplate = resolveTemplateForSetup(response);
      const merged = mergeSetupWithTemplate(response, resolvedTemplate);
      const saved = parseSavedAnswers(merged.saved_answers);
      templateRef.current = resolvedTemplate;
      loadedMomentIdRef.current = id;
      setTemplate(resolvedTemplate);
      setSetup(merged);
      setAnswers(stripTemplateMeta(saved));
      setPreview(null);
      setLoading(false);
    } catch (err) {
      loadedMomentIdRef.current = null;
      setError(err instanceof ApiError ? err.message : "Failed to load setup");
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!momentId) {
      loadedMomentIdRef.current = null;
      setSetup(null);
      setTemplate(null);
      setPreview(null);
      setAnswers({});
      templateRef.current = null;
      return;
    }
    void load(momentId);
  }, [momentId, load]);

  useEffect(() => {
    return () => {
      if (draftTimer.current) clearTimeout(draftTimer.current);
    };
  }, []);

  const persistDraft = useCallback(
    async (nextAnswers: PersonalSetupAnswers) => {
      if (!momentId) return false;
      const payload = enrichAnswersWithTemplateMeta(nextAnswers, templateRef.current);
      setSaveStatus("saving");
      try {
        await SetupRepository.saveDraft(momentId, payload);
        pendingAnswersRef.current = null;
        setSaveStatus("saved");
        return true;
      } catch {
        setSaveStatus("error");
        return false;
      }
    },
    [momentId],
  );

  const scheduleDraftSave = useCallback(
    (nextAnswers: PersonalSetupAnswers) => {
      if (!momentId) return;
      pendingAnswersRef.current = nextAnswers;
      setSaveStatus("dirty");
      if (draftTimer.current) clearTimeout(draftTimer.current);
      draftTimer.current = setTimeout(() => {
        draftTimer.current = null;
        void persistDraft(nextAnswers);
      }, 400);
    },
    [momentId, persistDraft],
  );

  const flushPendingSave = useCallback(async () => {
    if (draftTimer.current) {
      clearTimeout(draftTimer.current);
      draftTimer.current = null;
    }
    const pending = pendingAnswersRef.current;
    if (!pending) {
      if (saveStatus === "dirty") return persistDraft(answers);
      return saveStatus !== "error";
    }
    return persistDraft(pending);
  }, [answers, persistDraft, saveStatus]);

  const requestPreview = useCallback(async () => {
    if (!momentId) return null;
    try {
      const payload = enrichAnswersWithTemplateMeta(answers, templateRef.current);
      const previewResponse = await SetupRepository.preview(momentId, payload);
      setPreview(previewResponse);
      return previewResponse;
    } catch {
      setPreview(null);
      return null;
    }
  }, [momentId, answers]);

  const updateAnswer = useCallback(
    (fieldKey: string, value: string | string[]) => {
      setAnswers((prev) => {
        const next = { ...prev, [fieldKey]: value };
        scheduleDraftSave(next);
        return next;
      });
    },
    [scheduleDraftSave],
  );

  const toggleMulti = useCallback(
    (fieldKey: string, optionValue: string) => {
      setAnswers((prev) => {
        const current = Array.isArray(prev[fieldKey])
          ? (prev[fieldKey] as string[])
          : [];
        const nextSet = current.includes(optionValue)
          ? current.filter((v) => v !== optionValue)
          : [...current, optionValue];
        const next = { ...prev, [fieldKey]: nextSet };
        scheduleDraftSave(next);
        return next;
      });
    },
    [scheduleDraftSave],
  );

  const submit = useCallback(async () => {
    if (!momentId) return false;
    setSubmitting(true);
    setError(null);
    try {
      await flushPendingSave();
      const payload = enrichAnswersWithTemplateMeta(answers, templateRef.current);
      await SetupRepository.activate(momentId, payload);
      setSubmitting(false);
      return true;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to activate moment");
      setSubmitting(false);
      return false;
    }
  }, [momentId, answers, flushPendingSave]);

  const canSubmit =
    setup?.fields
      .filter((f) => f.required)
      .every((field) => {
        const value = answers[field.field_key];
        if (field.field_type === "multi_select") {
          return Array.isArray(value) && value.length > 0;
        }
        return typeof value === "string" && value.length > 0;
      }) ?? false;

  return {
    setup,
    template,
    preview,
    answers,
    loading,
    submitting,
    error,
    canSubmit,
    saveStatus,
    updateAnswer,
    toggleMulti,
    flushPendingSave,
    requestPreview,
    submit,
  };
}

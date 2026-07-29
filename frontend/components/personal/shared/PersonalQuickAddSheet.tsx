"use client";

import { useCallback, useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import {
  createPersonalQuickAdd,
  getPersonalQuickAddOptions,
  type PersonalQuickAddOptionsResponse,
} from "@/lib/api/client";

type QuickAddTarget = {
  momentTypeCode: string;
  apiEventType: string;
  title: string;
  subtitle: string;
};

function resolveTarget(eventType?: string | null): QuickAddTarget {
  const normalized = (eventType ?? "").toUpperCase();
  if (normalized === "MILESTONE" || normalized === "LOG_PROGRESS") {
    return {
      momentTypeCode: "FUTURE_BUILDING",
      apiEventType: "MILESTONE",
      title: "Log Progress",
      subtitle: "Capture a milestone in your future-building moment.",
    };
  }
  if (normalized === "CUSTOM_ACTIVITY" || normalized === "LOG_EXPERIENCE") {
    return {
      momentTypeCode: "LIFESTYLE",
      apiEventType: "EXPERIENCE",
      title: "Log Experience",
      subtitle: "Capture a meaningful lifestyle experience.",
    };
  }
  if (normalized === "REFLECTION") {
    return {
      momentTypeCode: "LIFE_OPERATIONS",
      apiEventType: "REFLECTION",
      title: "Log Reflection",
      subtitle: "Note how today felt.",
    };
  }
  return {
    momentTypeCode: "LIFE_OPERATIONS",
    apiEventType: "RECOVERY",
    title: "Log Recovery",
    subtitle: "Capture what restores your flow.",
  };
}

function buildRequest(momentId: string, target: QuickAddTarget) {
  const base = {
    moment_id: momentId,
    event_type: target.apiEventType,
    event_title: target.title,
  };
  switch (target.apiEventType) {
    case "MILESTONE":
      return { ...base, future_building: {} };
    case "EXPERIENCE":
      return { ...base, lifestyle: {} };
    case "REFLECTION":
      return { ...base, reflection: {} };
    default:
      return { ...base, recovery: {} };
  }
}

type PersonalQuickAddSheetProps = {
  initialEventType?: string | null;
  momentTypeCode?: string | null;
  momentId?: string | null;
  onClose: () => void;
  onSuccess?: () => void;
};

/** Legacy minimal quick-add sheet. Prefer `PersonalMomentQuickAddRouter` for personal home +. */
export function PersonalQuickAddSheet({
  initialEventType,
  momentTypeCode,
  momentId,
  onClose,
  onSuccess,
}: PersonalQuickAddSheetProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const target = resolveTarget(initialEventType);
  const resolvedTypeCode = momentTypeCode?.toUpperCase() ?? target.momentTypeCode;

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [options, setOptions] = useState<PersonalQuickAddOptionsResponse | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setOptions(await getPersonalQuickAddOptions(momentId ?? undefined));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load Quick Add.");
    } finally {
      setLoading(false);
    }
  }, [momentId]);

  useEffect(() => {
    void load();
  }, [load]);

  const moment =
    (momentId ? options?.moments.find((m) => m.moment_id === momentId) : null) ??
    options?.moments.find((m) => m.moment_type_code === resolvedTypeCode) ??
    options?.moments[0] ??
    null;

  async function handleSubmit() {
    if (!moment) return;
    setSubmitting(true);
    setError(null);
    try {
      await createPersonalQuickAdd(buildRequest(moment.moment_id, target));
      onSuccess?.();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Quick Add failed.");
      setSubmitting(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/50 sm:items-center"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-t-2xl border p-6 sm:rounded-2xl"
        style={{
          borderColor: colors.border,
          background: colors.surface,
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h2 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>{target.title}</h2>
        <p className="mt-2" style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
          {target.subtitle}
        </p>

        <div className="mt-6 space-y-4">
          {loading ? (
            <p style={{ color: colors.textSecondary }}>Loading…</p>
          ) : error ? (
            <p style={{ color: colors.error }}>{error}</p>
          ) : moment ? (
            <>
              <p style={{ ...personalTypography.labelSm, color: colors.textSecondary }}>
                Moment: {moment.moment_name}
              </p>
              <button
                type="button"
                disabled={submitting}
                onClick={() => void handleSubmit()}
                className="w-full rounded-xl py-3 font-semibold"
                style={{
                  background: colors.brandPrimary,
                  color: colors.brandOnPrimary,
                  opacity: submitting ? 0.7 : 1,
                }}
              >
                {submitting ? "Logging…" : "Log now"}
              </button>
            </>
          ) : (
            <p style={{ ...personalTypography.labelSm, color: colors.textSecondary }}>
              Activate a {resolvedTypeCode.replace(/_/g, " ").toLowerCase()} moment to use Quick Add.
            </p>
          )}
          <button
            type="button"
            onClick={onClose}
            className="w-full rounded-xl border py-3"
            style={{ borderColor: colors.border, color: colors.textSecondary }}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

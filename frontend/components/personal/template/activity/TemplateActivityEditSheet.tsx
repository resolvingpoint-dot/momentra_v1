"use client";

import { useCallback, useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import { getActivityAdapter } from "@/lib/personal/template/activity/getActivityAdapter";
import type {
  TemplateActivityDetail,
  TemplateActivityEditField,
} from "@/lib/personal/template/activity/types";
import { PersonalRepository } from "@/repositories/PersonalRepository";
import { getPersonalQuickAddOptions } from "@/lib/api/client";

type TemplateActivityEditSheetProps = {
  momentTypeCode: PersonalMomentTypeCode;
  eventId: string;
  eventType: string;
  onClose: () => void;
  onSuccess: () => void;
};

function readFieldValue(detail: TemplateActivityDetail, field: TemplateActivityEditField): string {
  const source = (detail.values as Record<string, unknown> | undefined) ?? detail;
  if (field.path) {
    const parts = field.path.split(".");
    let current: unknown = source;
    for (const part of parts) {
      if (!current || typeof current !== "object") return "";
      current = (current as Record<string, unknown>)[part];
    }
    return current == null ? "" : String(current);
  }
  const raw = source[field.key];
  return raw == null ? "" : String(raw);
}

function buildPatchBody(
  detail: TemplateActivityDetail,
  fields: TemplateActivityEditField[],
  values: Record<string, string>,
): Record<string, unknown> {
  const body: Record<string, unknown> = {};
  const source = (detail.values as Record<string, unknown> | undefined) ?? detail;

  for (const field of fields) {
    const value = values[field.key] ?? "";
    if (field.key === "event_title") {
      body.event_title = value.trim();
      continue;
    }
    if (field.key === "event_summary") {
      body.event_summary = value.trim() || null;
      continue;
    }
    if (field.path?.startsWith("expense.")) {
      const expense = {
        ...((source.expense as Record<string, unknown> | undefined) ?? {}),
        ...((body.expense as Record<string, unknown> | undefined) ?? {}),
      };
      const key = field.path.split(".")[1];
      if (key === "amount") {
        expense.amount = value;
      } else {
        expense[key] = value || undefined;
      }
      body.expense = expense;
      continue;
    }
    if (field.path?.startsWith("future_building.")) {
      const fb = {
        ...((source.future_building as Record<string, unknown> | undefined) ?? {}),
        ...((body.future_building as Record<string, unknown> | undefined) ?? {}),
      };
      const key = field.path.split(".")[1];
      fb[key] = value;
      body.future_building = fb;
    }
  }

  return body;
}

export function TemplateActivityEditSheet({
  momentTypeCode,
  eventId,
  onClose,
  onSuccess,
}: TemplateActivityEditSheetProps) {
  const adapter = getActivityAdapter(momentTypeCode);
  const { colors } = useThemeTokens();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [detail, setDetail] = useState<TemplateActivityDetail | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [accounts, setAccounts] = useState<Array<{ account_id: string; account_name: string }>>([]);

  const fields = detail?.edit_schema?.fields ?? [];

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [data, options] = await Promise.all([
        PersonalRepository.getTemplateActivityDetail(momentTypeCode, eventId),
        getPersonalQuickAddOptions().catch(() => ({ accounts: [] })),
      ]);
      setDetail(data);
      setAccounts(options.accounts ?? []);
      const schemaFields = data.edit_schema?.fields ?? [];
      const next: Record<string, string> = {};
      for (const field of schemaFields) {
        next[field.key] = readFieldValue(data, field);
      }
      setValues(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load activity.");
    } finally {
      setLoading(false);
    }
  }, [eventId, momentTypeCode]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  function setFieldValue(key: string, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!detail) return;
    setSubmitting(true);
    setError(null);
    try {
      const body = buildPatchBody(detail, fields, values);
      await PersonalRepository.patchTemplateActivity(momentTypeCode, eventId, body);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save changes.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete() {
    if (!window.confirm(adapter.deleteConfirm)) return;
    setDeleting(true);
    setError(null);
    try {
      await PersonalRepository.deleteTemplateActivity(momentTypeCode, eventId);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not delete activity.");
    } finally {
      setDeleting(false);
    }
  }

  function renderField(field: TemplateActivityEditField) {
    const value = values[field.key] ?? "";
    const labelStyle = {
      fontSize: 11,
      fontWeight: 700,
      opacity: 0.5,
      textTransform: "uppercase" as const,
    };
    const inputStyle = {
      background: colors.surfaceContainerLowest,
      borderColor: "rgba(255,255,255,0.05)",
      color: colors.textPrimary,
    };

    if (field.field_type === "textarea") {
      return (
        <label key={field.key} className="block">
          <span style={labelStyle}>{field.label}</span>
          <textarea
            value={value}
            onChange={(e) => setFieldValue(field.key, e.target.value)}
            rows={3}
            className="mt-2 w-full rounded-xl border px-4 py-3"
            style={inputStyle}
          />
        </label>
      );
    }

    if (field.field_type === "account") {
      return (
        <label key={field.key} className="block">
          <span style={labelStyle}>{field.label}</span>
          <select
            value={value}
            onChange={(e) => setFieldValue(field.key, e.target.value)}
            className="mt-2 w-full rounded-xl border px-4 py-3"
            style={inputStyle}
          >
            {accounts.map((account) => (
              <option key={account.account_id} value={account.account_id}>
                {account.account_name}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (field.field_type === "single_select" || field.field_type === "chip_grid") {
      const options = field.options ?? [];
      return (
        <label key={field.key} className="block">
          <span style={labelStyle}>{field.label}</span>
          <div className="mt-2 flex flex-wrap gap-2">
            {options.map((option) => {
              const active = value === option.value;
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => setFieldValue(field.key, option.value)}
                  className="rounded-full px-4 py-2 text-xs font-bold"
                  style={{
                    background: active ? colors.brandPrimary : colors.surfaceContainerHigh,
                    color: active ? colors.brandOnPrimary : colors.textSecondary,
                    border: "1px solid rgba(255,255,255,0.05)",
                  }}
                >
                  {option.label}
                </button>
              );
            })}
          </div>
        </label>
      );
    }

    return (
      <label key={field.key} className="block">
        <span style={labelStyle}>{field.label}</span>
        <input
          value={value}
          onChange={(e) => setFieldValue(field.key, e.target.value)}
          className="mt-2 w-full rounded-xl border px-4 py-3"
          style={inputStyle}
        />
      </label>
    );
  }

  const canDelete = detail?.edit_schema?.allowed_actions?.includes("delete") ?? true;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-end justify-center"
      style={{ background: "rgba(0,0,0,0.6)" }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-lg rounded-t-[32px] p-8"
        style={{ background: colors.surfaceContainerHigh, borderTop: "1px solid rgba(255,255,255,0.1)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-8 h-1.5 w-12 rounded-full" style={{ background: "rgba(255,255,255,0.1)" }} />
        <div className="mb-6">
          <h2 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
            {adapter.editTitle}
          </h2>
          <p style={{ ...personalTypography.bodyMd, opacity: 0.6 }}>{adapter.editSubtitle}</p>
        </div>

        {loading ? (
          <p style={{ opacity: 0.7 }}>Loading…</p>
        ) : (
          <form className="space-y-4" onSubmit={(e) => void handleSave(e)}>
            {fields.map(renderField)}

            {error ? <p style={{ color: colors.error, fontSize: 13 }}>{error}</p> : null}

            {canDelete ? (
              <button
                type="button"
                onClick={() => void handleDelete()}
                disabled={deleting || submitting}
                className="w-full rounded-2xl py-3 text-sm font-bold"
                style={{
                  background: "transparent",
                  color: colors.error,
                  border: `1px solid ${colors.error}55`,
                }}
              >
                {deleting ? "Deleting…" : adapter.deleteLabel}
              </button>
            ) : null}

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 rounded-2xl py-4 font-bold"
                style={{ background: `${colors.surfaceVariant}4d`, color: colors.textSecondary, border: "none" }}
              >
                {adapter.cancel}
              </button>
              <button
                type="submit"
                disabled={submitting || deleting}
                className="flex-[2] rounded-2xl py-4 font-bold"
                style={{ background: colors.brandPrimary, color: "#fff", border: "none" }}
              >
                {adapter.saveChanges}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

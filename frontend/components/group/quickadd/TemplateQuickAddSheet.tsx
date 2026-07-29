"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { GroupQuickAddShell } from "@/components/group/quickadd/GroupQuickAddShell";
import { GroupSkeletonBlocks } from "@/components/group/shared/skeleton/GroupSkeletonBlocks";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  buildLivingQuickAddPayload,
  buildPurchaseQuickAddPayload,
  canSubmitTemplateAction,
  defaultTemplateFormState,
  templateAction,
  type TemplateQuickAddFormState,
} from "@/lib/quick_add/payloadBuilders/groupTemplate";
import type { QuickAddField } from "@/lib/quick_add/types";
import {
  fetchGroupTemplateQuickAddContext,
  moduleCodeToActionId,
  submitGroupTemplateQuickAdd,
  type TemplateQuickAddKind,
} from "@/repositories/GroupTemplateQuickAddRepository";

type TemplateQuickAddSheetProps = {
  kind: TemplateQuickAddKind;
  momentId: string;
  /** Backend hub module_code (e.g. CONTRIBUTORS) or registry action_id */
  moduleOrActionId: string;
  onClose: () => void;
  onSuccess?: () => void;
};

function labelFor(value: string) {
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function contextOptions(
  context: Record<string, unknown> | null,
  fieldKey: string,
): Array<{ value: string; label: string }> {
  if (!context) return [];
  const candidates = [
    fieldKey,
    `${fieldKey}s`,
    `${fieldKey}_options`,
    fieldKey.replace(/_type$/, "_types"),
    fieldKey.replace(/_status$/, "_statuses"),
    fieldKey.replace(/_category$/, "_categories"),
    fieldKey === "role" ? "roles" : "",
    fieldKey === "usage_rights" ? "usage_rights_options" : "",
    fieldKey === "invite_method" ? "invite_methods" : "",
    fieldKey === "invite_status" ? "invite_statuses" : "",
    fieldKey === "scope" ? "scopes" : "",
    fieldKey === "visibility" ? "visibility_options" : "",
    fieldKey === "event_type" ? "event_types" : "",
    fieldKey === "status" ? "statuses" : "",
    fieldKey === "memory_category" ? "memory_categories" : "",
    fieldKey === "resident_role" ? "resident_roles" : "",
    fieldKey === "relationship_type" ? "relationship_types" : "",
    fieldKey === "expense_category" ? "expense_categories" : "",
    fieldKey === "split_type" ? "split_types" : "",
  ].filter(Boolean);

  for (const key of candidates) {
    const raw = context[key];
    if (!Array.isArray(raw)) continue;
    return raw.map((item) => {
      if (typeof item === "string") return { value: item, label: labelFor(item) };
      const record = item as Record<string, unknown>;
      return {
        value: String(record.value ?? record.id ?? ""),
        label: String(record.label ?? record.value ?? ""),
      };
    });
  }
  return [];
}

function FieldInput({
  field,
  value,
  onChange,
  options,
  colors,
}: {
  field: QuickAddField;
  value: TemplateQuickAddFormState[string];
  onChange: (next: TemplateQuickAddFormState[string]) => void;
  options: Array<{ value: string; label: string }>;
  colors: ReturnType<typeof useThemeTokens>["colors"];
}) {
  const inputStyle = {
    background: colors.surfaceContainer,
    color: colors.textPrimary,
    border: `1px solid ${colors.textSecondary}25`,
  };

  if (field.field_type === "single_select" || field.field_type === "segmented") {
    return (
      <div className="flex flex-wrap gap-2">
        {(options.length ? options : [{ value: "default", label: "Default" }]).map((opt) => {
          const selected = value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange(opt.value)}
              className="rounded-full px-3 py-1.5 text-xs font-semibold"
              style={{
                background: selected ? colors.primaryContainer : colors.surfaceContainer,
                color: selected ? colors.brandOnPrimary : colors.textPrimary,
              }}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    );
  }

  if (field.field_type === "textarea") {
    return (
      <textarea
        value={String(value ?? "")}
        onChange={(e) => onChange(e.target.value)}
        rows={3}
        className="w-full rounded-xl px-3 py-2 text-sm"
        style={inputStyle}
      />
    );
  }

  if (field.field_type === "toggle") {
    return (
      <button
        type="button"
        onClick={() => onChange(!value)}
        className="rounded-full px-3 py-1.5 text-xs font-semibold"
        style={{
          background: value ? colors.primaryContainer : colors.surfaceContainer,
          color: value ? colors.brandOnPrimary : colors.textPrimary,
        }}
      >
        {value ? "On" : "Off"}
      </button>
    );
  }

  if (field.field_type === "multi_select") {
    return (
      <input
        type="text"
        placeholder="Option 1, Option 2, ..."
        value={Array.isArray(value) ? value.join(", ") : String(value ?? "")}
        onChange={(e) =>
          onChange(
            e.target.value
              .split(",")
              .map((s) => s.trim())
              .filter(Boolean),
          )
        }
        className="w-full rounded-xl px-3 py-2 text-sm"
        style={inputStyle}
      />
    );
  }

  if (field.field_type === "media_upload") {
    return (
      <p className="text-xs" style={{ color: colors.textSecondary }}>
        Media upload is not required for this action.
      </p>
    );
  }

  return (
    <input
      type={field.field_type === "amount" ? "number" : field.field_type === "date" ? "date" : "text"}
      value={String(value ?? "")}
      onChange={(e) => onChange(e.target.value)}
      className="w-full rounded-xl px-3 py-2 text-sm"
      style={inputStyle}
      placeholder={field.label}
    />
  );
}

export function TemplateQuickAddSheet({
  kind,
  momentId,
  moduleOrActionId,
  onClose,
  onSuccess,
}: TemplateQuickAddSheetProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const templateId = kind === "purchase" ? "group.purchase" : "group.living";
  const actionId = moduleCodeToActionId(kind, moduleOrActionId);
  const action = templateAction(templateId, actionId);
  const [form, setForm] = useState<TemplateQuickAddFormState>(() =>
    defaultTemplateFormState(templateId, actionId),
  );
  const [context, setContext] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const ctx = await fetchGroupTemplateQuickAddContext(kind, momentId, actionId);
      setContext(ctx);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load form");
    } finally {
      setLoading(false);
    }
  }, [kind, momentId, actionId]);

  useEffect(() => {
    void load();
  }, [load]);

  const canSubmit = useMemo(
    () => canSubmitTemplateAction(templateId, actionId, form),
    [templateId, actionId, form],
  );

  async function handleSubmit() {
    if (!canSubmit) return;
    try {
      setSubmitting(true);
      setError(null);
      const payload =
        kind === "purchase"
          ? buildPurchaseQuickAddPayload(actionId, form)
          : buildLivingQuickAddPayload(actionId, form);
      await submitGroupTemplateQuickAdd(kind, momentId, actionId, payload);
      onSuccess?.();
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save");
    } finally {
      setSubmitting(false);
    }
  }

  if (!action) {
    return (
      <GroupQuickAddShell title="Quick Add" onClose={onClose}>
        <p className="py-8 text-center text-sm opacity-70">Unknown action.</p>
      </GroupQuickAddShell>
    );
  }

  return (
    <GroupQuickAddShell title={action.label} onClose={onClose}>
      {loading ? (
        <GroupSkeletonBlocks variant="moments" />
      ) : error && !context ? (
        <div className="space-y-3 py-8 text-center">
          <p className="text-sm opacity-80">{error}</p>
          <button type="button" className="text-sm font-semibold underline" onClick={() => void load()}>
            Retry
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {context?.status_line ? (
            <p className="text-sm" style={{ color: colors.textSecondary }}>
              {String(context.status_line)}
            </p>
          ) : null}

          {action.fields.map((field) => (
            <div key={field.key} className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wide" style={{ color: colors.textSecondary }}>
                {field.label}
                {field.required ? " *" : ""}
              </label>
              <FieldInput
                field={field}
                value={form[field.key]}
                onChange={(next) => setForm((prev) => ({ ...prev, [field.key]: next }))}
                options={contextOptions(context, field.key)}
                colors={colors}
              />
            </div>
          ))}

          {error ? (
            <p className="text-sm" style={{ color: colors.error }}>
              {error}
            </p>
          ) : null}

          <button
            type="button"
            disabled={!canSubmit || submitting}
            onClick={() => void handleSubmit()}
            className="mt-2 w-full rounded-full py-3 text-sm font-bold uppercase tracking-wide disabled:opacity-50"
            style={{
              background: `linear-gradient(135deg, ${colors.primaryContainer} 0%, ${colors.secondaryContainer ?? colors.primaryContainer} 100%)`,
              color: colors.brandOnPrimary,
            }}
          >
            {submitting ? "Saving…" : action.cta_label}
          </button>
        </div>
      )}
    </GroupQuickAddShell>
  );
}

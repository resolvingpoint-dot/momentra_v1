"use client";

import { useMemo } from "react";
import {
  ProgressiveActionForm,
  type FormState,
  type ProgressiveStep,
} from "@/components/business/actioncenter/ProgressiveActionForm";
import {
  TextField,
  TextArea,
  MoneyInput,
  DateInput,
  MemberPicker,
  CurrencyPicker,
  ChipSelector,
  Toggle,
  NotesField,
  MemberMultiPicker,
  VendorPicker,
  ApprovalPicker,
  CategoryPicker,
  PrioritySelector,
  StatusSelector,
} from "@/components/business/actioncenter/fields";
import type { BusinessRendererMeta, BusinessRendererField, BusinessCatalogMember } from "@/repositories/BusinessActionRepository";
import type { BusinessActionRendererProps } from "@/components/business/actioncenter/actionRendererRegistry";
import { schemaAmountToMinor } from "@/components/business/actioncenter/renderers/dedicatedHelpers";

type SchemaDrivenRendererProps = BusinessActionRendererProps & {
  rendererMeta: BusinessRendererMeta;
  titleKey?: string;
  amountKey?: string;
  buildReviewRows?: (state: FormState) => Array<{ label: string; value: string }>;
  transformPayload?: (raw: Record<string, unknown>) => Record<string, unknown>;
};

function renderField(
  field: BusinessRendererField,
  state: FormState,
  set: (key: string, value: FormState[string]) => void,
  errors: Record<string, string>,
  members: BusinessCatalogMember[],
) {
  const val = state[field.key] ?? field.default_value ?? "";
  const err = errors[field.key];
  const strVal = String(val);

  switch (field.field_type) {
    case "text":
      return (
        <TextField
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          required={field.required}
          error={err}
          placeholder={field.placeholder}
        />
      );
    case "textarea":
      return (
        <TextArea
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          required={field.required}
          error={err}
        />
      );
    case "amount":
      return (
        <MoneyInput
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          required={field.required}
          error={err}
          currencyCode={String(state.currency ?? "INR")}
        />
      );
    case "date":
      return (
        <DateInput
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          required={field.required}
          error={err}
        />
      );
    case "member_picker":
      return (
        <MemberPicker
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          members={members}
          required={field.required}
          error={err}
        />
      );
    case "member_multi_picker":
      return (
        <MemberMultiPicker
          key={field.key}
          label={field.label}
          value={Array.isArray(state[field.key]) ? (state[field.key] as string[]) : []}
          onChange={(v) => set(field.key, v)}
          members={members}
          required={field.required}
          error={err}
        />
      );
    case "currency":
      return (
        <CurrencyPicker
          key={field.key}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          label={field.label}
        />
      );
    case "single_select":
    case "segmented":
    case "chip_grid":
      return (
        <ChipSelector
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          options={field.options ?? []}
          required={field.required}
          error={err}
        />
      );
    case "category":
      return (
        <CategoryPicker
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          options={field.options ?? []}
          required={field.required}
          error={err}
        />
      );
    case "vendor":
      return (
        <VendorPicker
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          required={field.required}
          error={err}
        />
      );
    case "approval":
      return (
        <ApprovalPicker
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          members={members}
          required={field.required}
          error={err}
        />
      );
    case "priority":
      return (
        <PrioritySelector
          key={field.key}
          value={strVal}
          onChange={(v) => set(field.key, v)}
        />
      );
    case "status":
      return (
        <StatusSelector
          key={field.key}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          options={field.options}
        />
      );
    case "toggle":
      return (
        <Toggle
          key={field.key}
          label={field.label}
          value={state[field.key] === true || state[field.key] === "true"}
          onChange={(v) => set(field.key, v)}
        />
      );
    case "notes":
      return (
        <NotesField
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
        />
      );
    default:
      return (
        <TextField
          key={field.key}
          label={field.label}
          value={strVal}
          onChange={(v) => set(field.key, v)}
          required={field.required}
          error={err}
        />
      );
  }
}

function isFieldVisible(field: BusinessRendererField, state: FormState): boolean {
  if (!field.visible_when) return true;
  return String(state[field.visible_when.field] ?? "") === field.visible_when.equals;
}

export function SchemaDrivenRenderer({
  action,
  momentId,
  templateId,
  members,
  rendererMeta,
  onSubmit,
  onClose,
  onSuccess,
  titleKey,
  amountKey,
  buildReviewRows: customReviewRows,
  transformPayload,
}: SchemaDrivenRendererProps) {
  const reviewEnabled = action.supports?.review !== false && rendererMeta.review_enabled !== false;

  const steps: ProgressiveStep[] = useMemo(() => {
    const meta = rendererMeta;
    if (meta.steps?.length) {
      return meta.steps.map((s) => {
        const stepFields = meta.fields.filter((f) => f.step_id === s.id || s.field_keys.includes(f.key));
        return {
          id: s.id,
          title: s.title,
          render: ({ state, set, errors }) => (
            <div className="space-y-4">
              {stepFields.filter((f) => isFieldVisible(f, state)).map((f) => renderField(f, state, set, errors, members))}
            </div>
          ),
          validate: (state: FormState) => {
            const errs: Record<string, string> = {};
            for (const f of stepFields) {
              if (!f.required) continue;
              const v = state[f.key];
              if (v == null || v === "" || (Array.isArray(v) && !v.length)) {
                errs[f.key] = `${f.label} is required`;
              }
            }
            if (amountKey && stepFields.some((f) => f.key === amountKey)) {
              const n = Number.parseFloat(String(state[amountKey] ?? ""));
              if (!Number.isFinite(n) || n <= 0) errs[amountKey] = "Enter a valid amount greater than 0";
            }
            return errs;
          },
        };
      });
    }

    return [
      {
        id: "form",
        title: meta.title || action.label,
        render: ({ state, set, errors }) => (
          <div className="space-y-4">
            {meta.fields.filter((f) => isFieldVisible(f, state)).map((f) => renderField(f, state, set, errors, members))}
          </div>
        ),
        validate: (state: FormState) => {
          const errs: Record<string, string> = {};
          for (const f of meta.fields) {
            if (!f.required) continue;
            const v = state[f.key];
            if (v == null || v === "" || (Array.isArray(v) && !v.length)) {
              errs[f.key] = `${f.label} is required`;
            }
          }
          if (amountKey) {
            const n = Number.parseFloat(String(state[amountKey] ?? ""));
            if (!Number.isFinite(n) || n <= 0) errs[amountKey] = "Enter a valid amount greater than 0";
          }
          return errs;
        },
      },
    ];
  }, [rendererMeta, action, members, amountKey]);

  function defaultBuildPayload(s: FormState): Record<string, unknown> {
    const raw: Record<string, unknown> = {};
    for (const f of rendererMeta.fields) {
      const v = s[f.key];
      if (v !== undefined && v !== "") raw[f.key] = v;
    }
    raw.title = s[titleKey ?? "title"] ?? action.label;
    const normalized = schemaAmountToMinor(raw);
    return transformPayload ? transformPayload(normalized) : normalized;
  }

  function defaultReviewRows(s: FormState): Array<{ label: string; value: string }> {
    return rendererMeta.fields
      .filter((f) => {
        const v = s[f.key];
        return v !== undefined && v !== "" && !(Array.isArray(v) && !v.length);
      })
      .map((f) => ({
        label: f.label,
        value: Array.isArray(s[f.key]) ? (s[f.key] as string[]).join(", ") : String(s[f.key]),
      }));
  }

  return (
    <ProgressiveActionForm
      action={action}
      momentId={momentId}
      templateId={templateId}
      steps={steps}
      buildPayload={defaultBuildPayload}
      buildReviewRows={customReviewRows ?? defaultReviewRows}
      onSubmit={onSubmit}
      onClose={onClose}
      onSuccess={onSuccess}
      draftTitleKey={titleKey ?? "title"}
      reviewEnabled={reviewEnabled}
    />
  );
}

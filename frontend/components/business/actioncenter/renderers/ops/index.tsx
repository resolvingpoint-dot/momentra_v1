"use client";

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
  CurrencyPicker,
  ChipSelector,
  VendorPicker,
  NotesField,
  formatMoneyDisplay,
} from "@/components/business/actioncenter/fields";
import type { BusinessActionRendererProps } from "@/components/business/actioncenter/actionRendererRegistry";
import {
  chipLabel,
  moneyPayload,
  req,
  reqAmount,
  todayISO,
} from "@/components/business/actioncenter/renderers/dedicatedHelpers";

const SPEND_CATEGORIES = [
  { value: "purchase", label: "Purchase" },
  { value: "vendor_payment", label: "Vendor payment" },
  { value: "staff_cost", label: "Staff cost" },
  { value: "other", label: "Other" },
];

const VENDOR_EVENTS = [
  { value: "new_vendor", label: "New vendor" },
  { value: "vendor_issue", label: "Issue" },
  { value: "contract_renewal", label: "Renewal" },
  { value: "other", label: "Other" },
];

const SEVERITY = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

const IMPROVEMENT_TYPES = [
  { value: "process_improvement", label: "Process" },
  { value: "budget_control_improvement", label: "Budget control" },
  { value: "other", label: "Other" },
];

function DedicatedShell({
  props,
  steps,
  buildPayload,
  buildReviewRows,
  draftTitleKey = "title",
  initialState,
  saveLabel,
  reviewEnabled = true,
}: {
  props: BusinessActionRendererProps;
  steps: ProgressiveStep[];
  buildPayload: (s: FormState) => Record<string, unknown>;
  buildReviewRows: (s: FormState) => Array<{ label: string; value: string }>;
  draftTitleKey?: string;
  initialState?: FormState;
  saveLabel?: string;
  reviewEnabled?: boolean;
}) {
  return (
    <ProgressiveActionForm
      action={props.action}
      momentId={props.momentId}
      templateId={props.templateId}
      steps={steps}
      buildPayload={buildPayload}
      buildReviewRows={buildReviewRows}
      onSubmit={props.onSubmit}
      onClose={props.onClose}
      onSuccess={props.onSuccess}
      draftTitleKey={draftTitleKey}
      initialState={initialState}
      saveLabel={saveLabel ?? props.action.cta_label}
      reviewEnabled={reviewEnabled}
    />
  );
}

export function SpendEntryRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Spend details",
      validate: (s) => ({
        ...req(s, "title", "Spend name"),
        ...reqAmount(s),
        ...req(s, "spend_category", "Category"),
        ...req(s, "spend_date", "Date"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Spend name"
            value={String(state.title ?? "")}
            onChange={(v) => set("title", v)}
            required
            error={errors.title}
          />
          <MoneyInput
            label="Amount"
            value={String(state.amount ?? "")}
            onChange={(v) => set("amount", v)}
            required
            error={errors.amount}
            currencyCode={String(state.currency_code ?? "INR")}
          />
          <CurrencyPicker
            value={String(state.currency_code ?? "INR")}
            onChange={(v) => set("currency_code", v)}
          />
          <ChipSelector
            label="Category"
            value={String(state.spend_category ?? "")}
            onChange={(v) => set("spend_category", v)}
            options={SPEND_CATEGORIES}
            required
            error={errors.spend_category}
          />
          <DateInput
            label="Date"
            value={String(state.spend_date ?? "")}
            onChange={(v) => set("spend_date", v)}
            required
            error={errors.spend_date}
          />
          <VendorPicker
            label="Vendor"
            value={String(state.vendor_name ?? "")}
            onChange={(v) => set("vendor_name", v)}
          />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      initialState={{ currency_code: "INR", spend_date: todayISO() }}
      saveLabel="Save spend"
      buildPayload={(s) => ({
        title: s.title,
        ...moneyPayload(s),
        spend_category: s.spend_category,
        spend_date: s.spend_date,
        vendor_name: s.vendor_name || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Spend", value: String(s.title ?? "") },
        { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? ""), String(s.currency_code ?? "INR")) },
        { label: "Category", value: chipLabel(SPEND_CATEGORIES, String(s.spend_category ?? "")) },
        { label: "Date", value: String(s.spend_date ?? "") },
        { label: "Vendor", value: String(s.vendor_name || "—") },
      ]}
    />
  );
}

export function VendorUpdateRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Vendor update",
      validate: (s) => ({
        ...req(s, "vendor_name", "Vendor name"),
        ...req(s, "vendor_event_type", "Event"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <VendorPicker
            label="Vendor name"
            value={String(state.vendor_name ?? "")}
            onChange={(v) => set("vendor_name", v)}
            required
            error={errors.vendor_name}
          />
          <ChipSelector
            label="Event"
            value={String(state.vendor_event_type ?? "")}
            onChange={(v) => set("vendor_event_type", v)}
            options={VENDOR_EVENTS}
            required
            error={errors.vendor_event_type}
          />
          <TextArea
            label="Notes"
            value={String(state.description ?? "")}
            onChange={(v) => set("description", v)}
          />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      draftTitleKey="vendor_name"
      saveLabel="Save vendor update"
      buildPayload={(s) => ({
        title: String(s.vendor_name || props.action.label),
        vendor_name: s.vendor_name,
        vendor_event_type: s.vendor_event_type,
        description: s.description || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Vendor", value: String(s.vendor_name ?? "") },
        { label: "Event", value: chipLabel(VENDOR_EVENTS, String(s.vendor_event_type ?? "")) },
        { label: "Notes", value: String(s.description || "—") },
      ]}
    />
  );
}

export function OpsApprovalRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Approval request",
      validate: (s) => ({
        ...req(s, "title", "Request title"),
        ...req(s, "description", "Description"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Request title"
            value={String(state.title ?? "")}
            onChange={(v) => set("title", v)}
            required
            error={errors.title}
          />
          <MoneyInput
            label="Amount"
            value={String(state.amount ?? "")}
            onChange={(v) => set("amount", v)}
            currencyCode={String(state.currency_code ?? "INR")}
          />
          <CurrencyPicker
            value={String(state.currency_code ?? "INR")}
            onChange={(v) => set("currency_code", v)}
          />
          <TextArea
            label="Description"
            value={String(state.description ?? "")}
            onChange={(v) => set("description", v)}
            required
            error={errors.description}
          />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      initialState={{ currency_code: "INR" }}
      saveLabel="Request approval"
      buildPayload={(s) => {
        const money = s.amount ? moneyPayload(s) : {};
        return {
          title: s.title,
          description: s.description,
          ...money,
        };
      }}
      buildReviewRows={(s) => [
        { label: "Title", value: String(s.title ?? "") },
        {
          label: "Amount",
          value: s.amount
            ? formatMoneyDisplay(String(s.amount), String(s.currency_code ?? "INR"))
            : "—",
        },
        { label: "Description", value: String(s.description ?? "") },
      ]}
    />
  );
}

export function OpsIssueRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Issue details",
      validate: (s) => ({
        ...req(s, "title", "Issue title"),
        ...req(s, "severity", "Severity"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Issue title"
            value={String(state.title ?? "")}
            onChange={(v) => set("title", v)}
            required
            error={errors.title}
          />
          <ChipSelector
            label="Severity"
            value={String(state.severity ?? "")}
            onChange={(v) => set("severity", v)}
            options={SEVERITY}
            required
            error={errors.severity}
          />
          <TextArea
            label="Description"
            value={String(state.description ?? "")}
            onChange={(v) => set("description", v)}
          />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      saveLabel="Log issue"
      buildPayload={(s) => ({
        title: s.title,
        severity: s.severity,
        description: s.description || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Title", value: String(s.title ?? "") },
        { label: "Severity", value: chipLabel(SEVERITY, String(s.severity ?? "")) },
        { label: "Description", value: String(s.description || "—") },
      ]}
    />
  );
}

export function OperationalImprovementRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Improvement",
      validate: (s) => ({
        ...req(s, "title", "Improvement"),
        ...req(s, "improvement_type", "Type"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Improvement"
            value={String(state.title ?? "")}
            onChange={(v) => set("title", v)}
            required
            error={errors.title}
          />
          <ChipSelector
            label="Type"
            value={String(state.improvement_type ?? "")}
            onChange={(v) => set("improvement_type", v)}
            options={IMPROVEMENT_TYPES}
            required
            error={errors.improvement_type}
          />
          <TextArea
            label="Details"
            value={String(state.description ?? "")}
            onChange={(v) => set("description", v)}
          />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      saveLabel="Save improvement"
      // Review mandatory for operational improvement? Plan lists it as dedicated;
      // mandatory review list didn't include it explicitly — keep review on.
      reviewEnabled
      buildPayload={(s) => ({
        title: s.title,
        improvement_type: s.improvement_type,
        description: s.description || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Improvement", value: String(s.title ?? "") },
        { label: "Type", value: chipLabel(IMPROVEMENT_TYPES, String(s.improvement_type ?? "")) },
        { label: "Details", value: String(s.description || "—") },
      ]}
    />
  );
}

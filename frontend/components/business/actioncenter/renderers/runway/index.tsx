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

const INFLOW_TYPES = [
  { value: "revenue_collected", label: "Revenue" },
  { value: "investor_funding", label: "Investor funding" },
  { value: "owner_contribution", label: "Owner contribution" },
  { value: "bank_loan", label: "Loan" },
  { value: "other", label: "Other" },
];

const EXPENSE_CATEGORIES = [
  { value: "salaries", label: "Salaries" },
  { value: "marketing", label: "Marketing" },
  { value: "technology", label: "Technology" },
  { value: "operations", label: "Operations" },
  { value: "other", label: "Other" },
];

const SEVERITY = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

const UPDATE_TYPES = [
  { value: "cash_available", label: "Cash available" },
  { value: "monthly_burn", label: "Monthly burn" },
  { value: "revenue_estimate", label: "Revenue estimate" },
  { value: "runway_threshold", label: "Runway threshold" },
];

const DECISION_TYPES = [
  { value: "hiring", label: "Hiring" },
  { value: "expansion", label: "Expansion" },
  { value: "funding", label: "Funding" },
  { value: "cost_reduction", label: "Cost reduction" },
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

export function CashInflowRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Inflow details",
      validate: (s) => ({
        ...reqAmount(s),
        ...req(s, "inflow_type", "Type"),
        ...req(s, "inflow_date", "Date"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField label="Label" value={String(state.title ?? "")} onChange={(v) => set("title", v)} />
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
            label="Type"
            value={String(state.inflow_type ?? "")}
            onChange={(v) => set("inflow_type", v)}
            options={INFLOW_TYPES}
            required
            error={errors.inflow_type}
          />
          <DateInput
            label="Date"
            value={String(state.inflow_date ?? "")}
            onChange={(v) => set("inflow_date", v)}
            required
            error={errors.inflow_date}
          />
          <NotesField value={String(state.description ?? "")} onChange={(v) => set("description", v)} label="Notes" />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      initialState={{ currency_code: "INR", inflow_date: todayISO() }}
      saveLabel="Record inflow"
      buildPayload={(s) => ({
        title: String(s.title || props.action.label),
        ...moneyPayload(s),
        inflow_type: s.inflow_type,
        inflow_date: s.inflow_date,
        description: s.description || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Label", value: String(s.title || "—") },
        { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? ""), String(s.currency_code ?? "INR")) },
        { label: "Type", value: chipLabel(INFLOW_TYPES, String(s.inflow_type ?? "")) },
        { label: "Date", value: String(s.inflow_date ?? "") },
      ]}
    />
  );
}

export function ExpenseBurnRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Burn details",
      validate: (s) => ({
        ...reqAmount(s),
        ...req(s, "expense_category", "Category"),
        ...req(s, "expense_date", "Date"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
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
            value={String(state.expense_category ?? "")}
            onChange={(v) => set("expense_category", v)}
            options={EXPENSE_CATEGORIES}
            required
            error={errors.expense_category}
          />
          <DateInput
            label="Date"
            value={String(state.expense_date ?? "")}
            onChange={(v) => set("expense_date", v)}
            required
            error={errors.expense_date}
          />
          <NotesField value={String(state.description ?? "")} onChange={(v) => set("description", v)} label="Notes" />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      initialState={{ currency_code: "INR", expense_date: todayISO() }}
      draftTitleKey="expense_category"
      saveLabel="Record burn"
      buildPayload={(s) => ({
        title: String(s.title || chipLabel(EXPENSE_CATEGORIES, String(s.expense_category ?? "")) || props.action.label),
        ...moneyPayload(s),
        expense_category: s.expense_category,
        expense_date: s.expense_date,
        description: s.description || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? ""), String(s.currency_code ?? "INR")) },
        { label: "Category", value: chipLabel(EXPENSE_CATEGORIES, String(s.expense_category ?? "")) },
        { label: "Date", value: String(s.expense_date ?? "") },
      ]}
    />
  );
}

export function RunwayRiskRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Risk details",
      validate: (s) => ({
        ...req(s, "title", "Risk title"),
        ...req(s, "severity", "Severity"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Risk title"
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
      saveLabel="Log risk"
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

export function FinancialUpdateRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Financial update",
      validate: (s) => ({
        ...req(s, "update_type", "Update type"),
        ...req(s, "reason", "Reason"),
        ...reqAmount(s),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <ChipSelector
            label="Update type"
            value={String(state.update_type ?? "")}
            onChange={(v) => set("update_type", v)}
            options={UPDATE_TYPES}
            required
            error={errors.update_type}
          />
          <MoneyInput
            label="New value"
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
          <TextArea
            label="Reason"
            value={String(state.reason ?? "")}
            onChange={(v) => set("reason", v)}
            required
            error={errors.reason}
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
      draftTitleKey="update_type"
      saveLabel="Save update"
      buildPayload={(s) => ({
        title: chipLabel(UPDATE_TYPES, String(s.update_type ?? "")) || props.action.label,
        update_type: s.update_type,
        reason: s.reason,
        ...moneyPayload(s),
      })}
      buildReviewRows={(s) => [
        { label: "Type", value: chipLabel(UPDATE_TYPES, String(s.update_type ?? "")) },
        { label: "Value", value: formatMoneyDisplay(String(s.amount ?? ""), String(s.currency_code ?? "INR")) },
        { label: "Reason", value: String(s.reason ?? "") },
      ]}
    />
  );
}

export function StrategicDecisionRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Decision",
      validate: (s) => ({
        ...req(s, "title", "Decision"),
        ...req(s, "decision_type", "Type"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Decision"
            value={String(state.title ?? "")}
            onChange={(v) => set("title", v)}
            required
            error={errors.title}
          />
          <ChipSelector
            label="Type"
            value={String(state.decision_type ?? "")}
            onChange={(v) => set("decision_type", v)}
            options={DECISION_TYPES}
            required
            error={errors.decision_type}
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
      saveLabel="Save decision"
      buildPayload={(s) => ({
        title: s.title,
        decision_type: s.decision_type,
        description: s.description || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Decision", value: String(s.title ?? "") },
        { label: "Type", value: chipLabel(DECISION_TYPES, String(s.decision_type ?? "")) },
        { label: "Details", value: String(s.description || "—") },
      ]}
    />
  );
}

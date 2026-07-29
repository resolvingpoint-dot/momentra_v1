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
  MemberPicker,
  ApprovalPicker,
  NotesField,
  formatMoneyDisplay,
} from "@/components/business/actioncenter/fields";
import { SchemaDrivenRenderer } from "@/components/business/actioncenter/renderers/SchemaDrivenRenderer";
import type { BusinessActionRendererProps } from "@/components/business/actioncenter/actionRendererRegistry";
import {
  chipLabel,
  memberLabel,
  moneyPayload,
  req,
  reqAmount,
  schemaAmountToMinor,
} from "@/components/business/actioncenter/renderers/dedicatedHelpers";

const SEVERITY = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
  { value: "critical", label: "Critical" },
];

const PRIORITY = [
  { value: "low", label: "Low" },
  { value: "medium", label: "Medium" },
  { value: "high", label: "High" },
];

function schemaFallback(
  rendererId: string,
  title: string,
  fields: Array<{
    key: string;
    label: string;
    field_type: string;
    required?: boolean;
    options?: Array<{ value: string; label: string }>;
  }>,
) {
  return {
    renderer_id: rendererId,
    title,
    fields: fields.map((f) => ({
      ...f,
      placeholder: undefined,
      default_value: undefined,
      step_id: undefined,
      step_title: undefined,
      visible_when: undefined,
      options: f.options,
    })),
    review_enabled: true,
  };
}

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

/** Schema-OK: basic Team Update */
export function TeamUpdateRenderer(props: BusinessActionRendererProps) {
  const meta =
    props.rendererMeta ??
    schemaFallback("team_ops.team_update", "Team Update", [
      { key: "title", label: "Title", field_type: "text", required: true },
      { key: "description", label: "Details", field_type: "textarea" },
      {
        key: "priority",
        label: "Priority",
        field_type: "single_select",
        options: PRIORITY,
      },
    ]);

  return (
    <SchemaDrivenRenderer
      {...props}
      rendererMeta={meta}
      titleKey="title"
      transformPayload={(raw) => schemaAmountToMinor(raw)}
      buildReviewRows={(s: FormState) => [
        { label: "Title", value: String(s.title ?? "") },
        { label: "Details", value: String(s.description || "—") },
        { label: "Priority", value: String(s.priority || "—") },
      ]}
    />
  );
}

/** Schema-OK */
export function RecognitionRenderer(props: BusinessActionRendererProps) {
  const meta =
    props.rendererMeta ??
    schemaFallback("team_ops.recognition", "Recognition", [
      { key: "title", label: "Recognition", field_type: "text", required: true },
      { key: "recipient_member_id", label: "Recipient", field_type: "member_picker", required: true },
      { key: "notes", label: "Notes", field_type: "notes" },
    ]);

  return (
    <SchemaDrivenRenderer
      {...props}
      rendererMeta={meta}
      titleKey="title"
      buildReviewRows={(s: FormState) => [
        { label: "Recognition", value: String(s.title ?? "") },
        {
          label: "Recipient",
          value: memberLabel(props.members, String(s.recipient_member_id ?? "")),
        },
        { label: "Notes", value: String(s.notes || "—") },
      ]}
    />
  );
}

export function MeetingRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Meeting",
      validate: (s) => req(s, "title", "Meeting title"),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Meeting title"
            value={String(state.title ?? "")}
            onChange={(v) => set("title", v)}
            required
            error={errors.title}
          />
          <DateInput
            label="When"
            value={String(state.meeting_at ?? "")}
            onChange={(v) => set("meeting_at", v)}
          />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      reviewEnabled={false}
      saveLabel="Save meeting"
      buildPayload={(s) => ({
        title: s.title,
        meeting_at: s.meeting_at || undefined,
        notes: s.notes || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Title", value: String(s.title ?? "") },
        { label: "When", value: String(s.meeting_at || "—") },
        { label: "Notes", value: String(s.notes || "—") },
      ]}
    />
  );
}

export function IssueRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Issue",
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

export function ApprovalRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Approval request",
      validate: (s) => ({
        ...req(s, "title", "Request title"),
        ...reqAmount(s),
        ...req(s, "reason", "Reason"),
        ...req(s, "approver_id", "Approver"),
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
          <ApprovalPicker
            label="Approver"
            value={String(state.approver_id ?? "")}
            onChange={(v) => set("approver_id", v)}
            members={props.members}
            required
            error={errors.approver_id}
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
      buildPayload={(s) => ({
        title: s.title,
        ...moneyPayload(s),
        reason: s.reason,
        approver_id: s.approver_id,
      })}
      buildReviewRows={(s) => [
        { label: "Title", value: String(s.title ?? "") },
        { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? ""), String(s.currency_code ?? "INR")) },
        { label: "Reason", value: String(s.reason ?? "") },
        { label: "Approver", value: memberLabel(props.members, String(s.approver_id ?? "")) },
      ]}
    />
  );
}

/** Schema-OK */
export function ReviewRenderer(props: BusinessActionRendererProps) {
  const meta =
    props.rendererMeta ??
    schemaFallback("team_ops.review", "Review", [
      { key: "title", label: "Review title", field_type: "text", required: true },
      { key: "notes", label: "Notes", field_type: "notes" },
    ]);

  return (
    <SchemaDrivenRenderer
      {...props}
      rendererMeta={meta}
      titleKey="title"
      buildReviewRows={(s: FormState) => [
        { label: "Title", value: String(s.title ?? "") },
        { label: "Notes", value: String(s.notes || "—") },
      ]}
    />
  );
}

export function EscalationRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Escalation",
      validate: (s) => ({
        ...req(s, "title", "Escalation"),
        ...req(s, "severity", "Severity"),
      }),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Escalation"
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
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      saveLabel="Escalate"
      buildPayload={(s) => ({
        title: s.title,
        severity: s.severity,
        notes: s.notes || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Title", value: String(s.title ?? "") },
        { label: "Severity", value: chipLabel(SEVERITY, String(s.severity ?? "")) },
        { label: "Notes", value: String(s.notes || "—") },
      ]}
    />
  );
}

/** Schema-OK */
export function ParticipationRenderer(props: BusinessActionRendererProps) {
  const meta =
    props.rendererMeta ??
    schemaFallback("team_ops.participation", "Participation", [
      { key: "title", label: "Title", field_type: "text", required: true },
      { key: "member_id", label: "Member", field_type: "member_picker" },
      { key: "notes", label: "Notes", field_type: "notes" },
    ]);

  return (
    <SchemaDrivenRenderer
      {...props}
      rendererMeta={meta}
      titleKey="title"
      buildReviewRows={(s: FormState) => [
        { label: "Title", value: String(s.title ?? "") },
        { label: "Member", value: memberLabel(props.members, String(s.member_id ?? "")) },
        { label: "Notes", value: String(s.notes || "—") },
      ]}
    />
  );
}

export function MemberUpdateRenderer(props: BusinessActionRendererProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "details",
      title: "Member update",
      validate: (s) => req(s, "title", "Update"),
      render: ({ state, set, errors }) => (
        <div className="space-y-4">
          <TextField
            label="Update"
            value={String(state.title ?? "")}
            onChange={(v) => set("title", v)}
            required
            error={errors.title}
          />
          <MemberPicker
            label="Member"
            value={String(state.member_id ?? "")}
            onChange={(v) => set("member_id", v)}
            members={props.members}
          />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </div>
      ),
    },
  ];

  return (
    <DedicatedShell
      props={props}
      steps={steps}
      saveLabel="Save update"
      buildPayload={(s) => ({
        title: s.title,
        member_id: s.member_id || undefined,
        notes: s.notes || undefined,
      })}
      buildReviewRows={(s) => [
        { label: "Update", value: String(s.title ?? "") },
        { label: "Member", value: memberLabel(props.members, String(s.member_id ?? "")) },
        { label: "Notes", value: String(s.notes || "—") },
      ]}
    />
  );
}

/** Schema-OK */
export function NoteRenderer(props: BusinessActionRendererProps) {
  const meta =
    props.rendererMeta ??
    schemaFallback("team_ops.note", "Note", [
      { key: "title", label: "Title", field_type: "text", required: true },
      { key: "notes", label: "Note", field_type: "textarea", required: true },
    ]);

  return (
    <SchemaDrivenRenderer
      {...props}
      rendererMeta={meta}
      titleKey="title"
      buildReviewRows={(s: FormState) => [
        { label: "Title", value: String(s.title ?? "") },
        { label: "Note", value: String(s.notes ?? "").slice(0, 120) },
      ]}
    />
  );
}

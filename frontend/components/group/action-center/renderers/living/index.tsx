"use client";

import { useEffect, useState } from "react";
import { ProgressiveActionForm, type FormState, type ProgressiveStep } from "@/components/group/action-center/ProgressiveActionForm";
import {
  ChipSelector,
  DateField,
  EmailField,
  formatMoneyDisplay,
  MoneyField,
  NotesField,
  parseAmountMinor,
  ParticipantPicker,
  PhoneField,
  PrioritySelector,
  StatusSelector,
  TextArea,
  TextField,
  Toggle,
} from "@/components/group/action-center/fields";
import { PollComposer } from "@/components/group/action-center/fields/PollComposer";
import { ActionGlassCard, ActionSection } from "@/components/group/action-center/ui/ActionDesignSystem";
import { InviteMethodsPanel } from "@/components/group/invite/InviteMethodsPanel";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { InviteDraft } from "@/lib/api/group";
import { getInviteDraft } from "@/lib/api/group";
import type { QuickAddActionTemplate } from "@/lib/quick_add/types";
import { buildLivingQuickAddPayload } from "@/lib/quick_add/payloadBuilders/groupTemplate";
import {
  buildSharedPollPayload,
  POLL_INITIAL_STATE,
  pollReviewRows,
  validatePollFormState,
} from "@/lib/quick_add/payloadBuilders/sharedPoll";
import { submitGroupTemplateQuickAdd } from "@/repositories/GroupTemplateQuickAddRepository";
import { todayISODate } from "@/lib/quick_add/dateTimeDefaults";

type FormProps = {
  action: QuickAddActionTemplate;
  momentId: string;
  templateId: string;
  onClose: () => void;
  onSuccess?: () => void;
};

function req(state: FormState, key: string, label: string): Record<string, string> {
  if (!state[key]) return { [key]: `${label} is required` };
  return {};
}

function amountErr(state: FormState): Record<string, string> {
  const n = Number.parseFloat(String(state.amount ?? ""));
  if (!Number.isFinite(n) || n <= 0) return { amount: "Enter a valid amount greater than 0" };
  return {};
}

function livingForm(
  actionId: string,
  steps: ProgressiveStep[] | ((momentId: string) => ProgressiveStep[]),
  review: (s: FormState) => Array<{ label: string; value: string }>,
  mapState: (s: FormState) => FormState,
  submitActionId = actionId,
  initialState?: FormState,
) {
  return function Dedicated(props: FormProps) {
    const resolvedSteps = typeof steps === "function" ? steps(props.momentId) : steps;
    return (
      <ProgressiveActionForm
        {...props}
        steps={resolvedSteps}
        initialState={initialState}
        successSubtitle="Synced with your home."
        buildReviewRows={review}
        buildPayload={(s) => buildLivingQuickAddPayload(submitActionId === "RENT" || submitActionId === "UTILITY" ? "EXPENSE" : submitActionId, mapState(s) as never)}
        onSubmit={async (payload) => {
          const slugAction = submitActionId === "RENT" || submitActionId === "UTILITY" ? "EXPENSE" : submitActionId;
          await submitGroupTemplateQuickAdd("living", props.momentId, slugAction, payload);
        }}
      />
    );
  };
}

export const LivingRentForm = livingForm(
  "RENT",
  (momentId) => [
    {
      id: "rent",
      title: "Rent",
      validate: (s) => ({ ...req(s, "month", "Rent month"), ...amountErr(s), ...req(s, "due_date", "Due date") }),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Rent month" value={String(state.month ?? "")} onChange={(v) => set("month", v)} required error={errors.month} placeholder="e.g. July 2026" />
          <MoneyField label="Amount" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} required error={errors.amount} />
          <DateField label="Due date" value={String(state.due_date ?? "")} onChange={(v) => set("due_date", v)} required error={errors.due_date} />
          <ParticipantPicker label="Paid by" value={String(state.paid_by ?? "")} onChange={(v) => set("paid_by", v)} momentId={momentId} surface="living" readOnlyWhenSingle />
          <TextField label="Participants" value={String(state.participants ?? "")} onChange={(v) => set("participants", v)} />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Month", value: String(s.month ?? "") },
    { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? "")) },
    { label: "Due", value: String(s.due_date ?? "") },
  ],
  (s) => ({
    amount_minor: String(parseAmountMinor(String(s.amount ?? ""))),
    expense_category: "rent",
    expense_date: String(s.due_date ?? ""),
    split_type: "equal",
  }),
  "RENT",
  { due_date: todayISODate() },
);

export const LivingUtilityForm = livingForm(
  "UTILITY",
  [
    {
      id: "util",
      title: "Utility",
      validate: (s) => ({ ...req(s, "utility_type", "Utility type"), ...amountErr(s) }),
      render: ({ state, set, errors }) => (
        <>
          <ChipSelector
            label="Utility type"
            required
            value={String(state.utility_type ?? "")}
            onChange={(v) => set("utility_type", v)}
            error={errors.utility_type}
            options={[
              { value: "electricity", label: "Electricity" },
              { value: "water", label: "Water" },
              { value: "internet", label: "Internet" },
              { value: "gas", label: "Gas" },
              { value: "other", label: "Other" },
            ]}
          />
          <TextField label="Billing period" value={String(state.period ?? "")} onChange={(v) => set("period", v)} />
          <MoneyField label="Amount" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} required error={errors.amount} />
          <DateField label="Due date" value={String(state.due_date ?? "")} onChange={(v) => set("due_date", v)} />
          <TextField label="Meter reading" value={String(state.meter ?? "")} onChange={(v) => set("meter", v)} />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Type", value: String(s.utility_type ?? "") },
    { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? "")) },
  ],
  (s) => ({
    amount_minor: String(parseAmountMinor(String(s.amount ?? ""))),
    expense_category: "utilities",
    expense_date: String(s.due_date ?? ""),
    split_type: "equal",
  }),
  "UTILITY",
  { due_date: todayISODate() },
);

export const LivingExpenseForm = livingForm(
  "EXPENSE",
  (momentId) => [
    {
      id: "e",
      title: "Expense",
      validate: (s) => ({ ...amountErr(s), ...req(s, "expense_category", "Category") }),
      render: ({ state, set, errors }) => (
        <>
          <MoneyField label="Amount" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} required error={errors.amount} />
          <ChipSelector
            label="Category"
            required
            value={String(state.expense_category ?? "")}
            onChange={(v) => set("expense_category", v)}
            error={errors.expense_category}
            options={[
              { value: "rent", label: "Rent" },
              { value: "utilities", label: "Utilities" },
              { value: "groceries", label: "Groceries" },
              { value: "other", label: "Other" },
            ]}
          />
          <DateField label="Date" value={String(state.expense_date ?? "")} onChange={(v) => set("expense_date", v)} />
          <ParticipantPicker label="Paid by" value={String(state.paid_by ?? "")} onChange={(v) => set("paid_by", v)} momentId={momentId} surface="living" readOnlyWhenSingle />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? "")) },
    { label: "Category", value: String(s.expense_category ?? "") },
  ],
  (s) => ({
    amount_minor: String(parseAmountMinor(String(s.amount ?? ""))),
    expense_category: String(s.expense_category ?? "other"),
    expense_date: String(s.expense_date ?? ""),
    split_type: "equal",
  }),
  "EXPENSE",
  { expense_date: todayISODate() },
);

export const LivingContributorForm = livingForm(
  "CONTRIBUTION",
  (momentId) => [
    {
      id: "c",
      title: "Contribution",
      validate: (s) => amountErr(s),
      render: ({ state, set, errors }) => (
        <>
          <MoneyField label="Amount" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} required error={errors.amount} />
          <ParticipantPicker label="Contributor" value={String(state.contributor ?? "")} onChange={(v) => set("contributor", v)} momentId={momentId} surface="living" readOnlyWhenSingle />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </>
      ),
    },
  ],
  (s) => [{ label: "Amount", value: formatMoneyDisplay(String(s.amount ?? "")) }],
  (s) => ({ amount_minor: String(parseAmountMinor(String(s.amount ?? ""))) }),
);

export const LivingTaskForm = livingForm(
  "TASK",
  (momentId) => [
    {
      id: "t",
      title: "Task",
      validate: (s) => ({ ...req(s, "title", "Title"), ...req(s, "assignee", "Assignee") }),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Task title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} required error={errors.title} />
          <ParticipantPicker label="Assigned to" value={String(state.assignee ?? "")} onChange={(v) => set("assignee", v)} required error={errors.assignee} momentId={momentId} surface="living" readOnlyWhenSingle />
          <PrioritySelector value={String(state.priority ?? "medium")} onChange={(v) => set("priority", v)} />
          <DateField label="Due date" value={String(state.due_date ?? "")} onChange={(v) => set("due_date", v)} />
          <StatusSelector value={String(state.status ?? "open")} onChange={(v) => set("status", v)} />
          <TextField label="Estimated duration" value={String(state.duration ?? "")} onChange={(v) => set("duration", v)} placeholder="e.g. 30 min" />
          <Toggle label="Repeat" value={Boolean(state.repeat)} onChange={(v) => set("repeat", v)} />
          <Toggle label="Reminder" value={Boolean(state.reminder)} onChange={(v) => set("reminder", v)} />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Task", value: String(s.title ?? "") },
    { label: "Assignee", value: String(s.assignee ?? "") },
  ],
  (s) => ({
    title: String(s.title ?? ""),
    assignee_id: String(s.assignee ?? ""),
    priority: String(s.priority ?? "medium"),
  }),
  "TASK",
  { due_date: todayISODate() },
);

export const LivingMaintenanceForm = livingForm(
  "MAINTENANCE",
  [
    {
      id: "m",
      title: "Maintenance",
      validate: (s) => ({ ...req(s, "title", "Title"), ...req(s, "asset", "Asset"), ...req(s, "description", "Description") }),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Maintenance title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} required error={errors.title} />
          <TextField label="Asset" value={String(state.asset ?? "")} onChange={(v) => set("asset", v)} required error={errors.asset} />
          <TextField label="Vendor" value={String(state.vendor ?? "")} onChange={(v) => set("vendor", v)} />
          <MoneyField label="Estimated cost" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} />
          <ChipSelector
            label="Severity"
            value={String(state.severity ?? "medium")}
            onChange={(v) => set("severity", v)}
            options={[
              { value: "low", label: "Low" },
              { value: "medium", label: "Medium" },
              { value: "high", label: "High" },
            ]}
          />
          <DateField label="Due date" value={String(state.due_date ?? "")} onChange={(v) => set("due_date", v)} />
          <DateField label="Estimated completion" value={String(state.est_done ?? "")} onChange={(v) => set("est_done", v)} />
          <DateField label="Actual completion" value={String(state.actual_done ?? "")} onChange={(v) => set("actual_done", v)} />
          <StatusSelector value={String(state.status ?? "open")} onChange={(v) => set("status", v)} />
          <TextArea label="Description" value={String(state.description ?? "")} onChange={(v) => set("description", v)} required error={errors.description} />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Title", value: String(s.title ?? "") },
    { label: "Severity", value: String(s.severity ?? "") },
  ],
  (s) => ({
    maintenance_type: String(s.title ?? "repair"),
    severity: String(s.severity ?? "medium"),
    description: String(s.description ?? ""),
    due_date: String(s.due_date ?? ""),
  }),
  "MAINTENANCE",
  { due_date: todayISODate() },
);

export const LivingRuleForm = livingForm(
  "RULE",
  [
    {
      id: "r",
      title: "Rule",
      validate: (s) => ({ ...req(s, "title", "Title"), ...req(s, "text", "Description") }),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Rule title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} required error={errors.title} />
          <TextArea label="Description" value={String(state.text ?? "")} onChange={(v) => set("text", v)} required error={errors.text} />
          <DateField label="Effective date" value={String(state.effective ?? "")} onChange={(v) => set("effective", v)} />
          <ChipSelector
            label="Severity"
            value={String(state.severity ?? "normal")}
            onChange={(v) => set("severity", v)}
            options={[
              { value: "soft", label: "Soft" },
              { value: "normal", label: "Normal" },
              { value: "strict", label: "Strict" },
            ]}
          />
        </>
      ),
    },
  ],
  (s) => [{ label: "Rule", value: String(s.title ?? "") }],
  (s) => ({ text: `${s.title}: ${s.text}`, rule_type: String(s.severity ?? "normal") }),
  "RULE",
  { effective: todayISODate() },
);

export const LivingAssetForm = livingForm(
  "ASSET",
  [
    {
      id: "a",
      title: "Asset",
      validate: (s) => req(s, "name", "Name"),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Name" value={String(state.name ?? "")} onChange={(v) => set("name", v)} required error={errors.name} />
          <TextField label="Asset type" value={String(state.asset_type ?? "")} onChange={(v) => set("asset_type", v)} />
          <TextField label="Location" value={String(state.location ?? "")} onChange={(v) => set("location", v)} />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </>
      ),
    },
  ],
  (s) => [{ label: "Asset", value: String(s.name ?? "") }],
  (s) => s,
);

function LivingResidentInviteForm(props: FormProps) {
  const { colors } = useThemeTokens();
  const [showDetails, setShowDetails] = useState(false);
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("member");
  const [phone, setPhone] = useState("");
  const [email, setEmail] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [loadingDraft, setLoadingDraft] = useState(true);
  const [participantId, setParticipantId] = useState<string | null>(null);
  const [draft, setDraft] = useState<InviteDraft | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadingDraft(true);
    void getInviteDraft(props.momentId)
      .then((invite) => {
        if (!cancelled) {
          setDraft(invite);
          setLoadingDraft(false);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Could not load invite");
          setLoadingDraft(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [props.momentId]);

  async function saveDetails() {
    const name = fullName.trim();
    if (!name) {
      setShowDetails(false);
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const payload = {
        full_name: name,
        name,
        resident_role: role.trim() || "member",
        role: role.trim() || "member",
        notes: notes.trim() || undefined,
        phone: phone.trim() || undefined,
        email: email.trim() || undefined,
        status: "invited",
        relationship_type: "roommate",
      };
      const created = await submitGroupTemplateQuickAdd("living", props.momentId, "RESIDENT", payload);
      const id =
        created && typeof created === "object" && "id" in created
          ? String((created as { id: string }).id)
          : null;
      setParticipantId(id);
      const invite = await getInviteDraft(props.momentId, id);
      setDraft(invite);
      setShowDetails(false);
      props.onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save details");
    } finally {
      setBusy(false);
    }
  }

  const subtitle = fullName.trim()
    ? `Invite ${fullName.trim()} with QR, share, or a direct channel.`
    : "Share a link or QR for this home.";

  return (
    <div className="space-y-6 pb-8">
      <div>
        <h3 className="text-lg font-semibold">Choose invite method</h3>
        <p className="mt-1 text-sm" style={{ color: colors.textSecondary }}>
          {subtitle}
        </p>
      </div>

      {loadingDraft ? (
        <p className="text-sm" style={{ color: colors.textSecondary }}>
          Loading invite…
        </p>
      ) : null}

      {error && !showDetails ? (
        <p className="text-sm" style={{ color: colors.error }}>
          {error}
        </p>
      ) : null}

      {draft ? (
        <InviteMethodsPanel
          momentId={props.momentId}
          draft={draft}
          onDraftChange={setDraft}
          defaultEmail={email}
          defaultPhone={phone}
        />
      ) : null}

      {showDetails ? (
        <ActionGlassCard>
          <ActionSection title="Add details">
            <TextField label="Name" value={fullName} onChange={setFullName} />
            <ChipSelector
              label="Role"
              value={role}
              onChange={setRole}
              options={[
                { value: "owner", label: "Owner" },
                { value: "member", label: "Member" },
                { value: "tenant", label: "Tenant" },
                { value: "flatmate", label: "Flatmate" },
              ]}
            />
            <PhoneField value={phone} onChange={setPhone} />
            <EmailField value={email} onChange={setEmail} />
            <NotesField value={notes} onChange={setNotes} label="Optional note" />
            {error ? (
              <p className="text-sm" style={{ color: colors.error }}>
                {error}
              </p>
            ) : null}
            <div className="flex gap-2 pt-1">
              <button
                type="button"
                disabled={busy}
                className="flex-1 rounded-xl px-3 py-2.5 text-sm font-semibold disabled:opacity-60"
                style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
                onClick={() => void saveDetails()}
              >
                {busy ? "Saving…" : "Save details"}
              </button>
              <button
                type="button"
                className="rounded-xl px-3 py-2.5 text-sm font-medium"
                style={{ background: colors.surfaceContainer, color: colors.textSecondary }}
                onClick={() => setShowDetails(false)}
              >
                Cancel
              </button>
            </div>
          </ActionSection>
        </ActionGlassCard>
      ) : (
        <button
          type="button"
          className="w-full text-left text-sm font-semibold underline-offset-2 hover:underline"
          style={{ color: colors.primaryContainer }}
          onClick={() => {
            setError(null);
            setShowDetails(true);
          }}
        >
          {participantId || fullName.trim() ? "Edit details" : "Add details"}
        </button>
      )}

      <button
        type="button"
        className="w-full rounded-2xl px-4 py-3.5 text-sm font-semibold"
        style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
        onClick={props.onClose}
      >
        Done
      </button>
    </div>
  );
}

export function LivingResidentForm(props: FormProps) {
  return <LivingResidentInviteForm {...props} />;
}

export const LivingPollForm = livingForm(
  "POLL",
  [
    {
      id: "p",
      title: "Poll",
      validate: validatePollFormState,
      render: ({ state, set, errors }) => <PollComposer state={state} set={set} errors={errors} />,
    },
  ],
  pollReviewRows,
  (s) => buildSharedPollPayload(s),
  "POLL",
  POLL_INITIAL_STATE,
);

export const LivingMemoryForm = livingForm(
  "MEMORY",
  [
    {
      id: "mem",
      title: "Memory",
      validate: (s) => req(s, "memory_category", "Category"),
      render: ({ state, set, errors }) => (
        <>
          <ChipSelector
            label="Category"
            required
            value={String(state.memory_category ?? "")}
            onChange={(v) => set("memory_category", v)}
            error={errors.memory_category}
            options={[
              { value: "highlight", label: "Highlight" },
              { value: "party", label: "Party" },
              { value: "milestone", label: "Milestone" },
            ]}
          />
          <TextField label="Caption" value={String(state.caption ?? "")} onChange={(v) => set("caption", v)} />
        </>
      ),
    },
  ],
  (s) => [{ label: "Category", value: String(s.memory_category ?? "") }],
  (s) => s,
);

export const LivingUpdateForm = livingForm(
  "UPDATE",
  [
    {
      id: "u",
      title: "Update",
      validate: (s) => req(s, "body", "Announcement"),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} />
          <TextArea label="Announcement" value={String(state.body ?? "")} onChange={(v) => set("body", v)} required error={errors.body} />
        </>
      ),
    },
  ],
  (s) => [{ label: "Announcement", value: String(s.body ?? "") }],
  (s) => s,
);

"use client";

import { useEffect, useState } from "react";
import { ProgressiveActionForm, type FormState, type ProgressiveStep } from "@/components/group/action-center/ProgressiveActionForm";
import {
  ChipSelector,
  CurrencyPicker,
  DateField,
  EmailField,
  formatMoneyDisplay,
  MoneyField,
  NotesField,
  parseAmountMinor,
  ParticipantPicker,
  PercentageEditor,
  PhoneField,
  PhotoPlaceholder,
  TextField,
  Toggle,
  VisibilitySelector,
} from "@/components/group/action-center/fields";
import { PollComposer } from "@/components/group/action-center/fields/PollComposer";
import { ActionGlassCard, ActionSection } from "@/components/group/action-center/ui/ActionDesignSystem";
import { InviteMethodsPanel } from "@/components/group/invite/InviteMethodsPanel";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { InviteDraft } from "@/lib/api/group";
import { getInviteDraft } from "@/lib/api/group";
import type { QuickAddActionTemplate } from "@/lib/quick_add/types";
import {
  buildPurchaseQuickAddPayload,
} from "@/lib/quick_add/payloadBuilders/groupTemplate";
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
  const v = state[key];
  if (v == null || v === "") return { [key]: `${label} is required` };
  return {};
}

function amountErr(state: FormState): Record<string, string> {
  const n = Number.parseFloat(String(state.amount ?? ""));
  if (!Number.isFinite(n) || n <= 0) return { amount: "Enter a valid amount greater than 0" };
  return {};
}

function purchaseForm(
  actionId: string,
  steps: ProgressiveStep[] | ((momentId: string) => ProgressiveStep[]),
  review: (s: FormState) => Array<{ label: string; value: string }>,
  mapState: (s: FormState) => FormState,
  initialState?: FormState,
) {
  return function Dedicated(props: FormProps) {
    const resolvedSteps = typeof steps === "function" ? steps(props.momentId) : steps;
    return (
      <ProgressiveActionForm
        {...props}
        steps={resolvedSteps}
        initialState={initialState}
        successSubtitle="Synced with your purchase."
        buildReviewRows={review}
        buildPayload={(s) => buildPurchaseQuickAddPayload(actionId, mapState(s) as never)}
        onSubmit={async (payload) => {
          await submitGroupTemplateQuickAdd("purchase", props.momentId, actionId, payload);
        }}
      />
    );
  };
}

/** Invite-first contributor / participants — same pattern as Trip ExperienceParticipantForm. */
function PurchasePeopleInviteForm({
  actionId,
  noun,
  defaultRole,
  roleOptions,
  ...props
}: FormProps & {
  actionId: "CONTRIBUTOR" | "PARTICIPANTS";
  noun: string;
  defaultRole: string;
  roleOptions: Array<{ value: string; label: string }>;
}) {
  const { colors } = useThemeTokens();
  const [showDetails, setShowDetails] = useState(false);
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState(defaultRole);
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
      const payload =
        actionId === "CONTRIBUTOR"
          ? {
              name,
              role: role.trim() || defaultRole,
              notes: notes.trim() || undefined,
              phone: phone.trim() || undefined,
              email: email.trim() || undefined,
              status: "invited",
            }
          : {
              name,
              role: role.trim() || defaultRole,
              notes: notes.trim() || undefined,
              phone: phone.trim() || undefined,
              email: email.trim() || undefined,
              member_ids: [],
              invite_status: "invited",
            };
      const created = await submitGroupTemplateQuickAdd("purchase", props.momentId, actionId, payload);
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
    : `Share a link or QR for this ${noun}.`;

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
            <ChipSelector label="Role" value={role} onChange={setRole} options={roleOptions} />
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

export function PurchaseContributionForm(props: FormProps) {
  return (
    <PurchasePeopleInviteForm
      {...props}
      actionId="CONTRIBUTOR"
      noun="purchase"
      defaultRole="contributor"
      roleOptions={[
        { value: "owner", label: "Owner" },
        { value: "contributor", label: "Contributor" },
        { value: "viewer", label: "Viewer" },
      ]}
    />
  );
}

export function PurchaseParticipantForm(props: FormProps) {
  return (
    <PurchasePeopleInviteForm
      {...props}
      actionId="PARTICIPANTS"
      noun="purchase"
      defaultRole="member"
      roleOptions={[
        { value: "member", label: "Member" },
        { value: "contributor", label: "Contributor" },
        { value: "viewer", label: "Viewer" },
      ]}
    />
  );
}

export const PurchaseExpenseForm = purchaseForm(
  "EXPENSE",
  (momentId) => [
    {
      id: "e",
      title: "Expense",
      validate: (s) => amountErr(s),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} />
          <MoneyField label="Amount" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} required error={errors.amount} />
          <CurrencyPicker value={String(state.currency ?? "INR")} onChange={(v) => set("currency", v)} />
          <ParticipantPicker label="Paid by" value={String(state.paid_by ?? "")} onChange={(v) => set("paid_by", v)} momentId={momentId} surface="purchase" readOnlyWhenSingle />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
          <PhotoPlaceholder label="Receipt" />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? "")) },
    { label: "Notes", value: String(s.notes ?? "") },
  ],
  (s) => ({ amount_minor: String(parseAmountMinor(String(s.amount ?? ""))), warranty_notes: String(s.notes ?? "") }),
);

export const PurchasePurchaseForm = purchaseForm(
  "PURCHASE_ITEM",
  [
    {
      id: "p",
      title: "Purchase item",
      validate: (s) => req(s, "item_name", "Item name"),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Item name" value={String(state.item_name ?? "")} onChange={(v) => set("item_name", v)} required error={errors.item_name} />
          <TextField label="Quantity" value={String(state.qty ?? "1")} onChange={(v) => set("qty", v)} type="number" />
          <MoneyField label="Unit price" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} />
          <TextField label="Vendor" value={String(state.vendor ?? "")} onChange={(v) => set("vendor", v)} />
          <PhotoPlaceholder label="Warranty" />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Item", value: String(s.item_name ?? "") },
    { label: "Price", value: formatMoneyDisplay(String(s.amount ?? "")) },
  ],
  (s) => ({
    item_name: String(s.item_name ?? ""),
    target_price_minor: String(parseAmountMinor(String(s.amount ?? ""))),
    product_link: String(s.vendor ?? ""),
  }),
);

export const PurchaseOwnershipForm = purchaseForm(
  "OWNERSHIP",
  (momentId) => [
    {
      id: "o",
      title: "Ownership",
      validate: (s) => req(s, "usage_rights", "Usage rights"),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Item" value={String(state.item ?? "")} onChange={(v) => set("item", v)} />
          <ParticipantPicker label="Old owner" value={String(state.old_owner ?? "")} onChange={(v) => set("old_owner", v)} momentId={momentId} surface="purchase" readOnlyWhenSingle />
          <ParticipantPicker label="New owner" value={String(state.new_owner ?? "")} onChange={(v) => set("new_owner", v)} momentId={momentId} surface="purchase" readOnlyWhenSingle />
          <PercentageEditor label="Old share %" value={String(state.old_share ?? "")} onChange={(v) => set("old_share", v)} />
          <PercentageEditor label="New share %" value={String(state.allocation_pct ?? "")} onChange={(v) => set("allocation_pct", v)} />
          <DateField label="Effective date" value={String(state.effective ?? "")} onChange={(v) => set("effective", v)} />
          <ChipSelector
            label="Usage rights"
            required
            value={String(state.usage_rights ?? "")}
            onChange={(v) => set("usage_rights", v)}
            error={errors.usage_rights}
            options={[
              { value: "full", label: "Full" },
              { value: "shared", label: "Shared" },
              { value: "limited", label: "Limited" },
            ]}
          />
          <NotesField value={String(state.responsibility ?? "")} onChange={(v) => set("responsibility", v)} />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Item", value: String(s.item ?? "") },
    { label: "New share", value: String(s.allocation_pct ?? "") },
    { label: "Rights", value: String(s.usage_rights ?? "") },
  ],
  (s) => s,
  { effective: todayISODate() },
);

export const PurchaseVendorForm = purchaseForm(
  "VENDOR",
  [
    {
      id: "v",
      title: "Vendor",
      validate: (s) => req(s, "vendor_name", "Vendor name"),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Vendor name" value={String(state.vendor_name ?? "")} onChange={(v) => set("vendor_name", v)} required error={errors.vendor_name} />
          <TextField label="Contact" value={String(state.contact ?? "")} onChange={(v) => set("contact", v)} />
          <TextField label="GST" value={String(state.gst ?? "")} onChange={(v) => set("gst", v)} />
          <Toggle label="Preferred" value={Boolean(state.preferred)} onChange={(v) => set("preferred", v)} />
          <NotesField value={String(state.comparison_notes ?? "")} onChange={(v) => set("comparison_notes", v)} />
        </>
      ),
    },
  ],
  (s) => [{ label: "Vendor", value: String(s.vendor_name ?? "") }],
  (s) => s,
);

export const PurchaseDeliveryForm = purchaseForm(
  "DELIVERY",
  [
    {
      id: "d",
      title: "Delivery",
      validate: (s) => req(s, "event_type", "Event type"),
      render: ({ state, set, errors }) => (
        <>
          <ChipSelector
            label="Event type"
            required
            value={String(state.event_type ?? "")}
            onChange={(v) => set("event_type", v)}
            error={errors.event_type}
            options={[
              { value: "shipped", label: "Shipped" },
              { value: "arriving", label: "Arriving" },
              { value: "delivered", label: "Delivered" },
            ]}
          />
          <DateField label="Delivery date" value={String(state.delivery_date ?? "")} onChange={(v) => set("delivery_date", v)} />
          <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
        </>
      ),
    },
  ],
  (s) => [
    { label: "Event", value: String(s.event_type ?? "") },
    { label: "Date", value: String(s.delivery_date ?? "") },
  ],
  (s) => s,
  { delivery_date: todayISODate() },
);

export const PurchasePollForm = purchaseForm(
  "POLL",
  [
    {
      id: "poll",
      title: "Poll",
      validate: validatePollFormState,
      render: ({ state, set, errors }) => <PollComposer state={state} set={set} errors={errors} />,
    },
  ],
  pollReviewRows,
  (s) => buildSharedPollPayload(s),
  POLL_INITIAL_STATE,
);

export const PurchaseMemoryForm = purchaseForm(
  "MEMORY",
  [
    {
      id: "m",
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
              { value: "milestone", label: "Milestone" },
              { value: "delivery", label: "Delivery" },
            ]}
          />
          <TextField label="Caption" value={String(state.caption ?? "")} onChange={(v) => set("caption", v)} />
          <PhotoPlaceholder />
        </>
      ),
    },
  ],
  (s) => [{ label: "Category", value: String(s.memory_category ?? "") }],
  (s) => s,
);

export const PurchaseUpdateForm = purchaseForm(
  "UPDATE",
  [
    {
      id: "u",
      title: "Update",
      validate: (s) => req(s, "body", "Message"),
      render: ({ state, set, errors }) => (
        <>
          <TextField label="Title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} />
          <TextField label="Message" value={String(state.body ?? "")} onChange={(v) => set("body", v)} required error={errors.body} />
          <VisibilitySelector value={String(state.visibility ?? "everyone")} onChange={(v) => set("visibility", v)} />
        </>
      ),
    },
  ],
  (s) => [{ label: "Message", value: String(s.body ?? "") }],
  (s) => s,
);

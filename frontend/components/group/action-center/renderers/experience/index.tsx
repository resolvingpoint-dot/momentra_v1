"use client";

import { useEffect, useState } from "react";
import { ProgressiveActionForm, type FormState, type ProgressiveStep } from "@/components/group/action-center/ProgressiveActionForm";
import {
  ChipSelector,
  CurrencyPicker,
  DateField,
  EmailField,
  LocationField,
  MemberMultiSelect,
  MoneyField,
  NotesField,
  parseAmountMinor,
  formatMoneyDisplay,
  ParticipantPicker,
  PhoneField,
  PhotoPlaceholder,
  SplitEditor,
  SplitPreview,
  TagPicker,
  TextArea,
  TextField,
  TimeField,
  Toggle,
  fetchExpenseContextOnce,
  VisibilitySelector,
} from "@/components/group/action-center/fields";
import { MemoryMediaUploader, memoryPathsFromState } from "@/components/group/action-center/fields/MemoryMediaUploader";
import type { MemoryMediaFormat } from "@/lib/media/memoryUpload";
import { PollComposer } from "@/components/group/action-center/fields/PollComposer";
import { ActionSection, ActionGlassCard } from "@/components/group/action-center/ui/ActionDesignSystem";
import { InviteMethodsPanel } from "@/components/group/invite/InviteMethodsPanel";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { QuickAddActionTemplate } from "@/lib/quick_add/types";
import { buildTripQuickAddPayload } from "@/lib/quick_add/payloadBuilders/groupTrip";
import {
  buildSharedPollPayload,
  POLL_INITIAL_STATE,
  pollReviewRows,
  validatePollFormState,
} from "@/lib/quick_add/payloadBuilders/sharedPoll";
import { submitTripQuickAdd, fetchTripQuickAddContext } from "@/repositories/GroupTripQuickAddRepository";
import { requestWithRetry } from "@/lib/api/client";
import { getInviteDraft, type InviteDraft } from "@/lib/api/group";
import { getReferenceData } from "@/lib/reference_data/referenceDataStore";
import { findCurrency } from "@/lib/reference_data/money";
import { resolveExpenseCategories } from "@/lib/quick_add/resolveOptions";
import { composeOccurredAt, nowISOTime, todayISODate } from "@/lib/quick_add/dateTimeDefaults";

type FormProps = {
  action: QuickAddActionTemplate;
  momentId: string;
  templateId: string;
  onClose: () => void;
  onSuccess?: () => void;
  onSwitchAction?: (actionId: string) => void;
};

function req(state: FormState, key: string, label: string): Record<string, string> {
  const v = state[key];
  if (v == null || v === "" || (Array.isArray(v) && !v.length)) return { [key]: `${label} is required` };
  return {};
}

function amountErr(state: FormState, key = "amount"): Record<string, string> {
  const n = Number.parseFloat(String(state[key] ?? ""));
  if (!Number.isFinite(n) || n <= 0) return { [key]: "Enter a valid amount greater than 0" };
  return {};
}

export function ExperienceExpenseForm(props: FormProps) {
  const [initialState, setInitialState] = useState<FormState>({
    currency: "INR",
    split_type: "EQUAL",
    participants: [],
    allow_multi_currency: true,
    expense_date: todayISODate(),
    expense_time: nowISOTime(),
  });
  const [ready, setReady] = useState(false);
  const [memberOptions, setMemberOptions] = useState<Array<{ value: string; label: string }>>([]);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const ctx = await fetchExpenseContextOnce(props.momentId, "trip");
        if (cancelled) return;
        const opts = [
          ...(ctx.members ?? []).map((m) => ({ value: m.id, label: m.display_name })),
          ...(ctx.payers ?? []).map((p) => ({ value: p.id, label: p.display_name })),
        ];
        const dedup = Array.from(new Map(opts.map((r) => [r.value, r])).values());
        setMemberOptions(dedup);
        const memberIds = dedup.map((m) => m.value);
        setInitialState({
          currency: ctx.default_currency_code || "INR",
          allow_multi_currency: ctx.allow_multi_currency !== false,
          paid_by: ctx.default_paid_by_participant_id || memberIds[0] || "",
          participants: memberIds,
          split_type: "EQUAL",
          expense_date: todayISODate(),
          expense_time: nowISOTime(),
        });
      } catch {
        /* keep defaults */
      } finally {
        if (!cancelled) setReady(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [props.momentId]);

  const steps: ProgressiveStep[] = [
    {
      id: "form",
      title: "Expense",
      validate: (s) => {
        const ids = Array.isArray(s.participants) ? s.participants : [];
        return {
          ...req(s, "title", "Title"),
          ...amountErr(s),
          ...req(s, "category", "Category"),
          ...req(s, "paid_by", "Paid by"),
          ...(ids.length ? {} : { participants: "Select at least one participant" }),
        };
      },
      render: ({ state, set, errors }) => {
        const locked = state.allow_multi_currency === false;
        const fromBootstrap = resolveExpenseCategories();
        const selected = fromBootstrap.find((c) => c.code === String(state.category ?? ""));
        const children = (selected?.children ?? []).filter((c) => c.is_active !== false);
        const ids = Array.isArray(state.participants) ? state.participants : [];
        const currency = String(state.currency ?? "INR");
        const ref = findCurrency(getReferenceData()?.currencies ?? [], currency);
        const minorUnit = ref?.minor_unit ?? 2;
        const amountMinor = parseAmountMinor(String(state.amount ?? ""), minorUnit);
        return (
          <div className="space-y-6">
            <ActionSection title="Core Information">
              <TextField label="Title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} required error={errors.title} />
              <MoneyField
                label="Amount"
                value={String(state.amount ?? "")}
                onChange={(v) => set("amount", v)}
                required
                error={errors.amount}
                currencyCode={currency}
              />
              <CurrencyPicker
                value={currency}
                onChange={(v) => set("currency", v)}
                locked={locked}
              />
              <ChipSelector
                label="Category"
                required
                value={String(state.category ?? "")}
                onChange={(v) => {
                  set("category", v);
                  set("subcategory", "");
                }}
                error={errors.category}
                options={fromBootstrap.map((c) => ({ value: c.code, label: c.label }))}
              />
              {children.length > 0 ? (
                <ChipSelector
                  label="Subcategory"
                  value={String(state.subcategory ?? "")}
                  onChange={(v) => set("subcategory", v)}
                  options={children.map((c) => ({ value: c.code, label: c.label }))}
                />
              ) : null}
              <DateField label="Date" value={String(state.expense_date ?? "")} onChange={(v) => set("expense_date", v)} required />
              <TimeField label="Time" value={String(state.expense_time ?? "")} onChange={(v) => set("expense_time", v)} />
              <ParticipantPicker
                label="Paid by"
                value={String(state.paid_by ?? "")}
                onChange={(v) => set("paid_by", v)}
                required
                error={errors.paid_by}
                options={memberOptions}
                momentId={props.momentId}
                readOnlyWhenSingle
                onInviteParticipant={
                  props.onSwitchAction ? () => props.onSwitchAction?.("PARTICIPANT") : undefined
                }
              />
            </ActionSection>
            <ActionSection title="Split">
              <MemberMultiSelect
                label="Participants"
                value={ids}
                onChange={(next) => set("participants", next)}
                options={memberOptions}
                momentId={props.momentId}
                required
                error={errors.participants}
                onInviteParticipant={
                  props.onSwitchAction ? () => props.onSwitchAction?.("PARTICIPANT") : undefined
                }
              />
              <SplitEditor value={String(state.split_type ?? "EQUAL")} onChange={(v) => set("split_type", v)} />
              <SplitPreview
                amountMinor={amountMinor}
                currencyCode={currency}
                participantIds={ids}
                splitStyle={String(state.split_type ?? "EQUAL")}
              />
            </ActionSection>
            <ActionSection title="Notes">
              <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
            </ActionSection>
          </div>
        );
      },
    },
  ];

  if (!ready) {
    return <p className="py-8 text-center text-sm opacity-70">Loading expense form…</p>;
  }

  return (
    <ProgressiveActionForm
      {...props}
      steps={steps}
      initialState={initialState}
      draftTitleKey="title"
      heroImageUrl={null}
      buildPayload={(s) => {
        const currency = String(s.currency ?? "INR");
        const ref = findCurrency(getReferenceData()?.currencies ?? [], currency);
        const minorUnit = ref?.minor_unit ?? 2;
        const amountMinor = parseAmountMinor(String(s.amount ?? ""), minorUnit);
        const participantIds = Array.isArray(s.participants) ? s.participants : [];
        const occurred = composeOccurredAt(
          String(s.expense_date ?? ""),
          String(s.expense_time ?? ""),
        );
        return {
          ...buildTripQuickAddPayload("EXPENSE", {
            amount_minor: String(amountMinor),
            category: String(s.category ?? ""),
            split_type: String(s.split_type ?? "EQUAL"),
            paid_by_user_id: String(s.paid_by ?? ""),
            description: String(s.title ?? ""),
          }),
          title: String(s.title ?? ""),
          amount_minor: amountMinor,
          currency_code: currency,
          category_code: String(s.category ?? ""),
          category: String(s.category ?? ""),
          subcategory_code: String(s.subcategory ?? "") || null,
          occurred_at: occurred || undefined,
          expense_date: String(s.expense_date ?? "") || undefined,
          paid_by_participant_id: String(s.paid_by ?? ""),
          paid_by_user_id: String(s.paid_by ?? ""),
          participant_ids: participantIds,
          split_style: String(s.split_type ?? "EQUAL").toUpperCase(),
          notes: String(s.notes ?? "") || undefined,
        };
      }}
      onSubmit={async (payload) => {
        await submitTripQuickAdd(props.momentId, "EXPENSE", payload);
      }}
    />
  );
}

export function ExperienceBookingForm(props: FormProps) {
  const steps: ProgressiveStep[] = [
    {
      id: "form",
      title: "Booking",
      validate: (s) => ({ ...req(s, "title", "Booking name"), ...req(s, "booking_type", "Category") }),
      render: ({ state, set, errors }) => (
        <div className="space-y-6">
          <ActionSection title="Category">
            <ChipSelector
              label="Category"
              required
              value={String(state.booking_type ?? "")}
              onChange={(v) => set("booking_type", v)}
              error={errors.booking_type}
              options={[
                { value: "flight", label: "Flight" },
                { value: "hotel", label: "Hotel" },
                { value: "transport", label: "Transport" },
                { value: "venue", label: "Venue" },
                { value: "restaurant", label: "Restaurant" },
                { value: "activity", label: "Activity" },
                { value: "equipment", label: "Equipment" },
                { value: "other", label: "Other" },
              ]}
            />
            <ChipSelector
              label="Status"
              value={String(state.confirmation ?? "confirmed")}
              onChange={(v) => set("confirmation", v)}
              options={[
                { value: "planned", label: "Planned" },
                { value: "reserved", label: "Reserved" },
                { value: "confirmed", label: "Confirmed" },
                { value: "cancelled", label: "Cancelled" },
              ]}
            />
          </ActionSection>
          <ActionGlassCard>
            <ActionSection title="Core Information">
              <TextField label="Booking name" value={String(state.title ?? "")} onChange={(v) => set("title", v)} required error={errors.title} />
              <TextField label="Provider / Vendor" value={String(state.provider ?? "")} onChange={(v) => set("provider", v)} />
              <DateField label="Booking date" value={String(state.check_in ?? "")} onChange={(v) => set("check_in", v)} />
              <MoneyField label="Amount" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} currencyCode={String(state.currency ?? "INR")} />
              <CurrencyPicker value={String(state.currency ?? "INR")} onChange={(v) => set("currency", v)} />
              <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
            </ActionSection>
          </ActionGlassCard>
        </div>
      ),
    },
  ];
  return (
    <ProgressiveActionForm
      {...props}
      steps={steps}
      heroImageUrl={null}
      buildPayload={(s) => {
        const amountMinor = parseAmountMinor(String(s.amount ?? ""));
        return {
          ...buildTripQuickAddPayload("BOOKING", {
            booking_type: String(s.booking_type ?? ""),
            provider: String(s.provider ?? ""),
            // Match chip default ("confirmed"); previously fell back to "planned" when unset.
            booking_status: String(s.confirmation ?? "confirmed"),
            // Pass number so groupTrip.parseAmountMinor does not *100 again.
            amount_minor: amountMinor,
            description: String(s.notes ?? s.title ?? ""),
            title: String(s.title ?? s.provider ?? "Booking"),
            currency_code: String(s.currency ?? "INR"),
          }),
          amount_minor: amountMinor,
        };
      }}
      onSubmit={async (payload) => {
        await submitTripQuickAdd(props.momentId, "BOOKING", payload);
      }}
    />
  );
}

const BUDGET_ALLOC_CATS = [
  { code: "stay", label: "Stay", key: "alloc_stay" },
  { code: "travel", label: "Travel", key: "alloc_travel" },
  { code: "food", label: "Food", key: "alloc_food" },
  { code: "activities", label: "Activities", key: "alloc_activities" },
] as const;

function majorFromState(value: unknown): number {
  const n = Number.parseFloat(String(value ?? "").replace(/[^\d.]/g, ""));
  return Number.isFinite(n) && n >= 0 ? n : 0;
}

function redistributeBudgetAllocations(totalMajor: number): Record<string, string> {
  const n = BUDGET_ALLOC_CATS.length;
  if (totalMajor <= 0) {
    return Object.fromEntries(BUDGET_ALLOC_CATS.map((c) => [c.key, ""]));
  }
  const base = Math.floor((totalMajor * 100) / n) / 100;
  const rem = Math.round((totalMajor - base * n) * 100) / 100;
  return Object.fromEntries(
    BUDGET_ALLOC_CATS.map((c, i) => [c.key, String(i === 0 ? base + rem : base)]),
  );
}

export function ExperienceBudgetForm(props: FormProps) {
  const [initialState, setInitialState] = useState<FormState>({
    template_id: "custom",
    currency: "INR",
    split_method: "EQUAL",
    participant_count: "1",
    amount: "",
    alloc_stay: "",
    alloc_travel: "",
    alloc_food: "",
    alloc_activities: "",
  });
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const ctx = await fetchTripQuickAddContext(props.momentId, "BUDGET");
        if (cancelled) return;
        setInitialState((prev) => ({
          ...prev,
          participant_count: String(ctx.participant_count ?? 1),
          currency: String(ctx.default_currency_code ?? "INR"),
          template_id: String(prev.template_id || "custom"),
        }));
      } catch {
        /* keep defaults */
      } finally {
        if (!cancelled) setReady(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [props.momentId]);

  const steps: ProgressiveStep[] = [
    {
      id: "form",
      title: "Budget Plan",
      validate: (s) => {
        const errs = { ...amountErr(s) };
        const total = majorFromState(s.amount);
        const sum = BUDGET_ALLOC_CATS.reduce((acc, c) => acc + majorFromState(s[c.key]), 0);
        if (total > 0 && sum > 0 && Math.abs(sum - total) > 0.05) {
          errs.alloc_stay = `Allocations (₹${sum.toFixed(0)}) should match total (₹${total.toFixed(0)})`;
        }
        return errs;
      },
      render: ({ state, set, errors }) => {
        const total = majorFromState(state.amount);
        const participants = Math.max(1, Number.parseInt(String(state.participant_count ?? "1"), 10) || 1);
        const split = String(state.split_method ?? "EQUAL");
        const perPerson = split === "EQUAL" && total > 0 ? total / participants : null;
        const setTotal = (v: string) => {
          const next = majorFromState(v);
          set("amount", v);
          const redistributed = redistributeBudgetAllocations(next);
          for (const [k, val] of Object.entries(redistributed)) set(k, val);
        };
        return (
          <div className="space-y-6">
            <ActionSection title="Template">
              <ChipSelector
                label="Budget template"
                value={String(state.template_id ?? "custom")}
                onChange={(v) => set("template_id", v)}
                options={[
                  { value: "weekend", label: "Weekend getaway" },
                  { value: "adventure", label: "Adventure trip" },
                  { value: "custom", label: "Custom" },
                ]}
              />
            </ActionSection>
            <ActionGlassCard>
              <ActionSection title="Planning ceiling">
                <MoneyField
                  label="Total budget"
                  value={String(state.amount ?? "")}
                  onChange={setTotal}
                  required
                  error={errors.amount}
                  currencyCode={String(state.currency ?? "INR")}
                />
                <CurrencyPicker value={String(state.currency ?? "INR")} onChange={(v) => set("currency", v)} />
              </ActionSection>
            </ActionGlassCard>
            <ActionSection title="Category allocation">
              {BUDGET_ALLOC_CATS.map((cat) => {
                const amt = majorFromState(state[cat.key]);
                const pct = total > 0 ? Math.round((amt / total) * 1000) / 10 : 0;
                return (
                  <MoneyField
                    key={cat.code}
                    label={`${cat.label}${total > 0 ? ` (${pct}%)` : ""}`}
                    value={String(state[cat.key] ?? "")}
                    onChange={(v) => set(cat.key, v)}
                    currencyCode={String(state.currency ?? "INR")}
                    error={cat.code === "stay" ? errors.alloc_stay : undefined}
                  />
                );
              })}
            </ActionSection>
            <ActionSection title="Expected split">
              <ChipSelector
                label="Split method"
                value={split}
                onChange={(v) => set("split_method", v)}
                options={[
                  { value: "EQUAL", label: "Equal" },
                  { value: "CONTRIBUTION_BASED", label: "Contribution-based" },
                  { value: "CUSTOM", label: "Custom" },
                ]}
              />
              {perPerson != null ? (
                <p className="text-sm opacity-80">
                  About {formatMoneyDisplay(String(perPerson), String(state.currency ?? "INR"))} per person
                  ({participants} people)
                </p>
              ) : null}
            </ActionSection>
            <ActionSection title="Optional">
              <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
            </ActionSection>
          </div>
        );
      },
    },
  ];

  if (!ready) return null;

  return (
    <ProgressiveActionForm
      {...props}
      steps={steps}
      initialState={initialState}
      heroImageUrl={null}
      saveLabel="Save Planning Budget"
      draftTitleKey="amount"
      buildPayload={(s) => {
        const totalMajor = majorFromState(s.amount);
        const participants = Math.max(1, Number.parseInt(String(s.participant_count ?? "1"), 10) || 1);
        const allocations = BUDGET_ALLOC_CATS.map((cat) => {
          const amountMajor = majorFromState(s[cat.key]);
          return {
            category_code: cat.code,
            amount_major: amountMajor,
            percent: totalMajor > 0 ? Math.round((amountMajor / totalMajor) * 1000) / 10 : 0,
          };
        });
        return {
          template_id: String(s.template_id ?? "custom"),
          total_amount_major: totalMajor,
          currency_code: String(s.currency ?? "INR"),
          split_method: String(s.split_method ?? "EQUAL"),
          participant_count: participants,
          allocations,
          notes: String(s.notes ?? "").trim() || undefined,
        };
      }}
      onSubmit={async (payload) => {
        await submitTripQuickAdd(props.momentId, "BUDGET", payload);
      }}
    />
  );
}

function simpleTripForm(
  actionId: string,
  steps: ProgressiveStep[] | ((momentId: string) => ProgressiveStep[]),
  _review: (s: FormState) => Array<{ label: string; value: string }>,
  toState: (s: FormState) => Record<string, string | string[] | number | boolean>,
  initialState?: FormState,
) {
  return function DedicatedForm(props: FormProps) {
    const resolvedSteps = typeof steps === "function" ? steps(props.momentId) : steps;
    return (
      <ProgressiveActionForm
        {...props}
        steps={resolvedSteps}
        initialState={initialState}
        heroImageUrl={null}
        buildPayload={(s) => buildTripQuickAddPayload(actionId, toState(s))}
        onSubmit={async (payload) => {
          await submitTripQuickAdd(props.momentId, actionId, payload);
        }}
      />
    );
  };
}

export function ExperienceParticipantForm(props: FormProps) {
  const { colors } = useThemeTokens();
  const [showDetails, setShowDetails] = useState(false);
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("");
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
      const created = await submitTripQuickAdd(props.momentId, "PARTICIPANT", {
        full_name: name,
        phone: phone.trim() || null,
        email: email.trim() || null,
        assigned_role: role.trim() || null,
        notes: notes.trim() || null,
        status: "invited",
        relationship_type: "friend",
      });
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
    : "Share a link or QR for this experience.";

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
            <TextField label="Role" value={role} onChange={setRole} />
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

export const ExperienceContributionForm = simpleTripForm(
  "CONTRIBUTION",
  (momentId) => [
    {
      id: "form",
      title: "Contribution",
      validate: (s) => ({ ...amountErr(s), ...req(s, "contributor", "Contributor") }),
      render: ({ state, set, errors }) => (
        <div className="space-y-6">
          <ActionSection title="Category">
            <ChipSelector
              label="Category"
              value={String(state.allocation ?? "general")}
              onChange={(v) => set("allocation", v)}
              options={[
                { value: "stay", label: "Stay" },
                { value: "travel", label: "Travel" },
                { value: "food", label: "Food" },
                { value: "general", label: "General Contribution" },
              ]}
            />
          </ActionSection>
          <ActionGlassCard>
            <ActionSection title="Core Information">
              <ParticipantPicker label="Contributor" value={String(state.contributor ?? "")} onChange={(v) => set("contributor", v)} required error={errors.contributor} momentId={momentId} />
              <MoneyField label="Amount" value={String(state.amount ?? "")} onChange={(v) => set("amount", v)} required error={errors.amount} currencyCode={String(state.currency ?? "INR")} />
              <CurrencyPicker value={String(state.currency ?? "INR")} onChange={(v) => set("currency", v)} />
              <DateField label="Transaction date" value={String(state.date ?? "")} onChange={(v) => set("date", v)} />
              <ChipSelector
                label="Payment method"
                value={String(state.payment_method ?? "upi")}
                onChange={(v) => set("payment_method", v)}
                options={[
                  { value: "upi", label: "UPI" },
                  { value: "cash", label: "Cash" },
                  { value: "card", label: "Card" },
                  { value: "bank", label: "Bank" },
                ]}
              />
              <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
            </ActionSection>
          </ActionGlassCard>
        </div>
      ),
    },
  ],
  (s) => [
    { label: "Amount", value: formatMoneyDisplay(String(s.amount ?? ""), String(s.currency ?? "INR")) },
    { label: "Contributor", value: String(s.contributor ?? "") },
    { label: "Currency", value: String(s.currency ?? "INR") },
  ],
  (s) => ({
    // Pass number so groupTrip.parseAmountMinor does not *100 again.
    amount_minor: parseAmountMinor(String(s.amount ?? "")),
    contributor_id: String(s.contributor ?? ""),
    currency_code: String(s.currency ?? "INR"),
    payment_method: String(s.payment_method ?? ""),
    allocation_category: String(s.allocation ?? "general"),
  }),
);

export const ExperienceVendorForm = simpleTripForm(
  "VENDOR",
  [
    {
      id: "form",
      title: "Vendor",
      validate: (s) => ({ ...req(s, "vendor_name", "Vendor name"), ...req(s, "category", "Category") }),
      render: ({ state, set, errors }) => (
        <div className="space-y-6">
          <ActionSection title="Category">
            <ChipSelector
              label="Category"
              required
              value={String(state.category ?? "")}
              onChange={(v) => set("category", v)}
              error={errors.category}
              options={[
                { value: "stay", label: "Stay" },
                { value: "transport", label: "Transport" },
                { value: "activity", label: "Activity" },
                { value: "food", label: "Food" },
                { value: "other", label: "Other" },
              ]}
            />
          </ActionSection>
          <ActionGlassCard>
            <ActionSection title="Core Information">
              <TextField label="Vendor name" value={String(state.vendor_name ?? "")} onChange={(v) => set("vendor_name", v)} required error={errors.vendor_name} />
              <TextField label="Contact" value={String(state.contact_name ?? "")} onChange={(v) => set("contact_name", v)} />
              <PhoneField value={String(state.phone ?? "")} onChange={(v) => set("phone", v)} />
              <MoneyField label="Quoted amount" value={String(state.quoted ?? "")} onChange={(v) => set("quoted", v)} />
              <TextField label="GST" value={String(state.gst ?? "")} onChange={(v) => set("gst", v)} />
              <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
            </ActionSection>
          </ActionGlassCard>
        </div>
      ),
    },
  ],
  (s) => [
    { label: "Vendor", value: String(s.vendor_name ?? "") },
    { label: "Category", value: String(s.category ?? "") },
  ],
  (s) => ({
    vendor_name: String(s.vendor_name ?? ""),
    vendor_type: String(s.category ?? ""),
    contact: String(s.contact_name ?? s.phone ?? ""),
    notes: String(s.notes ?? ""),
  }),
);

export const ExperiencePollForm = simpleTripForm(
  "POLL",
  [
    {
      id: "form",
      title: "Poll",
      validate: validatePollFormState,
      render: ({ state, set, errors }) => (
        <ActionGlassCard>
          <ActionSection title="Poll">
            <PollComposer state={state} set={set} errors={errors} />
          </ActionSection>
        </ActionGlassCard>
      ),
    },
  ],
  pollReviewRows,
  (s) => buildSharedPollPayload(s),
  POLL_INITIAL_STATE,
);

export const ExperienceAttendanceForm = simpleTripForm(
  "ATTENDANCE",
  (momentId) => [
    {
      id: "form",
      title: "Attendance",
      validate: (s) => ({ ...req(s, "member", "Member"), ...req(s, "attendance_type", "Type") }),
      render: ({ state, set, errors }) => (
        <div className="space-y-6">
          <ActionSection title="Category">
            <ChipSelector
              label="Attendance type"
              required
              value={String(state.attendance_type ?? "")}
              onChange={(v) => set("attendance_type", v)}
              error={errors.attendance_type}
              options={[
                { value: "full", label: "Full trip" },
                { value: "partial", label: "Partial" },
                { value: "coming", label: "Coming" },
                { value: "maybe", label: "Maybe" },
                { value: "not_coming", label: "Not coming" },
              ]}
            />
            <ChipSelector
              label="Status"
              value={String(state.status ?? "confirmed")}
              onChange={(v) => set("status", v)}
              options={[
                { value: "confirmed", label: "Confirmed" },
                { value: "tentative", label: "Tentative" },
              ]}
            />
          </ActionSection>
          <ActionGlassCard>
            <ActionSection title="Core Information">
              <ParticipantPicker label="Member" value={String(state.member ?? "")} onChange={(v) => set("member", v)} required error={errors.member} momentId={momentId} />
              <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
            </ActionSection>
          </ActionGlassCard>
        </div>
      ),
    },
  ],
  (s) => [
    { label: "Member", value: String(s.member ?? "") },
    { label: "Type", value: String(s.attendance_type ?? "") },
  ],
  (s) => ({
    member_id: String(s.member ?? ""),
    attendance_type: String(s.attendance_type ?? ""),
    status: String(s.status ?? "confirmed").toUpperCase(),
    notes: String(s.notes ?? ""),
  }),
);

export const ExperiencePlanningItemForm = simpleTripForm(
  "PLANNING_ITEM",
  [
    {
      id: "form",
      title: "Planning item",
      validate: (s) => req(s, "title", "Title"),
      render: ({ state, set, errors }) => (
        <div className="space-y-6">
          <ActionSection title="Category">
            <ChipSelector
              label="Category"
              value={String(state.planning_category ?? "stay")}
              onChange={(v) => set("planning_category", v)}
              options={[
                { value: "stay", label: "Stay" },
                { value: "travel", label: "Travel" },
                { value: "activity", label: "Activity" },
                { value: "other", label: "Other" },
              ]}
            />
          </ActionSection>
          <ActionGlassCard>
            <ActionSection title="Core Information">
              <TextField label="Title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} required error={errors.title} />
              <ChipSelector
                label="Status"
                value={String(state.planning_status ?? "idea")}
                onChange={(v) => set("planning_status", v)}
                options={[
                  { value: "idea", label: "Idea" },
                  { value: "booked", label: "Booked" },
                  { value: "done", label: "Done" },
                ]}
              />
              <DateField label="Due date" value={String(state.due_date ?? "")} onChange={(v) => set("due_date", v)} />
              <NotesField value={String(state.notes ?? "")} onChange={(v) => set("notes", v)} />
            </ActionSection>
          </ActionGlassCard>
        </div>
      ),
    },
  ],
  (s) => [
    { label: "Title", value: String(s.title ?? "") },
    { label: "Category", value: String(s.planning_category ?? "") },
  ],
  (s) => ({
    title: String(s.title ?? ""),
    planning_category: String(s.planning_category ?? "stay"),
    planning_status: String(s.planning_status ?? "idea"),
    notes: String(s.notes ?? ""),
  }),
);

export const ExperienceMemoryForm = simpleTripForm(
  "MEMORY",
  (momentId) => [
    {
      id: "form",
      title: "Memory",
      validate: (s) => {
        const errs = req(s, "title", "Title");
        const format = String(s.memory_format ?? "note") as MemoryMediaFormat;
        if (format !== "note" && memoryPathsFromState(s.media_storage_paths).length === 0) {
          errs.media = `Add at least one ${format === "pdf" ? "PDF" : format}.`;
        }
        return errs;
      },
      render: ({ state, set, errors }) => {
        const format = String(state.memory_format ?? "note") as MemoryMediaFormat;
        return (
          <div className="space-y-6">
            <ActionSection title="Category">
              <ChipSelector
                label="Category"
                value={String(state.memory_category ?? "highlight")}
                onChange={(v) => set("memory_category", v)}
                options={[
                  { value: "moment", label: "Moment" },
                  { value: "highlight", label: "Highlight" },
                ]}
              />
              <ChipSelector
                label="Format"
                value={format}
                onChange={(v) => {
                  set("memory_format", v);
                  if (v === "note") set("media_storage_paths", []);
                }}
                options={[
                  { value: "photo", label: "Photo" },
                  { value: "video", label: "Video" },
                  { value: "pdf", label: "PDF" },
                  { value: "note", label: "Note" },
                ]}
              />
            </ActionSection>
            <ActionGlassCard>
              <ActionSection title="Core Information">
                <TextField label="Title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} required error={errors.title} />
                <TextArea label="The story" value={String(state.description ?? "")} onChange={(v) => set("description", v)} />
                <DateField label="Date" value={String(state.date ?? "")} onChange={(v) => set("date", v)} />
                <ChipSelector
                  label="Mood"
                  value={String(state.emotion ?? "")}
                  onChange={(v) => set("emotion", v)}
                  options={[
                    { value: "happy", label: "Happy" },
                    { value: "chill", label: "Chill" },
                    { value: "epic", label: "Epic" },
                  ]}
                />
                <MemoryMediaUploader
                  momentId={momentId}
                  format={format}
                  paths={memoryPathsFromState(state.media_storage_paths)}
                  onChange={(paths) => set("media_storage_paths", paths)}
                  error={errors.media}
                />
              </ActionSection>
            </ActionGlassCard>
          </div>
        );
      },
    },
  ],
  (s) => [
    { label: "Title", value: String(s.title ?? "") },
    { label: "Category", value: String(s.memory_category ?? "") },
    { label: "Format", value: String(s.memory_format ?? "") },
    {
      label: "Attachments",
      value: String(memoryPathsFromState(s.media_storage_paths).length || ""),
    },
  ],
  (s) => ({
    title: String(s.title ?? ""),
    caption: String(s.description ?? ""),
    description: String(s.description ?? ""),
    memory_category: String(s.memory_category ?? "highlight"),
    memory_format: String(s.memory_format ?? "note"),
    media_storage_paths: memoryPathsFromState(s.media_storage_paths),
  }),
  {
    memory_category: "highlight",
    memory_format: "photo",
    media_storage_paths: [],
  },
);

export const ExperienceUpdateForm = simpleTripForm(
  "UPDATE",
  [
    {
      id: "form",
      title: "Update",
      validate: (s) => ({ ...req(s, "title", "Title"), ...req(s, "body", "Description") }),
      render: ({ state, set, errors }) => (
        <div className="space-y-6">
          <ActionSection title="Category">
            <ChipSelector
              label="Importance"
              value={String(state.importance ?? "normal")}
              onChange={(v) => set("importance", v)}
              options={[
                { value: "low", label: "Low" },
                { value: "normal", label: "Normal" },
                { value: "high", label: "High" },
              ]}
            />
          </ActionSection>
          <ActionGlassCard>
            <ActionSection title="Core Information">
              <TextField label="Title" value={String(state.title ?? "")} onChange={(v) => set("title", v)} required error={errors.title} />
              <TextArea label="Description" value={String(state.body ?? "")} onChange={(v) => set("body", v)} required error={errors.body} />
              <Toggle label="Notify participants" value={Boolean(state.notify)} onChange={(v) => set("notify", v)} />
              <VisibilitySelector value={String(state.visibility ?? "everyone")} onChange={(v) => set("visibility", v)} />
            </ActionSection>
          </ActionGlassCard>
        </div>
      ),
    },
  ],
  (s) => [
    { label: "Title", value: String(s.title ?? "") },
    { label: "Importance", value: String(s.importance ?? "") },
  ],
  (s) => ({
    title: String(s.title ?? ""),
    body: String(s.body ?? ""),
    update_type: String(s.importance ?? "normal"),
    visibility: String(s.visibility ?? "everyone"),
  }),
);

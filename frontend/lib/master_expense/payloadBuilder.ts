import type { PersonalMasterExpenseRequest } from "@/lib/api/client";
import { createClientRequestId } from "@/lib/quick_add/draftStore";

export type MasterExpenseFormState = {
  title: string;
  amountMinor: number;
  currencyCode: string;
  accountId: string;
  categoryCode: string;
  subcategoryCode: string;
  occurredAt: string;
  feeling: string;
  meaningfulness: string;
  memorability: string;
  sharedEnabled: boolean;
  sharedWith: string[];
  relationshipImpact: string[];
  contextReason: string;
  notes: string;
};

export function buildMasterExpensePayload(
  form: MasterExpenseFormState,
  clientRequestId: string = createClientRequestId(),
): PersonalMasterExpenseRequest & {
  client_request_id: string;
  title: string;
  amount_minor: number;
  currency_code: string;
  account_id: string;
  category_code: string;
  occurred_at: string | null;
  experience: {
    feeling: string | null;
    meaningfulness: string | null;
    memorability: string | null;
  };
  shared: {
    is_shared: boolean;
    shared_with: string[];
    relationship_impact: string[];
  };
  context: { reason: string | null };
  notes: string | null;
} {
  const legacyExpense = {
    title: form.title.trim(),
    amount: String(form.amountMinor / 100),
    account_id: form.accountId,
    category_code: form.categoryCode || null,
    subcategory_code: form.subcategoryCode || null,
    currency_code: form.currencyCode,
    transaction_date: form.occurredAt || null,
  };

  return {
    client_request_id: clientRequestId,
    title: form.title.trim(),
    amount_minor: form.amountMinor,
    currency_code: form.currencyCode,
    account_id: form.accountId,
    category_code: form.categoryCode,
    subcategory_code: form.subcategoryCode || null,
    occurred_at: form.occurredAt || null,
    expense: legacyExpense,
    experience: {
      feeling: form.feeling || null,
      meaningfulness: form.meaningfulness || null,
      memorability: form.memorability || null,
    },
    shared_experience: {
      enabled: form.sharedEnabled,
      shared_with: form.sharedWith,
      relationship_impact: form.relationshipImpact[0] || null,
    },
    shared: {
      is_shared: form.sharedEnabled,
      shared_with: form.sharedWith,
      relationship_impact: form.relationshipImpact,
    },
    context: { reason: form.contextReason || null },
    notes: form.notes.trim() || null,
  };
}

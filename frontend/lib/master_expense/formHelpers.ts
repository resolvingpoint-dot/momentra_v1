import type { PersonalMasterExpenseOptionsResponse } from "@/lib/api/client";

export const MASTER_EXPENSE_VISIBLE_CHIP_LIMIT = 6;

export const MASTER_EXPENSE_DESCRIPTION_PLACEHOLDERS = [
  "Dinner with friends",
  "Groceries",
  "Uber ride",
  "Netflix subscription",
] as const;

export type MasterExpenseCategoryOption = {
  category_id: string;
  category_name: string;
  children?: Array<{ category_id: string; category_name: string }>;
};

/** Keep subcategory only when it still belongs to the newly selected category. */
export function resolveSubcategoryForCategory(
  categories: MasterExpenseCategoryOption[],
  categoryCode: string,
  currentSubcategory: string,
): string {
  if (!categoryCode || !currentSubcategory) return "";
  const children = categories.find((c) => c.category_id === categoryCode)?.children ?? [];
  return children.some((c) => c.category_id === currentSubcategory) ? currentSubcategory : "";
}

export function isMasterExpenseFormDirty(input: {
  title: string;
  amountMinor: number;
  subcategoryCode: string;
  feeling: string;
  meaningfulness: string;
  memorability: string;
  sharedWith: string[];
  relationshipImpact: string[];
  contextReason: string;
  notes: string;
}): boolean {
  return Boolean(
    input.title.trim() ||
      input.amountMinor > 0 ||
      input.subcategoryCode ||
      input.feeling ||
      input.meaningfulness ||
      input.memorability ||
      input.sharedWith.length ||
      input.relationshipImpact.length ||
      input.contextReason ||
      input.notes.trim(),
  );
}

export function canSaveMasterExpense(input: {
  lifeOperationsMomentId?: string | null;
  lifestyleMomentId?: string | null;
  title: string;
  amountMinor: number;
  accountId: string;
  categoryCode: string;
}): boolean {
  if (!input.lifeOperationsMomentId || !input.lifestyleMomentId) return false;
  return Boolean(
    input.title.trim() && input.amountMinor > 0 && input.accountId && input.categoryCode,
  );
}

export function formatWhenLabel(occurredAt: string, now: Date = new Date()): string {
  if (!occurredAt) return "Now";
  const datePart = occurredAt.slice(0, 10);
  const timePart = occurredAt.slice(11, 16);
  const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
  if (datePart === today) return `Today, ${timePart}`;
  return occurredAt.replace("T", " ");
}

export function whenPresetValue(
  key: "now" | "today" | "yesterday",
  now: Date = new Date(),
): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  const y = now.getFullYear();
  const m = pad(now.getMonth() + 1);
  const d = pad(now.getDate());
  const hh = pad(now.getHours());
  const mm = pad(now.getMinutes());
  if (key === "now") return `${y}-${m}-${d}T${hh}:${mm}`;
  if (key === "today") return `${y}-${m}-${d}T12:00`;
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  return `${yesterday.getFullYear()}-${pad(yesterday.getMonth() + 1)}-${pad(yesterday.getDate())}T12:00`;
}

export function visibleCategoryChips<T>(items: T[], limit = MASTER_EXPENSE_VISIBLE_CHIP_LIMIT): T[] {
  return items.slice(0, limit);
}

export function masterExpenseCoreFieldOrder(): string[] {
  return ["description", "amount", "category", "subcategory", "paid_from", "when", "impact", "more_details"];
}

export type MasterExpenseOptionsLike = Pick<
  PersonalMasterExpenseOptionsResponse,
  "categories" | "accounts" | "life_operations_moment_id" | "lifestyle_moment_id"
>;

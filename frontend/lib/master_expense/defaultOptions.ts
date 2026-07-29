import type { PersonalQuickAddFieldOption } from "@/lib/api/client";

export const MASTER_EXPENSE_FEELINGS: PersonalQuickAddFieldOption[] = [
  { value: "VERY_BAD", label: "Very Bad" },
  { value: "BAD", label: "Bad" },
  { value: "NEUTRAL", label: "Neutral" },
  { value: "GOOD", label: "Good" },
  { value: "GREAT", label: "Great" },
];

export const MASTER_EXPENSE_SCALE_LEVELS: PersonalQuickAddFieldOption[] = [
  { value: "LOW", label: "Low" },
  { value: "MEDIUM", label: "Medium" },
  { value: "HIGH", label: "High" },
];

export const MASTER_EXPENSE_SHARED_WITH: PersonalQuickAddFieldOption[] = [
  { value: "SPOUSE", label: "Spouse" },
  { value: "PARENTS", label: "Parents" },
  { value: "FAMILY", label: "Family" },
  { value: "FRIENDS", label: "Friends" },
  { value: "CUSTOM", label: "Custom" },
];

export const MASTER_EXPENSE_RELATIONSHIP_IMPACTS: PersonalQuickAddFieldOption[] = [
  { value: "STRENGTHENED_CONNECTION", label: "Strengthened Connection" },
  { value: "CELEBRATION_TOGETHER", label: "Celebration Together" },
  { value: "SUPPORT_GIVEN", label: "Support Given" },
];

export const MASTER_EXPENSE_CONTEXT_REASONS: PersonalQuickAddFieldOption[] = [
  { value: "CELEBRATION", label: "Celebration" },
  { value: "DAILY_NEED", label: "Daily Need" },
  { value: "GIFT", label: "Gift" },
  { value: "TRAVEL", label: "Travel" },
  { value: "OTHER", label: "Other" },
];

/** FAB sits above bottom nav + safe clearance (matches mobile). */
export const MASTER_EXPENSE_FAB_CLEARANCE_PX = 36;

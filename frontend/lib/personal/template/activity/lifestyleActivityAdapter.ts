/** Lifestyle activity adapter for template activity screens. */
import type { TemplateActivityAdapter } from "@/lib/personal/template/activity/types";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";

const LS_TYPES = new Set([
  "LIFESTYLE_EXPENSE",
  "EXPERIENCE",
  "WELLBEING",
  "DISCOVERY",
  "EXPRESSION",
  "CREATIVE",
  "ADJUST",
  "LIFESTYLE_ADJUST",
]);

export const lifestyleActivityAdapter: TemplateActivityAdapter = {
  momentTypeCode: "LIFESTYLE",
  screenTitle: "Activity",
  screenSubtitle: "Your lifestyle journey",
  searchPlaceholder: "Search experiences, wellbeing, spending...",
  emptyMessage: "No activity yet. Use Quick Add on Pulse to log your first lifestyle moment.",
  editTitle: "Edit Activity",
  editSubtitle: "Update this lifestyle log",
  saveChanges: "Save Changes",
  cancel: "Cancel",
  deleteLabel: "Delete activity",
  deleteConfirm: "Remove this log? It will be hidden from your timeline but kept for your records.",
  filters: [
    { id: "all", label: "All" },
    { id: "thisMonth", label: "This Month" },
    { id: "expense", label: "Expense" },
    { id: "experience", label: "Experiences" },
    { id: "wellbeing", label: "Wellbeing" },
    { id: "discovery", label: "Discovery" },
    { id: "expression", label: "Creative" },
    { id: "adjust", label: "Adjust" },
  ],
  filterMatches: (filterId, activityType) => {
    const t = activityType.toUpperCase();
    if (filterId === "all" || filterId === "thisMonth") return true;
    if (filterId === "expense") return t === "LIFESTYLE_EXPENSE";
    if (filterId === "experience") return t === "EXPERIENCE";
    if (filterId === "wellbeing") return t === "WELLBEING";
    if (filterId === "discovery") return t === "DISCOVERY";
    if (filterId === "expression") return t === "EXPRESSION" || t === "CREATIVE";
    if (filterId === "adjust") return t === "ADJUST" || t === "LIFESTYLE_ADJUST";
    return LS_TYPES.has(t);
  },
  formatAmount: lifeOpsPulseCopy.formatInrMinor,
  groupToday: "Today",
  groupYesterday: "Yesterday",
  groupThisWeek: "This Week",
  groupEarlier: "Earlier",
};

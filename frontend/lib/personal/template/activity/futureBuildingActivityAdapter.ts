import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import type { TemplateActivityAdapter } from "@/lib/personal/template/activity/types";

const FB_TYPES = new Set([
  "CONTRIBUTION",
  "MILESTONE",
  "OPPORTUNITY",
  "PIVOT",
  "PROGRESS",
  "LEARNING",
]);

export const futureBuildingActivityAdapter: TemplateActivityAdapter = {
  momentTypeCode: "FUTURE_BUILDING",
  screenTitle: "Activity",
  screenSubtitle: "Your future-building journey",
  searchPlaceholder: "Search milestones, learning, investments...",
  emptyMessage: "No activity yet. Use Quick Add on Pulse to log your first future event.",
  editTitle: "Edit Activity",
  editSubtitle: "Update this future-building log",
  saveChanges: "Save Changes",
  cancel: "Cancel",
  deleteLabel: "Delete activity",
  deleteConfirm: "Remove this log? It will be hidden from your timeline but kept for your records.",
  filters: [
    { id: "all", label: "All" },
    { id: "thisMonth", label: "This Month" },
    { id: "contribution", label: "Contributions" },
    { id: "milestone", label: "Milestones" },
    { id: "learning", label: "Learning" },
    { id: "progress", label: "Progress" },
    { id: "opportunity", label: "Opportunities" },
    { id: "pivot", label: "Pivots" },
  ],
  filterMatches: (filterId, activityType) => {
    const t = activityType.toUpperCase();
    if (filterId === "all" || filterId === "thisMonth") return true;
    if (filterId === "contribution") return t === "CONTRIBUTION";
    if (filterId === "milestone") return t === "MILESTONE";
    if (filterId === "learning") return t === "LEARNING";
    if (filterId === "progress") return t === "PROGRESS";
    if (filterId === "opportunity") return t === "OPPORTUNITY";
    if (filterId === "pivot") return t === "PIVOT";
    return FB_TYPES.has(t);
  },
  formatAmount: lifeOpsPulseCopy.formatInrMinor,
  groupToday: "Today",
  groupYesterday: "Yesterday",
  groupThisWeek: "This Week",
  groupEarlier: "Earlier",
};

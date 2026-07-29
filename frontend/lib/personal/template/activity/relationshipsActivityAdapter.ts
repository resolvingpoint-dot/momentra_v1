/** Relationships activity adapter for template activity screens. */
import type { TemplateActivityAdapter } from "@/lib/personal/template/activity/types";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";

const RS_TYPES = new Set([
  "CONNECTION",
  "SUPPORT",
  "SHARED_EXPERIENCE",
  "RELATIONSHIP_INVESTMENT",
  "ADJUST",
  "RELATIONSHIP_ADJUST",
]);

export const relationshipsActivityAdapter: TemplateActivityAdapter = {
  momentTypeCode: "RELATIONSHIPS",
  screenTitle: "Activity",
  screenSubtitle: "Your relationship journey",
  searchPlaceholder: "Search conversations, support, experiences...",
  emptyMessage: "No activity yet. Use Quick Add on Pulse to log your first relationship moment.",
  editTitle: "Edit Activity",
  editSubtitle: "Update this relationship log",
  saveChanges: "Save Changes",
  cancel: "Cancel",
  deleteLabel: "Delete activity",
  deleteConfirm: "Remove this log? It will be hidden from your timeline but kept for your records.",
  filters: [
    { id: "all", label: "All" },
    { id: "thisMonth", label: "This Month" },
    { id: "connection", label: "Conversation" },
    { id: "support", label: "Support" },
    { id: "experience", label: "Shared Experience" },
    { id: "gift", label: "Gift" },
    { id: "reflection", label: "Reflection" },
  ],
  filterMatches: (filterId, activityType) => {
    const t = activityType.toUpperCase();
    if (filterId === "all" || filterId === "thisMonth") return true;
    if (filterId === "connection") return t === "CONNECTION";
    if (filterId === "support") return t === "SUPPORT";
    if (filterId === "experience") return t === "SHARED_EXPERIENCE";
    if (filterId === "gift") return t === "RELATIONSHIP_INVESTMENT";
    if (filterId === "reflection") return t === "ADJUST" || t === "RELATIONSHIP_ADJUST";
    return RS_TYPES.has(t);
  },
  formatAmount: lifeOpsPulseCopy.formatInrMinor,
  groupToday: "Today",
  groupYesterday: "Yesterday",
  groupThisWeek: "This Week",
  groupEarlier: "Earlier",
};

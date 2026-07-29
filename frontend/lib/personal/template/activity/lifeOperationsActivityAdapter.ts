import { lifeOpsActivityCopy, filterMatchesEventType } from "@/lib/personal/life_operations/activity/lifeOpsActivityCopy";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import type { TemplateActivityAdapter } from "@/lib/personal/template/activity/types";

export const lifeOperationsActivityAdapter: TemplateActivityAdapter = {
  momentTypeCode: "LIFE_OPERATIONS",
  screenTitle: lifeOpsActivityCopy.screenTitle,
  screenSubtitle: lifeOpsActivityCopy.screenSubtitle,
  searchPlaceholder: lifeOpsActivityCopy.searchPlaceholder,
  emptyMessage: lifeOpsActivityCopy.empty,
  editTitle: lifeOpsActivityCopy.editTitle,
  editSubtitle: lifeOpsActivityCopy.editSubtitle,
  saveChanges: lifeOpsActivityCopy.saveChanges,
  cancel: lifeOpsActivityCopy.cancel,
  deleteLabel: "Delete activity",
  deleteConfirm: "Remove this log? It will be hidden from your timeline but kept for your records.",
  filters: [
    { id: "all", label: lifeOpsActivityCopy.filters.all },
    { id: "money", label: lifeOpsActivityCopy.filters.money },
    { id: "edited", label: lifeOpsActivityCopy.filters.edited },
    { id: "thisMonth", label: lifeOpsActivityCopy.filters.thisMonth },
    { id: "attention", label: lifeOpsActivityCopy.filters.attention },
    { id: "recovery", label: lifeOpsActivityCopy.filters.recovery },
    { id: "mood", label: lifeOpsActivityCopy.filters.mood },
    { id: "account", label: lifeOpsActivityCopy.filters.account },
    { id: "adjust", label: lifeOpsActivityCopy.filters.adjust },
  ],
  filterMatches: (filterId, activityType) =>
    filterMatchesEventType(filterId as Parameters<typeof filterMatchesEventType>[0], activityType),
  formatAmount: lifeOpsPulseCopy.formatInrMinor,
  groupToday: lifeOpsActivityCopy.groupToday,
  groupYesterday: lifeOpsActivityCopy.groupYesterday,
  groupThisWeek: lifeOpsActivityCopy.groupThisWeek,
  groupEarlier: lifeOpsActivityCopy.groupEarlier,
};

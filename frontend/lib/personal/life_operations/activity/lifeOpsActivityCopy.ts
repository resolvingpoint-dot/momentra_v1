export const lifeOpsActivityCopy = {
  screenTitle: "Activity",
  screenSubtitle: "Your daily rhythm & money",
  searchPlaceholder: "Search activity, logs, or amounts...",
  totalLogs: "Total Logs",
  thisMonth: "This Month",
  totalAmount: "Total Amount",
  filters: {
    all: "All",
    money: "Money",
    edited: "Edited",
    thisMonth: "This Month",
    attention: "Attention",
    recovery: "Recovery",
    mood: "Mood",
    account: "Account",
    adjust: "Adjust",
  },
  empty: "No activity logged yet. Use Quick Add on Pulse to capture your first log.",
  editTitle: "Edit Activity",
  editSubtitle: "Modify log details and notes",
  saveChanges: "Save Changes",
  cancel: "Cancel",
  titleLabel: "Title",
  amountLabel: "Amount",
  categoryLabel: "Category",
  accountLabel: "Account",
  dateLabel: "Date",
  noteLabel: "Note",
  groupToday: "Today",
  groupYesterday: "Yesterday",
  groupThisWeek: "This Week",
  groupEarlier: "Earlier",
};

export type LifeOpsActivityFilter =
  | "all"
  | "money"
  | "edited"
  | "thisMonth"
  | "attention"
  | "recovery"
  | "mood"
  | "account"
  | "adjust";

export function filterMatchesEventType(filter: LifeOpsActivityFilter, eventType: string): boolean {
  const t = eventType.toUpperCase();
  switch (filter) {
    case "all":
    case "edited":
    case "thisMonth":
      return true;
    case "money":
      return t === "EXPENSE";
    case "attention":
      return t === "COMMITMENT";
    case "recovery":
      return t === "RECOVERY";
    case "mood":
      return t === "REFLECTION";
    case "account":
      return t === "EXPENSE";
    case "adjust":
      return t === "RHYTHM";
    default:
      return true;
  }
}

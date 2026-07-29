/** Human-readable Intelligence OS copy — never expose raw enums in product UI. */

export const LO_SHEET_SUPPORTING = "Record what shapes how your day runs.";
export const LO_SELECTOR_HELPER = "Choose what you want to log.";

export const MONEY_ENTRY_TYPES = ["EXPENSE", "INCOME", "TRANSFER", "CONTRIBUTION"] as const;

export type MoneyEntryType = (typeof MONEY_ENTRY_TYPES)[number];

const RUNTIME_MODE_LABELS: Record<string, string> = {
  FLOW_MODE: "Flow",
  SURVIVAL_MODE: "Survival",
  RECOVERY_MODE: "Recovery",
  BUILD_MODE: "Build",
};

const RUNTIME_MODE_HINTS: Record<string, string> = {
  FLOW_MODE: "Balances pressure, recovery, and focus automatically.",
  SURVIVAL_MODE: "Protects capacity when load is high.",
  RECOVERY_MODE: "Prioritises rest and recharge.",
  BUILD_MODE: "Favours forward momentum and deep work.",
};

const SIGNAL_DIRECTION_LABELS: Record<string, string> = {
  DOWN: "Decrease",
  STABLE: "Keep",
  UP: "Increase",
};

const INTENSITY_LABELS: Record<string, string> = {
  LIGHT: "Light",
  MODERATE: "Moderate",
  HEAVY: "Heavy",
  LOW: "Low",
  HIGH: "High",
};

const SELECTOR_BLURB: Record<string, string> = {
  EXPENSE: "Track spending and pressure",
  COMMITMENT: "Log where focus is going",
  RECOVERY: "Capture rest and recharge",
  REFLECTION: "Reflect how you feel",
  RHYTHM: "Tune rhythm and priorities",
};

/** Map intention chips to runtime signal directions. */
export const INTENTION_SIGNAL_PRESETS: Record<
  string,
  Partial<Record<"pressure" | "recovery" | "focus" | "momentum", "DOWN" | "STABLE" | "UP">>
> = {
  "More Rest": { pressure: "DOWN", recovery: "UP", focus: "STABLE", momentum: "DOWN" },
  "More Balance": { pressure: "STABLE", recovery: "STABLE", focus: "STABLE", momentum: "STABLE" },
  "More Focus": { pressure: "STABLE", recovery: "STABLE", focus: "UP", momentum: "UP" },
  "More Recovery": { pressure: "DOWN", recovery: "UP", focus: "DOWN", momentum: "STABLE" },
};

export function loSelectorBlurb(eventType: string): string {
  return SELECTOR_BLURB[eventType.toUpperCase()] ?? "";
}

export function humanizeEnumLabel(value: string): string {
  if (!value) return "";
  if (RUNTIME_MODE_LABELS[value]) return RUNTIME_MODE_LABELS[value];
  if (SIGNAL_DIRECTION_LABELS[value]) return SIGNAL_DIRECTION_LABELS[value];
  if (INTENSITY_LABELS[value]) return INTENSITY_LABELS[value];
  return value
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export function runtimeModeLabel(mode: string): string {
  return RUNTIME_MODE_LABELS[mode] ?? humanizeEnumLabel(mode);
}

export function runtimeModeHint(mode: string): string {
  return RUNTIME_MODE_HINTS[mode] ?? "";
}

export function signalDirectionLabel(direction: string): string {
  return SIGNAL_DIRECTION_LABELS[direction] ?? humanizeEnumLabel(direction);
}

export function accountLabelForEntryType(transactionType: string): string {
  switch (transactionType) {
    case "INCOME":
      return "Received in";
    case "TRANSFER":
      return "From account";
    case "CONTRIBUTION":
      return "Paid from";
    default:
      return "Paid from";
  }
}

export function moneySaveLabel(transactionType: string): string {
  switch (transactionType) {
    case "INCOME":
      return "Save Income";
    case "TRANSFER":
      return "Save Transfer";
    case "CONTRIBUTION":
      return "Save Contribution";
    default:
      return "Save Expense";
  }
}

export function moneySuccessMessage(transactionType: string): string {
  switch (transactionType) {
    case "INCOME":
      return "Income saved";
    case "TRANSFER":
      return "Transfer saved";
    case "CONTRIBUTION":
      return "Contribution saved";
    default:
      return "Expense saved";
  }
}

export function tabSaveLabel(eventType: string, transactionType?: string): string {
  switch (eventType) {
    case "EXPENSE":
      return moneySaveLabel(transactionType ?? "EXPENSE");
    case "COMMITMENT":
      return "Log Attention State";
    case "RECOVERY":
      return "Log Recovery";
    case "REFLECTION":
      return "Save Mood";
    case "RHYTHM":
      return "Update Rhythm";
    default:
      return "Save Entry";
  }
}

export function tabSuccessMessage(eventType: string, transactionType?: string): string {
  switch (eventType) {
    case "EXPENSE":
      return moneySuccessMessage(transactionType ?? "EXPENSE");
    case "COMMITMENT":
      return "Attention entry saved";
    case "RECOVERY":
      return "Recovery logged";
    case "REFLECTION":
      return "Mood saved";
    case "RHYTHM":
      return "Rhythm updated";
    default:
      return "Saved";
  }
}

export function humanizeInsightTitle(title: string | null | undefined): string {
  if (!title) return "";
  return humanizeEnumLabel(title.trim());
}

export function compactInsightBody(
  title: string | null | undefined,
  body: string | null | undefined,
): string | null {
  const t = title?.trim();
  const b = body?.trim();
  if (!t && !b) return null;
  if (t && /^[A-Z0-9_]+$/.test(t)) {
    const nice = humanizeEnumLabel(t);
    if (b) return b.replace(t, nice);
    return `${nice} is worth recording while it is still fresh.`;
  }
  return b ?? t ?? null;
}

export function filterMoneyEntryTypes(
  options: Array<{ value: string; label: string }>,
): Array<{ value: string; label: string }> {
  const allowed = new Set<string>(MONEY_ENTRY_TYPES);
  const filtered = options.filter((o) => allowed.has(o.value));
  return filtered.length
    ? filtered
    : MONEY_ENTRY_TYPES.map((v) => ({
        value: v,
        label: humanizeEnumLabel(v === "EXPENSE" ? "Expense" : v),
      }));
}

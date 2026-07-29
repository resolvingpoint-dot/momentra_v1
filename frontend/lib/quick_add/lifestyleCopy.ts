/** Lifestyle Quick Add copy + success messages. */

export const LS_SHEET_SUPPORTING = "Record what shapes how you live.";
export const LS_SELECTOR_HELPER = "Choose what you want to capture.";

export const LS_EVENT_ALIASES: Record<string, string> = {
  CREATIVE: "EXPRESSION",
  LIFESTYLE_ADJUST: "ADJUST",
};

export function normalizeLifestyleEventType(raw?: string | null): string {
  const upper = (raw ?? "LIFESTYLE_EXPENSE").toUpperCase();
  return LS_EVENT_ALIASES[upper] ?? upper;
}

const SELECTOR_FALLBACK: Record<string, { title: string; blurb: string }> = {
  LIFESTYLE_EXPENSE: { title: "Expense", blurb: "Record lifestyle spending" },
  EXPERIENCE: { title: "Experience", blurb: "Save a memorable moment" },
  WELLBEING: { title: "Wellbeing", blurb: "Check in on a life area" },
  DISCOVERY: { title: "Discover", blurb: "Capture a new curiosity" },
  EXPRESSION: { title: "Create", blurb: "Record something you made" },
  ADJUST: { title: "Adjust", blurb: "Change a lifestyle priority" },
};

const TITLE_PLACEHOLDERS: Record<string, string> = {
  LIFESTYLE_EXPENSE: "Dinner with friends, yoga membership…",
  EXPERIENCE: "Dinner with college friends, weekend hike…",
  WELLBEING: "How work and rest are balancing this week…",
  DISCOVERY: "A new café nearby, a book idea…",
  EXPRESSION: "Product landing page, a new recipe…",
  ADJUST: "Spend less on eating out and cook more at home…",
};

export function lsSelectorFallback(eventType: string) {
  return SELECTOR_FALLBACK[eventType] ?? { title: eventType, blurb: "" };
}

export function lsTitlePlaceholder(eventType: string) {
  return TITLE_PLACEHOLDERS[eventType] ?? "What do you want to capture?";
}

export function lsSuccessMessage(eventType: string): string {
  switch (normalizeLifestyleEventType(eventType)) {
    case "LIFESTYLE_EXPENSE":
      return "Lifestyle expense saved";
    case "EXPERIENCE":
      return "Experience saved";
    case "WELLBEING":
      return "Wellbeing check-in saved";
    case "DISCOVERY":
      return "Discovery saved";
    case "EXPRESSION":
      return "Creation saved";
    case "ADJUST":
      return "Lifestyle updated";
    default:
      return "Entry saved";
  }
}

export function lsErrorMessage(eventType: string): string {
  switch (normalizeLifestyleEventType(eventType)) {
    case "LIFESTYLE_EXPENSE":
      return "Couldn't save the expense. Try again.";
    case "EXPERIENCE":
      return "Couldn't save the experience. Try again.";
    case "WELLBEING":
      return "Couldn't save the wellbeing check-in. Try again.";
    case "DISCOVERY":
      return "Couldn't save the discovery. Try again.";
    case "EXPRESSION":
      return "Couldn't save the creation. Try again.";
    case "ADJUST":
      return "Couldn't update Lifestyle. Try again.";
    default:
      return "Couldn't save. Try again.";
  }
}

export function lsSavingLabel(eventType: string): string {
  switch (normalizeLifestyleEventType(eventType)) {
    case "LIFESTYLE_EXPENSE":
      return "Saving Expense…";
    case "EXPERIENCE":
      return "Saving Experience…";
    case "WELLBEING":
      return "Saving Wellbeing…";
    case "DISCOVERY":
      return "Saving Discovery…";
    case "EXPRESSION":
      return "Saving Creation…";
    case "ADJUST":
      return "Updating Lifestyle…";
    default:
      return "Saving…";
  }
}

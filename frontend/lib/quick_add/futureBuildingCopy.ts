/** Future Building / Build Momentum copy + success messages. */

export const FB_SHEET_SUPPORTING =
  "Record something that moved you forward.";

export const FB_SELECTOR_HELPER =
  "Choose what kind of momentum you want to record.";

export const FB_EVENT_TYPES = new Set([
  "CONTRIBUTION",
  "MILESTONE",
  "OPPORTUNITY",
  "PIVOT",
  "PROGRESS",
  "LEARNING",
]);

const TITLE_PLACEHOLDERS: Record<string, string> = {
  CONTRIBUTION: "Product development, a course, family time…",
  MILESTONE: "Launched the first version, finished the course…",
  OPPORTUNITY: "A partnership intro, a new client lead…",
  PIVOT: "Changed the launch plan from ads to partnerships…",
  PROGRESS: "Completed onboarding screens, improved distance…",
  LEARNING: "Customers respond better when value is shown first…",
};

const SELECTOR_FALLBACK: Record<string, { title: string; blurb: string }> = {
  CONTRIBUTION: { title: "Investment", blurb: "Put in money or energy" },
  MILESTONE: { title: "Milestone", blurb: "Celebrate an achievement" },
  OPPORTUNITY: { title: "Opportunity", blurb: "Capture a new possibility" },
  PIVOT: { title: "Pivot", blurb: "Record a change in direction" },
  PROGRESS: { title: "Progress", blurb: "Log forward movement" },
  LEARNING: { title: "Learning", blurb: "Save a lesson or insight" },
};

export function fbTitlePlaceholder(eventType: string): string {
  return TITLE_PLACEHOLDERS[eventType] ?? "What moved you forward?";
}

export function fbSelectorFallback(eventType: string): { title: string; blurb: string } {
  return SELECTOR_FALLBACK[eventType] ?? { title: eventType, blurb: "" };
}

export function fbSuccessMessage(eventType: string): string {
  switch (eventType) {
    case "CONTRIBUTION":
      return "Investment saved";
    case "MILESTONE":
      return "Milestone saved";
    case "OPPORTUNITY":
      return "Opportunity saved";
    case "PIVOT":
      return "Pivot saved";
    case "PROGRESS":
      return "Progress saved";
    case "LEARNING":
      return "Learning saved";
    default:
      return "Entry saved";
  }
}

export function fbErrorMessage(eventType: string): string {
  switch (eventType) {
    case "CONTRIBUTION":
      return "Couldn't save investment. Try again.";
    case "MILESTONE":
      return "Couldn't save milestone. Try again.";
    case "OPPORTUNITY":
      return "Couldn't save opportunity. Try again.";
    case "PIVOT":
      return "Couldn't save pivot. Try again.";
    case "PROGRESS":
      return "Couldn't save progress. Try again.";
    case "LEARNING":
      return "Couldn't save learning. Try again.";
    default:
      return "Couldn't save. Try again.";
  }
}

export function fbSavingLabel(eventType: string): string {
  switch (eventType) {
    case "CONTRIBUTION":
      return "Saving Investment…";
    case "MILESTONE":
      return "Saving Milestone…";
    case "OPPORTUNITY":
      return "Saving Opportunity…";
    case "PIVOT":
      return "Saving Pivot…";
    case "PROGRESS":
      return "Saving Progress…";
    case "LEARNING":
      return "Saving Learning…";
    default:
      return "Saving…";
  }
}

export function fbCtaLabel(eventType: string, tabCta?: string | null): string {
  if (tabCta?.trim()) return tabCta;
  switch (eventType) {
    case "CONTRIBUTION":
      return "Save Investment";
    case "MILESTONE":
      return "Save Milestone";
    case "OPPORTUNITY":
      return "Save Opportunity";
    case "PIVOT":
      return "Save Pivot";
    case "PROGRESS":
      return "Save Progress";
    case "LEARNING":
      return "Save Learning";
    default:
      return "Save Entry";
  }
}

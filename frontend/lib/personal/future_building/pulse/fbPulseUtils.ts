import type { PersonalLiveRecentActivityItem } from "@/lib/api/personal";

const EVENT_IMPACT: Record<string, { tag: string; colorKey: "primary" | "secondary" | "tertiary" }> = {
  LEARNING: { tag: "+3 Learning", colorKey: "tertiary" },
  PROGRESS: { tag: "+4 Execution", colorKey: "tertiary" },
  MILESTONE: { tag: "+5 Opportunity", colorKey: "tertiary" },
  OPPORTUNITY: { tag: "+5 Opportunity", colorKey: "tertiary" },
  PIVOT: { tag: "+2 Momentum", colorKey: "tertiary" },
  CONTRIBUTION: { tag: "Investment", colorKey: "tertiary" },
};

export function fbActivityImpactTag(eventType: string, amountLabel?: string | null): string {
  const t = eventType.toUpperCase();
  if (t === "CONTRIBUTION") {
    const amount = amountLabel?.trim();
    return amount ? `Investment · ${amount}` : "Investment";
  }
  return EVENT_IMPACT[t]?.tag ?? `+1 ${eventType}`;
}

export function fbActivityCategoryLabel(
  eventType: string,
  categoryLabel: string,
  amountLabel?: string | null,
): string {
  const t = eventType.toUpperCase();
  const base = t === "CONTRIBUTION" ? "Investment" : categoryLabel || eventType;
  const amount = amountLabel?.trim();
  if (t === "CONTRIBUTION" && amount) return `${base} · ${amount}`;
  return base;
}

export function fbTimelineImpactLine(eventType: string): { label: string; accent: string } {
  const t = eventType.toUpperCase();
  if (t === "LEARNING") return { label: "Learning ↑", accent: "primary" };
  if (t === "PROGRESS") return { label: "Execution ↑", accent: "secondary" };
  if (t === "MILESTONE") return { label: "Future Momentum ↑", accent: "tertiary" };
  if (t === "OPPORTUNITY") return { label: "Opportunity ↑", accent: "tertiary" };
  if (t === "CONTRIBUTION") return { label: "Investment ↑", accent: "tertiary" };
  return { label: "Momentum ↑", accent: "primary" };
}

export function fbActivityIconKey(item: PersonalLiveRecentActivityItem): string {
  const t = item.event_type.toUpperCase();
  if (t === "LEARNING") return "school";
  if (t === "PROGRESS") return "rocket_launch";
  if (t === "MILESTONE") return "flag";
  if (t === "OPPORTUNITY") return "stars";
  return "step";
}

export const FB_PULSE_SUMMARY_IDS = ["learning", "execution", "momentum", "confidence"] as const;

export const FB_SEGMENT_COLORS = ["#c9bfff", "#cabeff", "#4cd6ff", "#6c4ef2"];

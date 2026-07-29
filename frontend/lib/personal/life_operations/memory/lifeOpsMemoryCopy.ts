export const lifeOpsMemoryCopy = {
  screenBreadcrumb: "Life Operations",
  screenTitle: "Memory",
  sectionLabels: {
    identity: "1 Identity Snapshot",
    corePattern: "2 Core Pattern",
    bestDrivers: "3 Best Drivers",
    lowestDrivers: "4 Lowest Drivers",
    returnBehaviors: "5 Highest Return Behaviors",
    emotionalDna: "6 Emotional DNA",
    behavioralPatterns: "7 Behavioral Patterns",
    evolution: "8 Evolution Timeline",
    aiInterpretation: "9 Momentra Interpretation",
    growthEdge: "10 Your Next Growth Edge",
  },
  confidenceLabel: "Confidence",
  patternConfidence: (pct: number) => `Pattern Confidence ${pct}%`,
  segmentColor(token: string, colors: { brandPrimary: string; tertiary?: string; error?: string }) {
    if (token === "tertiary") return colors.tertiary ?? "#4cd6ff";
    if (token === "error") return colors.error ?? "#ffb4ab";
    return colors.brandPrimary;
  },
};

export type PersonalMemoryCopy = typeof lifeOpsMemoryCopy;

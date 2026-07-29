export const lifestylePulseCopy = {
  screenBreadcrumb: "Personal / Pulse",
  screenTitle: "Lifestyle",
  liveMetricsBadge: "Live Vitality",
  vitalityTitle: "Lifestyle Vitality",
  vitalitySuffix: "/100",
  vitalityLabel: "Vitality",
  statSpend: "Lifestyle Spend",
  statExperiences: "Experiences",
  statDiscoveries: "Discoveries",
  statCreative: "Creative Sessions",
  recentActivityFeedTitle: "Recent Activity Feed",
  financialTitle: "Financial Pulse",
  scoreDriversTitle: "Score Drivers",
  stateGaugesTitle: "Current State",
  quickAddTitle: "Quick Launcher",
  trendsTitle: "Current Trends (30 Days)",
  intelligenceInsightTitle: "AI Insight",
  intelligenceActive: "Active",
  highPriorityOpportunity: "Growth Opportunity",
  viewAll: "View All",
  financialEmptyHint: "Lifestyle spending appears after your first logged experiences.",
  recentActivityEmptyFallback: "No activity captured yet. Log an experience to get started.",
  trendsJoyLegend: "Joy",
  trendsVitalityLegend: "Vitality",
  trendsAxis30dAgo: "30D Ago",
  trendsAxis15dAgo: "15D Ago",
  trendsAxisNow: "Now",
  trendsSparseEmpty: "Not enough history yet for a 30-day chart.",
  trendsSparseThreshold: 7,
  trendsDeltaLabel(start: number, end: number): string {
    return `${start} → ${end}`;
  },
  trendsDeltaSigned(delta: number): string {
    if (delta > 0) return `+${delta}`;
    return `${delta}`;
  },
  statusPillLabels: {
    fulfillmentRising: "Fulfillment Rising",
    creativityStrong: "Creativity Strong",
    explorationImproving: "Exploration Improving",
    lifestyleDriftLow: "Lifestyle Drift Low",
  },
  statusBands: {
    FLOURISHING: "Flourishing",
    ENRICHED: "Enriched",
    ROUTINE: "Routine",
  } as Record<string, string>,
  signalLabels: {
    joy: "Joy",
    fulfillment: "Fulfillment",
    vitality: "Vitality",
    exploration: "Exploration",
  } as Record<string, string>,
  driverLabels: {
    travel: "Travel",
    nature: "Nature",
    creativity: "Creativity",
    impulse: "Impulse",
  } as Record<string, string>,
  gaugeLabels: {
    fulfill: "Fulfill",
    vitality: "Vitality",
    explore: "Explore",
    create: "Create",
  } as Record<string, string>,
  quickAddActions: ["Expense", "Experience", "Wellbeing", "Discover", "Create", "Adjust"],
  formatInrMinor(minor: number): string {
    const rupees = minor / 100;
    if (rupees >= 1000) return `₹${(rupees / 1000).toFixed(1)}K`;
    return `₹${Math.round(rupees).toLocaleString("en-IN")}`;
  },
  trendArrow(trend: string): string {
    const t = trend.toUpperCase();
    if (t === "UP" || t === "STRONG_UP") return "↑";
    if (t === "DOWN") return "↓";
    return "→";
  },
};

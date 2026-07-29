export const fbPulseCopy = {
  screenBreadcrumb: "Personal / Pulse",
  screenTitle: "Future Momentum",
  momentumIndexTitle: "Current Pulse Score",
  momentumIndexSuffix: "/100",
  financialTitle: "Financial Momentum",
  recentActivityFeedTitle: "Recent Activity Feed",
  trendsTitle: "Current Trends",
  scoreDriversTitle: "Score Drivers",
  stateGaugesTitle: "State Snapshot",
  highPriorityOpportunity: "Priority Opportunity",
  intelligenceInsightTitle: "AI Intelligence Insight",
  aiInsightEngineTitle: "AI Insight Engine",
  quickAddTitle: "Quick Action Launcher",
  viewAll: "View All",
  financialTotalLabel: "Total",
  financialEmptyHint: "Investment breakdown appears after your first contribution.",
  recentActivityEmptyFallback: "No activity captured yet. Log learning, progress, or milestones.",
  trendsLearningLegend: "Learning",
  trendsExecutionLegend: "Execution",
  trendsProgressLegend: "Progress",
  trendsSparseThreshold: 7,
  statusBands: {
    EXPLORING: "Exploring",
    BUILDING: "Building",
    ACCELERATING: "Accelerating",
    EMERGING: "Emerging",
  } as Record<string, string>,
  trendArrow(trend: string): string {
    const t = trend.toUpperCase();
    if (t === "STRONG_UP" || t === "UP") return "↑";
    if (t === "DOWN") return "↓";
    return "→";
  },
  formatInrMinor(minor: number): string {
    const rupees = minor / 100;
    if (rupees >= 1000) return `₹${(rupees / 1000).toFixed(rupees % 1000 === 0 ? 0 : 1)}k`;
    return `₹${rupees.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  },
  quickAddActions: [
    { code: "CONTRIBUTION", label: "Log Contribution" },
    { code: "PROGRESS", label: "Log Progress" },
    { code: "MILESTONE", label: "Log Milestone" },
    { code: "OPPORTUNITY", label: "Log Opp" },
    { code: "LEARNING", label: "Log Learning" },
    { code: "PIVOT", label: "Log Pivot" },
  ],
};

export const lifeOpsPulseCopy = {
  screenBreadcrumb: "Personal / Pulse",
  screenTitle: "Life Operations",
  liveMetricsBadge: "Live Metrics",
  opsIndexTitle: "Life Operations Health",
  opsIndexSuffix: "/100",
  opsIndexLabel: "Ops Index",
  axisPressure: "Pressure",
  axisRecovery: "Recovery",
  axisDiscipline: "Discipline",
  axisAttention: "Attention",
  capacityMonthly: "Monthly Capacity",
  capacityUsed: "Spent this month",
  capacityRemaining: "Remaining",
  capacityUtilization: "Utilization",
  recentActivityListTitle: "Recent Activity",
  recentActivityListSubtitle: "Latest logs across your personal moments",
  recentActivityFeedTitle: "Recent Activity Feed",
  financialTitle: "Financial Intelligence",
  scoreDriversTitle: "Score Drivers Impact",
  stateGaugesTitle: "Current State Snapshot",
  quickAddTitle: "Quick Add Launcher",
  trendsTitle: "Current Trends (30 Days)",
  trendsPlaceholder: "Chart visualization coming soon",
  intelligenceInsightTitle: "Intelligence Insight",
  intelligenceActive: "Active",
  highPriorityOpportunity: "High Priority Opportunity",
  logRecoveryNow: "Log Recovery Now",
  viewAll: "View All",
  financialTotalLabel: "Total",
  financialEmptyHint: "Category spending appears after your first logged expenses.",
  recentActivityEmptyFallback:
    "No activity captured yet. Use Quick Add to log recovery, mood, money, and more.",
  trendsRecoveryLegend: "Recovery",
  trendsPressureLegend: "Pressure",
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
  stressImpactLabel: (n: number) => `-${n} Stress Impact`,
  capacityBoostLabel: (n: number) => `+${n} Capacity Boost`,
  statusPillLabels: {
    recoveryRising: "Recovery Rising",
    pressureStable: "Pressure Stable",
    moodImproving: "Mood Improving",
    budgetStrong: "Budget Strong",
  },
  statusBands: {
    STABLE_IMPROVING: "Stable and Improving",
    STABLE: "Stable",
    PRESSURE_ELEVATED: "Pressure Elevated",
    RECOVERY_NEEDED: "Recovery Needed",
    MOMENTUM_ACTIVE: "Momentum Active",
    "Insufficient data": "Insufficient data",
    "Mostly Stable": "Mostly Stable",
    "Stable Flow": "Stable Flow",
    "Pressure Building": "Pressure Building",
    "Needs Recovery": "Needs Recovery",
    "High Pressure": "High Pressure",
  } as Record<string, string>,
  insufficientDataLabel: "Insufficient data",
  dash: "—",
  signalLabels: {
    pressure: "Pressure",
    recovery: "Recovery",
    capacity: "Capacity",
    money: "Money",
  } as Record<string, string>,
  driverLabels: {
    recovery: "Recovery",
    consistency: "Consistency",
    mood: "Mood",
    pressure: "Pressure",
  } as Record<string, string>,
  gaugeLabels: {
    stress: "Stress",
    capacity: "Capacity",
    discipline: "Discipline",
    stability: "Stability",
  } as Record<string, string>,
  opportunityTitles: {
    protect_recovery: "Protect Recovery",
    stability_focus: "Stability Focus",
    adaptive_flow: "Adaptive Flow",
  } as Record<string, string>,
  opportunityBodies: {
    protect_recovery:
      "Add one recovery block before your next high-pressure engagement.",
    stability_focus: "Maintain current routines to preserve operational stability.",
    adaptive_flow: "Balance pressure and recovery as signals evolve.",
  } as Record<string, string>,
  intelligencePatterns: {
    recovery_dampening_pressure:
      "Neural analysis suggests recovery activity is effectively dampening pressure trends.",
    pressure_rising: "Pressure signals are building — simplify discretionary load this week.",
    recovery_improving: "Recovery continuity is strengthening your operating rhythm.",
  } as Record<string, string>,
  quickAddActions: [
    "Log Recovery",
    "Log Attention",
    "Log Mood",
    "Log Money",
    "Log Adjust",
  ],
  trendArrow(trend: string): string {
    if (trend === "STRONG_UP") return "↑↑";
    if (trend === "UP") return "↑";
    if (trend === "DOWN") return "↓";
    return "→";
  },
  formatInrMinor(minor: number): string {
    const rupees = minor / 100;
    return `₹${rupees.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  },
  formatCapacityMinor(minor: number | null | undefined, hasBudget: boolean): string {
    if (!hasBudget || minor == null) return "—";
    return lifeOpsPulseCopy.formatInrMinor(minor);
  },
  formatUtilization(percent: number | null | undefined, hasBudget: boolean): string {
    if (!hasBudget || percent == null) return "—";
    return `${percent}%`;
  },
};

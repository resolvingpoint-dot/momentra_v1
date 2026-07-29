export const relationshipsPulseCopy = {
  screenBreadcrumb: "Personal / Pulse",
  screenTitle: "Relationships",
  networkStability: "Network Stability",
  bondIndexSuffix: "/100",
  statusBands: {
    EMERGING: "Emerging",
    GROWING: "Growing",
    FLOURISHING: "Flourishing",
  } as Record<string, string>,
  statConnections: "Conns",
  statSupport: "Support",
  statExperiences: "Exp",
  statSpend: "Spent",
  summaryConnections: "Connections",
  summarySpend: "Rel Spend",
  recentActivityTitle: "Recent Activity",
  viewAll: "View All",
  financialTitle: "Financial Overview",
  trendsTitle: "Current Trends (30 Days)",
  trendsTrustLegend: "Trust",
  trendsConnLegend: "Conn",
  gaugesTitle: "Current State Snapshot",
  gaugeLabels: {
    conn: "CONN",
    trust: "TRUST",
    supp: "SUPP",
    belong: "BELONG",
  } as Record<string, string>,
  recommendationBadge: "Top Recommendation",
  signalsTitle: "Signals Analysis",
  intelligenceTitle: "Intelligence Engine",
  quickCaptureTitle: "Quick Pulse Capture",
  financialEmptyHint: "Relationship spending appears after your first logged investment.",
  recentActivityEmpty: "No activity captured yet. Log a connection to get started.",
  trendArrow(trend: string): string {
    if (trend === "UP" || trend === "STRONG_UP") return "↑";
    if (trend === "DOWN") return "↓";
    return "→";
  },
  formatInrMinor(minor: number): string {
    const rupees = minor / 100;
    if (rupees >= 1000) return `₹${(rupees / 1000).toFixed(1)}k`;
    return `₹${Math.round(rupees).toLocaleString("en-IN")}`;
  },
};

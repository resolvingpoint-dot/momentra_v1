export const relationshipsMomentsAccent = {
  pink: "#d63384",
  purple: "#6f42c1",
  cardBg: "rgba(20, 22, 48, 0.6)",
};

export const relationshipsMomentsCopy = {
  screenBreadcrumb: "Personal / Moments",
  screenTitle: "Relationships",
  journeyHeroSection: "Journey Hero",
  journeyHeroTitle: "Relationship Journey",
  pathMilestoneLabel: "Connection established",
  statConnections: "Connections",
  statSupport: "Support",
  statExperiences: "Experiences",
  statSpend: "Spend",
  journeyTimelineTitle: "Journey Timeline",
  journeyTimelineEmpty: "No journey events yet.",
  viewAll: "View all",
  moneyJourneyEmpty: "Relationship spending appears after your first logged investment.",
  totalSpend: "Total Spend",
  highestArea: "Highest Area",
  bestMonth: "Best Month",
  bestMomentsTitle: "Best Moments",
  bestMomentsEmpty: "No standout moments yet.",
  turningPointsTitle: "Turning Points",
  turningPointsEmpty: "No turning points yet.",
  statusBandLabel(band: string): string {
    const labels: Record<string, string> = {
      EMERGING: "Emerging",
      GROWING: "Growing",
      FLOURISHING: "Deeply Connected",
    };
    return labels[band] ?? band.replace(/_/g, " ");
  },
  formatInrMinor(minor: number): string {
    const rupees = minor / 100;
    if (rupees >= 1000) return `₹${(rupees / 1000).toFixed(1)}K`;
    return `₹${Math.round(rupees).toLocaleString("en-IN")}`;
  },
  formatInrFull(minor: number): string {
    return `₹${Math.round(minor / 100).toLocaleString("en-IN")}`;
  },
  moneySeriesColors: ["#d63384", "#4cd6ff", "#f59e0b"] as const,
};

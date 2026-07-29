export const fbMomentsCopy = {
  screenBreadcrumb: "Personal / Moments",
  screenTitle: "Future Building",
  journeyHeroSection: "The Story So Far",
  journeyHeroTitle: "Future Growth Journey",
  journeyTimelineTitle: "Journey Timeline",
  moneyJourneyTitle: "Money Journey",
  bestMomentsTitle: "Best Moments",
  turningPointsTitle: "Turning Points",
  viewAll: "View all",
  statusBandLabel(band: string, statusLabel?: string): string {
    if (statusLabel) return statusLabel;
    const labels: Record<string, string> = {
      EXPLORING: "Exploring",
      BUILDING: "Building",
      ACCELERATING: "Accelerating",
      EMERGING: "Emerging",
    };
    return labels[band] ?? band;
  },
  formatInrMinor(minor: number): string {
    const rupees = minor / 100;
    return `₹${rupees.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  },
};

import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";

export const lifeOpsMomentsCopy = {
  screenBreadcrumb: "Personal / Moments",
  screenTitle: "Life Operations",
  journeyHeroTitle: "Life Rhythm Journey",
  journeyHeroSection: "Journey Hero",
  journeyTimelineTitle: "Journey Timeline",
  journeyTimelineEmpty: "No journey events yet. Log recovery, mood, or money to build your timeline.",
  moneyJourneySection: "Money Journey",
  bestMomentsTitle: "Best Moments",
  bestMomentsEmpty: "Your standout weeks and months will appear here as you build history.",
  turningPointsTitle: "Turning Points",
  turningPointsEmpty: "Milestones appear as your life operations moment evolves.",
  statDaysActive: "Days Active",
  statRecoveryEvents: "Recovery Events",
  statAdjustmentsMade: "Adjustments Made",
  statPressureReduced: "Pressure Reduced",
  totalSpendLabel: "Total Spend",
  highestMonthLabel: "Highest Month",
  lowestMonthLabel: "Lowest Month",
  moneyJourneyEmpty: "Spending trends appear after your first logged expenses.",
  statusBandLabel(band: string): string {
    return lifeOpsPulseCopy.statusBands[band] ?? band.replace(/_/g, " ");
  },
  formatInrFromMinor(minor: number): string {
    return `₹${(minor / 100).toLocaleString("en-IN", {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    })}`;
  },
};

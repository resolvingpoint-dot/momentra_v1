export const lifestyleMomentsCopy = {
  screenBreadcrumb: "Personal / Moments",
  screenTitle: "Lifestyle",
  journeyHeroSection: "Journey Hero",
  journeyHeroTitle: "Current State",
  journeyTimelineTitle: "Journey Timeline",
  journeyTimelineEmpty: "Log experiences to build your lifestyle journey timeline.",
  statusBandLabel(band: string): string {
    const labels: Record<string, string> = {
      FLOURISHING: "Flourishing",
      ENRICHED: "Enriched",
      ROUTINE: "Routine",
    };
    return labels[band] ?? band.replace(/_/g, " ");
  },
  statExperiences: "Experiences",
  statDiscoveries: "Discoveries",
  statCreative: "Creative",
  statSpend: "Spend",
  formatInrMinor(minor: number): string {
    const rupees = minor / 100;
    if (rupees >= 1000) return `₹${(rupees / 1000).toFixed(1)}K`;
    return `₹${Math.round(rupees).toLocaleString("en-IN")}`;
  },
};

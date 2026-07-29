export const BUSINESS_LIFE_EMPTY_COPY = {
  hero: {
    eyebrow: "Your Business",
    title: "Journey Starts Here",
    subtitle:
      "Business Life brings together people, operations, finances, vendors and execution into one living view of your business.",
    ctaLabel: "Create First Business Moment",
    heroImage: "/business/life-hero-orbital.jpg",
  },
  futureBusiness: {
    sectionTitle: "Your Future Business",
    cards: [
      {
        title: "People Growth",
        description: "Build a strong leadership culture.",
        accent: "#A855F7",
        accentBg: "rgba(168, 85, 247, 0.2)",
      },
      {
        title: "Financial Strength",
        description: "Create runway and resilience.",
        accent: "#22C55E",
        accentBg: "rgba(34, 197, 94, 0.2)",
      },
      {
        title: "Operational Excellence",
        description: "Improve processes & efficiency.",
        accent: "#F59E0B",
        accentBg: "rgba(245, 158, 11, 0.2)",
      },
      {
        title: "Partner Network",
        description: "Build reliable relationships.",
        accent: "#3B82F6",
        accentBg: "rgba(59, 130, 246, 0.2)",
      },
    ] as const,
  },
  howItWorks: {
    sectionTitle: "How Business Life Works",
    steps: [
      { label: "Create\nMoments", accent: "#A855F7" },
      { label: "Invite\nContributors", accent: "#22C55E" },
      { label: "Record\nActivities", accent: "#F59E0B" },
      { label: "Build\nMomentum", accent: "#3B82F6" },
      { label: "Grow The\nBusiness", accent: "#EAB308" },
    ] as const,
  },
  whyTeams: {
    sectionTitle: "Why Teams Use Life",
    cards: [
      {
        title: "See Progress",
        description: "Understand where your business is heading.",
        accent: "#A855F7",
        accentBg: "rgba(168, 85, 247, 0.2)",
      },
      {
        title: "Increase Participation",
        description: "Help everyone contribute consistently.",
        accent: "#22C55E",
        accentBg: "rgba(34, 197, 94, 0.2)",
      },
      {
        title: "Align Teams",
        description: "Connect work across all operational moments.",
        accent: "#F59E0B",
        accentBg: "rgba(245, 158, 11, 0.2)",
      },
      {
        title: "Build Together",
        description: "Turn daily actions into business growth.",
        accent: "#3B82F6",
        accentBg: "rgba(59, 130, 246, 0.2)",
      },
    ] as const,
  },
  footer: {
    title: "Your Business Is Ready To Grow",
    subtitle:
      "Create operational moments and invite contributors to begin building your business story.",
    ctaLabel: "Create First Business Moment",
  },
} as const;

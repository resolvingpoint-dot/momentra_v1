import type { WorldId } from "@/lib/marketing/copy";

export type PulseHealth = "Healthy" | "Needs attention" | "At risk" | "On Track";

export type LivingMomentStatus = {
  label: string;
  tone?: "ok" | "pending" | "warn";
};

export type LivingMoment = {
  id: string;
  title: string;
  purpose: string;
  world: WorldId;
  participants?: number;
  budgetLabel?: string;
  savedLabel?: string;
  progress: number;
  timeline: string;
  statuses?: LivingMomentStatus[];
  memoryLabel?: string;
  pulse: {
    health: PulseHealth;
    score?: number;
    line: string;
  };
  aiInsight: string;
  metaLines?: string[];
};

/** Hero cycle — visitor should understand Momentra organizes life without reading */
export const heroCycleMoments: LivingMoment[] = [
  {
    id: "emergency-fund",
    title: "Emergency Fund",
    purpose: "Personal security",
    world: "personal",
    budgetLabel: "₹3,20,000 Goal",
    savedLabel: "₹2,35,000 Saved",
    progress: 73,
    timeline: "Recovery Updated",
    pulse: {
      health: "Healthy",
      score: 87,
      line: "Steady progress. You're closer than last month.",
    },
    aiInsight: "Salary credited. Contribution opportunity this week.",
    statuses: [{ label: "Recovery Updated", tone: "ok" }],
  },
  {
    id: "birthday",
    title: "Birthday",
    purpose: "Celebration",
    world: "group",
    participants: 8,
    budgetLabel: "₹12,000 Pool",
    progress: 68,
    timeline: "3 days left",
    pulse: {
      health: "On Track",
      score: 78,
      line: "Gift pool almost complete.",
    },
    aiInsight: "Two people haven't contributed yet.",
    statuses: [
      { label: "Venue Booked", tone: "ok" },
      { label: "Cake Pending", tone: "pending" },
    ],
    memoryLabel: "6 Photos",
  },
  {
    id: "wedding",
    title: "Wedding",
    purpose: "Family celebration",
    world: "group",
    participants: 24,
    budgetLabel: "₹4,50,000",
    progress: 54,
    timeline: "6 weeks",
    pulse: {
      health: "Needs attention",
      score: 62,
      line: "Vendor timeline needs confirmation.",
    },
    aiInsight: "Catering deposit due Friday.",
    statuses: [
      { label: "Venue Confirmed", tone: "ok" },
      { label: "Invites Pending", tone: "pending" },
    ],
  },
  {
    id: "home-renovation",
    title: "Home Renovation",
    purpose: "Living space",
    world: "personal",
    budgetLabel: "₹2,80,000",
    progress: 41,
    timeline: "Phase 2 of 4",
    pulse: {
      health: "On Track",
      score: 71,
      line: "Materials ordered. Crew scheduled.",
    },
    aiInsight: "Paint delivery delayed by 2 days.",
    statuses: [
      { label: "Demolition Done", tone: "ok" },
      { label: "Electrical Pending", tone: "pending" },
    ],
  },
  {
    id: "project-launch",
    title: "Project Launch",
    purpose: "Business delivery",
    world: "business",
    participants: 8,
    progress: 75,
    timeline: "Launch in 9 days",
    pulse: {
      health: "Healthy",
      score: 84,
      line: "Team coordination is healthy.",
    },
    aiInsight: "Two reviews still pending before freeze.",
    metaLines: ["6 Tasks Completed", "Budget On Track", "2 Reviews Pending"],
    statuses: [
      { label: "Budget On Track", tone: "ok" },
      { label: "2 Reviews Pending", tone: "pending" },
    ],
  },
  {
    id: "team-event",
    title: "Team Event",
    purpose: "Office gathering",
    world: "business",
    participants: 32,
    budgetLabel: "₹85,000",
    progress: 60,
    timeline: "Next Friday",
    pulse: {
      health: "On Track",
      score: 76,
      line: "RSVPs climbing. Venue locked.",
    },
    aiInsight: "Catering headcount needed by Wednesday.",
    statuses: [
      { label: "Venue Booked", tone: "ok" },
      { label: "18 RSVPs", tone: "ok" },
    ],
  },
  {
    id: "family-vacation",
    title: "Family Vacation",
    purpose: "Shared experience",
    world: "group",
    participants: 6,
    budgetLabel: "₹48,000",
    progress: 82,
    timeline: "Today",
    pulse: {
      health: "Healthy",
      score: 88,
      line: "Almost ready to go.",
    },
    aiInsight: "Hotel prices increased. Book transport today.",
    statuses: [
      { label: "Hotel Booked", tone: "ok" },
      { label: "Transport Pending", tone: "pending" },
    ],
    memoryLabel: "42 Photos",
  },
];

/** Fully expanded Goa Trip — teaches the product model alone */
export const goaTripMoment: LivingMoment = {
  id: "goa-trip",
  title: "Goa Trip",
  purpose: "Family Vacation",
  world: "group",
  participants: 6,
  budgetLabel: "₹48,000",
  progress: 82,
  timeline: "Today",
  pulse: {
    health: "Healthy",
    score: 88,
    line: "The trip is nearly ready.",
  },
  aiInsight: "Hotel prices increased. Recommend booking before Friday.",
  statuses: [
    { label: "Hotel Booked", tone: "ok" },
    { label: "Transport Pending", tone: "pending" },
  ],
  memoryLabel: "42 Photos",
};

export const worldIntroMoments: Record<WorldId, LivingMoment[]> = {
  personal: [
    heroCycleMoments[0],
    {
      id: "salary-received",
      title: "Salary Received",
      purpose: "Life Operations",
      world: "personal",
      progress: 100,
      timeline: "Today",
      budgetLabel: "₹92,000 In",
      pulse: {
        health: "Healthy",
        score: 92,
        line: "Income landed. Essentials covered.",
      },
      aiInsight: "Route ₹8,000 to Emergency Fund while balance is high.",
      statuses: [{ label: "Recovery Updated", tone: "ok" }],
    },
    {
      id: "future-goal",
      title: "Future Goal",
      purpose: "Dream building",
      world: "personal",
      budgetLabel: "₹5,00,000",
      progress: 18,
      timeline: "Year 1 of 4",
      pulse: {
        health: "On Track",
        score: 70,
        line: "First contribution logged.",
      },
      aiInsight: "Set a monthly auto-contribution to stay on pace.",
    },
  ],
  group: [
    goaTripMoment,
    {
      id: "group-wedding",
      title: "Wedding",
      purpose: "Family celebration",
      world: "group",
      participants: 24,
      budgetLabel: "₹4,50,000",
      progress: 54,
      timeline: "6 weeks",
      pulse: {
        health: "Needs attention",
        score: 62,
        line: "Vendor timeline needs confirmation.",
      },
      aiInsight: "Catering deposit due Friday.",
      statuses: [
        { label: "Venue Confirmed", tone: "ok" },
        { label: "Invites Pending", tone: "pending" },
      ],
    },
    {
      id: "apartment-living",
      title: "Apartment Living",
      purpose: "Shared home",
      world: "group",
      participants: 4,
      budgetLabel: "₹62,000 / mo",
      progress: 90,
      timeline: "This month",
      pulse: {
        health: "Healthy",
        score: 90,
        line: "Essentials covered. Duties rotated.",
      },
      aiInsight: "Electricity bill is due in 3 days.",
      statuses: [
        { label: "Rent Paid", tone: "ok" },
        { label: "Groceries Pending", tone: "pending" },
      ],
    },
  ],
  business: [
    heroCycleMoments[4],
    {
      id: "vendor-procurement",
      title: "Vendor Procurement",
      purpose: "Operations",
      world: "business",
      participants: 5,
      budgetLabel: "₹1,20,000",
      progress: 45,
      timeline: "PO open",
      pulse: {
        health: "Needs attention",
        score: 58,
        line: "Two vendor quotes awaiting review.",
      },
      aiInsight: "Approve quote B before mid-week cutoff.",
      statuses: [
        { label: "3 Quotes In", tone: "ok" },
        { label: "Approval Pending", tone: "pending" },
      ],
    },
    {
      id: "startup-launch",
      title: "Startup Launch",
      purpose: "Go-to-market",
      world: "business",
      participants: 11,
      budgetLabel: "₹3,40,000",
      progress: 67,
      timeline: "T-minus 14 days",
      pulse: {
        health: "On Track",
        score: 80,
        line: "Launch checklist is moving.",
      },
      aiInsight: "Press kit still missing final screenshots.",
      statuses: [
        { label: "Landing Live", tone: "ok" },
        { label: "Press Pending", tone: "pending" },
      ],
    },
  ],
};

export const liveActivityMoments = [
  "Goa Trip",
  "Birthday",
  "Emergency Fund",
  "Startup Launch",
  "Wedding",
  "Apartment Budget",
  "Home Renovation",
  "Team Event",
  "School Admission",
  "Festival Planning",
  "Medical Recovery",
  "Office Event",
];

export const scatteredTools = [
  "Calendar",
  "WhatsApp",
  "Excel",
  "Photos",
  "Splitwise",
  "UPI",
  "Email",
];

export const flywheelStages = [
  "Read Philosophy",
  "Understand Moments",
  "Create Moment",
  "Invite People",
  "Coordinate Life",
  "Create Memories",
  "AI Learns",
  "Future Moments Become Better",
  "Repeat",
];

export const lifeJourneyStages = [
  { name: "Intent", description: "Why this moment exists." },
  { name: "Create Moment", description: "Give it a living place." },
  { name: "Invite People", description: "Bring the right people in." },
  { name: "Plan Together", description: "Align the path forward." },
  { name: "Contribute", description: "Money, time, and care." },
  { name: "Coordinate", description: "Keep everyone in sync." },
  { name: "Complete", description: "Reach the finish together." },
  { name: "Capture Memory", description: "Keep what mattered." },
  { name: "Learn", description: "Carry insight forward." },
  { name: "Next Moment", description: "Life continues." },
];

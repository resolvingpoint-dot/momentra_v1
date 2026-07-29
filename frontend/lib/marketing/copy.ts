/** Momentra marketing copy — experience-first, moment-centric positioning */

export const siteMeta = {
  title: "Momentra — Life Happens in Moments",
  description:
    "Momentra is a living operating system for life—helping you plan, coordinate, and remember personal, group, and business moments.",
  keywords: [
    "Momentra",
    "Life Happens in Moments",
    "Moment-centric platform",
    "Personal moments",
    "Group coordination",
    "Shared financial moments",
    "Business moments",
    "Financial coordination platform",
    "Moment management",
    "Group planning app",
  ],
};

export const nav = {
  links: [
    { label: "Home", href: "/" },
    { label: "Personal", href: "/personal" },
    { label: "Group", href: "/group" },
    { label: "Business", href: "/business" },
    { label: "How Moments Work", href: "/how-moments-work" },
    { label: "Begin the Journey", href: "/book" },
  ],
  primaryCta: { label: "Start a Moment", href: "/app", event: "start_a_moment" },
  secondaryCta: { label: "Open the App", href: "/app", event: "open_app" },
};

export const hero = {
  headline: "Every important part of life is a moment.",
  momentTypes: [
    "Trips.",
    "Birthdays.",
    "Dreams.",
    "Responsibilities.",
    "Families.",
    "Businesses.",
  ],
  supporting:
    "Momentra helps you plan, coordinate, and remember every one of them.",
  primaryCta: {
    label: "Start Your First Moment",
    href: "/app",
    event: "start_first_moment",
  },
  secondaryCta: {
    label: "See How Moments Work",
    href: "/how-moments-work",
    event: "see_how_moments_work",
  },
  tertiary: {
    label: "Begin the Journey — Life Happens in Moments",
    href: "/book",
    event: "read_the_book",
  },
};

export const philosophy = {
  heading: "Technology should understand moments, not just transactions.",
  body: "For decades, financial technology organized life around transactions, accounts, categories, and budgets. But life never happened that way.",
  lines: [
    "Life happens in birthdays.",
    "In journeys.",
    "In homes.",
    "In goals.",
    "In responsibilities.",
    "In teams.",
    "In communities.",
    "In new beginnings.",
  ],
  closing: "Money moves through these moments. Momentra begins with the moment itself.",
};

export const whatIsAMoment = {
  heading: "A moment is more than an expense.",
  supporting:
    "In Momentra, a moment is a living space for something happening in your life.",
  facets: [
    "Purpose",
    "People",
    "Money",
    "Timeline",
    "Progress",
    "Memory",
    "AI Guidance",
  ],
  body: "Instead of scattering these across payment apps, chats, notes, spreadsheets, and memories, Momentra keeps them together from beginning to completion.",
  phrase: "One moment. One shared context. One place to understand what is happening.",
};

export const oneRealMoment = {
  eyebrow: "One Real Moment",
  heading: "See a moment come alive.",
  supporting:
    "Everything that matters about a trip—people, money, plans, pulse, memory, and guidance—lives in one place.",
};

export const lifeJourney = {
  heading: "Life doesn’t happen in transactions.",
  subheading: "It happens in moments.",
  supporting:
    "Momentra is a lifecycle platform—present from the first intent to the next beginning.",
};

export const scatteredStory = {
  heading: "We built software around the wrong thing.",
  supporting: "Life was scattered across tools that never talked to each other.",
  destination: "Everything flows into Momentra",
  result: "One Living Moment",
};

export const liveActivity = {
  heading: "Life is happening right now.",
  supporting: "Moments unfolding across personal goals, shared plans, and teams.",
  countLabel: "moments active today",
  // Default placeholder for testing. Override with NEXT_PUBLIC_MARKETING_ACTIVE_MOMENTS.
  count: "4,286",
};

export const flywheel = {
  heading: "The Momentra flywheel",
  supporting:
    "Philosophy becomes product. Product becomes memory. Memory makes the next moment better.",
};

export type WorldId = "personal" | "group" | "business";

export const worlds = {
  personal: {
    id: "personal" as const,
    label: "Personal",
    heading: "Your life has a rhythm.",
    supporting:
      "Personal moments help you organize the responsibilities, goals, routines, and transitions that shape your everyday life.",
    examples: [
      "Life Operations",
      "Emergency Fund",
      "Future Building",
      "New Home",
      "Education Plan",
      "Lifestyle Reset",
      "Personal Goal",
      "Emotional Security",
      "Custom Moment",
    ],
    featured: {
      title: "Life Operations",
      copy: "Bring income, essentials, commitments, recovery, and everyday rhythm into one living view.",
    },
    lifecycle: [
      "Define your rhythm and income",
      "Organize essentials and commitments",
      "Review and activate",
      "See the moment live",
      "Capture progress and learning",
    ],
    emotional:
      "Your finances are not separate from your life. They are part of how your life is taking shape.",
    cta: {
      label: "Explore Personal Moments",
      href: "/personal",
      event: "explore_personal",
    },
    mockup: {
      title: "Life Operations",
      subtitle: "Essentials · Commitments · Rhythm",
      pulse: [
        "Current rhythm: Steady",
        "What needs attention: 1 action",
        "Upcoming commitments: 2",
        "Progress toward stability",
      ],
      live: [
        "Recent recovery noted",
        "Essential payment completed",
        "Income received",
        "Commitment updated",
        "Personal note added",
      ],
      memory: [
        "What changed this month",
        "Decisions made",
        "Progress achieved",
        "Patterns learned",
      ],
      highlight: [
        "Essentials on track",
        "Two commitments upcoming",
        "Recovery improved",
        "One action needs attention",
      ],
    },
  },
  group: {
    id: "group" as const,
    label: "Group",
    heading: "The best moments are rarely lived alone.",
    supporting:
      "Group moments bring people, plans, contributions, responsibilities, and shared progress into one place.",
    examples: [
      "Shared Experience",
      "Friends Trip",
      "Shared Purchase",
      "Shared Living",
      "Shared Goal",
      "Birthday Gift Pool",
      "Community Coordination",
      "Family Celebration",
      "Custom Moment",
    ],
    featured: {
      title: "Goa Trip",
      copy: "Bring the people, plan, budget, responsibilities, contributions, updates, and memories of the trip into one shared moment.",
    },
    lifecycle: [
      "Create the experience",
      "Invite participants",
      "Define roles and responsibilities",
      "Organize contributions and shared plans",
      "Follow live progress",
      "Adjust as the group changes",
      "Complete and remember the moment",
    ],
    roles: ["Trip Lead", "Planner", "Explorer", "Budget Keeper", "Traveller"],
    emotional:
      "Shared moments become difficult when information is scattered. Momentra gives everyone one place to understand what is happening.",
    cta: {
      label: "Explore Group Moments",
      href: "/group",
      event: "explore_group",
    },
    mockup: {
      title: "Goa Trip",
      subtitle: "6 participants · Planning complete",
      pulse: [
        "Contributions 74%",
        "Hotel decision pending",
        "Next milestone in 4 days",
        "Travel plan on track",
      ],
      live: [
        "Santosh added a travel option",
        "Aarna completed her contribution",
        "Hotel budget updated",
        "Two participants confirmed",
        "Travel plan moved to the next milestone",
        "A memory was added",
      ],
      memory: [
        "Decisions the group made",
        "What the trip taught us",
        "Moments worth keeping",
      ],
      highlight: [
        "6 participants",
        "Planning complete",
        "Contributions 74%",
        "Hotel decision pending",
      ],
    },
  },
  business: {
    id: "business" as const,
    label: "Business",
    heading: "Businesses move through moments too.",
    supporting:
      "Every project, campaign, team operation, event, and launch has people, money, timelines, responsibilities, risks, and decisions.",
    examples: [
      "Team Operations",
      "Project Spend",
      "Event Operations",
      "Startup Runway",
      "Department Budget",
      "Vendor and Procurement",
      "Product Launch",
      "Marketing Campaign",
      "Custom Moment",
    ],
    featured: {
      title: "Q2 Campaign",
      copy: "Bring budget, owners, approvals, activities, milestones, risks, and live progress together inside one business moment.",
    },
    lifecycle: [
      "Define the operational intent",
      "Set the structure and financial scope",
      "Add people and responsibilities",
      "Establish governance",
      "Activate the moment",
      "Monitor activity and risks live",
      "Close with organizational memory",
    ],
    emotional:
      "Businesses do not operate through isolated transactions. They operate through coordinated moments.",
    cta: {
      label: "Explore Business Moments",
      href: "/business",
      event: "explore_business",
    },
    mockup: {
      title: "Q2 Campaign",
      subtitle: "Budget · Activities · Approvals",
      pulse: [
        "72% budget used",
        "Three activities active",
        "One approval pending",
        "Timeline health: Stable",
      ],
      live: [
        "Campaign activity added",
        "Budget checkpoint reached",
        "Approval requested",
        "Vendor payment recorded",
        "Risk raised",
        "Team update posted",
        "Milestone completed",
      ],
      memory: [
        "What the campaign achieved",
        "Decisions that shaped outcomes",
        "Learning for the next quarter",
      ],
      highlight: [
        "72% budget used",
        "Three activities active",
        "One approval pending",
        "Timeline health: Stable",
      ],
    },
  },
};

export const sharedArchitecture = {
  heading: "Different moments. One living architecture.",
  areas: [
    {
      name: "Pulse",
      description: "Understand the current state of the moment.",
      points: ["Health", "Progress", "What needs attention", "What comes next"],
    },
    {
      name: "Moments",
      description: "See every active, upcoming, and completed moment.",
      points: [
        "Active moments",
        "Upcoming plans",
        "Completed history",
        "One clear timeline",
      ],
    },
    {
      name: "Create",
      description: "Turn an intent into a structured moment.",
      points: [
        "Capture intent",
        "Define structure",
        "Assign what matters",
        "Launch the moment",
      ],
    },
    {
      name: "Life",
      description: "See how all your moments are shaping your life.",
      supporting:
        "Life brings Personal, Group, and Business together into one connected view—showing where your time, money, participation, and attention are moving.",
      points: [
        "Personal rhythm",
        "Shared commitments",
        "Business responsibilities",
        "Cross-moment demands",
        "What is changing across your life",
      ],
    },
    {
      name: "Memory",
      description:
        "Preserve what happened, what changed, and what the moment taught you.",
      points: [
        "What happened",
        "What changed",
        "What you learned",
        "What to carry forward",
      ],
    },
  ],
};

export const lifecycle = {
  heading: "A moment does not sit still.",
  supporting:
    "Momentra remains present throughout the full lifecycle of a moment—from the first idea to the final memory.",
  stages: [
    { name: "Intent", description: "Why is this moment being created?" },
    { name: "Structure", description: "What does it need to succeed?" },
    { name: "Participation", description: "Who is involved, and how?" },
    { name: "Activation", description: "When is the moment ready to begin?" },
    { name: "Live Progress", description: "What is happening now?" },
    { name: "Adjustment", description: "What needs to change as life changes?" },
    { name: "Completion", description: "What was achieved?" },
    { name: "Memory", description: "What should be carried forward?" },
  ],
};

export const intelligence = {
  heading: "Moment Intelligence, always present.",
  supporting:
    "AI is not a hidden feature. It lives inside every moment—watching pulse, timeline, funding, and people.",
  helpsWith: [
    "Missing setup information",
    "Contribution gaps",
    "Timeline risk",
    "Spending deviation",
    "Participation imbalance",
    "Upcoming responsibilities",
    "Suggested next steps",
    "Moment health",
    "Post-moment learning",
  ],
  demoInsights: [
    "Book flights before Friday.",
    "Two participants haven’t confirmed.",
    "Budget still healthy.",
  ],
  closing:
    "Momentra does not replace human decisions. It brings the right context forward before the moment loses direction.",
  healthStates: [
    "Healthy",
    "Needs attention",
    "At risk",
    "Back on track",
    "Completed",
  ],
};

export const comparison = {
  heading: "Not transaction-first. Moment-first.",
  traditional: {
    title: "Traditional financial applications",
    points: [
      "Begin with transactions",
      "Separate personal and shared activity",
      "Explain what happened",
      "Organize by categories",
      "End at payment or settlement",
      "Store data without preserving context",
    ],
  },
  momentra: {
    title: "Momentra",
    points: [
      "Begins with intent",
      "Connects people, plans, and money",
      "Works while the moment is unfolding",
      "Organizes by real-life context",
      "Continues through completion and memory",
      "Learns from the full lifecycle",
    ],
  },
};

export const book = {
  eyebrow: "Begin the Journey",
  heading: "The beginning of Momentra.",
  question:
    "Why does technology understand transactions so well, yet understand the moments behind them so poorly?",
  supporting:
    "Life Happens in Moments is not a downloadable brochure. It is where the philosophy starts—and where Momentra begins.",
  bridge: "Read the philosophy. Then live it.",
  bridgeLine: "Begin the journey. See the system. Create your first moment.",
  title: "Life Happens in Moments",
  exploreCta: {
    label: "Read the Philosophy",
    href: "/book",
    event: "read_the_book",
  },
  experienceCta: {
    label: "Experience Momentra",
    href: "/app",
    event: "start_first_moment",
  },
};

export const emotional = {
  lines: [
    "Money remembers the amount.",
    "People remember the moment.",
    "Technology remembered the transaction.",
    "Momentra remembers the whole story.",
  ],
};

export const mosaic = {
  personal: [
    {
      title: "Emergency Fund",
      stage: "Building",
      progress: "On track",
      update: "Contribution added",
    },
    {
      title: "New Home",
      stage: "Planning",
      progress: "Structure forming",
      update: "Timeline updated",
    },
    {
      title: "Life Operations",
      stage: "Live",
      progress: "Rhythm steady",
      update: "One action needs attention",
    },
    {
      title: "Education Goal",
      stage: "Active",
      progress: "Milestone near",
      update: "Decision pending",
    },
    {
      title: "Personal Reset",
      stage: "Starting",
      progress: "Intent clear",
      update: "First structure set",
    },
  ],
  group: [
    {
      title: "Goa Trip",
      stage: "Planning",
      progress: "74% contributions",
      update: "Hotel decision pending",
      people: "6 people",
    },
    {
      title: "Birthday Gift",
      stage: "Pooling",
      progress: "Almost there",
      update: "Two joined today",
      people: "8 people",
    },
    {
      title: "Shared Living",
      stage: "Live",
      progress: "Essentials covered",
      update: "Responsibility rotated",
      people: "4 people",
    },
    {
      title: "Community Festival",
      stage: "Coordinating",
      progress: "Roles assigned",
      update: "Vendor confirmed",
      people: "12 people",
    },
    {
      title: "Family Celebration",
      stage: "Upcoming",
      progress: "Plan forming",
      update: "Memory space ready",
      people: "9 people",
    },
  ],
  business: [
    {
      title: "Q2 Campaign",
      stage: "Live",
      progress: "72% budget used",
      update: "Approval pending",
    },
    {
      title: "Team Operations",
      stage: "Active",
      progress: "Health: Stable",
      update: "Risk reviewed",
    },
    {
      title: "Product Launch",
      stage: "Activation",
      progress: "Milestones set",
      update: "Owners assigned",
    },
    {
      title: "Event Operations",
      stage: "Live",
      progress: "Vendors on track",
      update: "Checkpoint reached",
    },
    {
      title: "Startup Runway",
      stage: "Monitoring",
      progress: "Runway visible",
      update: "Decision logged",
    },
  ],
};

export const finalCta = {
  heading: "Every life becomes a collection of moments.",
  supporting:
    "The question isn’t whether life happens in moments.",
  close: "The question is— Will yours be remembered?",
  primaryCta: {
    label: "Create Your First Moment",
    href: "/app",
    event: "start_first_moment",
  },
  secondaryCta: {
    label: "Begin the Journey",
    href: "/book",
    event: "read_the_book",
  },
  line: "Personal. Group. Business. One living operating system for life.",
};

export const footer = {
  statement: "Life happens in moments. Momentra helps them move forward.",
  columns: [
    {
      title: "Product",
      links: [
        { label: "Personal", href: "/personal" },
        { label: "Group", href: "/group" },
        { label: "Business", href: "/business" },
        { label: "How Moments Work", href: "/how-moments-work" },
        { label: "Open the App", href: "/app" },
      ],
    },
    {
      title: "Philosophy",
      links: [
        { label: "Begin the Journey", href: "/book" },
        { label: "How Moments Work", href: "/how-moments-work" },
        { label: "Stories", href: "/about" },
        { label: "Journal", href: "/about" },
      ],
    },
    {
      title: "Company",
      links: [
        { label: "About Momentra", href: "/about" },
        { label: "Contact", href: "/contact" },
        { label: "Careers", href: "/contact" },
        { label: "Press", href: "/contact" },
      ],
    },
    {
      title: "Legal",
      links: [
        { label: "Privacy", href: "/privacy" },
        { label: "Terms", href: "/terms" },
        { label: "Data Policy", href: "/data-policy" },
        { label: "Cookies", href: "/cookies" },
      ],
    },
  ],
};

export const pageCopy = {
  personal: {
    title: "Personal Moments — Momentra",
    description:
      "Organize the responsibilities, goals, routines, and transitions that shape your everyday life—without treating life like a budget spreadsheet.",
  },
  group: {
    title: "Group Moments — Momentra",
    description:
      "Bring people, plans, contributions, and shared progress into one place. Coordination first—not bill splitting.",
  },
  business: {
    title: "Business Moments — Momentra",
    description:
      "Coordinate projects, campaigns, launches, and team operations as living moments—not isolated expenses.",
  },
  howMomentsWork: {
    title: "How Moments Work — Momentra",
    description:
      "From intent to memory: experience the Momentra lifecycle and see a living moment unfold.",
  },
  book: {
    title: "Begin the Journey — Life Happens in Moments",
    description:
      "The philosophy behind Momentra. Where the idea begins—and becomes a living operating system for life.",
  },
  about: {
    title: "About Momentra",
    description:
      "Momentra is a moment-centric platform designed around how life actually unfolds.",
  },
  contact: {
    title: "Contact — Momentra",
    description: "Get in touch with the Momentra team.",
  },
  privacy: {
    title: "Privacy Policy — Momentra",
    description:
      "How Momentra collects, uses, shares, and protects your personal information.",
  },
  terms: {
    title: "Terms of Use — Momentra",
    description: "The terms governing your use of Momentra’s websites and services.",
  },
  dataPolicy: {
    title: "Data Policy — Momentra",
    description:
      "How Momentra processes, stores, retains, and governs product and operational data.",
  },
  cookies: {
    title: "Cookies Policy — Momentra",
    description:
      "How Momentra uses cookies, local storage, and similar technologies.",
  },
};

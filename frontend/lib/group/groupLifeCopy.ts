import type { LucideIcon } from "lucide-react";
import {
  Calendar,
  Home,
  ShoppingBag,
  Target,
  Users,
} from "lucide-react";

export type GroupLifeDimension = {
  code: string;
  title: string;
  shortTitle: string;
  whyDescription: string;
  accent: string;
  icon: LucideIcon;
  graphX: number;
  graphY: number;
  pulseDelayMs: number;
};

export const GROUP_LIFE_HERO_SUBTITLE =
  "Activate group moments and Momentra will reveal how participation, contributions, coordination, shared achievements and memories shape your group's evolution.";

export const GROUP_LIFE_PRIMARY_CTA = "Create First Group Moment";
export const GROUP_LIFE_SECONDARY_CTA = "Explore Group Types";
export const GROUP_LIFE_UNLOCKS_TITLE = "Life Intelligence Unlocks";
export const GROUP_LIFE_UNLOCKS_FOOTNOTE =
  "Visualizations will unlock as group data is captured.";
export const GROUP_LIFE_WHY_TITLE = "Why These 5 Dimensions Matter";
export const GROUP_LIFE_LOADING =
  "Loading your group's command center...";
export const GROUP_LIFE_FOOTER_QUOTE =
  "Life is a series of moments. Make them meaningful.";

export const GROUP_LIFE_DIMENSIONS: GroupLifeDimension[] = [
  {
    code: "SHARED_EXPERIENCE",
    title: "Shared Experience",
    shortTitle: "Experience",
    whyDescription: "Creates shared memories and participation.",
    accent: "#FFB598",
    icon: Calendar,
    graphX: 200,
    graphY: 80,
    pulseDelayMs: 0,
  },
  {
    code: "SHARED_PURCHASE",
    title: "Shared Purchase",
    shortTitle: "Purchase",
    whyDescription: "Creates ownership and contribution.",
    accent: "#F97316",
    icon: ShoppingBag,
    graphX: 320,
    graphY: 160,
    pulseDelayMs: 500,
  },
  {
    code: "SHARED_LIVING",
    title: "Shared Living",
    shortTitle: "Living",
    whyDescription: "Creates stability and routine.",
    accent: "#FBBF24",
    icon: Home,
    graphX: 280,
    graphY: 300,
    pulseDelayMs: 1000,
  },
  {
    code: "SHARED_GOAL",
    title: "Shared Goal",
    shortTitle: "Goal",
    whyDescription: "Creates progress and momentum.",
    accent: "#4ADE80",
    icon: Target,
    graphX: 120,
    graphY: 300,
    pulseDelayMs: 1500,
  },
  {
    code: "COMMUNITY_COORDINATION",
    title: "Community Coordination",
    shortTitle: "Community",
    whyDescription: "Creates belonging and engagement.",
    accent: "#818CF8",
    icon: Users,
    graphX: 80,
    graphY: 160,
    pulseDelayMs: 2000,
  },
];

export const GROUP_LIFE_UNLOCKS = [
  "Participation Health",
  "Coordination Health",
  "Contribution Health",
  "Group Growth",
  "Community Strength",
] as const;

export const GROUP_LIFE_ACCENT_BY_TOKEN: Record<string, string> = {
  teal_accent: "#FFB598",
  orange_accent: "#F97316",
  amber_accent: "#FBBF24",
  green_accent: "#4ADE80",
  indigo_accent: "#818CF8",
  purple_accent: "#A855F7",
};

export const GROUP_LIFE_COMMAND_CENTER_TITLE = "Command Center";
export const GROUP_LIFE_COMMAND_CENTER_SUBTITLE =
  "Cross-moment intelligence for participation, contribution, and coordination.";

export const GROUP_LIFE_GRAPH_CENTER = { x: 200, y: 200 } as const;

export const GROUP_LIFE_HERO = {
  minHeightPx: 320,
  viewportFraction: 0.48,
  maxGraphWidthPx: 384,
  hubSizePx: 80,
  glowColor: "rgba(255, 122, 61, 0.12)",
  glowShadow: "0 0 50px rgba(255, 122, 61, 0.25)",
  hubShadow: "0 0 30px rgba(255, 122, 61, 0.35)",
} as const;

export const GROUP_LIFE_MOTION = {
  nodePulseDurationMs: 3000,
  particleLineDurationMs: 10000,
  pulseStaggerMs: 500,
} as const;

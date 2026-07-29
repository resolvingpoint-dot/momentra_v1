import type { LucideIcon } from "lucide-react";
import { Briefcase, Network, Users, Wallet } from "lucide-react";
import type { AppContext } from "./appContext";

export type BottomNavTabId = "pulse" | "moments" | "add" | "life" | "memory";

export type BottomNavTabDef = {
  id: BottomNavTabId;
  label: string;
  iconName: string;
};

export const GROUP_BOTTOM_NAV: BottomNavTabDef[] = [
  { id: "pulse", label: "Pulse", iconName: "sparkles" },
  { id: "moments", label: "Moments", iconName: "book-open" },
  { id: "add", label: "", iconName: "plus" },
  { id: "life", label: "Life", iconName: "radio" },
  { id: "memory", label: "Memory", iconName: "history" },
];

export const PERSONAL_BOTTOM_NAV: BottomNavTabDef[] = [
  { id: "pulse", label: "Pulse", iconName: "activity" },
  { id: "moments", label: "Moments", iconName: "book-open" },
  { id: "add", label: "", iconName: "plus" },
  { id: "life", label: "Life", iconName: "heart" },
  { id: "memory", label: "Memory", iconName: "history" },
];

export const BUSINESS_BOTTOM_NAV: BottomNavTabDef[] = [
  { id: "pulse", label: "Pulse", iconName: "line-chart" },
  { id: "moments", label: "Moments", iconName: "layout-grid" },
  { id: "add", label: "", iconName: "plus" },
  { id: "life", label: "Life", iconName: "zap" },
  { id: "memory", label: "Memory", iconName: "brain" },
];

export function contextDisplayName(context: AppContext): string {
  switch (context) {
    case "personal":
      return "My Money";
    case "group":
      return "Group";
    case "business":
      return "Business";
    case "circle":
      return "Circle";
  }
}

/** Top context switcher icons — keep in sync with Android / iOS mappings. */
export function contextIcon(context: AppContext): LucideIcon {
  switch (context) {
    case "personal":
      return Wallet;
    case "group":
      return Users;
    case "business":
      return Briefcase;
    case "circle":
      return Network;
  }
}

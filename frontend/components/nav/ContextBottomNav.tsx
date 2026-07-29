"use client";

import type { BottomNavTabId } from "@/lib/bottomNavTabs";
import { ContextTabBar } from "@/components/nav/ContextTabBar";

type NavVariant = "personal" | "group" | "business";

type ContextBottomNavProps = {
  variant: NavVariant;
  selectedTab: BottomNavTabId;
  onTabSelect: (tab: BottomNavTabId) => void;
  onCreateMoment: () => void;
};

/**
 * Bottom navigation bar - visible on all screen sizes.
 * Sticky at bottom with thumb-reachable tabs.
 */
export function ContextBottomNav(props: ContextBottomNavProps) {
  return <ContextTabBar {...props} layout="bottom" />;
}

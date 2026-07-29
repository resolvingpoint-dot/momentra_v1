"use client";

import {
  Activity,
  BookOpen,
  Brain,
  Heart,
  History,
  LayoutGrid,
  Lightbulb,
  LineChart,
  Plus,
  Radio,
  Sparkles,
  Zap,
  type LucideIcon,
} from "lucide-react";
import {
  BUSINESS_BOTTOM_NAV,
  GROUP_BOTTOM_NAV,
  PERSONAL_BOTTOM_NAV,
  type BottomNavTabDef,
  type BottomNavTabId,
} from "@/lib/bottomNavTabs";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

const ICONS: Record<string, LucideIcon> = {
  sparkles: Sparkles,
  "book-open": BookOpen,
  plus: Plus,
  radio: Radio,
  history: History,
  heart: Heart,
  activity: Activity,
  lightbulb: Lightbulb,
  "line-chart": LineChart,
  "layout-grid": LayoutGrid,
  zap: Zap,
  brain: Brain,
};

type NavVariant = "personal" | "group" | "business";

const TABS_BY_VARIANT: Record<NavVariant, BottomNavTabDef[]> = {
  personal: PERSONAL_BOTTOM_NAV,
  group: GROUP_BOTTOM_NAV,
  business: BUSINESS_BOTTOM_NAV,
};

type ContextTabBarProps = {
  variant: NavVariant;
  selectedTab: BottomNavTabId;
  onTabSelect: (tab: BottomNavTabId) => void;
  onCreateMoment: () => void;
  layout: "bottom" | "header";
  className?: string;
};

export function ContextTabBar({
  variant,
  selectedTab,
  onTabSelect,
  onCreateMoment,
  layout,
  className = "",
}: ContextTabBarProps) {
  const tokens = useThemeTokens();
  const tabs = TABS_BY_VARIANT[variant];

  if (layout === "bottom") {
    return (
      <nav
        className={`fixed inset-x-0 bottom-0 z-40 border-t ${className}`}
        style={{
          background: `color-mix(in srgb, ${tokens.colors.surfaceContainer} 94%, transparent)`,
          borderColor: "rgba(255,255,255,0.1)",
          paddingBottom: "env(safe-area-inset-bottom)",
        }}
      >
        <div
          className="flex h-20 w-full items-center justify-around"
          style={{ minHeight: tokens.spacing.bottomNavHeight }}
        >
          {tabs.map((tab) => (
            <BottomTabButton
              key={tab.id}
              tab={tab}
              isSelected={selectedTab === tab.id}
              onTabSelect={onTabSelect}
              onCreateMoment={onCreateMoment}
              tokens={tokens}
            />
          ))}
        </div>
      </nav>
    );
  }

  return (
    <nav
      className={`shrink-0 border-b ${className}`}
      style={{
        background: `color-mix(in srgb, ${tokens.colors.surfaceContainer} 94%, transparent)`,
        borderColor: "rgba(255,255,255,0.1)",
      }}
    >
      <div className="mx-auto flex h-14 w-full max-w-[1080px] items-center gap-1 px-4 md:px-20">
        {tabs.map((tab) => {
          const Icon = ICONS[tab.iconName] ?? Plus;
          const isAdd = tab.id === "add";
          const isSelected = selectedTab === tab.id;

          if (isAdd) {
            return (
              <button
                key={tab.id}
                type="button"
                onClick={onCreateMoment}
                aria-label="Create moment"
                className="mx-2 flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold shadow-md transition-transform hover:scale-[1.02] active:scale-95"
                style={{
                  background: tokens.colors.primaryContainer,
                  color: tokens.colors.brandOnPrimary,
                }}
              >
                <Plus className="h-4 w-4" strokeWidth={2.5} />
                Create
              </button>
            );
          }

          const color = isSelected
            ? tokens.colors.brandPrimary
            : tokens.colors.textSecondary;

          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabSelect(tab.id)}
              className="flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors"
              style={{
                color,
                background: isSelected
                  ? `color-mix(in srgb, ${tokens.colors.primaryContainer} 25%, transparent)`
                  : "transparent",
              }}
            >
              <Icon className="h-4 w-4" strokeWidth={isSelected ? 2.5 : 2} />
              {tab.label}
            </button>
          );
        })}
      </div>
    </nav>
  );
}

function BottomTabButton({
  tab,
  isSelected,
  onTabSelect,
  onCreateMoment,
  tokens,
}: {
  tab: BottomNavTabDef;
  isSelected: boolean;
  onTabSelect: (tab: BottomNavTabId) => void;
  onCreateMoment: () => void;
  tokens: ReturnType<typeof useThemeTokens>;
}) {
  const Icon = ICONS[tab.iconName] ?? Plus;
  const isAdd = tab.id === "add";
  const color = isSelected
    ? tokens.colors.brandPrimary
    : tokens.colors.textSecondary;

  if (isAdd) {
    return (
      <button
        type="button"
        onClick={onCreateMoment}
        aria-label="Create moment"
        className="flex h-12 w-12 items-center justify-center rounded-full shadow-md"
        style={{
          background: tokens.colors.primaryContainer,
          color: tokens.colors.brandOnPrimary,
        }}
      >
        <Plus className="h-6 w-6" strokeWidth={2.5} />
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={() => onTabSelect(tab.id)}
      className="flex flex-1 flex-col items-center gap-0.5 py-2"
      style={{ color }}
    >
      <Icon className="h-6 w-6" strokeWidth={isSelected ? 2.5 : 2} />
      {tab.label ? (
        <span className="text-[11px] font-medium">{tab.label}</span>
      ) : null}
      {isSelected ? (
        <span
          className="mt-0.5 h-1 w-1 rounded-full"
          style={{ background: tokens.colors.brandPrimary }}
        />
      ) : null}
    </button>
  );
}

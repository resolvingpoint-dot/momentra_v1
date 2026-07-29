"use client";

import { useEffect, useState } from "react";
import { CreateEmpty as GroupCreateEmpty } from "@/components/group/empty/create/CreateEmpty";
import { LifeEmpty as GroupLifeEmpty } from "@/components/group/empty/life/LifeEmpty";
import { MemoryEmpty as GroupMemoryEmpty } from "@/components/group/empty/memory/MemoryEmpty";
import { MomentsEmpty as GroupMomentsEmpty } from "@/components/group/empty/moments/MomentsEmpty";
import { PulseEmpty as GroupPulseEmpty } from "@/components/group/empty/pulse/PulseEmpty";
import { QuickAddComingSoon } from "@/components/group/shared/QuickAddComingSoon";
import { ContextBottomNav } from "@/components/nav/ContextBottomNav";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { BottomNavTabId } from "@/lib/bottomNavTabs";
import { GROUP_CREATE_OPEN_EVENT } from "@/lib/groupShellEvents";
import { MomentraAnalytics } from "@/lib/analytics";
import { resolveScreenName, type ScreenOverlay } from "@/lib/analyticsScreens";

type GroupHomePlaceholderProps = {
  title: string;
};

export function GroupHomePlaceholder({ title: _title }: GroupHomePlaceholderProps) {
  const [selectedTab, setSelectedTab] = useState<BottomNavTabId>("pulse");
  const [previousTab, setPreviousTab] = useState<BottomNavTabId>("pulse");
  const [showCreateOverlay, setShowCreateOverlay] = useState(false);
  const [showQuickAddSheet, setShowQuickAddSheet] = useState(false);
  const tokens = useThemeTokens();
  const bottomPadding = tokens.spacing.bottomNavHeight + 16;
  const appContext = "group";

  const screenOverlay: ScreenOverlay = showCreateOverlay
    ? "create"
    : showQuickAddSheet
      ? "quick_add"
      : null;

  const visibleTab = selectedTab === "add" ? previousTab : selectedTab;

  useEffect(() => {
    const openCreate = () => setShowCreateOverlay(true);
    window.addEventListener(GROUP_CREATE_OPEN_EVENT, openCreate);
    return () => window.removeEventListener(GROUP_CREATE_OPEN_EVENT, openCreate);
  }, []);

  useEffect(() => {
    MomentraAnalytics.logScreen(
      resolveScreenName("group", selectedTab, screenOverlay, previousTab),
      "group",
    );
  }, [selectedTab, previousTab, screenOverlay]);

  function handleTabSelect(tab: BottomNavTabId) {
    if (tab === "add") {
      setShowQuickAddSheet(true);
      return;
    }
    MomentraAnalytics.logCustomEvent("tab_select", {
      app_context: appContext,
      tab,
    });
    setPreviousTab(tab);
    setSelectedTab(tab);
  }

  function openCreateOverlay() {
    MomentraAnalytics.logCustomEvent("create_moment_tap", {
      app_context: appContext,
      screen: resolveScreenName("group", selectedTab, null, previousTab),
    });
    setShowCreateOverlay(true);
  }

  function renderTabContent() {
    switch (visibleTab) {
      case "moments":
        return <GroupMomentsEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
      case "life":
        return <GroupLifeEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
      case "memory":
        return <GroupMemoryEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
      default:
        return <GroupPulseEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
    }
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col" style={{ background: tokens.colors.background }}>
      <div className="flex min-h-0 flex-1 flex-col">{renderTabContent()}</div>
      <ContextBottomNav
        variant="group"
        selectedTab={visibleTab}
        onTabSelect={handleTabSelect}
        onCreateMoment={openCreateOverlay}
      />
      {showQuickAddSheet ? <QuickAddComingSoon onClose={() => setShowQuickAddSheet(false)} /> : null}
      {showCreateOverlay ? (
        <GroupCreateEmpty onCreateMoment={openCreateOverlay} onClose={() => setShowCreateOverlay(false)} />
      ) : null}
    </div>
  );
}

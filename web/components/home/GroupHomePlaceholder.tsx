"use client";



import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";

import { CreateEmpty as GroupCreateEmpty } from "@/components/group/empty/create/CreateEmpty";

import { LifeEmpty as GroupLifeEmpty } from "@/components/group/empty/life/LifeEmpty";

import { MemoryEmpty as GroupMemoryEmpty } from "@/components/group/empty/memory/MemoryEmpty";

import { MomentsEmpty as GroupMomentsEmpty } from "@/components/group/empty/moments/MomentsEmpty";

import { PulseEmpty as GroupPulseEmpty } from "@/components/group/empty/pulse/PulseEmpty";

import { GroupLivingSetup } from "@/components/group/setup/GroupLivingSetup";
import { GroupPurchaseSetup } from "@/components/group/setup/GroupPurchaseSetup";
import { GroupTripSetup } from "@/components/group/setup/GroupTripSetup";

import { GroupMomentHeader } from "@/components/group/shared/GroupMomentHeader";
import { MomentInviteSheet } from "@/components/shared/MomentInviteSheet";
import type { GroupMomentSwitcherOption } from "@/components/group/shared/groupMomentRouting";

import {

  reconcileSelectedGroupMomentType,

  resolveGroupMomentManageContext,

  resolveGroupMomentSwitcherOptions,

  switcherOptionForType,

} from "@/components/group/shared/groupMomentRouting";

import { ContextBottomNav } from "@/components/nav/ContextBottomNav";

import { MomentManageSheet } from "@/components/shared/MomentManageSheet";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { toast } from "@/lib/toast/momentraToastStore";
import { groupActivationSuccessMessage } from "@/lib/toast/activationToastCopy";

import type { BottomNavTabId } from "@/lib/bottomNavTabs";

import {
  setSelectedGroupMomentTypeCode,
  type GroupMomentTypeCode,
} from "@/lib/group/groupMomentSession";

import { SetupRepository } from "@/repositories/SetupRepository";

import { ExperiencePulse } from "@/components/group/active/experience/ExperiencePulse";

import { ActiveMoments } from "@/components/group/active/experience/ActiveMoments";

import { ActiveMemory } from "@/components/group/active/experience/ActiveMemory";

import { SharedPurchasePulse } from "@/components/group/active/purchase/SharedPurchasePulse";

import { SharedPurchaseMoments } from "@/components/group/active/purchase/SharedPurchaseMoments";

import { SharedLivingPulse } from "@/components/group/active/living/SharedLivingPulse";
import { LivingActivityScreen } from "@/components/group/active/living/activity/LivingActivityScreen";
import { LivingActivityEditSheet } from "@/components/group/active/living/activity/LivingActivityEditSheet";
import {
  deleteTripActivity,
  getTripActivityDetail,
  listTripActivity,
  patchTripActivity,
} from "@/lib/api/group";

import { SharedLivingMoments } from "@/components/group/active/living/SharedLivingMoments";

import { SharedPurchaseMemory } from "@/components/group/active/purchase/SharedPurchaseMemory";

import { SharedLivingMemory } from "@/components/group/active/living/SharedLivingMemory";

import { GroupLifeCommandCenter } from "@/components/group/life/GroupLifeCommandCenter";

import { GroupActiveQuickAddOverlay } from "@/components/group/quickadd/GroupActiveQuickAddOverlay";

import {

  isActiveScreen,

  isEmptyScreen,

  isSetupScreen,

  resolveScreen,

} from "@/lib/screenResolver";

import { GROUP_CREATE_OPEN_EVENT, GROUP_OPEN_MOMENT_EVENT } from "@/lib/groupShellEvents";
import { LIFE360_SELECT_LIFE_TAB_EVENT } from "@/lib/life360ShellEvents";

import { MomentraAnalytics } from "@/lib/analytics";

import { resolveScreenName, type ScreenOverlay } from "@/lib/analyticsScreens";

import { useBootstrapStore } from "@/hooks/useBootstrap";

import { useGroupMomentSession } from "@/hooks/useGroupMomentSession";

import { GroupRepository } from "@/repositories/GroupRepository";
import {
  MomentLifecycleError,
  runMomentLifecycle,
  type LifecycleInventoryItem,
} from "@/lib/lifecycle/MomentLifecycleCoordinator";

import { invalidateGroupTabCaches, useTripMomentStream } from "@/hooks/useGroupTabCache";
import {
  applyGroupLifecyclePatch,
  ensureGroupSession,
  patchGroupDraftInStore,
  patchGroupMomentActivated,
  patchGroupMomentInInventory,
  refreshGroupSessionInventory,
  setGroupSelection,
  softRefreshGroupSession,
  useGroupSessionStore,
} from "@/stores/groupSessionStore";



type GroupHomePlaceholderProps = {

  title: string;

};



type GroupCreateType = GroupMomentTypeCode;



const TAB_LABELS: Record<BottomNavTabId, string> = {
  pulse: "Pulse",
  moments: "Moments",
  memory: "Memory",
  life: "Life",
  add: "Add",
};



export function GroupHomePlaceholder({ title: _title }: GroupHomePlaceholderProps) {

  const [selectedTab, setSelectedTab] = useState<BottomNavTabId>("pulse");

  const [previousTab, setPreviousTab] = useState<BottomNavTabId>("pulse");

  const [showCreateOverlay, setShowCreateOverlay] = useState(false);

  const [setupMomentId, setSetupMomentId] = useState<string | null>(null);

  const [setupMomentType, setSetupMomentType] = useState<GroupCreateType | null>(null);

  const [creating, setCreating] = useState(false);

  const [createError, setCreateError] = useState<string | null>(null);

  const groupSession = useGroupSessionStore();
  const sessionBootstrap = groupSession.session;
  const activeMomentId = groupSession.selectedMomentId;
  const activeMomentType = groupSession.selectedMomentType;
  const sessionLoaded = groupSession.lastLoadedAt != null || groupSession.error != null;
  const draftMomentId =
    sessionBootstrap?.has_draft && sessionBootstrap.draft_moment_id
      ? sessionBootstrap.draft_moment_id
      : null;
  const draftMomentType = (sessionBootstrap?.draft_moment_type ??
    null) as GroupCreateType | null;

  const [showQuickAdd, setShowQuickAdd] = useState(false);
  const [quickAddActionId, setQuickAddActionId] = useState<string | null>(null);
  const openQuickAdd = useCallback((actionId?: string) => {
    setQuickAddActionId(actionId ?? null);
    setShowQuickAdd(true);
  }, []);
  const closeQuickAdd = useCallback(() => {
    setShowQuickAdd(false);
    setQuickAddActionId(null);
  }, []);
  const [tripMomentsReloadKey, setTripMomentsReloadKey] = useState(0);
  const bumpTripReload = useCallback(() => {
    setTripMomentsReloadKey((k) => k + 1);
  }, []);
  useTripMomentStream(
    activeMomentId,
    bumpTripReload,
    Boolean(activeMomentId) &&
      (activeMomentType === "SHARED_EXPERIENCE" ||
        activeMomentType === "SHARED_PURCHASE" ||
        activeMomentType === "SHARED_LIVING"),
  );
  const [quickAddSuccess, setQuickAddSuccess] = useState<string | null>(null);
  const [showLivingActivity, setShowLivingActivity] = useState(false);
  const [editingLivingActivity, setEditingLivingActivity] = useState<{
    id: string;
    eventType: string;
  } | null>(null);
  const [livingActivityReloadToken, setLivingActivityReloadToken] = useState(0);

  const [showManageSheet, setShowManageSheet] = useState(false);
  const [inviteMoment, setInviteMoment] = useState<{
    momentId: string;
    label: string;
  } | null>(null);

  const selectedMomentTypeCode = useGroupMomentSession();

  const tokens = useThemeTokens();

  const bottomPadding = tokens.spacing.bottomNavHeight + 16;
  useEffect(() => {
    if (!quickAddSuccess) return;
    const timeout = window.setTimeout(() => setQuickAddSuccess(null), 2200);
    return () => window.clearTimeout(timeout);
  }, [quickAddSuccess]);

  // Open the joined moment after invite accept (QR scan or /invite/[token]).
  useEffect(() => {
    const onInviteJoined = (event: Event) => {
      const detail = (event as CustomEvent<{ moment_id?: string; moment_type?: string | null }>)
        .detail;
      const momentId = detail?.moment_id?.trim();
      if (!momentId) return;
      const typeFromResult = (detail.moment_type || "").toUpperCase();
      // Business joins are handled via openBusinessMomentAndPulse — do not map into Group.
      if (
        typeFromResult.includes("BUSINESS") ||
        typeFromResult.startsWith("TEAM_") ||
        typeFromResult === "ORG" ||
        typeFromResult.includes("OPERATIONS")
      ) {
        return;
      }
      const typeCode = (typeFromResult.includes("PURCHASE")
        ? "SHARED_PURCHASE"
        : typeFromResult.includes("LIVING")
          ? "SHARED_LIVING"
          : typeFromResult.includes("EXPERIENCE") || typeFromResult.includes("TRIP")
            ? "SHARED_EXPERIENCE"
            : "SHARED_EXPERIENCE") as GroupMomentTypeCode;
      setGroupSelection(typeCode, momentId);
      setSelectedTab("pulse");
      void softRefreshGroupSession();
    };
    const onOpenMoment = (event: Event) => {
      const detail = (event as CustomEvent<{ moment_id?: string; moment_type?: string | null }>)
        .detail;
      const momentId = detail?.moment_id?.trim();
      if (!momentId) return;
      const typeFromResult = (detail.moment_type || "").toUpperCase();
      const typeCode = (typeFromResult.includes("PURCHASE")
        ? "SHARED_PURCHASE"
        : typeFromResult.includes("LIVING")
          ? "SHARED_LIVING"
          : "SHARED_EXPERIENCE") as GroupMomentTypeCode;
      setGroupSelection(typeCode, momentId);
      setSelectedTab("pulse");
    };
    window.addEventListener("momentra:invite-joined", onInviteJoined);
    window.addEventListener(GROUP_OPEN_MOMENT_EVENT, onOpenMoment);
    return () => {
      window.removeEventListener("momentra:invite-joined", onInviteJoined);
      window.removeEventListener(GROUP_OPEN_MOMENT_EVENT, onOpenMoment);
    };
  }, []);


  const appContext = "group";

  const bootstrapState = useBootstrapStore();

  const bootstrap = bootstrapState.data;

  const visibleTab = selectedTab === "add" ? previousTab : selectedTab;

  // Lazy keep-alive: mount selected tab first; keep after first visit; never auto-mount off-tab.
  const [mountedTabs, setMountedTabs] = useState(() => new Set([visibleTab]));

  useEffect(() => {
    setMountedTabs((prev) => {
      if (prev.has(visibleTab)) return prev;
      const next = new Set(prev);
      next.add(visibleTab);
      return next;
    });
    try {
      performance.mark("selected-tab-visible");
    } catch {
      /* ignore */
    }
  }, [visibleTab]);

  const tabResolved = resolveScreen("group", visibleTab, bootstrap);



  const screenOverlay: ScreenOverlay = showCreateOverlay || setupMomentId ? "create" : null;



  const momentSwitcherOptions = useMemo(

    () => resolveGroupMomentSwitcherOptions(sessionBootstrap),

    [sessionBootstrap],

  );



  const manageContext = useMemo(

    () => resolveGroupMomentManageContext(selectedMomentTypeCode, sessionBootstrap),

    [selectedMomentTypeCode, sessionBootstrap],

  );



  const applySelectedMoment = useCallback((typeCode: GroupMomentTypeCode) => {

    const option = switcherOptionForType(momentSwitcherOptions, typeCode);

    if (option) {

      setGroupSelection(option.typeCode, option.momentId);

    }

  }, [momentSwitcherOptions]);



  useEffect(() => {
    const openCreate = () => setShowCreateOverlay(true);
    const selectLife = () => {
      setSelectedTab("life");
    };
    window.addEventListener(GROUP_CREATE_OPEN_EVENT, openCreate);
    window.addEventListener(LIFE360_SELECT_LIFE_TAB_EVENT, selectLife);
    return () => {
      window.removeEventListener(GROUP_CREATE_OPEN_EVENT, openCreate);
      window.removeEventListener(LIFE360_SELECT_LIFE_TAB_EVENT, selectLife);
    };
  }, []);



  useEffect(() => {
    if (momentSwitcherOptions.length === 0) return;

    const next = reconcileSelectedGroupMomentType(momentSwitcherOptions, selectedMomentTypeCode);

    if (next !== selectedMomentTypeCode) {
      setSelectedGroupMomentTypeCode(next);
    }

    applySelectedMoment(next);
  }, [momentSwitcherOptions, selectedMomentTypeCode, applySelectedMoment]);



  useEffect(() => {

    MomentraAnalytics.logScreen(

      resolveScreenName("group", selectedTab, screenOverlay, previousTab),

      "group",

    );

  }, [selectedTab, previousTab, screenOverlay]);



  async function refreshAfterManage() {

    await refreshGroupSessionInventory(false);

  }



  function handleMomentSwitcherSelect(option: { typeCode: GroupMomentTypeCode; momentId: string }) {

    if (option.typeCode === selectedMomentTypeCode && option.momentId === activeMomentId) return;

    setGroupSelection(option.typeCode, option.momentId);

  }

  async function archiveGroupMomentOption(option: GroupMomentSwitcherOption) {
    if (!option.momentId) return;
    if (!confirm(`Archive ${option.label}? This removes it from your active list.`)) return;
    if (option.momentId !== activeMomentId || option.typeCode !== selectedMomentTypeCode) {
      setGroupSelection(option.typeCode, option.momentId);
    }
    const inventory: LifecycleInventoryItem[] = (sessionBootstrap?.moments ?? [])
      .map((m) => ({
        momentId: String(m.id || ""),
        momentTypeCode: String(m.moment_type || ""),
        status: String(m.lifecycle_status || "ACTIVE"),
      }))
      .filter((m) => m.momentId);
    try {
      const result = await runMomentLifecycle({
        contextType: "GROUP",
        momentId: option.momentId,
        momentTypeCode: option.typeCode,
        action: "archive",
        previousStatus: "ACTIVE",
        inventory,
        selectedMomentId: option.momentId,
        refreshBootstrap: false,
      });
      applyGroupLifecyclePatch(
        option.momentId,
        "ARCHIVED",
        result.replacementMomentId,
        result.replacementMomentTypeCode,
      );
      await refreshAfterManage();
    } catch (e) {
      alert(e instanceof MomentLifecycleError ? e.userMessage : "Could not archive moment");
    }
  }

  async function leaveGroupMomentOption(option: GroupMomentSwitcherOption) {
    if (!option.momentId) return;
    if (
      !confirm(
        `Leave ${option.label}? You will lose access. The moment stays for others.`,
      )
    ) {
      return;
    }
    if (option.momentId !== activeMomentId || option.typeCode !== selectedMomentTypeCode) {
      setGroupSelection(option.typeCode, option.momentId);
    }
    const inventory: LifecycleInventoryItem[] = (sessionBootstrap?.moments ?? [])
      .map((m) => ({
        momentId: String(m.id || ""),
        momentTypeCode: String(m.moment_type || ""),
        status: String(m.lifecycle_status || "ACTIVE"),
      }))
      .filter((m) => m.momentId);
    try {
      const result = await runMomentLifecycle({
        contextType: "GROUP",
        momentId: option.momentId,
        momentTypeCode: option.typeCode,
        action: "leave",
        previousStatus: "ACTIVE",
        inventory,
        selectedMomentId: option.momentId,
        refreshBootstrap: false,
      });
      applyGroupLifecyclePatch(
        option.momentId,
        "LEFT",
        result.replacementMomentId,
        result.replacementMomentTypeCode,
      );
      await refreshAfterManage();
    } catch (e) {
      alert(e instanceof MomentLifecycleError ? e.userMessage : "Could not leave moment");
    }
  }



  function handleFabPress() {

    const hasActiveMoment = Boolean(activeMomentId) && momentSwitcherOptions.length > 0;

    if ((isActiveScreen(tabResolved) || hasActiveMoment) && activeMomentId) {
      openQuickAdd();
      return;
    }

    if (isSetupScreen(tabResolved) || (draftMomentId && momentSwitcherOptions.length === 0)) {

      resumeDraftSetup();

      return;

    }

    openCreateOverlay();

  }



  function handleTabSelect(tab: BottomNavTabId) {

    if (tab === "add") {

      handleFabPress();

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



  async function handleCreateTypeSelect(type: GroupCreateType) {

    MomentraAnalytics.logCustomEvent("create_moment_type_select", {

      app_context: appContext,

      moment_type: type,

      phase: "setup",

    });

    setCreating(true);

    setCreateError(null);

    try {

      if (draftMomentId && draftMomentType === type) {

        SetupRepository.rememberGroupMoment(draftMomentId, type);

        setSetupMomentId(draftMomentId);

        setSetupMomentType(type);

        setShowCreateOverlay(false);

        return;

      }

      const moment = await SetupRepository.createDraft({ moment_type_code: type });

      SetupRepository.rememberGroupMoment(moment.moment_id, type);

      setSetupMomentId(moment.moment_id);

      setSetupMomentType(type);

      setShowCreateOverlay(false);

      patchGroupDraftInStore(moment.moment_id, type);

    } catch (err) {

      setCreateError(err instanceof Error ? err.message : "Failed to start setup");

    } finally {

      setCreating(false);

    }

  }



  function resumeDraftSetup() {

    if (!draftMomentId || !draftMomentType) return;

    SetupRepository.rememberGroupMoment(draftMomentId, draftMomentType);

    setSetupMomentId(draftMomentId);

    setSetupMomentType(draftMomentType);

  }



  async function handleSetupActivated() {

    const activatedId = setupMomentId;

    const activatedType = setupMomentType;

    setSetupMomentId(null);

    setSetupMomentType(null);

    setShowCreateOverlay(false);

    if (activatedId && activatedType) {

      patchGroupMomentActivated(activatedId, activatedType);

      setSelectedTab("pulse");

      invalidateGroupTabCaches(activatedId);

      toast.success(groupActivationSuccessMessage(activatedType));

    }

    void softRefreshGroupSession();

  }



  function openSetupForManage(typeCode: GroupMomentTypeCode, momentId: string) {

    SetupRepository.rememberGroupMoment(momentId, typeCode);

    setSetupMomentId(momentId);

    setSetupMomentType(typeCode);

  }



  function SetupScreenForType() {

    if (!setupMomentId || !setupMomentType) return null;

    const props = {

      momentId: setupMomentId,

      onClose: () => {

        setSetupMomentId(null);

        setSetupMomentType(null);

      },

      onActivated: () => void handleSetupActivated(),

    };

    if (setupMomentType === "SHARED_PURCHASE") return <GroupPurchaseSetup {...props} />;

    if (setupMomentType === "SHARED_LIVING") return <GroupLivingSetup {...props} />;

    return <GroupTripSetup {...props} />;

  }



  function renderResumeCard() {

    if (!draftMomentId) return null;

    return (

      <div className="mx-auto w-full max-w-lg px-5 pb-4" style={{ paddingTop: 12 }}>

        <button

          type="button"

          onClick={resumeDraftSetup}

          className="w-full rounded-2xl px-5 py-4 text-left"

          style={{

            background: tokens.colors.surfaceContainer,

            color: tokens.colors.textPrimary,

            border: `1px solid color-mix(in srgb, ${tokens.colors.primaryContainer} 50%, transparent)`,

          }}

        >

          <p className="text-xs font-bold tracking-widest opacity-70">RESUME SETUP</p>

          <p className="mt-1 text-base font-semibold">

            Continue {draftMomentType?.replaceAll("_", " ").toLowerCase() ?? "group"} draft

          </p>

        </button>

      </div>

    );

  }



  function renderKeepAliveTabs(panels: {
    pulse: ReactNode;
    moments: ReactNode;
    memory: ReactNode;
    life: ReactNode;
  }) {
    const tabKeys = ["pulse", "moments", "memory", "life"] as const;
    return (
      <div className="relative flex min-h-0 flex-1 flex-col">
        {tabKeys.map((tab) => {
          if (!mountedTabs.has(tab)) return null;
          const active = visibleTab === tab;
          return (
            <section
              key={tab}
              hidden={!active}
              aria-hidden={!active}
              className={active ? "flex min-h-0 flex-1 flex-col" : undefined}
            >
              {panels[tab]}
            </section>
          );
        })}
      </div>
    );
  }

  function renderActiveExperience() {
    if (!activeMomentId) return renderActivePlaceholder();

    const onQuickAdd = openQuickAdd;
    const life = (
      <GroupLifeCommandCenter
        bottomPadding={bottomPadding}
        onCreateMomentType={(type) => void handleCreateTypeSelect(type as GroupCreateType)}
      />
    );

    return renderKeepAliveTabs({
      pulse: (
        <ExperiencePulse
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
          onViewAllActivity={() => setShowLivingActivity(true)}
          onEditActivity={(id, eventType) => setEditingLivingActivity({ id, eventType })}
        />
      ),
      moments: (
        <ActiveMoments
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
        />
      ),
      memory: (
        <ActiveMemory
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
        />
      ),
      life,
    });
  }

  function renderActivePurchase() {
    if (!activeMomentId) return renderActivePlaceholder();

    const onQuickAdd = openQuickAdd;
    const life = (
      <GroupLifeCommandCenter
        bottomPadding={bottomPadding}
        onCreateMomentType={(type) => void handleCreateTypeSelect(type as GroupCreateType)}
      />
    );

    return renderKeepAliveTabs({
      pulse: (
        <SharedPurchasePulse
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
        />
      ),
      moments: (
        <SharedPurchaseMoments
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
        />
      ),
      memory: (
        <SharedPurchaseMemory
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
        />
      ),
      life,
    });
  }

  function renderActiveLiving() {
    if (!activeMomentId) return renderActivePlaceholder();

    const onQuickAdd = openQuickAdd;
    const life = (
      <GroupLifeCommandCenter
        bottomPadding={bottomPadding}
        onCreateMomentType={(type) => void handleCreateTypeSelect(type as GroupCreateType)}
      />
    );

    return renderKeepAliveTabs({
      pulse: (
        <SharedLivingPulse
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
          onViewAllActivity={() => setShowLivingActivity(true)}
          onEditActivity={(id, eventType) => setEditingLivingActivity({ id, eventType })}
        />
      ),
      moments: (
        <SharedLivingMoments
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
        />
      ),
      memory: (
        <SharedLivingMemory
          momentId={activeMomentId}
          onQuickAdd={onQuickAdd}
          bottomPadding={bottomPadding}
          reloadKey={tripMomentsReloadKey}
        />
      ),
      life,
    });
  }



  function renderActiveByType() {

    if (activeMomentType === "SHARED_EXPERIENCE") return renderActiveExperience();

    if (activeMomentType === "SHARED_PURCHASE") return renderActivePurchase();

    if (activeMomentType === "SHARED_LIVING") return renderActiveLiving();

    return renderActivePlaceholder();

  }



  function renderActivePlaceholder() {

    return (

      <div

        className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6 text-center"

        style={{ paddingBottom: bottomPadding, color: tokens.colors.textPrimary }}

      >

        <p className="text-lg font-semibold">Loading your group moment</p>

        <p className="max-w-sm text-sm opacity-70" style={{ color: tokens.colors.textSecondary }}>

          We found an active group but could not load its dashboard yet. Try refreshing, or open

          setup again if you just activated.

        </p>

        <button

          type="button"

          onClick={() => void ensureGroupSession(true)}

          className="mt-2 rounded-full px-4 py-2 text-sm font-semibold"

          style={{ background: tokens.colors.primaryContainer, color: tokens.colors.onPrimaryContainer }}

        >

          Retry

        </button>

      </div>

    );

  }



  function renderTabContent() {

    if (tabResolved === "loading") {

      return (

        <div className="flex min-h-0 flex-1 items-center justify-center" style={{ paddingBottom: bottomPadding }}>

          <p className="text-sm opacity-70">Loading…</p>

        </div>

      );

    }



    // Cross-moment Life command center: show when group has active moments even if bootstrap lagged.

    if (visibleTab === "life" && momentSwitcherOptions.length > 0) {

      return (

        <GroupLifeCommandCenter

          bottomPadding={bottomPadding}

          onCreateMomentType={(type) => void handleCreateTypeSelect(type as GroupCreateType)}

        />

      );

    }



    // Active moment wins over stale SETUP pulse module / leftover draft (all tabs).

    if (momentSwitcherOptions.length > 0 && (activeMomentId || activeMomentType)) {

      if (!sessionLoaded) {

        return (

          <div className="flex min-h-0 flex-1 items-center justify-center" style={{ paddingBottom: bottomPadding }}>

            <p className="text-sm opacity-70">Loading…</p>

          </div>

        );

      }

      return renderActiveByType();

    }



    if (isSetupScreen(tabResolved)) {

      const showPulseDraftResume = Boolean(draftMomentId) && visibleTab === "pulse";

      return (

        <div className="flex min-h-0 flex-1 flex-col">

          {visibleTab !== "pulse" ? renderResumeCard() : null}

          <div className="flex min-h-0 flex-1 flex-col">

            {visibleTab === "moments" ? (

              <GroupMomentsEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />

            ) : visibleTab === "life" ? (

              <GroupLifeEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />

            ) : visibleTab === "memory" ? (

              <GroupMemoryEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />

            ) : (

              <GroupPulseEmpty

                onCreateMoment={openCreateOverlay}

                bottomPadding={bottomPadding}

                mode={showPulseDraftResume ? "draft_resume" : "no_moment"}

                onContinueSetup={showPulseDraftResume ? resumeDraftSetup : undefined}

              />

            )}

          </div>

        </div>

      );

    }



    if (isEmptyScreen(tabResolved)) {

      switch (visibleTab) {

        case "moments":

          return <GroupMomentsEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;

        case "life":

          return <GroupLifeEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;

        case "memory":

          return <GroupMemoryEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;

        default:

          return (

            <GroupPulseEmpty

              onCreateMoment={openCreateOverlay}

              bottomPadding={bottomPadding}

              mode={draftMomentId ? "draft_resume" : "no_moment"}

              onContinueSetup={draftMomentId ? resumeDraftSetup : undefined}

            />

          );

      }

    }



    // Empty switcher inventory wins over stale ACTIVE bootstrap (archive-all).
    // Do not fall through to "Loading your group moment".
    if (momentSwitcherOptions.length === 0) {
      switch (visibleTab) {
        case "moments":
          return <GroupMomentsEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
        case "life":
          return <GroupLifeEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
        case "memory":
          return <GroupMemoryEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
        default:
          return (
            <GroupPulseEmpty
              onCreateMoment={openCreateOverlay}
              bottomPadding={bottomPadding}
              mode={draftMomentId ? "draft_resume" : "no_moment"}
              onContinueSetup={draftMomentId ? resumeDraftSetup : undefined}
            />
          );
      }
    }



    if (!sessionLoaded) {

      return (

        <div className="flex min-h-0 flex-1 items-center justify-center" style={{ paddingBottom: bottomPadding }}>

          <p className="text-sm opacity-70">Loading…</p>

        </div>

      );

    }

    return renderActiveByType();

  }



  const showGroupManageHeader =

    (isActiveScreen(tabResolved) || momentSwitcherOptions.length > 0) &&

    momentSwitcherOptions.length > 0 &&

    (visibleTab === "pulse" ||

      visibleTab === "moments" ||

      visibleTab === "memory" ||

      visibleTab === "life");



  function wrapActiveTabWithHeader(content: ReactNode) {

    if (!showGroupManageHeader) return content;

    return (

      <div className="flex min-h-0 flex-1 flex-col">

        <GroupMomentHeader

          tabLabel={TAB_LABELS[visibleTab]}

          options={momentSwitcherOptions}

          selectedTypeCode={selectedMomentTypeCode}

          onSelect={handleMomentSwitcherSelect}

          onManageClick={manageContext ? () => setShowManageSheet(true) : undefined}

          onInviteMoment={(option) => {
            if (!option.momentId) return;
            if (option.momentId !== activeMomentId || option.typeCode !== selectedMomentTypeCode) {
              setGroupSelection(option.typeCode, option.momentId);
            }
            setInviteMoment({ momentId: option.momentId, label: option.label });
          }}

          onDeleteMoment={(option) => {
            void archiveGroupMomentOption(option);
          }}

          onLeaveMoment={(option) => {
            void leaveGroupMomentOption(option);
          }}

        />

        <div className="flex min-h-0 flex-1 flex-col">{content}</div>

      </div>

    );

  }



  return (

    <div className="flex min-h-0 flex-1 flex-col" style={{ background: tokens.colors.background }}>

      <div className="flex min-h-0 flex-1 flex-col">

        {wrapActiveTabWithHeader(renderTabContent())}

      </div>

      <ContextBottomNav

        variant="group"

        selectedTab={visibleTab}

        onTabSelect={handleTabSelect}

        onCreateMoment={handleFabPress}

      />

      {showCreateOverlay && (

        <GroupCreateEmpty

          onCreateMoment={openCreateOverlay}

          onClose={() => setShowCreateOverlay(false)}

          onSharedExperience={() => void handleCreateTypeSelect("SHARED_EXPERIENCE")}

          onSharedLiving={() => void handleCreateTypeSelect("SHARED_LIVING")}

          onSharedPurchase={() => void handleCreateTypeSelect("SHARED_PURCHASE")}

        />

      )}

      {creating ? (

        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/40">

          <p className="rounded-xl px-4 py-3 text-sm" style={{ background: tokens.colors.surfaceContainer }}>

            Starting setup…

          </p>

        </div>

      ) : null}

      {createError ? (

        <div className="fixed bottom-24 left-1/2 z-[60] -translate-x-1/2 rounded-xl px-4 py-3 text-sm"

          style={{ background: tokens.colors.error, color: "#fff" }}>

          {createError}

        </div>

      ) : null}

      {quickAddSuccess ? (
        <div
          className="fixed bottom-24 left-1/2 z-[60] -translate-x-1/2 rounded-2xl px-4 py-3 text-sm font-semibold shadow-lg"
          style={{ background: tokens.colors.primaryContainer, color: tokens.colors.brandOnPrimary }}
        >
          {quickAddSuccess}
        </div>
      ) : null}

      {setupMomentId ? <SetupScreenForType /> : null}

      {showQuickAdd && activeMomentId ? (

        <GroupActiveQuickAddOverlay

          momentId={activeMomentId}

          momentTypeCode={activeMomentType ?? "SHARED_EXPERIENCE"}

          initialActionId={quickAddActionId}

          onClose={() => {
            closeQuickAdd();
          }}

          onSuccess={() => {
            if (activeMomentId) invalidateGroupTabCaches(activeMomentId);
            setTripMomentsReloadKey((key) => key + 1);
            setQuickAddSuccess("Quick Add saved");
            closeQuickAdd();
          }}

        />

      ) : null}

      {showLivingActivity &&
      activeMomentId &&
      (activeMomentType === "SHARED_LIVING" || activeMomentType === "SHARED_EXPERIENCE") ? (
        <LivingActivityScreen
          key={livingActivityReloadToken}
          momentId={activeMomentId}
          onBack={() => setShowLivingActivity(false)}
          onEditActivity={(id, eventType) => setEditingLivingActivity({ id, eventType })}
          reloadToken={livingActivityReloadToken}
          {...(activeMomentType === "SHARED_EXPERIENCE"
            ? {
                title: "Trip activity",
                subtitle: "View and edit experience updates",
                listActivity: listTripActivity,
              }
            : {})}
        />
      ) : null}

      {editingLivingActivity &&
      activeMomentId &&
      (activeMomentType === "SHARED_LIVING" || activeMomentType === "SHARED_EXPERIENCE") ? (
        <LivingActivityEditSheet
          momentId={activeMomentId}
          eventId={editingLivingActivity.id}
          onClose={() => setEditingLivingActivity(null)}
          onSuccess={() => {
            setLivingActivityReloadToken((t) => t + 1);
            if (activeMomentId) invalidateGroupTabCaches(activeMomentId);
            setTripMomentsReloadKey((key) => key + 1);
          }}
          {...(activeMomentType === "SHARED_EXPERIENCE"
            ? {
                getDetail: getTripActivityDetail,
                patchActivity: patchTripActivity,
                deleteActivity: deleteTripActivity,
              }
            : {})}
        />
      ) : null}

      <MomentInviteSheet
        open={Boolean(inviteMoment)}
        onClose={() => setInviteMoment(null)}
        momentId={inviteMoment?.momentId ?? null}
        momentLabel={inviteMoment?.label}
        variant="group"
      />

      <MomentManageSheet

        open={showManageSheet}

        context={manageContext}

        onClose={() => setShowManageSheet(false)}

        isOwner={manageContext?.isOwned !== false}

        onEditSetup={() => {

          if (!manageContext) return;

          openSetupForManage(manageContext.typeCode, manageContext.momentId);

        }}

        onEditName={async (name) => {
          if (!manageContext) return;
          await GroupRepository.patchMoment(manageContext.momentId, { moment_name: name });
          patchGroupMomentInInventory(manageContext.momentId, { name });
          await refreshAfterManage();
        }}

        onPause={async () => {
          if (!manageContext) return;
          const inventory: LifecycleInventoryItem[] = (sessionBootstrap?.moments ?? []).map((m) => ({
            momentId: String(m.id || ""),
            momentTypeCode: String(m.moment_type || ""),
            status: String(m.lifecycle_status || "ACTIVE"),
          })).filter((m) => m.momentId);
          try {
            const result = await runMomentLifecycle({
              contextType: "GROUP",
              momentId: manageContext.momentId,
              momentTypeCode: manageContext.typeCode,
              action: "pause",
              previousStatus: manageContext.status || "ACTIVE",
              inventory,
              selectedMomentId: manageContext.momentId,
              refreshBootstrap: false,
            });
            applyGroupLifecyclePatch(
              manageContext.momentId,
              "PAUSED",
              result.replacementMomentId,
              result.replacementMomentTypeCode,
            );
            await refreshAfterManage();
          } catch (e) {
            if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
            throw e;
          }
        }}

        onResume={async () => {
          if (!manageContext) return;
          const inventory: LifecycleInventoryItem[] = (sessionBootstrap?.moments ?? []).map((m) => ({
            momentId: String(m.id || ""),
            momentTypeCode: String(m.moment_type || ""),
            status: String(m.lifecycle_status || "PAUSED"),
          })).filter((m) => m.momentId);
          try {
            const result = await runMomentLifecycle({
              contextType: "GROUP",
              momentId: manageContext.momentId,
              momentTypeCode: manageContext.typeCode,
              action: "resume",
              previousStatus: manageContext.status || "PAUSED",
              inventory,
              selectedMomentId: manageContext.momentId,
              refreshBootstrap: false,
            });
            applyGroupLifecyclePatch(
              manageContext.momentId,
              "ACTIVE",
              result.replacementMomentId,
              result.replacementMomentTypeCode,
            );
            await refreshAfterManage();
          } catch (e) {
            if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
            throw e;
          }
        }}

        onComplete={async () => {
          if (!manageContext) return;
          const inventory: LifecycleInventoryItem[] = (sessionBootstrap?.moments ?? []).map((m) => ({
            momentId: String(m.id || ""),
            momentTypeCode: String(m.moment_type || ""),
            status: String(m.lifecycle_status || "ACTIVE"),
          })).filter((m) => m.momentId);
          try {
            const result = await runMomentLifecycle({
              contextType: "GROUP",
              momentId: manageContext.momentId,
              momentTypeCode: manageContext.typeCode,
              action: "complete",
              previousStatus: manageContext.status || "ACTIVE",
              inventory,
              selectedMomentId: manageContext.momentId,
              refreshBootstrap: false,
            });
            applyGroupLifecyclePatch(
              manageContext.momentId,
              "COMPLETED",
              result.replacementMomentId,
              result.replacementMomentTypeCode,
            );
            await refreshAfterManage();
          } catch (e) {
            if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
            throw e;
          }
        }}

        onArchive={async () => {
          if (!manageContext) return;
          const inventory: LifecycleInventoryItem[] = (sessionBootstrap?.moments ?? []).map((m) => ({
            momentId: String(m.id || ""),
            momentTypeCode: String(m.moment_type || ""),
            status: String(m.lifecycle_status || "ACTIVE"),
          })).filter((m) => m.momentId);
          try {
            const result = await runMomentLifecycle({
              contextType: "GROUP",
              momentId: manageContext.momentId,
              momentTypeCode: manageContext.typeCode,
              action: "archive",
              previousStatus: manageContext.status || "ACTIVE",
              inventory,
              selectedMomentId: manageContext.momentId,
              refreshBootstrap: false,
            });
            applyGroupLifecyclePatch(
              manageContext.momentId,
              "ARCHIVED",
              result.replacementMomentId,
              result.replacementMomentTypeCode,
            );
            await refreshAfterManage();
          } catch (e) {
            if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
            throw e;
          }
        }}

        onDeletePermanently={async () => {
          if (!manageContext) return;
          const inventory: LifecycleInventoryItem[] = (sessionBootstrap?.moments ?? []).map((m) => ({
            momentId: String(m.id || ""),
            momentTypeCode: String(m.moment_type || ""),
            status: String(m.lifecycle_status || "ACTIVE"),
          })).filter((m) => m.momentId);
          try {
            const result = await runMomentLifecycle({
              contextType: "GROUP",
              momentId: manageContext.momentId,
              momentTypeCode: manageContext.typeCode,
              action: "delete",
              previousStatus: manageContext.status || "ACTIVE",
              inventory,
              selectedMomentId: manageContext.momentId,
              refreshBootstrap: false,
            });
            applyGroupLifecyclePatch(
              manageContext.momentId,
              "DELETED",
              result.replacementMomentId,
              result.replacementMomentTypeCode,
            );
            await refreshAfterManage();
          } catch (e) {
            if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
            throw e;
          }
        }}

        onLeave={async () => {
          if (!manageContext) return;
          const inventory: LifecycleInventoryItem[] = (sessionBootstrap?.moments ?? []).map((m) => ({
            momentId: String(m.id || ""),
            momentTypeCode: String(m.moment_type || ""),
            status: String(m.lifecycle_status || "ACTIVE"),
          })).filter((m) => m.momentId);
          try {
            const result = await runMomentLifecycle({
              contextType: "GROUP",
              momentId: manageContext.momentId,
              momentTypeCode: manageContext.typeCode,
              action: "leave",
              previousStatus: manageContext.status || "ACTIVE",
              inventory,
              selectedMomentId: manageContext.momentId,
              refreshBootstrap: false,
            });
            applyGroupLifecyclePatch(
              manageContext.momentId,
              "LEFT",
              result.replacementMomentId,
              result.replacementMomentTypeCode,
            );
            await refreshAfterManage();
          } catch (e) {
            if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
            throw e;
          }
        }}

      />

    </div>

  );

}



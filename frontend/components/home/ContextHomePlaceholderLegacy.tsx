"use client";

// Shared personal + business home shell. Group uses GroupHomePlaceholder; Personal uses PersonalHomePlaceholder.
import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { CreateEmpty as BusinessCreateEmpty } from "@/components/business/empty/create/CreateEmpty";
import { BusinessMomentSetup } from "@/components/business/setup/BusinessMomentSetup";
import { MemoryEmpty as BusinessMemoryEmpty } from "@/components/business/empty/memory/MemoryEmpty";
import { LifeEmpty as BusinessLifeEmpty } from "@/components/business/empty/life/LifeEmpty";
import { MomentsEmpty as BusinessMomentsEmpty } from "@/components/business/empty/moments/MomentsEmpty";
import { PulseEmpty as BusinessPulseEmpty } from "@/components/business/empty/pulse/PulseEmpty";
import { BusinessActionCenterShell } from "@/components/business/actioncenter/BusinessActionCenterShell";
import { TeamOperationsActiveTabs } from "@/components/business/active/team-operations/TeamOperationsActiveTabs";
import { BusinessRunwayActiveTabs } from "@/components/business/active/business-runway/BusinessRunwayActiveTabs";
import { BusinessOperationsActiveTabs } from "@/components/business/active/business-operations/BusinessOperationsActiveTabs";
import { BusinessNoMomentActionHint } from "@/components/business/shared/BusinessNoMomentActionHint";
import type { TeamOpsEventItem } from "@/lib/api/businessActive";
import { invalidateBusinessActiveCaches, softInvalidateBusinessAggCaches } from "@/hooks/useBusinessActiveTabs";
import { applyBusinessMutationSuccess } from "@/lib/business/businessOptimisticMutation";
import {
  MomentLifecycleError,
  runMomentLifecycle,
  type LifecycleInventoryItem,
} from "@/lib/lifecycle/MomentLifecycleCoordinator";
import {
  ensureBusinessBootstrap,
  ensureBusinessCreateOptions,
  getBusinessSessionSnapshot,
  refreshBusinessSessionInventory,
  setBusinessSelection,
  patchBusinessMomentInInventory,
  useBusinessSessionStore,
} from "@/stores/businessSessionStore";
import { prefetchBusinessActionCatalog } from "@/hooks/useBusinessActionCenter";
import { useAuth } from "@/components/auth/AuthProvider";
import { CreateEmpty as PersonalCreateEmpty } from "@/components/personal/empty/create/CreateEmpty";
import { LifeEmpty as PersonalLifeEmpty } from "@/components/personal/empty/life/LifeEmpty";
import { RelationshipsMemory, RelationshipsMemorySkeleton } from "@/components/personal/emotional_security/memory/RelationshipsMemory";
import { RelationshipsMoments, RelationshipsMomentsSkeleton } from "@/components/personal/emotional_security/moments/RelationshipsMoments";
import { RelationshipsPulse, RelationshipsPulseSkeleton } from "@/components/personal/emotional_security/pulse/RelationshipsPulse";
import { FutureBuildingMemory, FutureBuildingMemorySkeleton } from "@/components/personal/future_building/memory/FutureBuildingMemory";
import { FutureBuildingMoments, FutureBuildingMomentsSkeleton } from "@/components/personal/future_building/moments/FutureBuildingMoments";
import { FutureBuildingPulse, FutureBuildingPulseSkeleton } from "@/components/personal/future_building/pulse/FutureBuildingPulse";
import { LifestyleMemory, LifestyleMemorySkeleton } from "@/components/personal/lifestyle/memory/LifestyleMemory";
import { LifestyleMoments, LifestyleMomentsSkeleton } from "@/components/personal/lifestyle/moments/LifestyleMoments";
import { LifestylePulse } from "@/components/personal/lifestyle/pulse/LifestylePulse";
import { MemoryEmpty as PersonalMemoryEmpty } from "@/components/personal/empty/memory/MemoryEmpty";
import { MomentsEmpty as PersonalMomentsEmpty } from "@/components/personal/empty/moments/MomentsEmpty";
import { LifeOperationsMemory, LifeOperationsMemorySkeleton, LifeOperationsMemoryEmpty } from "@/components/personal/life_operations/memory/LifeOperationsMemory";
import { TemplateMemoryScreen, TemplateMemorySkeleton, TemplateMemoryEmpty } from "@/components/personal/template/TemplateMemoryScreen";
import { LifeOperationsMoments, LifeOperationsMomentsSkeleton, LifeOperationsMomentsEmpty } from "@/components/personal/life_operations/moments/LifeOperationsMoments";
import { LifeOperationsPulse } from "@/components/personal/life_operations/pulse/LifeOperationsPulse";
import { LifeOperationsPulseSkeleton } from "@/components/personal/life_operations/pulse/LifeOperationsPulseSkeleton";
import { SkeletonCrossfade } from "@/components/personal/shared/skeleton/SkeletonCrossfade";
import { TemplateActivityScreen } from "@/components/personal/template/activity/TemplateActivityScreen";
import { TemplateActivityEditSheet } from "@/components/personal/template/activity/TemplateActivityEditSheet";
import { MasterExpenseOrchestrator } from "@/components/personal/master-expense/MasterExpenseOrchestrator";
import { MyMoneyFloatingAdd } from "@/components/shell/MyMoneyFloatingAdd";
import {
  activeCardForType,
  isActiveMoment,
  isActiveMomentStatus,
  isDraftMoment,
  logQuickAddGateBlocked,
  memoryHasTypePayload,
  momentTypeLabel,
  momentsHasTypePayload,
  pulseHasTypePayload,
  reconcileSelectedMomentType,
  resolveMomentSwitcherOptions,
  resolvePersonalMomentManageContext,
  resolveQuickAddGate,
  templateMomentsEnabled,
  type PersonalMomentManageContext,
  type PersonalMomentSwitcherOption,
} from "@/components/personal/shared/personalMomentRouting";
import { PersonalTabErrorBoundary } from "@/components/personal/shared/PersonalTabErrorBoundary";
import {
  memorySkeletonForType,
  momentsSkeletonForType,
  pulseSkeletonForType,
} from "@/components/personal/shared/templateTabSkeletons";
import { PersonalMomentHeader } from "@/components/personal/shared/PersonalMomentHeader";
import { PersonalMomentManageSheet } from "@/components/personal/shared/PersonalMomentManageSheet";
import { MomentManageSheet } from "@/components/shared/MomentManageSheet";
import { MomentInviteSheet } from "@/components/shared/MomentInviteSheet";
import {
  resolveBusinessMomentManageContext,
  resolveBusinessMomentSwitcherOptions,
  resolveSelectedBusinessMoment,
} from "@/components/business/shared/businessMomentRouting";
import { BusinessMomentHeader } from "@/components/business/shared/BusinessMomentHeader";
import type { BusinessMomentSwitcherOption } from "@/components/business/shared/businessMomentRouting";
import { PersonalMomentSetup } from "@/components/personal/shared/setup/PersonalMomentSetup";
import { PersonalLife, PersonalLifeSkeleton } from "@/components/personal/life/PersonalLife";
import { PulseEmpty as PersonalPulseEmpty } from "@/components/personal/empty/pulse/PulseEmpty";
import { PersonalMomentQuickAddRouter } from "@/components/personal/shared/PersonalMomentQuickAddRouter";
import { PersistentTabStack } from "@/components/shared/AnimatedTabPanel";
import { ContextBottomNav } from "@/components/nav/ContextBottomNav";
import { OfflineBanner } from "@/components/shared/OfflineBanner";
import { PullToRefresh } from "@/components/shared/PullToRefresh";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { BUSINESS_CREATE_OPEN_EVENT, BUSINESS_OPEN_MOMENT_EVENT, BUSINESS_SELECT_PULSE_EVENT } from "@/lib/businessShellEvents";
import type { BottomNavTabId } from "@/lib/bottomNavTabs";
import { PERSONAL_CREATE_OPEN_EVENT } from "@/lib/personalShellEvents";
import { LIFE360_SELECT_LIFE_TAB_EVENT } from "@/lib/life360ShellEvents";
import {
  ApiError,
  patchBusinessMoment,
} from "@/lib/api/client";
import { fetchPersonalCreateOptions } from "@/lib/personal/personalCreateOptions";
import { hasTypeSessionCacheHint } from "@/lib/personal/sessionCacheHint";
import { SetupRepository } from "@/repositories/SetupRepository";
import { PersonalRepository, invalidateAfterQuickAdd, invalidateAfterTemplateLifecycle } from "@/repositories/PersonalRepository";
import { getContextSnapshot } from "@/stores/contextStore";
import { shouldRenderActivePulseDashboard } from "@/lib/setup/templates/registry";
import type { PersonalCreateOptionCard, PersonalCreateOptionsResponse } from "@/lib/api/personal";
import type {
  BusinessSetupState,
} from "@/lib/api/business";
import { MomentraAnalytics } from "@/lib/analytics";
import {
  resolveScreenName,
  type ScreenOverlay,
} from "@/lib/analyticsScreens";
import { usePersonalLife } from "@/hooks/usePersonalLife";
import { usePersonalMemory, seedPersonalMemoryCache, invalidatePersonalMemoryCache } from "@/hooks/usePersonalMemory";
import { usePersonalMomentSession } from "@/hooks/usePersonalMomentSession";
import { usePersonalPulse, getPersonalPulseCache, seedPersonalPulseCache, invalidatePersonalPulseCache } from "@/hooks/usePersonalPulse";
import { usePersonalMoments, getPersonalMomentsCache, seedPersonalMomentsCache, invalidatePersonalMomentsCache } from "@/hooks/usePersonalMoments";
import { seedPersonalLifeCache } from "@/hooks/usePersonalLife";
import { isInflight } from "@/lib/cache/cacheStore";
import {
  hasCachedActiveSessionHint,
  warmUpPersonalSessionFromDisk,
  softRefreshPersonalSession,
  refreshPersonalSessionInventory,
  patchPersonalMomentActivated,
  patchPersonalDraftCreated,
  patchPersonalMomentInInventory,
  ensurePersonalCreateOptions,
  setPersonalMomentType,
  usePersonalSessionStore,
  bumpPersonalSessionGeneration,
} from "@/stores/personalSessionStore";
import { prefetchQuickAddOptions } from "@/hooks/useQuickAddOptions";
import {
  useTemplateLife,
  useTemplateMemory,
  useTemplateMoments,
  getTemplateMemoryCache,
  getTemplateMomentsCache,
  seedTemplateMemoryCache,
  seedTemplateMomentsCache,
} from "@/hooks/useTemplateProjection";
import {
  setSelectedMomentTypeCode,
  isMyMoneyTemplateCode,
  type PersonalMomentTypeCode,
} from "@/lib/personal/personalMomentSession";
import { useBootstrapStore } from "@/hooks/useBootstrap";
import {
  contextStateFor,
  getBootstrap,
  invalidateBootstrapAfterMutation,
  loadBootstrap,
  moduleStateFor,
  patchMyMoneyModuleStateInBootstrap,
} from "@/stores/bootstrapStore";
import {
  isEmptyScreen,
  isSetupScreen,
  isActiveScreen,
  resolveScreen,
  shouldLoadTabData,
  contextStateFromBootstrap,
} from "@/lib/screenResolver";
import type { AppContext } from "@/lib/appContext";
import { BusinessRepository } from "@/repositories/BusinessRepository";
import { BusinessSetupRepository } from "@/repositories/BusinessSetupRepository";
import {
  beginBusinessSetupOpen,
  markBusinessSetupBootstrapDone,
  markBusinessSetupCreateDone,
} from "@/lib/telemetry/businessSetupTelemetry";

function TabPanel({ title, bottomPadding }: { title: string; bottomPadding: number }) {
  const tokens = useThemeTokens();
  return (
    <div
      className="flex min-h-0 flex-1 flex-col items-center justify-center px-6"
      style={{
        background: tokens.colors.background,
        color: tokens.colors.textPrimary,
        paddingBottom: bottomPadding,
      }}
    >
      <h1 className="text-2xl font-semibold">{title}</h1>
      <p className="mt-2 text-sm opacity-70">Placeholder â€” feature screens coming soon</p>
    </div>
  );
}

type ContextHomePlaceholderLegacyProps = {
  variant: "personal" | "business";
  title: string;
};

export function ContextHomePlaceholderLegacy({
  variant,
  title,
}: ContextHomePlaceholderLegacyProps) {
  const { user } = useAuth();
  const businessUserId = user?.id ?? null;
  const [selectedTab, setSelectedTab] = useState<BottomNavTabId>("pulse");
  const [previousTab, setPreviousTab] = useState<BottomNavTabId>("pulse");
  const visibleTab = selectedTab === "add" ? previousTab : selectedTab;
  const appContext: AppContext = variant === "personal" ? "personal" : "business";
  const { data: bootstrap } = useBootstrapStore();
  const tabResolved = resolveScreen(appContext, visibleTab, bootstrap);
  /** Always load business session on Business home â€” even when bootstrap says EMPTY. */
  const businessSessionEnabled = variant === "business";
  const [showCreateOverlay, setShowCreateOverlay] = useState(false);
  const [showMomentSetup, setShowMomentSetup] = useState(false);
  const [setupMomentId, setSetupMomentId] = useState<string | null>(null);
  const [setupTypeCode, setSetupTypeCode] = useState<PersonalMomentTypeCode>("LIFE_OPERATIONS");
  const [createOptions, setCreateOptions] = useState<PersonalCreateOptionsResponse | null>(null);
  const [loadingCreateOptions, setLoadingCreateOptions] = useState(false);
  const [creatingTypeCode, setCreatingTypeCode] = useState<PersonalMomentTypeCode | null>(null);
  const [createError, setCreateError] = useState<string | null>(null);
  const [showQuickAddSheet, setShowQuickAddSheet] = useState(false);
  const [quickAddWarm, setQuickAddWarm] = useState(false);
  const [quickAddEventType, setQuickAddEventType] = useState<string | null>(null);
  const [quickAddResolvedMomentId, setQuickAddResolvedMomentId] = useState<string | null>(null);
  const [pendingMomentType, setPendingMomentType] = useState<PersonalMomentTypeCode | null>(null);
  const [shellCreateOptions, setShellCreateOptions] = useState<PersonalCreateOptionsResponse | null>(null);
  const [loadingShellCreateOptions, setLoadingShellCreateOptions] = useState(false);
  const [reconciledActivePulse, setReconciledActivePulse] = useState(false);
  const [holdReconcileTypeCode, setHoldReconcileTypeCode] = useState<PersonalMomentTypeCode | null>(null);
  const [showManageSheet, setShowManageSheet] = useState(false);
  const [inviteMoment, setInviteMoment] = useState<{
    momentId: string;
    label: string;
  } | null>(null);
  const businessSession = useBusinessSessionStore();
  const selectedBusinessMomentType = businessSession.selectedMomentType;
  const selectedBusinessMomentId = businessSession.selectedMomentId;
  const businessBootstrap = businessSession.bootstrap;
  const businessCreateOptions = businessSession.createOptions;
  const businessSessionError = businessSession.error;
  const businessSessionLoading = businessSession.loading;
  const [businessSessionRetryKey, setBusinessSessionRetryKey] = useState(0);
  const [showBusinessSetup, setShowBusinessSetup] = useState(false);
  const [businessSetupMomentId, setBusinessSetupMomentId] = useState<string | null>(null);
  const [businessSetupTypeCode, setBusinessSetupTypeCode] = useState("TEAM_OPERATIONS");
  const [businessSetupSeed, setBusinessSetupSeed] = useState<BusinessSetupState | null>(null);
  const [businessCreateError, setBusinessCreateError] = useState<string | null>(null);
  const [creatingBusinessType, setCreatingBusinessType] = useState<string | null>(null);
  const [teamOpsReloadKey, setTeamOpsReloadKey] = useState(0);
  const [teamOpsOptimistic, setTeamOpsOptimistic] = useState<TeamOpsEventItem[]>([]);
  const [showTeamOpsActivity, setShowTeamOpsActivity] = useState(false);
  const [teamOpsActivityEventId, setTeamOpsActivityEventId] = useState<string | null>(null);
  const [runwayReloadKey, setRunwayReloadKey] = useState(0);
  const [runwayOptimistic, setRunwayOptimistic] = useState<TeamOpsEventItem[]>([]);
  const [showRunwayActivity, setShowRunwayActivity] = useState(false);
  const [runwayActivityEventId, setRunwayActivityEventId] = useState<string | null>(null);
  const [opsReloadKey, setOpsReloadKey] = useState(0);
  const [opsOptimistic, setOpsOptimistic] = useState<TeamOpsEventItem[]>([]);
  const [showOpsActivity, setShowOpsActivity] = useState(false);
  const [opsActivityEventId, setOpsActivityEventId] = useState<string | null>(null);
  const [showLifeOpsActivity, setShowLifeOpsActivity] = useState(false);
  const [showMasterExpense, setShowMasterExpense] = useState(false);
  const [editingActivity, setEditingActivity] = useState<{
    id: string;
    eventType: string;
    momentTypeCode?: string;
  } | null>(null);
  const [activityReloadToken, setActivityReloadToken] = useState(0);
  const tokens = useThemeTokens();
  const selectedMomentTypeCode = usePersonalMomentSession();
  const preliminaryActiveCard = activeCardForType(
    createOptions?.cards ?? shellCreateOptions?.cards ?? [],
    selectedMomentTypeCode,
  );
  const hasActiveMoment = isActiveMoment(preliminaryActiveCard);
  const createOptionsHydrating = variant === "personal" && loadingShellCreateOptions;
  const sessionCacheHint =
    variant === "personal" &&
    (hasTypeSessionCacheHint(selectedMomentTypeCode, {
      pulse: getPersonalPulseCache(selectedMomentTypeCode),
      moments: getPersonalMomentsCache(selectedMomentTypeCode),
      templateMoments: getTemplateMomentsCache(selectedMomentTypeCode),
      templateMemory: getTemplateMemoryCache(selectedMomentTypeCode),
    }) ||
      hasCachedActiveSessionHint(selectedMomentTypeCode));
  const pulseEnabled =
    variant === "personal" &&
    visibleTab === "pulse" &&
    (shouldLoadTabData(resolveScreen("personal", "pulse", bootstrap)) ||
      hasActiveMoment ||
      sessionCacheHint ||
      createOptionsHydrating);
  const momentsEnabled =
    variant === "personal" &&
    visibleTab === "moments" &&
    (shouldLoadTabData(resolveScreen("personal", "moments", bootstrap)) ||
      hasActiveMoment ||
      sessionCacheHint);
  const memoryEnabled =
    variant === "personal" &&
    visibleTab === "memory" &&
    (shouldLoadTabData(resolveScreen("personal", "memory", bootstrap)) ||
      hasActiveMoment ||
      sessionCacheHint);
  const lifeEnabled =
    variant === "personal" &&
    visibleTab === "life" &&
    (shouldLoadTabData(resolveScreen("personal", "life", bootstrap)) ||
      hasActiveMoment ||
      sessionCacheHint);
  const {
    pulse: personalPulse,
    loading: pulseLoading,
    refreshing: pulseRefreshing,
    rebuilding: pulseRebuilding,
    error: pulseError,
    reload: reloadPulse,
    revalidate: revalidatePulse,
    refreshAfterSetup,
  } = usePersonalPulse({ enabled: pulseEnabled });
  const {
    moments: personalMoments,
    loading: momentsLoading,
    refreshing: momentsRefreshing,
    rebuilding: momentsRebuilding,
    error: momentsError,
    reload: reloadMoments,
    revalidate: revalidateMoments,
    refreshAfterSetup: refreshMomentsAfterSetup,
  } = usePersonalMoments({ enabled: momentsEnabled });
  const legacyMemoryEnabled =
    memoryEnabled && !(variant === "personal" && isMyMoneyTemplateCode(selectedMomentTypeCode));
  const {
    memory: personalMemory,
    loading: memoryLoading,
    refreshing: memoryRefreshing,
    rebuilding: memoryRebuilding,
    error: memoryError,
    reload: reloadMemory,
    revalidate: revalidateMemory,
    refreshAfterSetup: refreshMemoryAfterSetup,
  } = usePersonalMemory({ enabled: legacyMemoryEnabled });
  const {
    life: personalLife,
    loading: lifeLoading,
    refreshing: lifeRefreshing,
    rebuilding: lifeRebuilding,
    error: lifeError,
    reload: reloadLife,
    revalidate: revalidateLife,
    refreshAfterSetup: refreshLifeAfterSetup,
  } = usePersonalLife({ enabled: lifeEnabled });
  const loTemplateEnabled = templateMomentsEnabled(selectedMomentTypeCode);
  const isMyMoneyTemplate = isMyMoneyTemplateCode(selectedMomentTypeCode);
  const templateLifeEnabled = false;
  const templateMemoryEnabled =
    variant === "personal" && isMyMoneyTemplate && visibleTab === "memory";
  const {
    data: templateMoments,
    loading: templateMomentsLoading,
    refreshing: templateMomentsRefreshing,
    rebuilding: templateMomentsRebuilding,
    error: templateMomentsError,
    reload: reloadTemplateMoments,
    revalidate: revalidateTemplateMoments,
    refreshAfterSetup: refreshTemplateMomentsAfterSetup,
  } = useTemplateMoments(selectedMomentTypeCode, {
    enabled: momentsEnabled && loTemplateEnabled,
  });
  const { refreshAfterSetup: refreshTemplateLifeAfterSetup } = useTemplateLife(
    selectedMomentTypeCode,
    { enabled: templateLifeEnabled },
  );
  const {
    data: templateMemory,
    loading: templateMemoryLoading,
    refreshing: templateMemoryRefreshing,
    rebuilding: templateMemoryRebuilding,
    error: templateMemoryError,
    reload: reloadTemplateMemory,
    revalidate: revalidateTemplateMemory,
    refreshAfterSetup: refreshTemplateMemoryAfterSetup,
  } = useTemplateMemory(selectedMomentTypeCode, {
    enabled: templateMemoryEnabled,
  });

  const momentsProjectionRetried = useRef(false);
  const memoryProjectionRetried = useRef(false);
  useEffect(() => {
    if (
      templateMoments?.status === "ACTIVE" &&
      !templateMoments.moment_projection &&
      !templateMomentsLoading &&
      !momentsProjectionRetried.current &&
      !isInflight(`personal:template_moments:${selectedMomentTypeCode}`)
    ) {
      momentsProjectionRetried.current = true;
      void reloadTemplateMoments();
    }
    if (templateMoments?.moment_projection) {
      momentsProjectionRetried.current = false;
    }
  }, [templateMoments, templateMomentsLoading, reloadTemplateMoments, selectedMomentTypeCode]);

  useEffect(() => {
    if (
      templateMemory?.status === "ACTIVE" &&
      !templateMemory.memory_projection &&
      !templateMemoryLoading &&
      !memoryProjectionRetried.current &&
      !isInflight(`personal:template_memory:${selectedMomentTypeCode}`)
    ) {
      memoryProjectionRetried.current = true;
      void reloadTemplateMemory();
    }
    if (templateMemory?.memory_projection) {
      memoryProjectionRetried.current = false;
    }
  }, [templateMemory, templateMemoryLoading, reloadTemplateMemory, selectedMomentTypeCode]);

  useEffect(() => {
    if (variant !== "personal") return;
    const disk = warmUpPersonalSessionFromDisk(selectedMomentTypeCode);
    if (disk.pulse) seedPersonalPulseCache(selectedMomentTypeCode, disk.pulse);
    if (disk.moments) seedPersonalMomentsCache(selectedMomentTypeCode, disk.moments);
    if (disk.memory) seedPersonalMemoryCache(selectedMomentTypeCode, disk.memory);
    if (disk.life) seedPersonalLifeCache(disk.life);
    if (disk.templateMoments) seedTemplateMomentsCache(selectedMomentTypeCode, disk.templateMoments);
    if (disk.templateMemory) seedTemplateMemoryCache(selectedMomentTypeCode, disk.templateMemory);
  }, [variant, selectedMomentTypeCode]);

  const tabTitles: Record<BottomNavTabId, string> = {
    pulse: "Pulse",
    moments: "Moments",
    add: "Create",
    life: "Life",
    memory: "Memory",
  };

  async function openQuickAdd(eventType?: string | null) {
    setQuickAddEventType(eventType ?? null);
    setQuickAddResolvedMomentId(null);

    if (variant === "personal") {
      let gate = quickAddGate;
      if (!gate.hasActiveMoment) {
        logQuickAddGateBlocked(selectedMomentTypeCode, gate);
        setQuickAddWarm(true);
        setShowQuickAddSheet(true);
        return;
      }

      let momentId = gate.momentId ?? manageContext?.momentId ?? null;

      setQuickAddWarm(true);
      setShowQuickAddSheet(true);
      void prefetchQuickAddOptions(momentId ?? undefined);

      if (!momentId) {
        const createCards = createOptions?.cards ?? shellCreateOptions?.cards;
        if (createCards && personalMoments) {
          gate = resolveQuickAddGate({
            momentTypeCode: selectedMomentTypeCode,
            bootstrap,
            createCards,
            homeCards: personalMoments.cards,
            pulse: personalPulse,
            switcherOptions: resolveMomentSwitcherOptions(personalMoments, createCards),
            lifeOpsDetailMomentId: personalMoments.life_operations_detail?.moment_id,
          });
          momentId = gate.momentId ?? manageContext?.momentId ?? null;
          if (momentId) {
            setQuickAddResolvedMomentId(momentId);
            void prefetchQuickAddOptions(momentId);
            return;
          }
        }

        void (async () => {
          try {
            const [opts, home] = await Promise.all([
              fetchPersonalCreateOptions(),
              PersonalRepository.getMomentsHome(),
            ]);
            setShellCreateOptions(opts);
            gate = resolveQuickAddGate({
              momentTypeCode: selectedMomentTypeCode,
              bootstrap,
              createCards: opts.cards,
              homeCards: home.cards,
              pulse: personalPulse,
              switcherOptions: resolveMomentSwitcherOptions(home, opts.cards),
              lifeOpsDetailMomentId: home.life_operations_detail?.moment_id,
            });
            const resolved = gate.momentId ?? manageContext?.momentId ?? null;
            setQuickAddResolvedMomentId(resolved);
            if (resolved) void prefetchQuickAddOptions(resolved);
          } catch {
            // LifeOperationsQuickAddSheet can resolve moment from options API.
          }
        })();
        return;
      }

      setQuickAddResolvedMomentId(momentId);
      return;
    }

    setQuickAddWarm(true);
    setShowQuickAddSheet(true);
    if (variant === "business" && businessManageContext?.momentId) {
      void prefetchBusinessActionCatalog(businessManageContext.momentId);
    }
  }

  function showCreateStub() {
    alert("Create moment â€” coming soon");
  }

  function handleTabSelect(tab: BottomNavTabId) {
    if (tab !== "add") {
      void MomentraAnalytics.logCustomEvent("tab_select", {
        app_context: variant,
        tab,
      });
    }
    setPreviousTab(selectedTab);
    setSelectedTab(tab);
  }

  function currentOverlay(): ScreenOverlay {
    if (showMomentSetup) return "life_ops_setup";
    if (showCreateOverlay) return "create";
    if (editingActivity) return "life_ops_edit_activity";
    if (showMasterExpense) return "master_expense";
    if (showLifeOpsActivity) return "life_ops_activity";
    if (showQuickAddSheet) return "quick_add";
    return null;
  }

  function openMasterExpense() {
    void MomentraAnalytics.logCustomEvent("master_expense_fab_tap", {
      app_context: variant,
      tab: selectedTab === "add" ? previousTab : selectedTab,
    });
    setShowMasterExpense(true);
  }

  useEffect(() => {
    if (variant !== "personal") return;
    if (showMomentSetup) return;
    const screen = resolveScreen("personal", visibleTab, bootstrap);
    const needsCreateOptions = isSetupScreen(screen) || showCreateOverlay;
    if (!needsCreateOptions) {
      return;
    }
    setLoadingShellCreateOptions(true);
    void fetchPersonalCreateOptions()
      .then(setShellCreateOptions)
      .catch(() => setShellCreateOptions(null))
      .finally(() => setLoadingShellCreateOptions(false));
  }, [variant, visibleTab, bootstrap, showCreateOverlay, showMomentSetup, selectedMomentTypeCode]);

  // Business open: shell owns ensureBusinessBootstrap. Retry forces a recovery load.
  // Warm action catalog when inventory is ready â€” do not re-bootstrap on every mount.
  useEffect(() => {
    if (!businessSessionEnabled) return;
    let cancelled = false;
    void (async () => {
      if (businessSessionRetryKey > 0) {
        await ensureBusinessBootstrap(true);
      }
      if (cancelled) return;
      const sessionBootstrap = getBusinessSessionSnapshot().bootstrap;
      if (!sessionBootstrap) return;
      const moments = sessionBootstrap.moments ?? [];
      const hasActive = moments.some((m) => {
        const status = (m.status || "").toUpperCase();
        return !status || status === "ACTIVE" || status === "PAUSED";
      });
      const cards = sessionBootstrap.moments_home?.cards ?? [];
      const hasActiveLinked =
        hasActive ||
        cards.some((c) => {
          const status = (c.linked_moment_status || "").toUpperCase();
          return (
            Boolean(c.linked_moment_id) &&
            (status === "ACTIVE" || status === "PAUSED")
          );
        });
      if (hasActiveLinked) {
        const current = getBootstrap();
        const businessCtx = contextStateFromBootstrap(current, "business");
        if (!current || businessCtx === "EMPTY") {
          invalidateBootstrapAfterMutation();
        }
      }
      const snap = getBusinessSessionSnapshot();
      const invMoments = snap.bootstrap?.moments ?? [];
      const invHome = snap.bootstrap?.moments_home;
      const invEmpty =
        invHome?.is_empty === true ||
        (typeof invHome?.active_moment_count === "number" &&
          invHome.active_moment_count === 0) ||
        invMoments.length === 0;
      const mid = invEmpty ? null : snap.selectedMomentId;
      if (mid) void prefetchBusinessActionCatalog(mid);
    })();
    return () => {
      cancelled = true;
    };
  }, [businessSessionEnabled, businessSessionRetryKey, businessBootstrap]);

  // Lazy create-options: Personal overlay + Business Create only.
  useEffect(() => {
    if (!showCreateOverlay) return;
    if (variant === "personal") {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- loading state for async create options
      setLoadingCreateOptions(true);
      setCreateError(null);
      void fetchPersonalCreateOptions()
        .then((options) => {
          setCreateOptions(options);
          setShellCreateOptions(options);
        })
        .catch(() => setCreateOptions(null))
        .finally(() => setLoadingCreateOptions(false));
      return;
    }
    if (variant === "business") {
      void ensureBusinessCreateOptions();
    }
  }, [showCreateOverlay, variant]);

  const activeCard = activeCardForType(
    createOptions?.cards ?? shellCreateOptions?.cards ?? [],
    selectedMomentTypeCode,
  );
  const typeLabel = momentTypeLabel(selectedMomentTypeCode);
  const momentSwitcherOptions = resolveMomentSwitcherOptions(
    personalMoments,
    createOptions?.cards ?? shellCreateOptions?.cards,
  );
  const hideScreenHeader = momentSwitcherOptions.length > 0;
  const manageContext: PersonalMomentManageContext | null = resolvePersonalMomentManageContext(
    selectedMomentTypeCode,
    createOptions?.cards ?? shellCreateOptions?.cards ?? [],
    personalMoments?.cards,
  );

  const quickAddGate = useMemo(
    () =>
      resolveQuickAddGate({
        momentTypeCode: selectedMomentTypeCode,
        bootstrap,
        createCards: createOptions?.cards ?? shellCreateOptions?.cards ?? [],
        homeCards: personalMoments?.cards,
        pulse: personalPulse,
        switcherOptions: momentSwitcherOptions,
        lifeOpsDetailMomentId: personalMoments?.life_operations_detail?.moment_id,
      }),
    [
      selectedMomentTypeCode,
      bootstrap,
      createOptions?.cards,
      shellCreateOptions?.cards,
      personalMoments?.cards,
      personalMoments?.life_operations_detail?.moment_id,
      personalPulse,
      momentSwitcherOptions,
    ],
  );


  const businessSwitcherOptions = resolveBusinessMomentSwitcherOptions(
    businessBootstrap?.moments_home?.cards ?? [],
    businessCreateOptions?.cards ?? [],
    businessBootstrap?.moments ?? [],
  );

  const businessManageContext = resolveBusinessMomentManageContext(
    selectedBusinessMomentType,
    businessCreateOptions?.cards ?? [],
    businessBootstrap?.moments_home?.cards ?? [],
    businessBootstrap?.moments ?? [],
  );

  useEffect(() => {
    if (businessSwitcherOptions.length === 0) return;
    // Empty inventory: never re-bind from stale linked cards after delete-all.
    const moments = businessBootstrap?.moments ?? [];
    const home = businessBootstrap?.moments_home;
    const inventoryEmpty =
      home?.is_empty === true ||
      (typeof home?.active_moment_count === "number" && home.active_moment_count === 0) ||
      moments.length === 0;
    if (inventoryEmpty) return;
    // Inventory already validated selection in the store; only sync if store empty
    // and switcher has options (card fallback path without moments[]).
    if (selectedBusinessMomentId) return;
    const next = resolveSelectedBusinessMoment(
      businessSwitcherOptions,
      selectedBusinessMomentType,
      selectedBusinessMomentId,
    );
    if (next.typeCode !== selectedBusinessMomentType || next.momentId !== selectedBusinessMomentId) {
      setBusinessSelection(next.typeCode, next.momentId);
    }
  }, [
    businessSwitcherOptions,
    selectedBusinessMomentType,
    selectedBusinessMomentId,
    businessBootstrap,
  ]);

  // Empty inventory wins over ghost selection (deleted/archived last moment).
  useEffect(() => {
    if (variant !== "business" || !businessBootstrap) return;
    const moments = businessBootstrap.moments ?? [];
    const home = businessBootstrap.moments_home;
    const inventoryEmpty =
      home?.is_empty === true ||
      (typeof home?.active_moment_count === "number" && home.active_moment_count === 0) ||
      moments.length === 0;
    if (!inventoryEmpty) return;
    if (selectedBusinessMomentId) {
      setBusinessSelection(selectedBusinessMomentType || "", null);
    }
  }, [variant, businessBootstrap, selectedBusinessMomentId, selectedBusinessMomentType]);

  async function refreshAfterManage(opts?: { skipBootstrapInvalidate?: boolean }) {
    if (variant === "business") {
      // Business variant shouldn't use this path - they use refreshAfterBusinessManage
      // But keep this guard for safety
      if (!opts?.skipBootstrapInvalidate) {
        invalidateBootstrapAfterMutation();
      }
      const options = await fetchPersonalCreateOptions(true);
      setCreateOptions(options);
      setShellCreateOptions(options);
      await refreshAfterSetup();
      await refreshMomentsAfterSetup();
      await refreshMemoryAfterSetup();
      await refreshLifeAfterSetup();
      await refreshTemplateMomentsAfterSetup();
      await refreshTemplateLifeAfterSetup();
      await refreshTemplateMemoryAfterSetup();
      return;
    }
    // Personal soft path:
    void opts;
    await ensurePersonalCreateOptions(true);
    await refreshPersonalSessionInventory(false);
    // Only refresh the visible tab's force reload, not all 7:
    if (visibleTab === "pulse") await refreshAfterSetup();
    else if (visibleTab === "moments") await refreshMomentsAfterSetup();
    else if (visibleTab === "memory") {
      await refreshMemoryAfterSetup();
      await refreshTemplateMemoryAfterSetup();
    } else if (visibleTab === "life") await refreshLifeAfterSetup();
  }


  async function refreshAfterBusinessManage(opts?: {
    momentId?: string | null;
    momentTypeCode?: string | null;
  }) {
    await refreshBusinessSessionInventory(false);
    const snap = getBusinessSessionSnapshot();
    const moments = snap.bootstrap?.moments ?? [];
    const home = snap.bootstrap?.moments_home;
    const inventoryEmpty =
      home?.is_empty === true ||
      (typeof home?.active_moment_count === "number" && home.active_moment_count === 0) ||
      moments.length === 0;

    const momentId =
      opts?.momentId !== undefined
        ? opts.momentId
        : snap.selectedMomentId || null;
    const typeCode =
      opts?.momentTypeCode ||
      snap.selectedMomentType ||
      "TEAM_OPERATIONS";

    if (inventoryEmpty || !momentId) {
      setBusinessSelection(typeCode || "", null);
      invalidateBootstrapAfterMutation();
      return;
    }

    setBusinessSelection(typeCode, momentId);
    void prefetchBusinessActionCatalog(momentId);
    const code = typeCode.toUpperCase();
    if (code === "BUSINESS_RUNWAY") setRunwayReloadKey((k) => k + 1);
    else if (code === "BUSINESS_OPERATIONS" || code === "DEPARTMENT_OPERATIONS") {
      setOpsReloadKey((k) => k + 1);
    } else setTeamOpsReloadKey((k) => k + 1);
  }

  /** Soft inventory reconcile after setup GET â€” do not force full bootstrap. */
  function refreshBusinessSessionAfterSetupReady() {
    void refreshBusinessSessionInventory(false).then(() => {
      markBusinessSetupBootstrapDone();
    });
  }

  function handleBusinessMomentSwitcherSelect(option: {
    typeCode: string;
    momentId?: string | null;
  }) {
    setBusinessSelection(option.typeCode, option.momentId ?? null);
  }

  function handleMomentSwitcherSelect(option: PersonalMomentSwitcherOption) {
    if (option.typeCode === selectedMomentTypeCode) return;
    setPersonalMomentType(option.typeCode);
    setSelectedMomentTypeCode(option.typeCode);
  }

  async function archivePersonalMomentOption(option: PersonalMomentSwitcherOption) {
    if (!option.momentId) return;
    if (!confirm(`Archive ${option.label}? This removes it from your active list.`)) return;
    if (option.typeCode !== selectedMomentTypeCode) {
      setPersonalMomentType(option.typeCode);
      setSelectedMomentTypeCode(option.typeCode);
    }
    const inventory: LifecycleInventoryItem[] = (createOptions?.cards ?? [])
      .filter((c) => c.linked_moment_id)
      .map((c) => ({
        momentId: c.linked_moment_id as string,
        momentTypeCode: c.moment_type_code,
        status: c.linked_moment_status || "ACTIVE",
      }));
    try {
      await runMomentLifecycle({
        contextType: "PERSONAL",
        momentId: option.momentId,
        momentTypeCode: option.typeCode,
        action: "archive",
        previousStatus: "ACTIVE",
        inventory,
        selectedMomentId: option.momentId,
      });
      await refreshAfterManage({ skipBootstrapInvalidate: true });
    } catch (e) {
      alert(e instanceof MomentLifecycleError ? e.userMessage : "Could not archive moment");
    }
  }

  async function archiveBusinessMomentOption(option: BusinessMomentSwitcherOption) {
    if (!option.momentId) return;
    if (!confirm(`Archive ${option.label}? This removes it from your active list.`)) return;
    if (
      option.typeCode !== selectedBusinessMomentType ||
      option.momentId !== selectedBusinessMomentId
    ) {
      setBusinessSelection(option.typeCode, option.momentId);
    }
    const snap = getBusinessSessionSnapshot();
    const inventory: LifecycleInventoryItem[] = (snap.bootstrap?.moments ?? []).map((m) => ({
      momentId: m.moment_id,
      momentTypeCode: m.moment_type_code || "",
      status: m.status || "ACTIVE",
    }));
    try {
      const result = await runMomentLifecycle(
        {
          contextType: "BUSINESS",
          momentId: option.momentId,
          momentTypeCode: option.typeCode,
          action: "archive",
          previousStatus: "ACTIVE",
          inventory,
          selectedMomentId: snap.selectedMomentId,
        },
        {
          onOptimistic: ({ replacementMomentId, replacementMomentTypeCode }) => {
            if (replacementMomentId) {
              setBusinessSelection(
                replacementMomentTypeCode || option.typeCode,
                replacementMomentId,
              );
            } else {
              setBusinessSelection(option.typeCode, null);
            }
          },
        },
      );
      await refreshAfterBusinessManage({
        momentId: result.replacementMomentId,
        momentTypeCode: result.replacementMomentTypeCode,
      });
    } catch (e) {
      alert(e instanceof MomentLifecycleError ? e.userMessage : "Could not archive moment");
    }
  }

  useEffect(() => {
    if (!holdReconcileTypeCode) return;
    if (momentSwitcherOptions.some((o) => o.typeCode === holdReconcileTypeCode)) {
      setHoldReconcileTypeCode(null);
    }
  }, [momentSwitcherOptions, holdReconcileTypeCode]);

  useEffect(() => {
    if (momentSwitcherOptions.length === 0) return;
    const next = reconcileSelectedMomentType(
      momentSwitcherOptions,
      selectedMomentTypeCode,
      holdReconcileTypeCode,
    );
    if (next !== selectedMomentTypeCode) {
      setSelectedMomentTypeCode(next);
    }
  }, [momentSwitcherOptions, selectedMomentTypeCode, holdReconcileTypeCode]);

  function wrapTabWithOfflineRefresh(
    content: ReactNode,
    opts: {
      hasCache: boolean;
      busy: boolean;
      hasError: boolean;
      onRefresh: () => void | Promise<void>;
    },
  ) {
    return (
      <>
        <OfflineBanner visible={opts.hasCache && opts.busy && opts.hasError} />
        <PullToRefresh onRefresh={() => void opts.onRefresh()}>{content}</PullToRefresh>
      </>
    );
  }

  function wrapMomentsTab(content: ReactNode) {
    return wrapTabWithOfflineRefresh(content, {
      hasCache: loTemplateEnabled ? Boolean(templateMoments) : Boolean(personalMoments),
      busy: loTemplateEnabled ? templateMomentsLoading : momentsLoading,
      hasError: loTemplateEnabled ? Boolean(templateMomentsError) : Boolean(momentsError),
      onRefresh: () => (loTemplateEnabled ? reloadTemplateMoments() : reloadMoments()),
    });
  }

  function wrapLifeTab(content: ReactNode) {
    return wrapTabWithOfflineRefresh(content, {
      hasCache: Boolean(personalLife),
      busy: lifeLoading,
      hasError: Boolean(lifeError),
      onRefresh: () => reloadLife(),
    });
  }

  function wrapMemoryTab(content: ReactNode) {
    return wrapTabWithOfflineRefresh(content, {
      hasCache: isMyMoneyTemplate ? Boolean(templateMemory) : Boolean(personalMemory),
      busy: isMyMoneyTemplate ? templateMemoryLoading : memoryLoading,
      hasError: isMyMoneyTemplate ? Boolean(templateMemoryError) : Boolean(memoryError),
      onRefresh: () => (isMyMoneyTemplate ? reloadTemplateMemory() : reloadMemory()),
    });
  }

  const lifeOpsActivityMomentId =
    activeCard?.linked_moment_id ??
    manageContext?.momentId ??
    quickAddGate.momentId ??
    templateMoments?.moment?.moment_id ??
    personalPulse?.life_operations?.dashboard_card?.moment_id ??
    null;

  function wrapPersonalTabWithHeader(tabLabel: string, content: ReactNode) {
    if (momentSwitcherOptions.length === 0) return content;
    return (
      <div className="flex min-h-0 flex-1 flex-col">
        <PersonalMomentHeader
          tabLabel={tabLabel}
          options={momentSwitcherOptions}
          selectedTypeCode={selectedMomentTypeCode}
          onSelect={handleMomentSwitcherSelect}
          onManageClick={
            manageContext ? () => setShowManageSheet(true) : undefined
          }
          onDeleteMoment={(option) => {
            void archivePersonalMomentOption(option);
          }}
        />
        <div className="flex min-h-0 flex-1 flex-col overflow-hidden">{content}</div>
      </div>
    );
  }

  function openMomentSetup(momentId: string, typeCode: PersonalMomentTypeCode) {
    setSetupMomentId(momentId);
    setSetupTypeCode(typeCode);
    setShowMomentSetup(true);
    setShowCreateOverlay(true);
  }

  function openActiveMomentPulse(typeCode: PersonalMomentTypeCode) {
    setPersonalMomentType(typeCode);
    setShowCreateOverlay(false);
    setShowMomentSetup(false);
    setSetupMomentId(null);
    setPreviousTab(selectedTab);
    setSelectedTab("pulse");
    void softRefreshPersonalSession();
  }

  function continueDraftSetup(card: PersonalCreateOptionCard) {
    if (!card.linked_moment_id) return;
    setSelectedMomentTypeCode(card.moment_type_code as PersonalMomentTypeCode);
    openMomentSetup(card.linked_moment_id, card.moment_type_code as PersonalMomentTypeCode);
  }

  async function handleBeginMoment(typeCode: PersonalMomentTypeCode) {
    setCreateError(null);
    setCreatingTypeCode(typeCode);
    const card = activeCardForType(
      createOptions?.cards ?? shellCreateOptions?.cards ?? [],
      typeCode,
    );
    try {
      if (card?.has_draft && card.linked_moment_id && card.linked_moment_status === "DRAFT") {
        setSelectedMomentTypeCode(typeCode);
        openMomentSetup(card.linked_moment_id, typeCode);
        return;
      }

      if (card?.linked_moment_id && isActiveMoment(card)) {
        openActiveMomentPulse(typeCode);
        return;
      }

      const moment = await SetupRepository.createDraft({ moment_type_code: typeCode });
      patchPersonalDraftCreated(typeCode, moment.moment_id);
      setSelectedMomentTypeCode(typeCode);

      if (moment.status === "DRAFT") {
        openMomentSetup(moment.moment_id, typeCode);
        return;
      }

      if (moment.status === "ACTIVE" || moment.status === "PAUSED" || moment.status === "COMPLETED") {
        openActiveMomentPulse(typeCode);
        return;
      }

      setCreateError(`Unable to start ${momentTypeLabel(typeCode)}. Please try again.`);
    } catch (err) {
      setCreateError(err instanceof ApiError ? err.message : "Failed to create moment");
    } finally {
      setCreatingTypeCode(null);
    }
  }

  function closeMomentSetup() {
    setShowMomentSetup(false);
    setSetupMomentId(null);
  }

  async function handleMomentActivated() {
    const activatedType = setupTypeCode;
    const activatedId = setupMomentId;
    setHoldReconcileTypeCode(setupTypeCode);
    closeMomentSetup();
    setShowCreateOverlay(false);
    setPreviousTab(selectedTab);
    setSelectedTab("pulse");
    if (activatedId && activatedType) {
      patchPersonalMomentActivated(activatedType, activatedId);
      invalidatePersonalPulseCache(activatedType);
      invalidatePersonalMomentsCache(activatedType);
      invalidatePersonalMemoryCache(activatedType);
    }
    void softRefreshPersonalSession();
    void ensurePersonalCreateOptions(true);
  }

  useEffect(() => {
    if (!pendingMomentType || loadingCreateOptions || !createOptions) return;
    const typeCode = pendingMomentType;
    // eslint-disable-next-line react-hooks/set-state-in-effect -- clear pending action before handling
    setPendingMomentType(null);
    void handleBeginMoment(typeCode);
  }, [pendingMomentType, loadingCreateOptions, createOptions, handleBeginMoment]);

  useEffect(() => {
    const overlay = currentOverlay();
    const screenName = resolveScreenName(variant, selectedTab, overlay, previousTab);
    void MomentraAnalytics.logScreen(screenName, variant);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- currentOverlay is a stable function; only external UI state matters
  }, [variant, selectedTab, previousTab, showCreateOverlay, showQuickAddSheet, showMomentSetup, showLifeOpsActivity, editingActivity]);

  useEffect(() => {
    if (showQuickAddSheet) {
      void MomentraAnalytics.logCustomEvent("quick_add_open", { app_context: variant });
    }
  }, [showQuickAddSheet, variant]);

  function openCreateOverlay() {
    const screenName = resolveScreenName(variant, selectedTab, null, previousTab);
    void MomentraAnalytics.logCustomEvent("create_moment_tap", {
      app_context: variant,
      screen: screenName,
    });
    setShowCreateOverlay(true);
  }

  function beginMomentFromMoments(typeCode: PersonalMomentTypeCode = selectedMomentTypeCode) {
    const screenName = resolveScreenName(variant, selectedTab, null, previousTab);
    void MomentraAnalytics.logCustomEvent("create_moment_tap", {
      app_context: variant,
      screen: screenName,
      entry: "moments",
      moment_type: typeCode,
    });
    setPendingMomentType(typeCode);
    setShowCreateOverlay(true);
  }

  useEffect(() => {
    const openCreate = () => setShowCreateOverlay(true);
    const selectLife = () => {
      setPreviousTab(selectedTab);
      setSelectedTab("life");
    };
    window.addEventListener(LIFE360_SELECT_LIFE_TAB_EVENT, selectLife);
    if (variant === "personal") {
      window.addEventListener(PERSONAL_CREATE_OPEN_EVENT, openCreate);
      return () => {
        window.removeEventListener(PERSONAL_CREATE_OPEN_EVENT, openCreate);
        window.removeEventListener(LIFE360_SELECT_LIFE_TAB_EVENT, selectLife);
      };
    }
    if (variant === "business") {
      const selectPulse = () => {
        setSelectedTab("pulse");
        setPreviousTab("pulse");
      };
      const openMoment = (event: Event) => {
        const detail = (event as CustomEvent<{ momentId?: string; typeCode?: string }>).detail;
        const momentId = detail?.momentId?.trim();
        const typeCode = (detail?.typeCode ?? "").trim();
        if (!momentId) return;
        setBusinessSelection(typeCode, momentId);
        selectPulse();
      };
      window.addEventListener(BUSINESS_CREATE_OPEN_EVENT, openCreate);
      window.addEventListener(BUSINESS_SELECT_PULSE_EVENT, selectPulse);
      window.addEventListener(BUSINESS_OPEN_MOMENT_EVENT, openMoment);
      return () => {
        window.removeEventListener(BUSINESS_CREATE_OPEN_EVENT, openCreate);
        window.removeEventListener(BUSINESS_SELECT_PULSE_EVENT, selectPulse);
        window.removeEventListener(BUSINESS_OPEN_MOMENT_EVENT, openMoment);
        window.removeEventListener(LIFE360_SELECT_LIFE_TAB_EVENT, selectLife);
      };
    }
    return () => window.removeEventListener(LIFE360_SELECT_LIFE_TAB_EVENT, selectLife);
  }, [variant, selectedTab]);

  const bottomPadding = tokens.spacing.bottomNavHeight + tokens.spacing.md;

  const personalFabVisible =
    variant === "personal" &&
    !showMasterExpense &&
    !showQuickAddSheet &&
    !showCreateOverlay &&
    !showMomentSetup &&
    !showLifeOpsActivity &&
    !editingActivity &&
    (visibleTab === "pulse" ||
      visibleTab === "moments" ||
      visibleTab === "life" ||
      visibleTab === "memory");

  const showBusinessManageHeader =
    variant === "business" &&
    businessSwitcherOptions.length > 0 &&
    (visibleTab === "pulse" ||
      visibleTab === "moments" ||
      visibleTab === "memory" ||
      visibleTab === "life");

  function bumpTeamOpsProjections(
    optimistic?: TeamOpsEventItem,
    opts?: { skipHardInvalidate?: boolean },
  ) {
    if (optimistic) {
      setTeamOpsOptimistic((prev) => [optimistic, ...prev].slice(0, 5));
    }
    if (opts?.skipHardInvalidate) {
      softInvalidateBusinessAggCaches(businessUserId);
    } else if (businessManageContext?.momentId) {
      invalidateBusinessActiveCaches(businessManageContext.momentId, businessUserId);
    } else {
      invalidateBusinessActiveCaches(undefined, businessUserId);
    }
    setTeamOpsReloadKey((k) => k + 1);
  }

  function bumpRunwayProjections(
    optimistic?: TeamOpsEventItem,
    opts?: { skipHardInvalidate?: boolean },
  ) {
    if (optimistic) {
      setRunwayOptimistic((prev) => [optimistic, ...prev].slice(0, 5));
    }
    if (opts?.skipHardInvalidate) {
      softInvalidateBusinessAggCaches(businessUserId);
    } else if (businessManageContext?.momentId) {
      invalidateBusinessActiveCaches(businessManageContext.momentId, businessUserId);
    } else {
      invalidateBusinessActiveCaches(undefined, businessUserId);
    }
    setRunwayReloadKey((k) => k + 1);
  }

  function bumpOpsProjections(
    optimistic?: TeamOpsEventItem,
    opts?: { skipHardInvalidate?: boolean },
  ) {
    if (optimistic) {
      setOpsOptimistic((prev) => [optimistic, ...prev].slice(0, 5));
    }
    if (opts?.skipHardInvalidate) {
      softInvalidateBusinessAggCaches(businessUserId);
    } else if (businessManageContext?.momentId) {
      invalidateBusinessActiveCaches(businessManageContext.momentId, businessUserId);
    } else {
      invalidateBusinessActiveCaches(undefined, businessUserId);
    }
    setOpsReloadKey((k) => k + 1);
  }

  useEffect(() => {
    if (teamOpsReloadKey === 0) return;
    const t = window.setTimeout(() => setTeamOpsOptimistic([]), 2000);
    return () => window.clearTimeout(t);
  }, [teamOpsReloadKey]);

  useEffect(() => {
    if (runwayReloadKey === 0) return;
    const t = window.setTimeout(() => setRunwayOptimistic([]), 2000);
    return () => window.clearTimeout(t);
  }, [runwayReloadKey]);

  useEffect(() => {
    if (opsReloadKey === 0) return;
    const t = window.setTimeout(() => setOpsOptimistic([]), 2000);
    return () => window.clearTimeout(t);
  }, [opsReloadKey]);


  const tabBarProps = {
    variant,
    selectedTab: visibleTab,
    onTabSelect: handleTabSelect,
    onCreateMoment: () => {
      if (variant === "personal" || variant === "business") {
        openQuickAdd(null);
        setSelectedTab(previousTab);
      } else {
        showCreateStub();
      }
    },
  };

  function renderPersonalPulse() {
    const screen = resolveScreen("personal", "pulse", bootstrap);
    const hasCachedActiveSession =
      isActiveMoment(activeCard) ||
      hasActiveMoment ||
      createOptionsHydrating ||
      Boolean(personalPulse && pulseHasTypePayload(personalPulse, selectedMomentTypeCode)) ||
      Boolean(
        getPersonalPulseCache(selectedMomentTypeCode) &&
          pulseHasTypePayload(getPersonalPulseCache(selectedMomentTypeCode)!, selectedMomentTypeCode),
      ) ||
      Boolean(
        personalMoments &&
          momentsHasTypePayload(personalMoments, selectedMomentTypeCode),
      ) ||
      Boolean(
        getPersonalMomentsCache(selectedMomentTypeCode) &&
          momentsHasTypePayload(
            getPersonalMomentsCache(selectedMomentTypeCode)!,
            selectedMomentTypeCode,
          ),
      ) ||
      Boolean(templateMoments?.moment_projection) ||
      Boolean(getTemplateMomentsCache(selectedMomentTypeCode)?.moment_projection) ||
      Boolean(getTemplateMemoryCache(selectedMomentTypeCode)?.memory_projection) ||
      hasTypeSessionCacheHint(selectedMomentTypeCode);
    if (screen === "loading") {
      return pulseSkeletonForType(selectedMomentTypeCode, { bottomPadding });
    }
    if (isEmptyScreen(screen) && !hasCachedActiveSession) {
      if (createOptionsHydrating || (pulseLoading && !personalPulse)) {
        return pulseSkeletonForType(selectedMomentTypeCode, { bottomPadding });
      }
      return <PersonalPulseEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
    }

    const hasDraft = isDraftMoment(activeCard);
    const hasActive = isActiveMoment(activeCard);

    if (isSetupScreen(screen) && hasDraft && activeCard) {
      return (
        <PersonalPulseEmpty
          mode="draft_resume"
          momentTypeLabel={typeLabel}
          onCreateMoment={openCreateOverlay}
          onContinueSetup={() => continueDraftSetup(activeCard)}
          bottomPadding={bottomPadding}
        />
      );
    }

    if (personalPulse && !personalPulse.is_empty && pulseHasTypePayload(personalPulse, selectedMomentTypeCode)) {
      switch (selectedMomentTypeCode) {
        case "FUTURE_BUILDING":
          return personalPulse.future_building?.metrics ? (
            <FutureBuildingPulse
              pulse={personalPulse.future_building}
              bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
              onQuickAdd={(eventType) => openQuickAdd(eventType)}
              onViewAllActivity={() => setShowLifeOpsActivity(true)}
              onEditActivity={(id, eventType) => setEditingActivity({ id, eventType })}
            />
          ) : personalPulse.future_building ? (
            <FutureBuildingPulseSkeleton bottomPadding={bottomPadding} />
          ) : null;
        case "LIFESTYLE":
          return personalPulse.lifestyle ? (
            <LifestylePulse
              pulse={personalPulse.lifestyle}
              bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
              onQuickAdd={(eventType) => openQuickAdd(eventType)}
              onViewAllActivity={() => setShowLifeOpsActivity(true)}
              onEditActivity={(id, eventType) => setEditingActivity({ id, eventType })}
            />
          ) : null;
        case "RELATIONSHIPS":
          return personalPulse.emotional_security?.metrics ? (
            <RelationshipsPulse
              pulse={personalPulse.emotional_security}
              bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
              onQuickAdd={(eventType) => openQuickAdd(eventType)}
              onViewAllActivity={() => setShowLifeOpsActivity(true)}
              onEditActivity={(id, eventType) => setEditingActivity({ id, eventType })}
            />
          ) : personalPulse.emotional_security ? (
            <RelationshipsPulseSkeleton bottomPadding={bottomPadding} />
          ) : null;
        default:
          if (!shouldRenderActivePulseDashboard("LIFE_OPERATIONS")) return null;
          return (
            <SkeletonCrossfade
              showSkeleton={(pulseLoading || pulseRefreshing || pulseRebuilding) && !personalPulse.life_operations?.metrics}
              skeleton={<LifeOperationsPulseSkeleton />}
            >
              {personalPulse.life_operations ? (
                <LifeOperationsPulse
                  pulse={personalPulse.life_operations}
                  bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
                  onQuickAdd={(eventType) => openQuickAdd(eventType)}
                  onViewAllActivity={() => setShowLifeOpsActivity(true)}
                  onEditActivity={(id, eventType) => setEditingActivity({ id, eventType })}
                  onRetryLoad={() => void reloadPulse()}
                />
              ) : (
                <LifeOperationsPulseSkeleton />
              )}
            </SkeletonCrossfade>
          );
      }
    }

    if (pulseLoading && !personalPulse && !pulseRefreshing) {
      return pulseSkeletonForType(selectedMomentTypeCode, { bottomPadding });
    }

    if (hasActive && (pulseLoading || pulseRefreshing || pulseRebuilding)) {
      return pulseSkeletonForType(selectedMomentTypeCode, { bottomPadding });
    }

    if (pulseError && !hasDraft && (!personalPulse || personalPulse.is_empty || !pulseHasTypePayload(personalPulse, selectedMomentTypeCode))) {
      return (
        <div
          className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
          style={{ paddingBottom: bottomPadding }}
        >
          <p className="text-center text-sm" style={{ color: tokens.colors.error }}>
            {pulseError}
          </p>
          <button
            type="button"
            onClick={() => void reloadPulse()}
            className="rounded-xl px-6 py-2 text-sm font-semibold"
            style={{
              background: tokens.colors.primaryContainer,
              color: tokens.colors.brandOnPrimary,
            }}
          >
            Retry
          </button>
        </div>
      );
    }

    if (hasDraft && activeCard) {
      return (
        <PersonalPulseEmpty
          mode="draft_resume"
          momentTypeLabel={typeLabel}
          onCreateMoment={openCreateOverlay}
          onContinueSetup={() => continueDraftSetup(activeCard)}
          bottomPadding={bottomPadding}
        />
      );
    }

    // ACTIVE inventory but settled without usable pulse payload â€” Retry, never infinite skeleton.
    if (
      hasActive &&
      !pulseLoading &&
      !pulseRefreshing &&
      !pulseRebuilding &&
      (!personalPulse ||
        personalPulse.is_empty ||
        !pulseHasTypePayload(personalPulse, selectedMomentTypeCode))
    ) {
      return (
        <div
          className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
          style={{ paddingBottom: bottomPadding }}
        >
          <p className="text-center text-sm" style={{ color: tokens.colors.textSecondary }}>
            Your moment is active. Pulse is still preparing â€” tap Retry if this takes too long.
          </p>
          <button
            type="button"
            onClick={() => void reloadPulse()}
            className="rounded-xl px-6 py-2 text-sm font-semibold"
            style={{
              background: tokens.colors.primaryContainer,
              color: tokens.colors.brandOnPrimary,
            }}
          >
            Retry
          </button>
        </div>
      );
    }

    return <PersonalPulseEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />;
  }

  function renderPersonalMoments() {
    const hasDraft = isDraftMoment(activeCard);
    const hasActive = isActiveMoment(activeCard);
    const momentsBusy =
      momentsLoading ||
      momentsRefreshing ||
      momentsRebuilding ||
      templateMomentsLoading ||
      templateMomentsRefreshing ||
      templateMomentsRebuilding;

    const momentsPreparingRetry = (
      <div
        className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
        style={{ paddingBottom: bottomPadding }}
      >
        <p className="text-center text-sm" style={{ color: tokens.colors.textSecondary }}>
          Your moment is active. Moments is still preparing â€” tap Retry if this takes too long.
        </p>
        <button
          type="button"
          onClick={() => void (loTemplateEnabled ? reloadTemplateMoments() : reloadMoments())}
          className="rounded-xl px-6 py-2 text-sm font-semibold"
          style={{
            background: tokens.colors.primaryContainer,
            color: tokens.colors.brandOnPrimary,
          }}
        >
          Retry
        </button>
      </div>
    );

    if (loTemplateEnabled && (hasActive || templateMoments)) {
      if (templateMoments?.status === "ACTIVE") {
        if (selectedMomentTypeCode === "FUTURE_BUILDING") {
          const projection = templateMoments.moment_projection;
          const detail = projection
            ? { metrics: projection }
            : personalMoments?.future_building_detail;
          if (detail?.metrics?.journey_hero && detail.metrics.money_journey) {
            return (
              <FutureBuildingMoments
                detail={detail as import("@/lib/api/personalDomainTypes").PersonalFutureBuildingMomentDetail}
                bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (detail && !momentsBusy) {
            return momentsPreparingRetry;
          }
          if (detail?.metrics) {
            return <FutureBuildingMomentsSkeleton bottomPadding={bottomPadding} />;
          }
        }
        if (selectedMomentTypeCode === "LIFESTYLE") {
          const projection = templateMoments.moment_projection;
          const detail = projection
            ? { metrics: projection }
            : personalMoments?.lifestyle_detail;
          if (detail?.metrics?.journey_hero && detail.metrics.money_journey) {
            return (
              <LifestyleMoments
                detail={detail as import("@/lib/api/personalDomainTypes").PersonalLifestyleMomentDetail}
                bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (detail && !momentsBusy) {
            return momentsPreparingRetry;
          }
          if (detail?.metrics) {
            return <LifestyleMomentsSkeleton bottomPadding={bottomPadding} />;
          }
        }
        if (selectedMomentTypeCode === "RELATIONSHIPS") {
          const projection = templateMoments.moment_projection;
          const detail = projection
            ? { metrics: projection }
            : personalMoments?.emotional_security_detail;
          if (detail?.metrics?.journey_hero) {
            return (
              <RelationshipsMoments
                detail={detail as import("@/lib/api/personalDomainTypes").PersonalEmotionalSecurityMomentDetail}
                bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (detail && !momentsBusy) {
            return momentsPreparingRetry;
          }
          if (detail?.metrics) {
            return <RelationshipsMomentsSkeleton bottomPadding={bottomPadding} />;
          }
        }
        if (!templateMoments.moment_projection) {
          if (selectedMomentTypeCode === "LIFE_OPERATIONS") {
            const legacyMetrics = personalMoments?.life_operations_detail?.metrics;
            if (legacyMetrics) {
              return (
                <LifeOperationsMoments
                  data={{
                    moment_type_code: "LIFE_OPERATIONS",
                    status: "ACTIVE",
                    moment: null,
                    moment_projection: legacyMetrics,
                    setup_summary: { pressure_sources: [], recovery_supports: [], runtime_priorities: [], identity_chips: [] },
                    recent_events: [],
                    accounts_summary: { total_accounts: 0, active_accounts: 0, accounts: [] },
                    timeline_count: 0,
                    last_activity_at: null,
                    progress: { label: "", subtitle: "", blocks: [] },
                  }}
                  bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
                  onManage={() => setShowManageSheet(true)}
                />
              );
            }
          }
          if (momentsProjectionRetried.current && !momentsBusy) {
            return (
              <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6" style={{ paddingBottom: bottomPadding }}>
                <p className="text-sm opacity-70">Couldn&apos;t load your moments journey.</p>
                <button type="button" onClick={() => void reloadTemplateMoments()} className="text-sm underline">
                  Retry
                </button>
              </div>
            );
          }
          if (!momentsBusy && hasActive) {
            return momentsPreparingRetry;
          }
          return momentsSkeletonForType(selectedMomentTypeCode, { bottomPadding });
        }
        return (
          <LifeOperationsMoments
            data={templateMoments}
            bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
            onManage={() => setShowManageSheet(true)}
            onComplete={async () => {
              const mid = templateMoments.moment?.moment_id;
              if (!mid) return;
              await PersonalRepository.completeTemplateMoment(selectedMomentTypeCode, mid);
              invalidateAfterTemplateLifecycle(selectedMomentTypeCode);
              await refreshAfterManage();
            }}
            onArchive={async () => {
              const mid = templateMoments.moment?.moment_id;
              if (!mid) return;
              await PersonalRepository.archiveTemplateMoment(selectedMomentTypeCode, mid);
              invalidateAfterTemplateLifecycle(selectedMomentTypeCode);
              await refreshAfterManage();
            }}
          />
        );
      }
      if ((templateMomentsLoading || templateMomentsRebuilding) && !templateMoments) {
        return momentsSkeletonForType(selectedMomentTypeCode, { bottomPadding });
      }
      if (templateMomentsError && !templateMoments) {
        return (
          <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6" style={{ paddingBottom: bottomPadding }}>
            <p className="text-sm text-red-400">{templateMomentsError}</p>
            <button type="button" onClick={() => void reloadTemplateMoments()} className="text-sm underline">
              Retry
            </button>
          </div>
        );
      }
      if (templateMoments?.status === "SETUP" || hasDraft) {
        return (
          <PersonalMomentsEmpty
            momentTypeLabel={typeLabel}
            onCreateMoment={openCreateOverlay}
            onBeginLifeOps={() =>
              activeCard
                ? continueDraftSetup(activeCard)
                : beginMomentFromMoments(selectedMomentTypeCode)
            }
            bottomPadding={bottomPadding}
          />
        );
      }
      if (hasActive && momentsBusy) {
        return momentsSkeletonForType(selectedMomentTypeCode, { bottomPadding });
      }
      if (hasActive) {
        return momentsPreparingRetry;
      }
    }

    if (personalMoments && momentsHasTypePayload(personalMoments, selectedMomentTypeCode)) {
      switch (selectedMomentTypeCode) {
        case "FUTURE_BUILDING":
          return personalMoments.future_building_detail?.metrics ? (
            <FutureBuildingMoments detail={personalMoments.future_building_detail} bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader} />
          ) : personalMoments.future_building_detail ? (
            momentsBusy ? (
              <FutureBuildingMomentsSkeleton bottomPadding={bottomPadding} />
            ) : (
              momentsPreparingRetry
            )
          ) : null;
        case "LIFESTYLE":
          return personalMoments.lifestyle_detail?.metrics?.journey_hero &&
            personalMoments.lifestyle_detail.metrics.money_journey ? (
            <LifestyleMoments
              detail={personalMoments.lifestyle_detail}
              bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
            />
          ) : personalMoments.lifestyle_detail ? (
            momentsBusy ? (
              <LifestyleMomentsSkeleton bottomPadding={bottomPadding} />
            ) : (
              momentsPreparingRetry
            )
          ) : null;
        case "RELATIONSHIPS":
          return personalMoments.emotional_security_detail?.metrics ? (
            <RelationshipsMoments
              detail={personalMoments.emotional_security_detail}
              bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
            />
          ) : personalMoments.emotional_security_detail ? (
            momentsBusy ? (
              <RelationshipsMomentsSkeleton bottomPadding={bottomPadding} />
            ) : (
              momentsPreparingRetry
            )
          ) : null;
        default:
          if (personalMoments.life_operations_detail?.metrics) {
            return (
              <LifeOperationsMoments
                data={{
                  moment_type_code: "LIFE_OPERATIONS",
                  status: "ACTIVE",
                  moment: null,
                  moment_projection: personalMoments.life_operations_detail.metrics,
                  setup_summary: { pressure_sources: [], recovery_supports: [], runtime_priorities: [], identity_chips: [] },
                  recent_events: [],
                  accounts_summary: { total_accounts: 0, active_accounts: 0, accounts: [] },
                  timeline_count: 0,
                  last_activity_at: null,
                  progress: { label: "", subtitle: "", blocks: [] },
                }}
                bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
              />
            );
          }
          return momentsBusy ? (
            <LifeOperationsMomentsSkeleton bottomPadding={bottomPadding} />
          ) : (
            momentsPreparingRetry
          );
      }
    }

    if (momentsLoading && !personalMoments) {
      return momentsSkeletonForType(selectedMomentTypeCode, { bottomPadding });
    }

    if (hasActive && momentsBusy) {
      return momentsSkeletonForType(selectedMomentTypeCode, { bottomPadding });
    }

    if (momentsError && !personalMoments && !hasDraft) {
      return (
        <div
          className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
          style={{ paddingBottom: bottomPadding }}
        >
          <p className="text-center text-sm" style={{ color: tokens.colors.error }}>
            {momentsError}
          </p>
          <button
            type="button"
            onClick={() => void reloadMoments()}
            className="rounded-xl px-6 py-2 text-sm font-semibold"
            style={{
              background: tokens.colors.primaryContainer,
              color: tokens.colors.brandOnPrimary,
            }}
          >
            Retry
          </button>
        </div>
      );
    }

    if (hasDraft && activeCard) {
      return (
        <PersonalMomentsEmpty
          momentTypeLabel={typeLabel}
          onCreateMoment={openCreateOverlay}
          onBeginLifeOps={() => continueDraftSetup(activeCard)}
          bottomPadding={bottomPadding}
        />
      );
    }

    if (
      hasActive &&
      !momentsBusy &&
      (!personalMoments ||
        personalMoments.is_empty ||
        !momentsHasTypePayload(personalMoments, selectedMomentTypeCode))
    ) {
      return momentsPreparingRetry;
    }

    if (createOptionsHydrating) {
      return momentsSkeletonForType(selectedMomentTypeCode, { bottomPadding });
    }

    return (
      <PersonalMomentsEmpty
        onCreateMoment={openCreateOverlay}
        onBeginLifeOps={() => beginMomentFromMoments(selectedMomentTypeCode)}
        bottomPadding={bottomPadding}
      />
    );
  }

  function isTemplateMomentActive(tab: BottomNavTabId = visibleTab): boolean {
    return (
      isActiveMoment(activeCard) ||
      quickAddGate.hasActiveMoment ||
      isActiveMomentStatus(manageContext?.status) ||
      isActiveScreen(resolveScreen("personal", tab, bootstrap))
    );
  }

  function renderPersonalLife() {
    const metrics = personalLife?.metrics ?? personalLife?.life_projection ?? null;
    const hasUsableMetrics =
      metrics &&
      typeof metrics === "object" &&
      "life_health" in metrics &&
      metrics.life_health != null;
    const lifeBusy = lifeLoading || lifeRefreshing || lifeRebuilding;
    if (hasUsableMetrics) {
      return (
        <PersonalLife
          metrics={metrics as import("@/lib/api/personal").PersonalLifeMetrics}
          dateRangeLabel={personalLife?.date_range_label}
          bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
          onQuickAdd={(eventType) => openQuickAdd(eventType)}
          onCreateMoment={openCreateOverlay}
        />
      );
    }
    if (lifeBusy && !hasUsableMetrics) {
      return <PersonalLifeSkeleton bottomPadding={bottomPadding} />;
    }
    if (lifeError && !personalLife) {
      return (
        <div
          className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
          style={{ paddingBottom: bottomPadding }}
        >
          <p className="text-sm text-red-400">{lifeError}</p>
          <button type="button" onClick={() => void reloadLife()} className="text-sm underline">
            Retry
          </button>
        </div>
      );
    }
    if (isTemplateMomentActive("life") || (personalLife && !personalLife.is_empty)) {
      return (
        <div
          className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
          style={{ paddingBottom: bottomPadding }}
        >
          <p className="text-sm opacity-70">Couldn&apos;t load your life dashboard.</p>
          <button type="button" onClick={() => void reloadLife()} className="text-sm underline">
            Retry
          </button>
        </div>
      );
    }
    return (
      <PersonalLifeEmpty
        onCreateMoment={openCreateOverlay}
        onBeginLifeOps={() => beginMomentFromMoments("LIFE_OPERATIONS")}
        bottomPadding={bottomPadding}
      />
    );
  }

  function renderPersonalMemory() {
    const memoryBusy =
      memoryLoading ||
      memoryRefreshing ||
      memoryRebuilding ||
      templateMemoryLoading ||
      templateMemoryRefreshing ||
      templateMemoryRebuilding;

    const memoryPreparingRetry = (
      <div
        className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
        style={{ paddingBottom: bottomPadding }}
      >
        <p className="text-center text-sm" style={{ color: tokens.colors.textSecondary }}>
          Your moment is active. Memory is still preparing â€” tap Retry if this takes too long.
        </p>
        <button
          type="button"
          onClick={() => void (isMyMoneyTemplate ? reloadTemplateMemory() : reloadMemory())}
          className="rounded-xl px-6 py-2 text-sm font-semibold"
          style={{
            background: tokens.colors.primaryContainer,
            color: tokens.colors.brandOnPrimary,
          }}
        >
          Retry
        </button>
      </div>
    );

    if (isMyMoneyTemplate) {
      if (templateMemory?.status === "ACTIVE") {
        if (selectedMomentTypeCode === "FUTURE_BUILDING") {
          if (templateMemory.memory_projection) {
            return (
              <FutureBuildingMemory
                memory={
                  {
                    metrics: templateMemory.memory_projection,
                  } as import("@/lib/api/personalDomainTypes").PersonalFutureBuildingMemory
                }
                bottomPadding={bottomPadding}
                hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (personalMemory?.future_building?.metrics) {
            return (
              <FutureBuildingMemory
                memory={personalMemory.future_building}
                bottomPadding={bottomPadding}
                hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (memoryProjectionRetried.current && !memoryBusy) {
            return (
              <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6" style={{ paddingBottom: bottomPadding }}>
                <p className="text-sm opacity-70">Couldn&apos;t load your memory.</p>
                <button type="button" onClick={() => void reloadTemplateMemory()} className="text-sm underline">
                  Retry
                </button>
              </div>
            );
          }
          if (!memoryBusy) {
            return memoryPreparingRetry;
          }
          return <FutureBuildingMemorySkeleton bottomPadding={bottomPadding} />;
        }

        if (selectedMomentTypeCode === "LIFE_OPERATIONS") {
          if (templateMemory.memory_projection) {
            return (
              <LifeOperationsMemory data={templateMemory} bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader} />
            );
          }
          if (personalMemory?.life_operations?.metrics) {
            return (
              <LifeOperationsMemory
                data={{
                  moment_type_code: "LIFE_OPERATIONS",
                  status: "ACTIVE",
                  memory_projection: personalMemory.life_operations.metrics,
                }}
                bottomPadding={bottomPadding}
                hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (memoryProjectionRetried.current && !memoryBusy) {
            return (
              <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6" style={{ paddingBottom: bottomPadding }}>
                <p className="text-sm opacity-70">Couldn&apos;t load your memory.</p>
                <button type="button" onClick={() => void reloadTemplateMemory()} className="text-sm underline">
                  Retry
                </button>
              </div>
            );
          }
          if (!memoryBusy) {
            return memoryPreparingRetry;
          }
          return <LifeOperationsMemorySkeleton bottomPadding={bottomPadding} />;
        }

        if (selectedMomentTypeCode === "LIFESTYLE") {
          if (templateMemory.memory_projection) {
            return (
              <LifestyleMemory
                metrics={
                  templateMemory.memory_projection as unknown as import("@/lib/api/personal").PersonalLifestyleMemoryMetrics
                }
                bottomPadding={bottomPadding}
                hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (personalMemory?.lifestyle?.metrics) {
            return (
              <LifestyleMemory
                metrics={personalMemory.lifestyle.metrics}
                bottomPadding={bottomPadding}
                hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (memoryProjectionRetried.current && !memoryBusy) {
            return (
              <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6" style={{ paddingBottom: bottomPadding }}>
                <p className="text-sm opacity-70">Couldn&apos;t load your memory.</p>
                <button type="button" onClick={() => void reloadTemplateMemory()} className="text-sm underline">
                  Retry
                </button>
              </div>
            );
          }
          if (!memoryBusy) {
            return memoryPreparingRetry;
          }
          return <LifestyleMemorySkeleton bottomPadding={bottomPadding} />;
        }

        if (selectedMomentTypeCode === "RELATIONSHIPS") {
          if (templateMemory.memory_projection) {
            return (
              <RelationshipsMemory
                memory={
                  {
                    metrics: templateMemory.memory_projection,
                  } as import("@/lib/api/personalDomainTypes").PersonalEmotionalSecurityMemory
                }
                bottomPadding={bottomPadding}
                hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (personalMemory?.emotional_security?.metrics) {
            return (
              <RelationshipsMemory
                memory={personalMemory.emotional_security}
                bottomPadding={bottomPadding}
                hideScreenHeader={hideScreenHeader}
              />
            );
          }
          if (memoryProjectionRetried.current && !memoryBusy) {
            return (
              <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6" style={{ paddingBottom: bottomPadding }}>
                <p className="text-sm opacity-70">Couldn&apos;t load your memory.</p>
                <button type="button" onClick={() => void reloadTemplateMemory()} className="text-sm underline">
                  Retry
                </button>
              </div>
            );
          }
          if (!memoryBusy) {
            return memoryPreparingRetry;
          }
          return <RelationshipsMemorySkeleton bottomPadding={bottomPadding} />;
        }

        return <TemplateMemoryEmpty bottomPadding={bottomPadding} />;
      }
      if ((templateMemoryLoading || templateMemoryRebuilding) && !templateMemory) {
        return memorySkeletonForType(selectedMomentTypeCode, { bottomPadding });
      }
      if (templateMemoryError && !templateMemory) {
        return (
          <div className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6" style={{ paddingBottom: bottomPadding }}>
            <p className="text-sm text-red-400">{templateMemoryError}</p>
            <button type="button" onClick={() => void reloadTemplateMemory()} className="text-sm underline">
              Retry
            </button>
          </div>
        );
      }
      if (isTemplateMomentActive("memory") && memoryBusy) {
        return memorySkeletonForType(selectedMomentTypeCode, { bottomPadding });
      }
      if (isTemplateMomentActive("memory")) {
        return memoryPreparingRetry;
      }
      if (selectedMomentTypeCode === "LIFESTYLE" && personalMemory?.lifestyle?.metrics) {
        return (
          <LifestyleMemory
            metrics={personalMemory.lifestyle.metrics}
            bottomPadding={bottomPadding}
            hideScreenHeader={hideScreenHeader}
          />
        );
      }
      return <TemplateMemoryEmpty bottomPadding={bottomPadding} />;
    }

    const hasActive = isActiveMoment(activeCard);

    if (!isMyMoneyTemplate && personalMemory && memoryHasTypePayload(personalMemory, selectedMomentTypeCode)) {
      switch (selectedMomentTypeCode) {
        case "FUTURE_BUILDING":
          return personalMemory.future_building?.metrics ? (
            <FutureBuildingMemory memory={personalMemory.future_building} bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader} />
          ) : personalMemory.future_building ? (
            memoryBusy ? (
              <FutureBuildingMemorySkeleton bottomPadding={bottomPadding} />
            ) : (
              memoryPreparingRetry
            )
          ) : null;
        case "LIFESTYLE":
          return personalMemory.lifestyle?.metrics ? (
            <LifestyleMemory metrics={personalMemory.lifestyle.metrics} bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader} />
          ) : null;
        case "RELATIONSHIPS":
          return personalMemory.emotional_security?.metrics ? (
            <RelationshipsMemory memory={personalMemory.emotional_security} bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader} />
          ) : personalMemory.emotional_security ? (
            memoryBusy ? (
              <RelationshipsMemorySkeleton bottomPadding={bottomPadding} />
            ) : (
              memoryPreparingRetry
            )
          ) : null;
        default:
          if (personalMemory.life_operations?.metrics) {
            return (
              <LifeOperationsMemory
                data={{
                  moment_type_code: "LIFE_OPERATIONS",
                  status: "ACTIVE",
                  memory_projection: personalMemory.life_operations.metrics,
                }}
                bottomPadding={bottomPadding} hideScreenHeader={hideScreenHeader}
              />
            );
          }
          return memoryBusy ? (
            <LifeOperationsMemorySkeleton bottomPadding={bottomPadding} />
          ) : (
            memoryPreparingRetry
          );
      }
    }

    if (memoryLoading && !personalMemory) {
      return (
        <div className="flex min-h-0 flex-1 items-center justify-center" style={{ paddingBottom: bottomPadding }}>
          <p className="text-sm opacity-70">Loading memoryâ€¦</p>
        </div>
      );
    }

    if (hasActive && memoryBusy) {
      return memorySkeletonForType(selectedMomentTypeCode, { bottomPadding });
    }

    if (memoryError && !personalMemory) {
      return (
        <div
          className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
          style={{ paddingBottom: bottomPadding }}
        >
          <p className="text-center text-sm" style={{ color: tokens.colors.error }}>
            {memoryError}
          </p>
          <button
            type="button"
            onClick={() => void reloadMemory()}
            className="rounded-xl px-6 py-2 text-sm font-semibold"
            style={{
              background: tokens.colors.primaryContainer,
              color: tokens.colors.brandOnPrimary,
            }}
          >
            Retry
          </button>
        </div>
      );
    }

    if (
      !isMyMoneyTemplate &&
      hasActive &&
      !memoryBusy &&
      (!personalMemory ||
        personalMemory.is_empty ||
        !memoryHasTypePayload(personalMemory, selectedMomentTypeCode))
    ) {
      return memoryPreparingRetry;
    }

    if (createOptionsHydrating && isMyMoneyTemplate) {
      if (selectedMomentTypeCode === "FUTURE_BUILDING") {
        return <FutureBuildingMemorySkeleton bottomPadding={bottomPadding} />;
      }
      return <LifeOperationsMemorySkeleton bottomPadding={bottomPadding} />;
    }

    return (
      <PersonalMemoryEmpty
        momentTypeLabel={typeLabel}
        onCreateMoment={openCreateOverlay}
        bottomPadding={bottomPadding}
      />
    );
  }

  function renderPersonalPersistentTabs() {
    return (
      <PersistentTabStack
        activeTab={visibleTab}
        previousTab={previousTab}
        tabs={[
          {
            id: "pulse",
            children: wrapPersonalTabWithHeader(
              "Pulse",
              <>
                <OfflineBanner
                  visible={Boolean(personalPulse) && pulseRefreshing && Boolean(pulseError)}
                />
                <PullToRefresh onRefresh={() => void reloadPulse()}>
                  <PersonalTabErrorBoundary
                    section="Pulse"
                    bottomPadding={bottomPadding}
                    onRetry={() => void reloadPulse()}
                  >
                    {renderPersonalPulse()}
                  </PersonalTabErrorBoundary>
                </PullToRefresh>
              </>,
            ),
          },
          {
            id: "moments",
            children: wrapPersonalTabWithHeader(
              "Moments",
              wrapMomentsTab(
                <PersonalTabErrorBoundary
                  section="Moments"
                  bottomPadding={bottomPadding}
                  onRetry={() =>
                    void (loTemplateEnabled ? reloadTemplateMoments() : reloadMoments())
                  }
                >
                  {renderPersonalMoments()}
                </PersonalTabErrorBoundary>,
              ),
            ),
          },
          {
            id: "life",
            children: wrapPersonalTabWithHeader(
              "Life",
              wrapLifeTab(
                <PersonalTabErrorBoundary
                  section="Life"
                  bottomPadding={bottomPadding}
                  onRetry={() => void reloadLife()}
                >
                  {renderPersonalLife()}
                </PersonalTabErrorBoundary>,
              ),
            ),
          },
          {
            id: "memory",
            children: wrapPersonalTabWithHeader(
              "Memory",
              wrapMemoryTab(
                <PersonalTabErrorBoundary
                  section="Memory"
                  bottomPadding={bottomPadding}
                  onRetry={() =>
                    void (isMyMoneyTemplate ? reloadTemplateMemory() : reloadMemory())
                  }
                >
                  {renderPersonalMemory()}
                </PersonalTabErrorBoundary>,
              ),
            ),
          },
        ]}
      />
    );
  }

  function renderPersonalContent() {
    switch (visibleTab) {
      case "pulse":
        return wrapPersonalTabWithHeader(
          "Pulse",
          <>
            <OfflineBanner visible={Boolean(personalPulse) && (pulseLoading || Boolean(pulseError))} />
            <PullToRefresh onRefresh={() => void reloadPulse()}>
              <PersonalTabErrorBoundary
                section="Pulse"
                bottomPadding={bottomPadding}
                onRetry={() => void reloadPulse()}
              >
                {renderPersonalPulse()}
              </PersonalTabErrorBoundary>
            </PullToRefresh>
          </>,
        );
      case "moments":
        return wrapPersonalTabWithHeader(
          "Moments",
          wrapMomentsTab(
            <PersonalTabErrorBoundary
              section="Moments"
              bottomPadding={bottomPadding}
              onRetry={() => void (loTemplateEnabled ? reloadTemplateMoments() : reloadMoments())}
            >
              {renderPersonalMoments()}
            </PersonalTabErrorBoundary>,
          ),
        );
      case "life":
        return wrapPersonalTabWithHeader(
          "Life",
          wrapLifeTab(
            <PersonalTabErrorBoundary
              section="Life"
              bottomPadding={bottomPadding}
              onRetry={() => void reloadLife()}
            >
              {renderPersonalLife()}
            </PersonalTabErrorBoundary>,
          ),
        );
      case "memory":
        return wrapPersonalTabWithHeader(
          "Memory",
          wrapMemoryTab(
            <PersonalTabErrorBoundary
              section="Memory"
              bottomPadding={bottomPadding}
              onRetry={() => void (isMyMoneyTemplate ? reloadTemplateMemory() : reloadMemory())}
            >
              {renderPersonalMemory()}
            </PersonalTabErrorBoundary>,
          ),
        );
      default:
        return (
          <TabPanel
            title={`${title} Â· ${tabTitles[visibleTab]}`}
            bottomPadding={bottomPadding}
          />
        );
    }
  }

  function renderBusinessContent() {
    const businessResolved = resolveScreen("business", visibleTab, bootstrap);
    // Inventory emptiness wins over ghost selection after delete-all.
    const moments = businessBootstrap?.moments ?? [];
    const home = businessBootstrap?.moments_home;
    const inventoryEmpty =
      Boolean(businessBootstrap) &&
      (home?.is_empty === true ||
        (typeof home?.active_moment_count === "number" && home.active_moment_count === 0) ||
        moments.length === 0);

    // Group parity: Pulse mounts the switcher-bound moment id (no DRAFT re-resolve gate).
    const boundId = inventoryEmpty ? null : selectedBusinessMomentId?.trim() || null;
    const boundType = inventoryEmpty
      ? ""
      : (selectedBusinessMomentType || "").toUpperCase();
    const teamOpsMomentId =
      boundType === "TEAM_OPERATIONS" && boundId ? boundId : null;
    const runwayMomentId =
      boundType === "BUSINESS_RUNWAY" && boundId ? boundId : null;
    const opsMomentId =
      (boundType === "BUSINESS_OPERATIONS" || boundType === "DEPARTMENT_OPERATIONS") &&
      boundId
        ? boundId
        : null;

    const renderBusinessEmptyShell = () => {
      switch (visibleTab) {
        case "pulse":
          return (
            <BusinessPulseEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />
          );
        case "moments":
          return (
            <BusinessMomentsEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />
          );
        case "memory":
          return (
            <BusinessMemoryEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />
          );
        case "life":
          return (
            <BusinessLifeEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />
          );
        default:
          return (
            <BusinessPulseEmpty onCreateMoment={openCreateOverlay} bottomPadding={bottomPadding} />
          );
      }
    };

    if (inventoryEmpty) {
      return renderBusinessEmptyShell();
    }

    if (businessResolved === "loading" && !teamOpsMomentId && !runwayMomentId && !opsMomentId) {
      return (
        <div className="flex min-h-0 flex-1 items-center justify-center" style={{ paddingBottom: bottomPadding }}>
          <p className="text-sm opacity-70">Loadingâ€¦</p>
        </div>
      );
    }

    if (
      !teamOpsMomentId &&
      !runwayMomentId &&
      !opsMomentId &&
      businessSessionLoading &&
      !businessBootstrap &&
      !businessCreateOptions
    ) {
      return (
        <div className="flex min-h-0 flex-1 items-center justify-center" style={{ paddingBottom: bottomPadding }}>
          <p className="text-sm opacity-70">Loadingâ€¦</p>
        </div>
      );
    }

    if (
      !teamOpsMomentId &&
      !runwayMomentId &&
      !opsMomentId &&
      businessSessionError &&
      !businessSessionLoading
    ) {
      return (
        <div
          className="flex min-h-0 flex-1 flex-col items-center justify-center gap-3 px-6"
          style={{ paddingBottom: bottomPadding }}
        >
          <p className="text-center text-sm" style={{ color: tokens.colors.error }}>
            {businessSessionError}
          </p>
          <button
            type="button"
            onClick={() => setBusinessSessionRetryKey((k) => k + 1)}
            className="rounded-xl px-6 py-2 text-sm font-semibold"
            style={{
              background: tokens.colors.primaryContainer,
              color: tokens.colors.brandOnPrimary,
            }}
          >
            Retry
          </button>
        </div>
      );
    }

    if (showRunwayActivity && runwayMomentId) {
      return (
        <BusinessRunwayActiveTabs
          momentId={runwayMomentId}
          tab="activity"
          bottomPadding={bottomPadding}
          reloadKey={runwayReloadKey}
          userId={businessUserId}
          optimisticItems={runwayOptimistic}
          activityEventId={runwayActivityEventId}
          onCloseActivity={() => {
            setShowRunwayActivity(false);
            setRunwayActivityEventId(null);
          }}
          onChanged={() => bumpRunwayProjections()}
        />
      );
    }

    if (runwayMomentId) {
      const onQuickAdd = () => openQuickAdd(null);
      const tab =
        visibleTab === "moments"
          ? "moments"
          : visibleTab === "life"
            ? "life"
            : visibleTab === "memory"
              ? "memory"
              : "pulse";
      return (
        <BusinessRunwayActiveTabs
          momentId={runwayMomentId}
          tab={tab}
          bottomPadding={bottomPadding}
          reloadKey={runwayReloadKey}
          userId={businessUserId}
          optimisticItems={runwayOptimistic}
          onQuickAdd={onQuickAdd}
          onOpenActivity={(eventId) => {
            setRunwayActivityEventId(eventId ?? null);
            setShowRunwayActivity(true);
          }}
          onChanged={() => bumpRunwayProjections()}
        />
      );
    }

    if (showOpsActivity && opsMomentId) {
      return (
        <BusinessOperationsActiveTabs
          momentId={opsMomentId}
          tab="activity"
          bottomPadding={bottomPadding}
          reloadKey={opsReloadKey}
          userId={businessUserId}
          optimisticItems={opsOptimistic}
          activityEventId={opsActivityEventId}
          onCloseActivity={() => {
            setShowOpsActivity(false);
            setOpsActivityEventId(null);
          }}
          onChanged={() => bumpOpsProjections()}
        />
      );
    }

    if (opsMomentId) {
      const onQuickAdd = () => openQuickAdd(null);
      const tab =
        visibleTab === "moments"
          ? "moments"
          : visibleTab === "life"
            ? "life"
            : visibleTab === "memory"
              ? "memory"
              : "pulse";
      return (
        <BusinessOperationsActiveTabs
          momentId={opsMomentId}
          tab={tab}
          bottomPadding={bottomPadding}
          reloadKey={opsReloadKey}
          userId={businessUserId}
          optimisticItems={opsOptimistic}
          onQuickAdd={onQuickAdd}
          onOpenActivity={(eventId) => {
            setOpsActivityEventId(eventId ?? null);
            setShowOpsActivity(true);
          }}
          onChanged={() => bumpOpsProjections()}
        />
      );
    }

    if (showTeamOpsActivity && teamOpsMomentId) {
      return (
        <TeamOperationsActiveTabs
          momentId={teamOpsMomentId}
          tab="activity"
          bottomPadding={bottomPadding}
          reloadKey={teamOpsReloadKey}
          userId={businessUserId}
          optimisticItems={teamOpsOptimistic}
          activityEventId={teamOpsActivityEventId}
          onCloseActivity={() => {
            setShowTeamOpsActivity(false);
            setTeamOpsActivityEventId(null);
          }}
          onChanged={() => bumpTeamOpsProjections()}
        />
      );
    }

    if (teamOpsMomentId) {
      const onQuickAdd = () => openQuickAdd(null);
      const tab =
        visibleTab === "moments"
          ? "moments"
          : visibleTab === "life"
            ? "life"
            : visibleTab === "memory"
              ? "memory"
              : "pulse";
      return (
        <TeamOperationsActiveTabs
          momentId={teamOpsMomentId}
          tab={tab}
          bottomPadding={bottomPadding}
          reloadKey={teamOpsReloadKey}
          userId={businessUserId}
          optimisticItems={teamOpsOptimistic}
          onQuickAdd={onQuickAdd}
          onOpenActivity={(eventId) => {
            setTeamOpsActivityEventId(eventId ?? null);
            setShowTeamOpsActivity(true);
          }}
          onChanged={() => bumpTeamOpsProjections()}
        />
      );
    }

    if (isEmptyScreen(businessResolved) || isSetupScreen(businessResolved)) {
      return renderBusinessEmptyShell();
    }

    // Active nonâ€“Team Ops verticals ship in Runs 9â€“10 â€” keep honest empty shell for now.
    return renderBusinessEmptyShell();
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <main className="flex min-h-0 flex-1 flex-col overflow-y-auto">
        <div className="w-full flex-1 px-4 pb-6 sm:px-6 lg:px-8">
          {showBusinessManageHeader ? (
            <BusinessMomentHeader
              tabLabel={tabTitles[visibleTab]}
              options={businessSwitcherOptions}
              selectedTypeCode={selectedBusinessMomentType}
              onSelect={handleBusinessMomentSwitcherSelect}
              onManageClick={
                businessManageContext ? () => setShowManageSheet(true) : undefined
              }
              onInviteMoment={(option) => {
                if (!option.momentId) return;
                if (
                  option.typeCode !== selectedBusinessMomentType ||
                  option.momentId !== selectedBusinessMomentId
                ) {
                  setBusinessSelection(option.typeCode, option.momentId);
                }
                setInviteMoment({ momentId: option.momentId, label: option.label });
              }}
              onDeleteMoment={(option) => {
                void archiveBusinessMomentOption(option);
              }}
            />
          ) : null}
          {variant === "personal" ? (
            renderPersonalPersistentTabs()
          ) : variant === "business" ? (
            renderBusinessContent()
          ) : (
            <TabPanel
              title={`${title} Â· ${tabTitles[visibleTab]}`}
              bottomPadding={bottomPadding}
            />
          )}
        </div>
      </main>
      {personalFabVisible ? <MyMoneyFloatingAdd onOpen={openMasterExpense} /> : null}
      <ContextBottomNav {...tabBarProps} />

      {variant === "personal" && quickAddWarm ? (
        <PersonalMomentQuickAddRouter
          open={showQuickAddSheet}
          momentTypeCode={selectedMomentTypeCode}
          momentId={
            quickAddResolvedMomentId ??
            quickAddGate.momentId ??
            manageContext?.momentId ??
            activeCard?.linked_moment_id ??
            null
          }
          hasActiveMoment={quickAddGate.hasActiveMoment}
          initialEventType={quickAddEventType}
          onClose={() => {
            setShowQuickAddSheet(false);
            setQuickAddEventType(null);
            setQuickAddResolvedMomentId(null);
          }}
          onBeginSetup={() => {
            setShowQuickAddSheet(false);
            setQuickAddEventType(null);
            void beginMomentFromMoments(selectedMomentTypeCode);
          }}
          onSuccess={() => {
            // submitQuickAdd already called invalidateAfterQuickAdd — soft revalidate visible tab only.
            if (visibleTab === "pulse") void revalidatePulse();
            else if (visibleTab === "moments") {
              void revalidateMoments();
              if (loTemplateEnabled) void revalidateTemplateMoments();
            } else if (visibleTab === "memory") {
              void revalidateMemory();
              void revalidateTemplateMemory();
            } else if (visibleTab === "life") void revalidateLife();
            else void revalidatePulse();
          }}
        />
      ) : null}
      {variant === "business" && showQuickAddSheet ? (
        businessManageContext?.momentId && businessManageContext?.typeCode ? (
          <BusinessActionCenterShell
            momentId={businessManageContext.momentId}
            momentTypeCode={businessManageContext.typeCode}
            momentName={businessManageContext.momentName ?? null}
            userId={businessUserId ?? "local"}
            onClose={() => setShowQuickAddSheet(false)}
            onSuccess={(result) => {
              const mid = businessManageContext.momentId;
              const typeCode = businessManageContext.typeCode;
              const patched = applyBusinessMutationSuccess({
                momentId: mid,
                momentTypeCode: typeCode,
                userId: businessUserId,
                response: result?.mutationResponse,
              });
              const optimistic =
                patched ??
                ({
                  event_id: `optimistic-${Date.now()}`,
                  action_type: result?.action_type ?? "TEAM_UPDATE",
                  title: result?.title ?? "Just recorded",
                  occurred_at: new Date().toISOString(),
                  source_moment_id: mid,
                } satisfies TeamOpsEventItem);
              const soft = { skipHardInvalidate: true as const };
              if (typeCode === "BUSINESS_RUNWAY") {
                bumpRunwayProjections(optimistic, soft);
              } else if (
                typeCode === "BUSINESS_OPERATIONS" ||
                typeCode?.toUpperCase() === "DEPARTMENT_OPERATIONS"
              ) {
                bumpOpsProjections(optimistic, soft);
              } else {
                bumpTeamOpsProjections(optimistic, soft);
              }
              setShowQuickAddSheet(false);
            }}
          />
        ) : (
          <BusinessNoMomentActionHint onClose={() => setShowQuickAddSheet(false)} />
        )
      ) : null}

      {variant === "personal" && showCreateOverlay ? (
        <>
          <PersonalCreateEmpty
            options={createOptions}
            loadingOptions={loadingCreateOptions}
            creatingTypeCode={creatingTypeCode}
            createError={createError}
            onBeginMoment={(typeCode) => void handleBeginMoment(typeCode)}
            onClose={() => {
              if (showMomentSetup) {
                closeMomentSetup();
              } else {
                setShowCreateOverlay(false);
              }
            }}
          />
          {showMomentSetup && setupMomentId ? (
            <PersonalMomentSetup
              momentId={setupMomentId}
              onClose={closeMomentSetup}
              onActivated={handleMomentActivated}
            />
          ) : null}
        </>
      ) : null}

      {variant === "personal" && showMasterExpense ? (
        <MasterExpenseOrchestrator
          onBack={() => setShowMasterExpense(false)}
          onSuccess={() => {
            void revalidateLife();
            void revalidatePulse();
            void revalidateMoments();
            void revalidateMemory();
            void revalidateTemplateMemory();
            void revalidateTemplateMoments();
          }}
        />
      ) : null}

      {variant === "personal" &&
      showLifeOpsActivity &&
      lifeOpsActivityMomentId &&
      (selectedMomentTypeCode === "LIFE_OPERATIONS" ||
        selectedMomentTypeCode === "FUTURE_BUILDING" ||
        selectedMomentTypeCode === "LIFESTYLE" ||
        selectedMomentTypeCode === "RELATIONSHIPS") ? (
        <TemplateActivityScreen
          key={activityReloadToken}
          momentTypeCode={selectedMomentTypeCode}
          momentId={lifeOpsActivityMomentId}
          onBack={() => setShowLifeOpsActivity(false)}
          onEditActivity={(id, eventType, momentTypeCode) =>
            setEditingActivity({ id, eventType, momentTypeCode })
          }
        />
      ) : null}

      {variant === "personal" &&
      editingActivity &&
      (selectedMomentTypeCode === "LIFE_OPERATIONS" ||
        selectedMomentTypeCode === "FUTURE_BUILDING" ||
        selectedMomentTypeCode === "LIFESTYLE" ||
        selectedMomentTypeCode === "RELATIONSHIPS") ? (
        <TemplateActivityEditSheet
          momentTypeCode={
            (editingActivity.momentTypeCode as typeof selectedMomentTypeCode) ||
            selectedMomentTypeCode
          }
          eventId={editingActivity.id}
          eventType={editingActivity.eventType}
          onClose={() => setEditingActivity(null)}
          onSuccess={() => {
            setActivityReloadToken((t) => t + 1);
            invalidateAfterQuickAdd(selectedMomentTypeCode);
            if (visibleTab === "pulse") void revalidatePulse();
            else if (visibleTab === "moments") {
              void revalidateMoments();
              if (selectedMomentTypeCode === "FUTURE_BUILDING" || loTemplateEnabled) {
                void revalidateTemplateMoments();
              }
            } else if (visibleTab === "memory") {
              void revalidateMemory();
              void revalidateTemplateMemory();
            } else if (visibleTab === "life") void revalidateLife();
            else {
              void revalidatePulse();
              void revalidateTemplateMemory();
              if (selectedMomentTypeCode === "FUTURE_BUILDING" || loTemplateEnabled) {
                void revalidateTemplateMoments();
              }
            }
          }}
        />
      ) : null}

      {variant === "business" && showCreateOverlay ? (
        <BusinessCreateEmpty
          options={businessCreateOptions}
          creatingType={creatingBusinessType}
          onCreateMoment={async (typeCode) => {
            const code = (typeCode ?? "TEAM_OPERATIONS").toUpperCase();
            if (
              code !== "TEAM_OPERATIONS" &&
              code !== "BUSINESS_RUNWAY" &&
              code !== "BUSINESS_OPERATIONS"
            ) {
              return;
            }
            setBusinessCreateError(null);
            setCreatingBusinessType(code);
            beginBusinessSetupOpen({ moment_type_code: code });
            try {
              const created = await BusinessSetupRepository.createDraft({
                moment_type_code: code,
              });
              markBusinessSetupCreateDone(created.moment_id);
              setBusinessSetupMomentId(created.moment_id);
              setBusinessSetupTypeCode(created.moment_type_code);
              setBusinessSetupSeed(created);
              setShowCreateOverlay(false);
              setShowBusinessSetup(true);
              // Bootstrap/create-options deferred until setup state loads (onSetupReady).
            } catch (err) {
              setBusinessCreateError(
                err instanceof ApiError ? err.message : "Could not create draft",
              );
            } finally {
              setCreatingBusinessType(null);
            }
          }}
          onClose={() => setShowCreateOverlay(false)}
        />
      ) : null}

      {variant === "business" && showBusinessSetup && businessSetupMomentId ? (
        <BusinessMomentSetup
          momentId={businessSetupMomentId}
          momentTypeCode={businessSetupTypeCode}
          initialSetup={businessSetupSeed}
          onClose={() => {
            setShowBusinessSetup(false);
            setBusinessSetupMomentId(null);
            setBusinessSetupSeed(null);
          }}
          onSetupReady={refreshBusinessSessionAfterSetupReady}
          onActivated={() => {
            const activatedId = businessSetupMomentId;
            const activatedType = businessSetupTypeCode;
            setShowBusinessSetup(false);
            setBusinessSetupMomentId(null);
            setBusinessSetupSeed(null);
            if (activatedId) {
              patchBusinessMomentInInventory({
                moment_id: activatedId,
                moment_type_id: "",
                moment_type_code: activatedType,
                moment_name: activatedType,
                status: "ACTIVE",
              });
              setBusinessSelection(activatedType, activatedId);
            }
            // Soft inventory reconcile in background â€” activate response already returned.
            void refreshAfterBusinessManage({
              momentId: activatedId,
              momentTypeCode: activatedType,
            }).finally(() => {
              markBusinessSetupBootstrapDone();
            });
          }}
        />
      ) : null}

      {variant === "business" && businessCreateError ? (
        <div className="pointer-events-none fixed bottom-24 left-1/2 z-40 -translate-x-1/2 rounded-full bg-red-500/90 px-4 py-2 text-xs text-white">
          {businessCreateError}
          {creatingBusinessType ? ` (${creatingBusinessType})` : ""}
        </div>
      ) : null}

      <MomentInviteSheet
        open={Boolean(inviteMoment)}
        onClose={() => setInviteMoment(null)}
        momentId={inviteMoment?.momentId ?? null}
        momentLabel={inviteMoment?.label}
        variant="business"
      />

      {variant === "personal" ? (
        <PersonalMomentManageSheet
          open={showManageSheet}
          context={manageContext}
          onClose={() => setShowManageSheet(false)}
          onEditSetup={() => {
            if (!manageContext) return;
            openMomentSetup(manageContext.momentId, manageContext.typeCode);
          }}
          onEditName={async (name) => {
            if (!manageContext) return;
            await PersonalRepository.patchMoment(manageContext.momentId, { moment_name: name });
            await refreshAfterManage();
          }}
          onPause={async () => {
            if (!manageContext) return;
            const inventory: LifecycleInventoryItem[] = (createOptions?.cards ?? [])
              .filter((c) => c.linked_moment_id)
              .map((c) => ({
                momentId: c.linked_moment_id as string,
                momentTypeCode: c.moment_type_code,
                status: c.linked_moment_status || "ACTIVE",
              }));
            try {
              const result = await runMomentLifecycle({
                contextType: "PERSONAL",
                momentId: manageContext.momentId,
                momentTypeCode: manageContext.typeCode,
                action: "pause",
                previousStatus: manageContext.status || "ACTIVE",
                inventory,
                selectedMomentId: manageContext.momentId,
              });
              await refreshAfterManage({ skipBootstrapInvalidate: true });
              if (result.replacementMomentId) {
                // selection reconcile happens via refreshed create options
              }
            } catch (e) {
              if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
              throw e;
            }
          }}
          onResume={async () => {
            if (!manageContext) return;
            const inventory: LifecycleInventoryItem[] = (createOptions?.cards ?? [])
              .filter((c) => c.linked_moment_id)
              .map((c) => ({
                momentId: c.linked_moment_id as string,
                momentTypeCode: c.moment_type_code,
                status: c.linked_moment_status || "PAUSED",
              }));
            try {
              await runMomentLifecycle({
                contextType: "PERSONAL",
                momentId: manageContext.momentId,
                momentTypeCode: manageContext.typeCode,
                action: "resume",
                previousStatus: manageContext.status || "PAUSED",
                inventory,
                selectedMomentId: manageContext.momentId,
              });
              await refreshAfterManage({ skipBootstrapInvalidate: true });
            } catch (e) {
              if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
              throw e;
            }
          }}
          onArchive={async () => {
            if (!manageContext) return;
            const inventory: LifecycleInventoryItem[] = (createOptions?.cards ?? [])
              .filter((c) => c.linked_moment_id)
              .map((c) => ({
                momentId: c.linked_moment_id as string,
                momentTypeCode: c.moment_type_code,
                status: c.linked_moment_status || "ACTIVE",
              }));
            try {
              await runMomentLifecycle({
                contextType: "PERSONAL",
                momentId: manageContext.momentId,
                momentTypeCode: manageContext.typeCode,
                action: "archive",
                previousStatus: manageContext.status || "ACTIVE",
                inventory,
                selectedMomentId: manageContext.momentId,
                refreshBootstrap: false,
              });
              if (templateMomentsEnabled(manageContext.typeCode)) {
                invalidateAfterTemplateLifecycle(manageContext.typeCode);
              } else {
                invalidateBootstrapAfterMutation();
              }
              await refreshAfterManage({ skipBootstrapInvalidate: true });
            } catch (e) {
              if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
              throw e;
            }
          }}
          onComplete={async () => {
            if (!manageContext) return;
            if (!templateMomentsEnabled(manageContext.typeCode)) return;
            const inventory: LifecycleInventoryItem[] = (createOptions?.cards ?? [])
              .filter((c) => c.linked_moment_id)
              .map((c) => ({
                momentId: c.linked_moment_id as string,
                momentTypeCode: c.moment_type_code,
                status: c.linked_moment_status || "ACTIVE",
              }));
            try {
              await runMomentLifecycle({
                contextType: "PERSONAL",
                momentId: manageContext.momentId,
                momentTypeCode: manageContext.typeCode,
                action: "complete",
                previousStatus: manageContext.status || "ACTIVE",
                inventory,
                selectedMomentId: manageContext.momentId,
                refreshBootstrap: false,
              });
              invalidateAfterTemplateLifecycle(manageContext.typeCode);
              await refreshAfterManage({ skipBootstrapInvalidate: true });
            } catch (e) {
              if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
              throw e;
            }
          }}
        />
      ) : null}
      {variant === "business" ? (
        <MomentManageSheet
          open={showManageSheet}
          context={businessManageContext}
          onClose={() => setShowManageSheet(false)}
          onEditSetup={() => {
            if (!businessManageContext) return;
            setShowManageSheet(false);
            const status = (businessManageContext.status || "").toUpperCase();
            if (status === "DRAFT" || status === "SETUP") {
              setBusinessSetupSeed(null);
              setBusinessSetupMomentId(businessManageContext.momentId);
              setBusinessSetupTypeCode(businessManageContext.typeCode);
              setShowBusinessSetup(true);
            } else {
              setShowCreateOverlay(true);
            }
          }}
          onEditName={async (name) => {
            if (!businessManageContext) return;
            await BusinessRepository.patchMoment(businessManageContext.momentId, { moment_name: name });
            await refreshAfterBusinessManage();
          }}
          onPause={async () => {
            if (!businessManageContext) return;
            const snap = getBusinessSessionSnapshot();
            const inventory: LifecycleInventoryItem[] = (snap.bootstrap?.moments ?? []).map((m) => ({
              momentId: m.moment_id,
              momentTypeCode: m.moment_type_code || "",
              status: m.status || "ACTIVE",
            }));
            try {
              const result = await runMomentLifecycle(
                {
                  contextType: "BUSINESS",
                  momentId: businessManageContext.momentId,
                  momentTypeCode: businessManageContext.typeCode,
                  action: "pause",
                  previousStatus: businessManageContext.status || "ACTIVE",
                  inventory,
                  selectedMomentId: snap.selectedMomentId,
                },
                {
                  onOptimistic: ({ replacementMomentId, replacementMomentTypeCode }) => {
                    if (replacementMomentId) {
                      setBusinessSelection(
                        replacementMomentTypeCode || businessManageContext.typeCode,
                        replacementMomentId,
                      );
                    }
                  },
                },
              );
              await refreshAfterBusinessManage({
                momentId: result.replacementMomentId,
                momentTypeCode: result.replacementMomentTypeCode,
              });
            } catch (e) {
              if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
              throw e;
            }
          }}
          onResume={async () => {
            if (!businessManageContext) return;
            const snap = getBusinessSessionSnapshot();
            const inventory: LifecycleInventoryItem[] = (snap.bootstrap?.moments ?? []).map((m) => ({
              momentId: m.moment_id,
              momentTypeCode: m.moment_type_code || "",
              status: m.status || "PAUSED",
            }));
            try {
              const result = await runMomentLifecycle(
                {
                  contextType: "BUSINESS",
                  momentId: businessManageContext.momentId,
                  momentTypeCode: businessManageContext.typeCode,
                  action: "resume",
                  previousStatus: businessManageContext.status || "PAUSED",
                  inventory,
                  selectedMomentId: snap.selectedMomentId,
                },
                {
                  onOptimistic: ({ replacementMomentId, replacementMomentTypeCode }) => {
                    if (replacementMomentId) {
                      setBusinessSelection(
                        replacementMomentTypeCode || businessManageContext.typeCode,
                        replacementMomentId,
                      );
                    }
                  },
                },
              );
              await refreshAfterBusinessManage({
                momentId: result.replacementMomentId ?? businessManageContext.momentId,
                momentTypeCode:
                  result.replacementMomentTypeCode ?? businessManageContext.typeCode,
              });
            } catch (e) {
              if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
              throw e;
            }
          }}
          onComplete={async () => {
            if (!businessManageContext) return;
            const snap = getBusinessSessionSnapshot();
            const inventory: LifecycleInventoryItem[] = (snap.bootstrap?.moments ?? []).map((m) => ({
              momentId: m.moment_id,
              momentTypeCode: m.moment_type_code || "",
              status: m.status || "ACTIVE",
            }));
            try {
              const result = await runMomentLifecycle(
                {
                  contextType: "BUSINESS",
                  momentId: businessManageContext.momentId,
                  momentTypeCode: businessManageContext.typeCode,
                  action: "complete",
                  previousStatus: businessManageContext.status || "ACTIVE",
                  inventory,
                  selectedMomentId: snap.selectedMomentId,
                },
                {
                  onOptimistic: ({ replacementMomentId, replacementMomentTypeCode }) => {
                    if (replacementMomentId) {
                      setBusinessSelection(
                        replacementMomentTypeCode || businessManageContext.typeCode,
                        replacementMomentId,
                      );
                    }
                  },
                },
              );
              await refreshAfterBusinessManage({
                momentId: result.replacementMomentId,
                momentTypeCode: result.replacementMomentTypeCode,
              });
            } catch (e) {
              if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
              throw e;
            }
          }}
          onArchive={async () => {
            if (!businessManageContext) return;
            const snap = getBusinessSessionSnapshot();
            const inventory: LifecycleInventoryItem[] = (snap.bootstrap?.moments ?? []).map((m) => ({
              momentId: m.moment_id,
              momentTypeCode: m.moment_type_code || "",
              status: m.status || "ACTIVE",
            }));
            try {
              const result = await runMomentLifecycle(
                {
                  contextType: "BUSINESS",
                  momentId: businessManageContext.momentId,
                  momentTypeCode: businessManageContext.typeCode,
                  action: "archive",
                  previousStatus: businessManageContext.status || "ACTIVE",
                  inventory,
                  selectedMomentId: snap.selectedMomentId,
                },
                {
                  onOptimistic: ({ replacementMomentId, replacementMomentTypeCode }) => {
                    if (replacementMomentId) {
                      setBusinessSelection(
                        replacementMomentTypeCode || businessManageContext.typeCode,
                        replacementMomentId,
                      );
                    } else {
                      setBusinessSelection(businessManageContext.typeCode, null);
                    }
                  },
                },
              );
              await refreshAfterBusinessManage({
                momentId: result.replacementMomentId,
                momentTypeCode: result.replacementMomentTypeCode,
              });
            } catch (e) {
              if (e instanceof MomentLifecycleError) throw new Error(e.userMessage);
              throw e;
            }
          }}
        />
      ) : null}
    </div>
  );
}

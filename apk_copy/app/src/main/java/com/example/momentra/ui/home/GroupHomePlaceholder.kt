package com.example.momentra.ui.home

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.example.momentra.ui.shared.MomentraToast
import com.example.momentra.ui.shared.MomentraToastCopy
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.momentra.analytics.MomentraAnalytics
import com.example.momentra.analytics.ScreenOverlay
import com.example.momentra.analytics.groupTabSlug
import com.example.momentra.analytics.resolveScreenName
import com.example.momentra.analytics.visibleGroupTabSlug
import com.example.momentra.data.models.GroupSessionBootstrapDto
import com.example.momentra.data.repository.GroupSessionHolder
import com.example.momentra.data.repository.SetupRepository
import com.example.momentra.data.stream.TripMomentSseClient
import com.example.momentra.ui.group.shared.rememberGroupPalette
import com.example.momentra.data.models.GroupMomentUpdateRequestDto
import com.example.momentra.data.store.BootstrapStore
import com.example.momentra.data.store.ResolvedScreen
import com.example.momentra.data.store.ScreenResolver
import com.example.momentra.ui.components.MomentraFullScreenDialog
import com.example.momentra.ui.components.bottomNavContentPadding
import com.example.momentra.ui.group.actioncenter.GroupActionCenterShell
import com.example.momentra.ui.group.shared.GroupQuickAddFallbackSheet
import com.example.momentra.ui.group.empty.create.CreateEmptyScreen as GroupCreateEmptyScreen
import com.example.momentra.ui.group.empty.create.GroupCreateViewModel
import com.example.momentra.ui.group.empty.life.LifeEmptyScreen as GroupLifeEmptyScreen
import com.example.momentra.ui.group.empty.memory.MemoryEmptyScreen as GroupMemoryEmptyScreen
import com.example.momentra.ui.group.empty.moments.MomentsEmptyScreen as GroupMomentsEmptyScreen
import com.example.momentra.ui.group.empty.pulse.PulseEmptyScreen as GroupPulseEmptyScreen
import com.example.momentra.ui.group.life.GroupLifeScreen
import com.example.momentra.ui.group.memory.trip.TripMemoryScreen
import com.example.momentra.ui.group.moments.trip.TripMomentsScreen
import com.example.momentra.ui.group.pulse.trip.TripPulseScreen
import com.example.momentra.ui.group.settlement.TripSettlementScreen
import com.example.momentra.ui.group.pulse.purchase.PurchasePulseScreen
import com.example.momentra.ui.group.moments.purchase.PurchaseMomentsScreen
import com.example.momentra.ui.group.memory.purchase.PurchaseMemoryScreen
import com.example.momentra.ui.group.pulse.living.LivingPulseScreen
import com.example.momentra.ui.group.pulse.living.GroupActivitySource
import com.example.momentra.ui.group.pulse.living.LivingActivityScreen
import com.example.momentra.ui.group.pulse.living.LivingActivityEditSheet
import com.example.momentra.ui.group.moments.living.LivingMomentsScreen
import com.example.momentra.ui.group.memory.living.LivingMemoryScreen
import com.example.momentra.ui.group.setup.experience.SharedExperienceSetupScreen
import com.example.momentra.ui.group.setup.living.SharedLivingSetupScreen
import com.example.momentra.ui.group.setup.purchase.SharedPurchaseSetupScreen
import com.example.momentra.ui.setup.GuidedSetupLoadingPlaceholder
import com.example.momentra.ui.shared.MomentraLoadingIndicator
import com.example.momentra.ui.group.shared.BottomNavBar as GroupBottomNavBar
import com.example.momentra.ui.group.shared.BottomTab as GroupBottomTab
import com.example.momentra.ui.personal.shared.motion.PersistentTabPane
import com.example.momentra.ui.group.shared.GroupGlassCard
import com.example.momentra.ui.group.shared.GroupPrimaryCta
import com.example.momentra.ui.group.GroupMomentManageViewModel
import com.example.momentra.ui.group.GroupSessionViewModel
import com.example.momentra.ui.shared.lifecycle.LifecycleAction
import com.example.momentra.ui.shared.lifecycle.LifecycleContextType
import com.example.momentra.ui.shared.lifecycle.MomentLifecycleCoordinator
import com.example.momentra.ui.shared.lifecycle.MomentLifecycleException
import com.example.momentra.ui.group.shared.GroupMomentManageSheet
import com.example.momentra.ui.group.shared.GroupMomentTabScaffold
import com.example.momentra.ui.group.shared.GroupMomentAccessGate
import com.example.momentra.ui.group.shared.deriveGroupSessionMomentState
import com.example.momentra.ui.group.shared.resolveGroupMomentManageContext
import com.example.momentra.ui.group.shared.resolveGroupMomentSwitcherOptions
import com.example.momentra.ui.personal.empty.create.LoadState
import com.example.momentra.ui.shell.ShellActionRouter
import com.example.momentra.ui.theme.AppContext
import com.example.momentra.ui.theme.AppSpacing
import kotlinx.coroutines.launch
import kotlinx.serialization.json.JsonObject

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GroupHomePlaceholder(
    createViewModel: GroupCreateViewModel = viewModel(),
    sessionViewModel: GroupSessionViewModel = viewModel(),
) {
    var selectedTab by rememberSaveable { mutableStateOf(GroupBottomTab.PULSE) }
    val visitedTabs = remember {
        mutableStateOf(setOf(GroupBottomTab.PULSE))
    }
    LaunchedEffect(selectedTab) {
        if (selectedTab != GroupBottomTab.ADD) {
            visitedTabs.value = visitedTabs.value + selectedTab
            MomentraAnalytics.logEvent("perf_mark", mapOf("name" to "selected-tab-visible"))
        }
    }
    var previousTab by rememberSaveable { mutableStateOf(GroupBottomTab.PULSE) }
    var showCreateOverlay by rememberSaveable { mutableStateOf(false) }
    var showQuickAddSheet by rememberSaveable { mutableStateOf(false) }
    var quickAddActionId by rememberSaveable { mutableStateOf<String?>(null) }
    fun openQuickAdd(actionId: String? = null) {
        quickAddActionId = actionId
        showQuickAddSheet = true
    }
    fun closeQuickAdd() {
        showQuickAddSheet = false
        quickAddActionId = null
    }
    var tripMomentsReloadKey by rememberSaveable { mutableStateOf(0) }
    var showManageSheet by rememberSaveable { mutableStateOf(false) }
    var inviteMomentId by rememberSaveable { mutableStateOf<String?>(null) }
    var inviteMomentLabel by rememberSaveable { mutableStateOf<String?>(null) }
    var archiveConfirmId by rememberSaveable { mutableStateOf<String?>(null) }
    var archiveConfirmType by rememberSaveable { mutableStateOf<String?>(null) }
    var archiveConfirmLabel by rememberSaveable { mutableStateOf<String?>(null) }
    var leaveConfirmId by rememberSaveable { mutableStateOf<String?>(null) }
    var leaveConfirmType by rememberSaveable { mutableStateOf<String?>(null) }
    var leaveConfirmLabel by rememberSaveable { mutableStateOf<String?>(null) }
    var selectedMomentType by rememberSaveable { mutableStateOf("") }
    val groupBootstrap by sessionViewModel.bootstrap.collectAsState()
    val sessionLoading by sessionViewModel.loading.collectAsState()
    var showLivingActivity by rememberSaveable { mutableStateOf(false) }
    var showTripSettlement by rememberSaveable { mutableStateOf(false) }
    var editingLivingActivityId by rememberSaveable { mutableStateOf<String?>(null) }
    var livingActivityReloadToken by rememberSaveable { mutableStateOf(0) }

    val groupManageViewModel: GroupMomentManageViewModel = viewModel()
    val manageScope = rememberCoroutineScope()

    val bootstrapState by BootstrapStore.state.collectAsState()
    val appBootstrap = bootstrapState.data
    val visibleTabSlug = visibleGroupTabSlug(selectedTab, previousTab)
    val tabResolved = ScreenResolver.resolve(AppContext.GROUP, visibleTabSlug, appBootstrap)

    var draftMomentId by rememberSaveable { mutableStateOf<String?>(null) }
    var draftMomentType by rememberSaveable { mutableStateOf<String?>(null) }
    var activeMomentType by rememberSaveable { mutableStateOf<String?>(null) }
    var focusMomentId by rememberSaveable { mutableStateOf<String?>(null) }
    var hasDraft by rememberSaveable { mutableStateOf(false) }
    /** Survives process death while setup overlay is open — reopens the same draft. */
    var openSetupMomentId by rememberSaveable { mutableStateOf<String?>(null) }
    var openSetupMomentType by rememberSaveable { mutableStateOf<String?>(null) }

    val setupMoment by createViewModel.setupMoment.collectAsState()
    val creatingTypeCode by createViewModel.creatingTypeCode.collectAsState()
    val createError by createViewModel.createError.collectAsState()
    val setupActivated by createViewModel.setupActivated.collectAsState()
    val openActiveAfterSetup by createViewModel.openActiveAfterSetup.collectAsState()
    val setupViewModel = createViewModel.setupViewModel
    val setupState by setupViewModel.setupState.collectAsState()
    val setupPreview by setupViewModel.setupPreview.collectAsState()
    val submittingSetup by setupViewModel.submittingSetup.collectAsState()
    val setupError by setupViewModel.setupError.collectAsState()
    val setupSaveState by setupViewModel.saveStatus.collectAsState()
    val previewError by setupViewModel.previewError.collectAsState()
    val previewLoading by setupViewModel.previewLoading.collectAsState()
    val showMomentSetup = setupMoment != null
    val setupLoading = setupState is LoadState.Loading || setupState is LoadState.Idle
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    var skipFirstGroupResume by remember { mutableStateOf(true) }

    // Cross-client archive sync: refresh inventory when returning to foreground.
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event != Lifecycle.Event.ON_RESUME) return@LifecycleEventObserver
            if (skipFirstGroupResume) {
                skipFirstGroupResume = false
                return@LifecycleEventObserver
            }
            manageScope.launch {
                sessionViewModel.softRefreshGroupSession()
                groupBootstrap?.let { bootstrap ->
                    val momentState = deriveGroupSessionMomentState(bootstrap, selectedMomentType)
                    selectedMomentType = momentState.selectedMomentType
                    activeMomentType = momentState.activeMomentType
                    focusMomentId = momentState.focusMomentId
                    draftMomentId = momentState.draftMomentId
                    draftMomentType = momentState.draftMomentType
                    hasDraft = momentState.hasDraft
                }
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    LaunchedEffect(Unit) {
        // forceNextEnsure (set on logout) forces network so prior account inventory cannot stick.
        sessionViewModel.ensureGroupSession(force = false)
    }

    LaunchedEffect(groupBootstrap) {
        if (groupBootstrap == null) {
            // rememberSaveable can restore prior account moment ids across logout remount.
            selectedMomentType = ""
            activeMomentType = null
            focusMomentId = null
            draftMomentId = null
            draftMomentType = null
            hasDraft = false
            return@LaunchedEffect
        }
        groupBootstrap?.let { bootstrap ->
            val pinned = ShellActionRouter.peekPinnedGroupMomentId()
            if (!pinned.isNullOrBlank()) {
                val option = resolveGroupMomentSwitcherOptions(bootstrap)
                    .firstOrNull { it.momentId == pinned }
                if (option != null) {
                    selectedMomentType = option.typeCode
                    activeMomentType = option.typeCode
                    focusMomentId = option.momentId
                    ShellActionRouter.clearPinnedGroupMomentId()
                    MomentraAnalytics.logEvent("invite_destination_opened")
                } else {
                    // Keep pin until inventory includes the accepted moment.
                    focusMomentId = pinned
                }
                return@let
            }
            val momentState = deriveGroupSessionMomentState(bootstrap, selectedMomentType)
            selectedMomentType = momentState.selectedMomentType
            activeMomentType = momentState.activeMomentType
            focusMomentId = momentState.focusMomentId
            draftMomentId = momentState.draftMomentId
            draftMomentType = momentState.draftMomentType
            hasDraft = momentState.hasDraft

            if (hasDraft && !bootstrap.draftMomentId.isNullOrBlank() &&
                !bootstrap.draftMomentType.isNullOrBlank()
            ) {
                SetupRepository.rememberGroupMoment(
                    bootstrap.draftMomentId!!,
                    bootstrap.draftMomentType!!,
                )
            }
        }
    }

    val switcherOptions = resolveGroupMomentSwitcherOptions(groupBootstrap)
    val manageContext = resolveGroupMomentManageContext(selectedMomentType, groupBootstrap)
    val isSetupPhase = tabResolved.name.startsWith("SETUP_")
    val isActivePhase = tabResolved.name.startsWith("ACTIVE_")
    val hasActiveGroupMoments = switcherOptions.isNotEmpty()
    val showGroupLifeCommandCenter = hasActiveGroupMoments
    val isExperienceActive = hasActiveGroupMoments && activeMomentType == "SHARED_EXPERIENCE"
    val isPurchaseActive = hasActiveGroupMoments && activeMomentType == "SHARED_PURCHASE"
    val isLivingActive = hasActiveGroupMoments && activeMomentType == "SHARED_LIVING"

    fun refreshAfterGroupManage(
        replacementMomentId: String? = null,
        replacementMomentTypeCode: String? = null,
        useExplicitSelection: Boolean = false,
    ) {
        manageScope.launch {
            sessionViewModel.softRefreshGroupSession()
            val bootstrap = sessionViewModel.bootstrap.value ?: return@launch
            val options = resolveGroupMomentSwitcherOptions(bootstrap)
            if (useExplicitSelection && !replacementMomentId.isNullOrBlank()) {
                val type = replacementMomentTypeCode ?: selectedMomentType
                selectedMomentType = type
                activeMomentType = type
                focusMomentId = replacementMomentId
            } else if (options.isEmpty()) {
                selectedMomentType = ""
                activeMomentType = null
                focusMomentId = null
            } else {
                val momentState = deriveGroupSessionMomentState(bootstrap, selectedMomentType)
                selectedMomentType = momentState.selectedMomentType
                activeMomentType = momentState.activeMomentType
                focusMomentId = momentState.focusMomentId
            }
        }
    }

    fun runGroupLifecycle(action: LifecycleAction) {
        val ctx = manageContext ?: return
        manageScope.launch {
            val inventory = MomentLifecycleCoordinator.groupInventory(groupBootstrap?.moments.orEmpty())
            runCatching {
                MomentLifecycleCoordinator.run(
                    contextType = LifecycleContextType.GROUP,
                    momentId = ctx.momentId,
                    momentTypeCode = ctx.typeCode,
                    action = action,
                    inventory = inventory,
                    selectedMomentId = focusMomentId,
                    previousStatus = ctx.status,
                )
            }.onSuccess { result ->
                showManageSheet = false
                val excludeOnSuccess =
                    action == LifecycleAction.ARCHIVE || action == LifecycleAction.COMPLETE
                if (excludeOnSuccess) {
                    refreshAfterGroupManage(
                        replacementMomentId = result.replacementMomentId,
                        replacementMomentTypeCode = result.replacementMomentTypeCode ?: ctx.typeCode,
                        useExplicitSelection = !result.replacementMomentId.isNullOrBlank(),
                    )
                    val toastLabel = when (action) {
                        LifecycleAction.COMPLETE -> "Moment completed"
                        else -> "Moment archived"
                    }
                    MomentraToast.success(toastLabel)
                } else {
                    refreshAfterGroupManage()
                    val toastLabel = when (action) {
                        LifecycleAction.PAUSE -> "Moment paused"
                        else -> "Moment resumed"
                    }
                    MomentraToast.success(toastLabel)
                }
            }.onFailure { err ->
                val msg = (err as? MomentLifecycleException)?.message
                    ?: err.message
                    ?: "Could not update moment"
                MomentraToast.error(msg)
            }
        }
    }

    fun handleGroupMomentSwitcherSelect(option: com.example.momentra.ui.group.shared.GroupMomentSwitcherOption) {
        selectedMomentType = option.typeCode
        activeMomentType = option.typeCode
        focusMomentId = option.momentId
    }

    @Composable
    fun wrapActiveWithHeader(tabLabel: String, content: @Composable () -> Unit) {
        if (hasActiveGroupMoments && switcherOptions.isNotEmpty()) {
            GroupMomentTabScaffold(
                tabLabel = tabLabel,
                switcherOptions = switcherOptions,
                selectedTypeCode = selectedMomentType,
                onSelect = { handleGroupMomentSwitcherSelect(it) },
                onManageClick = if (manageContext != null) ({ showManageSheet = true }) else null,
                onInviteMoment = { option ->
                    handleGroupMomentSwitcherSelect(option)
                    inviteMomentId = option.momentId
                    inviteMomentLabel = option.label
                },
                onDeleteMoment = { option ->
                    archiveConfirmId = option.momentId
                    archiveConfirmType = option.typeCode
                    archiveConfirmLabel = option.label
                },
                onLeaveMoment = { option ->
                    leaveConfirmId = option.momentId
                    leaveConfirmType = option.typeCode
                    leaveConfirmLabel = option.label
                },
                content = content,
            )
        } else {
            content()
        }
    }

    LaunchedEffect(setupActivated) {
        if (setupActivated) {
            val activatedType = openSetupMomentType
                ?: setupMoment?.momentTypeCode
                ?: selectedMomentType
                ?: "SHARED_EXPERIENCE"
            createViewModel.consumeSetupActivated()
            showCreateOverlay = false
            openSetupMomentId = null
            openSetupMomentType = null
            sessionViewModel.softRefreshGroupSession()
            groupBootstrap?.let { bootstrap ->
                val momentState = deriveGroupSessionMomentState(bootstrap, selectedMomentType)
                selectedMomentType = momentState.selectedMomentType
                activeMomentType = momentState.activeMomentType
                focusMomentId = momentState.focusMomentId
                draftMomentId = momentState.draftMomentId
                draftMomentType = momentState.draftMomentType
                hasDraft = momentState.hasDraft
            }
            MomentraToast.success(
                MomentraToastCopy.groupActivationSuccess(context, activatedType),
            )
        }
    }

    LaunchedEffect(setupMoment?.momentId, setupMoment?.momentTypeCode) {
        val moment = setupMoment
        if (moment != null) {
            openSetupMomentId = moment.momentId
            openSetupMomentType = moment.momentTypeCode
        }
    }

    // Process death / ViewModel loss: overlay still open with saved draft ids → reopen once.
    var didAutoResumeOpenSetup by rememberSaveable { mutableStateOf(false) }
    LaunchedEffect(showCreateOverlay, openSetupMomentId, setupMoment, creatingTypeCode) {
        if (!showCreateOverlay) {
            didAutoResumeOpenSetup = false
            return@LaunchedEffect
        }
        if (
            setupMoment == null &&
            creatingTypeCode == null &&
            !openSetupMomentId.isNullOrBlank() &&
            !didAutoResumeOpenSetup
        ) {
            val type = openSetupMomentType?.takeIf { it.isNotBlank() }
                ?: draftMomentType?.takeIf { it.isNotBlank() }
            if (type != null) {
                didAutoResumeOpenSetup = true
                createViewModel.resumeDraft(openSetupMomentId!!, type)
            }
        }
    }

    LaunchedEffect(openActiveAfterSetup) {
        if (openActiveAfterSetup) {
            createViewModel.consumeOpenActiveAfterSetup()
            showCreateOverlay = false
        }
    }

    val appContext = "group"
    val activeId = focusMomentId.orEmpty()

    // SSE invalidate → bump reloadKey for pulse/moments/memory (all Group templates)
    val sseActive = isExperienceActive || isPurchaseActive || isLivingActive
    LaunchedEffect(activeId, sseActive) {
        if (!sseActive || activeId.isBlank()) return@LaunchedEffect
        if (GroupMomentAccessGate.wasCleared(activeId)) return@LaunchedEffect
        val job = TripMomentSseClient.start(
            scope = this,
            momentId = activeId,
            onInvalidate = { tripMomentsReloadKey += 1 },
            onTerminalFailure = { momentId, _ ->
                manageScope.launch {
                    GroupMomentAccessGate.onInaccessible(momentId)
                    focusMomentId = sessionViewModel.selectedMomentId.value
                }
            },
        )
        try {
            job.join()
        } finally {
            job.cancel()
        }
    }

    DisposableEffect(Unit) {
        GroupMomentAccessGate.handler = { momentId ->
            sessionViewModel.handleMomentInaccessible(momentId)
            focusMomentId = sessionViewModel.selectedMomentId.value
        }
        onDispose { GroupMomentAccessGate.handler = null }
    }

    fun openCreateOverlay() {
        val screen = resolveScreenName(
            appContext,
            visibleGroupTabSlug(selectedTab, previousTab),
            ScreenOverlay.NONE,
        )
        MomentraAnalytics.logEvent(
            "create_moment_tap",
            mapOf("app_context" to appContext, "screen" to screen),
        )
        showCreateOverlay = true
    }

    fun openSetupForType(typeCode: String) {
        MomentraAnalytics.logEvent(
            "create_moment_type_select",
            mapOf("app_context" to appContext, "moment_type" to typeCode, "phase" to "empty_cta"),
        )
        // Keep create overlay up so the loading → setup handoff stays on one sheet.
        showCreateOverlay = true
        createViewModel.openSetupForType(typeCode)
    }

    fun resumeSetupDraft() {
        val id = draftMomentId?.takeIf { it.isNotBlank() } ?: openSetupMomentId
        val type = draftMomentType?.takeIf { it.isNotBlank() }
            ?: openSetupMomentType?.takeIf { it.isNotBlank() }
        if (!id.isNullOrBlank() && !type.isNullOrBlank()) {
            showCreateOverlay = true
            createViewModel.resumeDraft(id, type)
        } else if (!id.isNullOrBlank()) {
            // Type unknown — still resume; repository probes group categories.
            showCreateOverlay = true
            createViewModel.resumeDraft(id, "SHARED_EXPERIENCE")
        } else {
            openCreateOverlay()
        }
    }

    val screenOverlay = when {
        showCreateOverlay -> ScreenOverlay.CREATE
        showQuickAddSheet -> ScreenOverlay.QUICK_ADD
        else -> ScreenOverlay.NONE
    }
    LaunchedEffect(selectedTab, previousTab, showCreateOverlay, showQuickAddSheet) {
        val screenName = resolveScreenName(
            appContext,
            visibleGroupTabSlug(selectedTab, previousTab),
            screenOverlay,
        )
        MomentraAnalytics.logScreen(screenName, appContext)
    }

    DisposableEffect(Unit) {
        ShellActionRouter.registerGroupNewMomentHandler { showCreateOverlay = true }
        ShellActionRouter.registerGroupSelectLifeHandler { selectedTab = GroupBottomTab.LIFE }
        ShellActionRouter.registerGroupOpenMomentHandler { momentId, momentType ->
            manageScope.launch {
                MomentraAnalytics.logEvent("invite_group_selected")
                val inInventory = sessionViewModel.refreshAndSelectMoment(momentId, momentType)
                val bootstrap = sessionViewModel.bootstrap.value
                val option = resolveGroupMomentSwitcherOptions(bootstrap)
                    .firstOrNull { it.momentId == momentId }
                if (option != null) {
                    selectedMomentType = option.typeCode
                    activeMomentType = option.typeCode
                    focusMomentId = option.momentId
                    ShellActionRouter.clearPinnedGroupMomentId()
                    MomentraAnalytics.logEvent("invite_destination_opened")
                } else {
                    focusMomentId = momentId
                    if (!momentType.isNullOrBlank()) {
                        selectedMomentType = momentType
                        activeMomentType = momentType
                    }
                    if (inInventory) {
                        ShellActionRouter.clearPinnedGroupMomentId()
                    }
                }
                selectedTab = GroupBottomTab.PULSE
            }
        }
        onDispose {
            ShellActionRouter.unregisterGroupNewMomentHandler()
            ShellActionRouter.unregisterGroupOpenMomentHandler()
            ShellActionRouter.unregisterGroupSelectLifeHandler()
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        if (groupBootstrap == null && sessionLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .bottomNavContentPadding(includeScrollClearance = false),
                contentAlignment = Alignment.Center,
            ) {
                MomentraLoadingIndicator(label = "Loading moments…")
            }
        } else {
        Box(modifier = Modifier.fillMaxSize().bottomNavContentPadding(includeScrollClearance = false)) {
            // Lazy keep-alive: compose selected tab first; keep after first visit.
            val keepAliveTabs = listOf(
                GroupBottomTab.PULSE,
                GroupBottomTab.MOMENTS,
                GroupBottomTab.MEMORY,
                GroupBottomTab.LIFE,
            )
            keepAliveTabs.forEach { tab ->
                if (tab !in visitedTabs.value) return@forEach
                PersistentTabPane(visible = selectedTab == tab) {
                    when (tab) {
                GroupBottomTab.PULSE -> {
                    // Empty switcher wins over stale ACTIVE bootstrap (archive-all) — web parity.
                    // Active moment only when switcher has inventory + a bound id.
                    val showActivePulse = hasActiveGroupMoments && activeId.isNotBlank()
                    val pulseExperience = showActivePulse && activeMomentType == "SHARED_EXPERIENCE"
                    val pulsePurchase = showActivePulse && activeMomentType == "SHARED_PURCHASE"
                    val pulseLiving = showActivePulse && activeMomentType == "SHARED_LIVING"
                    when {
                        tabResolved == ResolvedScreen.LOADING ->
                            GroupPulseEmptyScreen(onCreateMoment = { openCreateOverlay() })
                        pulseExperience -> wrapActiveWithHeader("Pulse") {
                            TripPulseScreen(
                                momentId = activeId,
                                reloadKey = tripMomentsReloadKey,
                                onQuickAdd = { openQuickAdd(it) },
                                onViewAllActivity = { showLivingActivity = true },
                                onEditActivity = { id -> editingLivingActivityId = id },
                                onOpenSettlement = { showTripSettlement = true },
                            )
                        }
                        pulsePurchase -> wrapActiveWithHeader("Pulse") {
                            PurchasePulseScreen(
                                momentId = activeId,
                                reloadKey = tripMomentsReloadKey,
                                onQuickAdd = { openQuickAdd(it) },
                                onViewAllActivity = { showLivingActivity = true },
                                onOpenSettlement = { showTripSettlement = true },
                            )
                        }
                        pulseLiving -> wrapActiveWithHeader("Pulse") {
                            LivingPulseScreen(
                                momentId = activeId,
                                reloadToken = livingActivityReloadToken + tripMomentsReloadKey,
                                onQuickAdd = { openQuickAdd(it) },
                                onViewAllActivity = { showLivingActivity = true },
                                onEditActivity = { id -> editingLivingActivityId = id },
                                onOpenSettlement = { showTripSettlement = true },
                            )
                        }
                        showActivePulse -> wrapActiveWithHeader("Pulse") { GroupActivePhasePlaceholder() }
                        // Draft resume only when there is no live group moment to show.
                        (isSetupPhase || hasDraft) && !hasActiveGroupMoments ->
                            GroupPulseEmptyScreen(
                                onCreateMoment = { openCreateOverlay() },
                                onSharedExperience = { openSetupForType("SHARED_EXPERIENCE") },
                                onSharedPurchase = { openSetupForType("SHARED_PURCHASE") },
                                onSharedLiving = { openSetupForType("SHARED_LIVING") },
                                resumeDraft = true,
                                onContinueSetup = { resumeSetupDraft() },
                            )
                        else -> GroupPulseEmptyScreen(
                            onCreateMoment = { openCreateOverlay() },
                            onSharedExperience = { openSetupForType("SHARED_EXPERIENCE") },
                            onSharedPurchase = { openSetupForType("SHARED_PURCHASE") },
                            onSharedLiving = { openSetupForType("SHARED_LIVING") },
                        )
                    }
                }
                GroupBottomTab.MOMENTS -> {
                    when {
                        tabResolved == ResolvedScreen.LOADING ->
                            GroupMomentsEmptyScreen(onCreateMoment = { openCreateOverlay() })
                        hasActiveGroupMoments && activeMomentType == "SHARED_EXPERIENCE" -> wrapActiveWithHeader("Moments") {
                            if (activeId.isNotBlank()) {
                                TripMomentsScreen(
                                    momentId = activeId,
                                    reloadKey = tripMomentsReloadKey,
                                    onQuickAdd = { openQuickAdd() },
                                )
                            } else {
                                GroupMomentsEmptyScreen(onCreateMoment = { openCreateOverlay() })
                            }
                        }
                        hasActiveGroupMoments && activeMomentType == "SHARED_PURCHASE" -> wrapActiveWithHeader("Moments") {
                            PurchaseMomentsScreen(momentId = activeId.ifBlank { focusMomentId })
                        }
                        hasActiveGroupMoments && activeMomentType == "SHARED_LIVING" -> wrapActiveWithHeader("Moments") {
                            LivingMomentsScreen(momentId = activeId.ifBlank { focusMomentId })
                        }
                        hasActiveGroupMoments -> wrapActiveWithHeader("Moments") { GroupActivePhasePlaceholder(label = "Moments") }
                        isSetupPhase || hasDraft ->
                            GroupSetupResumeCard(
                                title = "Continue group setup",
                                subtitle = "Finish your draft to unlock Moments.",
                                onContinue = { resumeSetupDraft() },
                            )
                        else -> GroupMomentsEmptyScreen(onCreateMoment = { openCreateOverlay() })
                    }
                }
                GroupBottomTab.MEMORY -> {
                    when {
                        tabResolved == ResolvedScreen.LOADING ->
                            GroupMemoryEmptyScreen(onCreateMoment = { openCreateOverlay() })
                        hasActiveGroupMoments && activeMomentType == "SHARED_EXPERIENCE" -> wrapActiveWithHeader("Memory") {
                            TripMemoryScreen(
                                momentId = activeId.ifBlank { focusMomentId },
                                reloadKey = tripMomentsReloadKey,
                                onQuickAdd = { openQuickAdd() },
                            )
                        }
                        hasActiveGroupMoments && activeMomentType == "SHARED_PURCHASE" -> wrapActiveWithHeader("Memory") {
                            PurchaseMemoryScreen(momentId = activeId.ifBlank { focusMomentId })
                        }
                        hasActiveGroupMoments && activeMomentType == "SHARED_LIVING" -> wrapActiveWithHeader("Memory") {
                            LivingMemoryScreen(momentId = activeId.ifBlank { focusMomentId })
                        }
                        hasActiveGroupMoments -> wrapActiveWithHeader("Memory") { GroupActivePhasePlaceholder(label = "Memory") }
                        isSetupPhase || hasDraft ->
                            GroupSetupResumeCard(
                                title = "Continue group setup",
                                subtitle = "Finish your draft to unlock Memory.",
                                onContinue = { resumeSetupDraft() },
                            )
                        else -> GroupMemoryEmptyScreen(onCreateMoment = { openCreateOverlay() })
                    }
                }
                GroupBottomTab.LIFE -> {
                    when {
                        tabResolved == ResolvedScreen.LOADING ->
                            GroupLifeEmptyScreen(onCreateMoment = { openCreateOverlay() })
                        !hasActiveGroupMoments && (isSetupPhase || hasDraft) ->
                            GroupSetupResumeCard(
                                title = "Continue group setup",
                                subtitle = "Finish your draft to unlock Life.",
                                onContinue = { resumeSetupDraft() },
                            )
                        hasActiveGroupMoments && (isExperienceActive || isPurchaseActive || isLivingActive) ->
                            wrapActiveWithHeader("Life") {
                                GroupLifeScreen(onCreateMomentType = { type ->
                                    when (type) {
                                        "SHARED_EXPERIENCE", "SHARED_PURCHASE", "SHARED_LIVING" -> openSetupForType(type)
                                        else -> openCreateOverlay()
                                    }
                                })
                            }
                        hasActiveGroupMoments -> wrapActiveWithHeader("Life") { GroupActivePhasePlaceholder(label = "Life") }
                        else -> GroupLifeEmptyScreen(onCreateMoment = { openCreateOverlay() })
                    }
                }
                else -> Unit
                    }
                }
            }
        }
        } // end else (session loaded)
        GroupBottomNavBar(
            selectedTab = selectedTab,
            onTabSelected = { tab ->
                if (tab != GroupBottomTab.ADD) {
                    MomentraAnalytics.logEvent(
                        "tab_select",
                        mapOf("app_context" to appContext, "tab" to groupTabSlug(tab)),
                    )
                }
                if (tab == GroupBottomTab.ADD) {
                    if (hasActiveGroupMoments && activeId.isNotBlank()) {
                        openQuickAdd()
                    } else if ((isSetupPhase || hasDraft) && !hasActiveGroupMoments) {
                        resumeSetupDraft()
                    } else {
                        openCreateOverlay()
                    }
                    selectedTab = previousTab
                } else {
                    previousTab = tab
                    selectedTab = tab
                }
            },
            onCreateMoment = {
                if (hasActiveGroupMoments && activeId.isNotBlank()) {
                    openQuickAdd()
                } else if ((isSetupPhase || hasDraft) && !hasActiveGroupMoments) {
                    resumeSetupDraft()
                } else {
                    openCreateOverlay()
                }
                selectedTab = previousTab
            },
            modifier = Modifier.align(Alignment.BottomCenter),
        )

        if (showQuickAddSheet && (isExperienceActive || isPurchaseActive || isLivingActive)) {
            val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
            val momentType = when {
                isExperienceActive -> "SHARED_EXPERIENCE"
                isPurchaseActive -> "SHARED_PURCHASE"
                isLivingActive -> "SHARED_LIVING"
                else -> "SHARED_EXPERIENCE"
            }
            ModalBottomSheet(
                onDismissRequest = {
                    closeQuickAdd()
                    tripMomentsReloadKey += 1
                },
                sheetState = sheetState,
                containerColor = rememberGroupPalette().background,
            ) {
                GroupActionCenterShell(
                    momentId = activeId.ifBlank { focusMomentId.orEmpty() },
                    momentTypeCode = momentType,
                    initialActionId = quickAddActionId,
                    onClose = { closeQuickAdd() },
                    onSuccess = {
                        closeQuickAdd()
                        tripMomentsReloadKey += 1
                        MomentraToast.success("Quick Add saved")
                    },
                )
            }
        } else if (showQuickAddSheet) {
            GroupQuickAddFallbackSheet(onDismiss = { closeQuickAdd() })
        }

        if (showCreateOverlay) {
            MomentraFullScreenDialog(
                onDismissRequest = {
                    if (setupMoment != null) {
                        createViewModel.dismissSetup()
                    } else {
                        showCreateOverlay = false
                    }
                },
            ) {
                Box(modifier = Modifier.fillMaxSize()) {
                    GroupCreateEmptyScreen(
                        onCreateMoment = { openCreateOverlay() },
                        onSharedExperience = { openSetupForType("SHARED_EXPERIENCE") },
                        onSharedLiving = { openSetupForType("SHARED_LIVING") },
                        onSharedPurchase = { openSetupForType("SHARED_PURCHASE") },
                        onClose = {
                            if (setupMoment != null) {
                                createViewModel.dismissSetup()
                            } else {
                                showCreateOverlay = false
                            }
                        },
                    )
                    if (creatingTypeCode != null && !showMomentSetup) {
                        Box(
                            modifier = Modifier.fillMaxSize().background(
                                rememberGroupPalette().background.copy(alpha = 0.55f),
                            ),
                            contentAlignment = Alignment.Center,
                        ) {
                            CircularProgressIndicator()
                        }
                    }
                    createError?.let { err ->
                        Text(
                            err,
                            color = MaterialTheme.colorScheme.error,
                            modifier = Modifier
                                .align(Alignment.BottomCenter)
                                .padding(24.dp),
                        )
                    }
                    if (showMomentSetup) {
                        val momentId = setupMoment?.momentId
                        val typeCode = setupMoment?.momentTypeCode ?: "SHARED_EXPERIENCE"
                        Box(modifier = Modifier.fillMaxSize()) {
                            when (val state = setupState) {
                                is LoadState.Loading, is LoadState.Idle -> {
                                    GuidedSetupLoadingPlaceholder()
                                }
                                is LoadState.Error -> {
                                    Column(
                                        modifier = Modifier
                                            .fillMaxSize()
                                            .padding(24.dp),
                                        verticalArrangement = Arrangement.Center,
                                        horizontalAlignment = Alignment.CenterHorizontally,
                                    ) {
                                        Text(
                                            state.message,
                                            style = MaterialTheme.typography.bodyMedium,
                                            color = MaterialTheme.colorScheme.error,
                                            textAlign = TextAlign.Center,
                                        )
                                        TextButton(
                                            onClick = { createViewModel.retryLoadSetup() },
                                            enabled = !setupLoading,
                                            modifier = Modifier.padding(top = 12.dp),
                                        ) {
                                            Text("Retry")
                                        }
                                        TextButton(
                                            onClick = {
                                                createViewModel.dismissSetup()
                                                openSetupMomentId = null
                                                openSetupMomentType = null
                                                showCreateOverlay = false
                                            },
                                        ) {
                                            Text("Close")
                                        }
                                    }
                                }
                                is LoadState.Loaded -> {
                                    if (momentId != null) {
                                        val draftSave: (JsonObject) -> Unit = { answers ->
                                            setupViewModel.scheduleDraftSave(momentId, answers)
                                        }
                                        val flushDraft: (JsonObject, (Boolean) -> Unit) -> Unit =
                                            { answers, onComplete ->
                                                setupViewModel.flushPendingSave(
                                                    momentId,
                                                    answers,
                                                    onComplete,
                                                )
                                            }
                                        val previewRefresh: (JsonObject) -> Unit = { answers ->
                                            setupViewModel.refreshPreview(momentId, answers)
                                        }
                                        val onSubmit: (JsonObject) -> Unit = { answers ->
                                            createViewModel.submitSetup(answers)
                                        }
                                        when (typeCode) {
                                            "SHARED_PURCHASE" -> SharedPurchaseSetupScreen(
                                                setup = state.data,
                                                preview = setupPreview,
                                                submitting = submittingSetup,
                                                error = setupError,
                                                onClose = { createViewModel.dismissSetup() },
                                                onDraftSave = draftSave,
                                                onFlushDraft = flushDraft,
                                                onPreviewRefresh = previewRefresh,
                                                onSubmit = onSubmit,
                                                saveState = setupSaveState,
                                                previewError = previewError,
                                                previewLoading = previewLoading,
                                                onClearPreviewError = { setupViewModel.clearPreviewError() },
                                            )
                                            "SHARED_LIVING" -> SharedLivingSetupScreen(
                                                setup = state.data,
                                                preview = setupPreview,
                                                submitting = submittingSetup,
                                                error = setupError,
                                                onClose = { createViewModel.dismissSetup() },
                                                onDraftSave = draftSave,
                                                onFlushDraft = flushDraft,
                                                onPreviewRefresh = previewRefresh,
                                                onSubmit = onSubmit,
                                                saveState = setupSaveState,
                                                previewError = previewError,
                                                previewLoading = previewLoading,
                                                onClearPreviewError = { setupViewModel.clearPreviewError() },
                                            )
                                            else -> SharedExperienceSetupScreen(
                                                setup = state.data,
                                                preview = setupPreview,
                                                submitting = submittingSetup,
                                                error = setupError,
                                                onClose = { createViewModel.dismissSetup() },
                                                onDraftSave = draftSave,
                                                onFlushDraft = flushDraft,
                                                onPreviewRefresh = previewRefresh,
                                                onSubmit = onSubmit,
                                                saveState = setupSaveState,
                                                previewError = previewError,
                                                previewLoading = previewLoading,
                                                onClearPreviewError = { setupViewModel.clearPreviewError() },
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    }
                    IconButton(
                        onClick = {
                            if (setupMoment != null) {
                                createViewModel.dismissSetup()
                                openSetupMomentId = null
                                openSetupMomentType = null
                            } else {
                                showCreateOverlay = false
                                openSetupMomentId = null
                                openSetupMomentType = null
                            }
                        },
                        modifier = Modifier.align(Alignment.TopEnd),
                    ) {
                        Icon(Icons.Default.Close, contentDescription = "Close")
                    }
                }
            }
        }

        if (showLivingActivity && (isLivingActive || isExperienceActive) && activeId.isNotBlank()) {
            MomentraFullScreenDialog(onDismissRequest = { showLivingActivity = false }) {
                LivingActivityScreen(
                    momentId = activeId,
                    reloadToken = livingActivityReloadToken,
                    onBack = { showLivingActivity = false },
                    onEditActivity = { id -> editingLivingActivityId = id },
                    source = if (isExperienceActive) GroupActivitySource.TRIP else GroupActivitySource.LIVING,
                )
            }
        }

        if (showTripSettlement && (isExperienceActive || isPurchaseActive || isLivingActive) && activeId.isNotBlank()) {
            MomentraFullScreenDialog(onDismissRequest = { showTripSettlement = false }) {
                TripSettlementScreen(
                    momentId = activeId,
                    onBack = { showTripSettlement = false },
                )
            }
        }

        editingLivingActivityId?.let { id ->
            if ((isLivingActive || isExperienceActive) && activeId.isNotBlank()) {
                LivingActivityEditSheet(
                    momentId = activeId,
                    eventId = id,
                    onDismiss = { editingLivingActivityId = null },
                    onSaved = {
                        livingActivityReloadToken += 1
                        tripMomentsReloadKey += 1
                    },
                    source = if (isExperienceActive) GroupActivitySource.TRIP else GroupActivitySource.LIVING,
                )
            }
        }

        GroupMomentManageSheet(
            visible = showManageSheet,
            context = manageContext,
            onDismiss = { showManageSheet = false },
            onEditSetup = {
                showManageSheet = false
                manageContext?.let { ctx ->
                    SetupRepository.rememberGroupMoment(ctx.momentId, ctx.typeCode)
                    createViewModel.resumeDraft(ctx.momentId, ctx.typeCode)
                    showCreateOverlay = true
                }
            },
            onEditName = { name ->
                manageContext?.let { ctx ->
                    groupManageViewModel.patchMoment(
                        momentId = ctx.momentId,
                        body = GroupMomentUpdateRequestDto(momentName = name),
                        onSuccess = {
                            refreshAfterGroupManage()
                            MomentraToast.success("Moment updated")
                        },
                        onError = { MomentraToast.error(it) },
                    )
                }
            },
            onPause = { runGroupLifecycle(LifecycleAction.PAUSE) },
            onResume = { runGroupLifecycle(LifecycleAction.RESUME) },
            onComplete = { runGroupLifecycle(LifecycleAction.COMPLETE) },
            onArchive = { runGroupLifecycle(LifecycleAction.ARCHIVE) },
            onDeletePermanently = { runGroupLifecycle(LifecycleAction.DELETE) },
            isOwner = manageContext?.isOwned != false,
            onLeave = { runGroupLifecycle(LifecycleAction.LEAVE) },
        )

        inviteMomentId?.let { mid ->
            com.example.momentra.ui.shared.MomentInviteBottomSheet(
                momentId = mid,
                momentLabel = inviteMomentLabel,
                onDismiss = {
                    inviteMomentId = null
                    inviteMomentLabel = null
                },
            )
        }

        archiveConfirmId?.let { mid ->
            val type = archiveConfirmType.orEmpty()
            val label = archiveConfirmLabel ?: "this moment"
            androidx.compose.material3.AlertDialog(
                onDismissRequest = {
                    archiveConfirmId = null
                    archiveConfirmType = null
                    archiveConfirmLabel = null
                },
                title = { androidx.compose.material3.Text("Archive moment") },
                text = {
                    androidx.compose.material3.Text(
                        "Archive $label? This removes it from your active list.",
                    )
                },
                confirmButton = {
                    androidx.compose.material3.TextButton(
                        onClick = {
                            archiveConfirmId = null
                            archiveConfirmType = null
                            archiveConfirmLabel = null
                            handleGroupMomentSwitcherSelect(
                                com.example.momentra.ui.group.shared.GroupMomentSwitcherOption(
                                    typeCode = type,
                                    label = label,
                                    momentId = mid,
                                ),
                            )
                            manageScope.launch {
                                val inventory = MomentLifecycleCoordinator.groupInventory(
                                    groupBootstrap?.moments.orEmpty(),
                                )
                                runCatching {
                                    MomentLifecycleCoordinator.run(
                                        contextType = LifecycleContextType.GROUP,
                                        momentId = mid,
                                        momentTypeCode = type,
                                        action = LifecycleAction.ARCHIVE,
                                        inventory = inventory,
                                        selectedMomentId = mid,
                                        previousStatus = "ACTIVE",
                                    )
                                }.onSuccess { result ->
                                    refreshAfterGroupManage(
                                        replacementMomentId = result.replacementMomentId,
                                        replacementMomentTypeCode = result.replacementMomentTypeCode ?: type,
                                        useExplicitSelection = !result.replacementMomentId.isNullOrBlank(),
                                    )
                                    MomentraToast.success("Moment archived")
                                }.onFailure {
                                    MomentraToast.error(it.message ?: "Could not archive")
                                }
                            }
                        },
                    ) {
                        androidx.compose.material3.Text("Archive")
                    }
                },
                dismissButton = {
                    androidx.compose.material3.TextButton(
                        onClick = {
                            archiveConfirmId = null
                            archiveConfirmType = null
                            archiveConfirmLabel = null
                        },
                    ) {
                        androidx.compose.material3.Text("Cancel")
                    }
                },
            )
        }

        leaveConfirmId?.let { mid ->
            val type = leaveConfirmType.orEmpty()
            val label = leaveConfirmLabel ?: "this moment"
            androidx.compose.material3.AlertDialog(
                onDismissRequest = {
                    leaveConfirmId = null
                    leaveConfirmType = null
                    leaveConfirmLabel = null
                },
                title = { androidx.compose.material3.Text("Leave moment") },
                text = {
                    androidx.compose.material3.Text(
                        "Leave $label? You will lose access. The moment stays for others.",
                    )
                },
                confirmButton = {
                    androidx.compose.material3.TextButton(
                        onClick = {
                            leaveConfirmId = null
                            leaveConfirmType = null
                            leaveConfirmLabel = null
                            handleGroupMomentSwitcherSelect(
                                com.example.momentra.ui.group.shared.GroupMomentSwitcherOption(
                                    typeCode = type,
                                    label = label,
                                    momentId = mid,
                                ),
                            )
                            manageScope.launch {
                                val inventory = MomentLifecycleCoordinator.groupInventory(
                                    groupBootstrap?.moments.orEmpty(),
                                )
                                runCatching {
                                    MomentLifecycleCoordinator.run(
                                        contextType = LifecycleContextType.GROUP,
                                        momentId = mid,
                                        momentTypeCode = type,
                                        action = LifecycleAction.LEAVE,
                                        inventory = inventory,
                                        selectedMomentId = mid,
                                        previousStatus = "ACTIVE",
                                    )
                                }.onSuccess { result ->
                                    refreshAfterGroupManage(
                                        replacementMomentId = result.replacementMomentId,
                                        replacementMomentTypeCode = result.replacementMomentTypeCode ?: type,
                                        useExplicitSelection = !result.replacementMomentId.isNullOrBlank(),
                                    )
                                    MomentraToast.success("Left moment")
                                }.onFailure {
                                    MomentraToast.error(it.message ?: "Could not leave")
                                }
                            }
                        },
                    ) {
                        androidx.compose.material3.Text("Leave")
                    }
                },
                dismissButton = {
                    androidx.compose.material3.TextButton(
                        onClick = {
                            leaveConfirmId = null
                            leaveConfirmType = null
                            leaveConfirmLabel = null
                        },
                    ) {
                        androidx.compose.material3.Text("Cancel")
                    }
                },
            )
        }
    }
}

@Composable
private fun GroupActivePhasePlaceholder(label: String = "Pulse") {
    val palette = rememberGroupPalette()
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(palette.background)
            .padding(horizontal = AppSpacing.screenHorizontal),
        contentAlignment = Alignment.Center,
    ) {
        GroupGlassCard(modifier = Modifier.fillMaxWidth()) {
            Column(
                verticalArrangement = Arrangement.spacedBy(12.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(
                    "Group $label is active",
                    style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                    color = palette.onSurface,
                    textAlign = TextAlign.Center,
                )
                Text(
                    "Active Trip / Purchase / Living dashboards ship after Phase 2 setup. " +
                        "Your moment is live — coordination surfaces will open here next.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = palette.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                )
            }
        }
    }
}

@Composable
private fun GroupSetupResumeCard(
    title: String,
    subtitle: String,
    onContinue: () -> Unit,
) {
    val palette = rememberGroupPalette()
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(palette.background)
            .padding(horizontal = AppSpacing.screenHorizontal),
        contentAlignment = Alignment.Center,
    ) {
        GroupGlassCard(modifier = Modifier.fillMaxWidth()) {
            Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
                Text(
                    title,
                    style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                    color = palette.onSurface,
                )
                Text(subtitle, style = MaterialTheme.typography.bodyMedium, color = palette.onSurfaceVariant)
                GroupPrimaryCta(label = "Continue Setup", onClick = onContinue)
            }
        }
    }
}

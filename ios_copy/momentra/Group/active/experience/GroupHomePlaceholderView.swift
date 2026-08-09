import SwiftUI
import Combine

struct GroupHomePlaceholderView: View {
    @ObservedObject private var sessionManager = GroupSessionManager.shared
    @ObservedObject private var bootstrapStore = BootstrapStore.shared
    @ObservedObject private var groupSession = GroupSessionStore.shared
    @Environment(\.scenePhase) private var scenePhase
    @State private var createViewModel = GroupCreateViewModel()
    @State private var selectedTab: GroupBottomTab = .pulse
    @State private var previousTab: GroupBottomTab = .pulse
    @State private var showCreateOverlay = false
    @State private var showActionCenter = false
    @State private var quickAddActionId: String? = nil
    @State private var showManageSheet = false
    @State private var inviteMomentId: String?
    @State private var inviteMomentLabel: String?
    @State private var switcherArchiveOption: GroupMomentSwitcherOption?
    @State private var switcherLeaveOption: GroupMomentSwitcherOption?
    @State private var showFallbackSheet = false
    @State private var selectedMomentType = GroupMomentSelectionHolder.store.selectedMomentTypeCode
    @State private var tripMomentsReloadKey = 0
    @State private var tripMomentStream = TripMomentStreamClient()
    @State private var showLivingActivity = false
    @State private var showTripSettlement = false
    @State private var editingLivingActivityId: String?
    @State private var livingActivityReloadToken = 0

    private var switcherOptions: [GroupMomentSwitcherOption] {
        resolveGroupMomentSwitcherOptions(bootstrap: groupSession.bootstrap)
    }

    private var manageContext: GroupMomentManageContext? {
        resolveGroupMomentManageContext(typeCode: selectedMomentType, bootstrap: groupSession.bootstrap)
    }

    private var activeMomentTypeForUI: String? {
        switcherOptions.first(where: { $0.typeCode == selectedMomentType })?.typeCode
            ?? sessionManager.activeMomentType
    }

    private var activeExperienceMomentId: String? {
        switcherOptions.first(where: { $0.typeCode == "SHARED_EXPERIENCE" })?.momentId
            ?? (activeMomentTypeForUI == "SHARED_EXPERIENCE" ? sessionManager.activeMomentId : nil)
    }

    private var activePurchaseMomentId: String? {
        switcherOptions.first(where: { $0.typeCode == "SHARED_PURCHASE" })?.momentId
            ?? (activeMomentTypeForUI == "SHARED_PURCHASE" ? sessionManager.activeMomentId : nil)
    }

    private var activeLivingMomentId: String? {
        switcherOptions.first(where: { $0.typeCode == "SHARED_LIVING" })?.momentId
            ?? (activeMomentTypeForUI == "SHARED_LIVING" ? sessionManager.activeMomentId : nil)
    }

    private var actionCenterMomentId: String? {
        switch activeMomentTypeForUI ?? sessionManager.activeMomentType {
        case "SHARED_PURCHASE": return activePurchaseMomentId
        case "SHARED_LIVING": return activeLivingMomentId
        default: return activeExperienceMomentId
        }
    }

    private var activityListMomentId: String? {
        switch activeMomentTypeForUI {
        case "SHARED_LIVING": return activeLivingMomentId
        case "SHARED_EXPERIENCE": return activeExperienceMomentId
        default: return nil
        }
    }

    private var activityListSource: GroupActivitySource {
        activeMomentTypeForUI == "SHARED_EXPERIENCE" ? .trip : .living
    }

    /// Moment id for TripSettlementView — trip APIs reused for purchase/living.
    private var settlementMomentId: String? {
        switch activeMomentTypeForUI ?? sessionManager.activeMomentType {
        case "SHARED_PURCHASE": return activePurchaseMomentId
        case "SHARED_LIVING": return activeLivingMomentId
        default: return activeExperienceMomentId
        }
    }

    private var screenOverlay: ScreenOverlay {
        if showCreateOverlay || createViewModel.setupMoment != nil { return .create }
        return .none
    }

    private var currentScreenName: String {
        AnalyticsScreens.resolveScreenName(
            appContext: appContext,
            tabSlug: AnalyticsScreens.visibleGroupTabSlug(
                selectedTab: selectedTab,
                previousTab: previousTab
            ),
            overlay: screenOverlay
        )
    }

    private var visibleTabSlug: String {
        AnalyticsScreens.visibleGroupTabSlug(selectedTab: selectedTab, previousTab: previousTab)
    }

    private var tabResolved: ResolvedScreen {
        ScreenResolver.resolve(context: .group, tab: visibleTabSlug, bootstrap: bootstrapStore.data)
    }

    private var shouldLoadSession: Bool {
        ScreenResolver.shouldLoadTabData(tabResolved)
            || ScreenResolver.isSetup(tabResolved)
            || ScreenResolver.isEmpty(tabResolved)
    }

    private func loadSessionIfNeeded() async {
        guard shouldLoadSession else { return }
        await groupSession.ensureGroupSession()
        createViewModel.syncDraftFromSession(groupSession.bootstrap)
    }

    private func openCreateOverlay() {
        let screen = AnalyticsScreens.resolveScreenName(
            appContext: appContext,
            tabSlug: AnalyticsScreens.visibleGroupTabSlug(
                selectedTab: selectedTab,
                previousTab: previousTab
            ),
            overlay: .none
        )
        MomentraAnalytics.logEvent(
            "create_moment_tap",
            params: ["app_context": appContext, "screen": screen]
        )
        showCreateOverlay = true
    }
    
    private func handleCreateTypeSelect(momentType: String) {
        MomentraAnalytics.logEvent(
            "create_moment_type_select",
            params: [
                "app_context": appContext,
                "moment_type": momentType,
                "phase": "setup",
            ]
        )
        // Dismiss create cover first so setup presentation isn't blocked by a stacked cover.
        showCreateOverlay = false
        Task {
            try? await Task.sleep(nanoseconds: 80_000_000)
            await createViewModel.openSetupForType(momentType)
        }
    }

    private func openQuickAdd(_ actionId: String? = nil) {
        quickAddActionId = actionId
        showActionCenter = true
    }

    private func handleQuickAdd() {
        let hasActiveMoment = !(switcherOptions.isEmpty) && (
            activeExperienceMomentId != nil || activePurchaseMomentId != nil || activeLivingMomentId != nil
        )
        guard hasActiveMoment else {
            if createViewModel.hasDraft, createViewModel.setupMoment == nil {
                resumeDraftSetup()
            } else {
                showFallbackSheet = true
            }
            return
        }

        if let momentType = activeMomentTypeForUI ?? sessionManager.activeMomentType,
           ["SHARED_EXPERIENCE", "SHARED_PURCHASE", "SHARED_LIVING"].contains(momentType) {
            openQuickAdd()
        }
    }

    private func resumeDraftSetup() {
        createViewModel.resumeDraft()
    }

    private func handleSetupActivated() {
        let typeCode = createViewModel.setupMoment?.momentTypeCode
            ?? createViewModel.draftMomentType
            ?? selectedMomentType
        createViewModel.clearDraftAfterActivate()
        showCreateOverlay = false
        MomentraToastCenter.shared.success(
            MomentraToastCopy.groupActivationSuccess(momentTypeCode: typeCode)
        )
        Task {
            await groupSession.softRefreshGroupSession()
            createViewModel.syncDraftFromSession(groupSession.bootstrap)
        }
    }

    @ViewBuilder
    private func setupResumeBanner() -> some View {
        // Pulse empty already surfaces draft resume CTA; avoid a duplicate banner there.
        if createViewModel.hasDraft, createViewModel.setupMoment == nil, selectedTab != .pulse {
            Button(action: resumeDraftSetup) {
                VStack(alignment: .leading, spacing: 6) {
                    Text("RESUME SETUP")
                        .font(GroupTypography.label(size: 11))
                        .tracking(1.5)
                        .foregroundStyle(GroupTheme.onSurfaceVariant)
                    Text("Continue \(createViewModel.draftTypeDisplayLabel) draft")
                        .font(GroupTypography.subhead(size: 16))
                        .foregroundStyle(GroupTheme.onSurface)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(16)
                .background(GroupTheme.surfaceContainer)
                .overlay(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .stroke(GroupTheme.primary.opacity(0.45), lineWidth: 1)
                )
                .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
            }
            .buttonStyle(.plain)
            .padding(.horizontal, GroupTheme.screenHorizontal)
            .padding(.top, 12)
        }
    }

    private let appContext = "group"

    private func syncSelectionFromBootstrap() {
        if let pinned = ShellActionRouter.peekPinnedGroupMomentId() {
            let id = pinned.uuidString
            let options = switcherOptions
            if let option = options.first(where: {
                $0.momentId.caseInsensitiveCompare(id) == .orderedSame
                    || $0.momentId == pinned.uuidString
            }) {
                selectedMomentType = option.typeCode
                GroupMomentSelectionHolder.store.apply(typeCode: option.typeCode, momentId: option.momentId)
                ShellActionRouter.clearPinnedGroupMomentId()
                MomentraAnalytics.logEvent("invite_destination_opened")
                return
            }
            // Keep pin until inventory includes the accepted moment.
            GroupMomentSelectionHolder.store.apply(
                typeCode: selectedMomentType.isEmpty ? "SHARED_EXPERIENCE" : selectedMomentType,
                momentId: id
            )
            return
        }
        let options = switcherOptions
        if options.isEmpty {
            selectedMomentType = ""
            GroupMomentSelectionHolder.store.clear()
            return
        }
        selectedMomentType = reconcileSelectedGroupMomentType(options: options, current: selectedMomentType)
        if let option = options.first(where: { $0.typeCode == selectedMomentType }) {
            GroupMomentSelectionHolder.store.apply(typeCode: option.typeCode, momentId: option.momentId)
        }
    }

    private func refreshAfterGroupManage(
        replacementMomentId: String? = nil,
        replacementMomentTypeCode: String? = nil,
        useExplicitSelection: Bool = false
    ) async {
        await groupSession.softRefreshGroupSession()
        createViewModel.syncDraftFromSession(groupSession.bootstrap)
        if useExplicitSelection, let replacementMomentId, !replacementMomentId.isEmpty {
            let type = replacementMomentTypeCode ?? selectedMomentType
            selectedMomentType = type
            GroupMomentSelectionHolder.store.apply(typeCode: type, momentId: replacementMomentId)
        } else {
            syncSelectionFromBootstrap()
        }
    }

    private func runGroupLifecycle(action: LifecycleAction) {
        guard let manageContext else { return }
        Task {
            do {
                let inventory = MomentLifecycleCoordinator.groupInventory(
                    moments: groupSession.bootstrap?.sessionMoments ?? []
                )
                let result = try await MomentLifecycleCoordinator.run(
                    contextType: .group,
                    momentId: manageContext.momentId,
                    momentTypeCode: manageContext.typeCode,
                    action: action,
                    inventory: inventory,
                    selectedMomentId: GroupMomentSelectionHolder.store.selectedMomentId,
                    previousStatus: manageContext.status
                )
                showManageSheet = false
                let excludeOnSuccess = action == .archive || action == .complete || action == .delete || action == .leave
                if excludeOnSuccess {
                    await refreshAfterGroupManage(
                        replacementMomentId: result.replacementMomentId,
                        replacementMomentTypeCode: result.replacementMomentTypeCode ?? manageContext.typeCode,
                        useExplicitSelection: result.replacementMomentId != nil
                    )
                } else {
                    await refreshAfterGroupManage()
                }
            } catch let err as MomentLifecycleError {
                MomentraToastCenter.shared.error(err.userMessage)
            } catch {
                MomentraToastCenter.shared.error(error.localizedDescription)
            }
        }
    }

    @ViewBuilder
    private func groupTabWithHeader<Content: View>(
        tabLabel: String,
        @ViewBuilder content: () -> Content
    ) -> some View {
        if switcherOptions.isEmpty || !ScreenResolver.shouldLoadTabData(tabResolved) {
            content()
        } else {
            VStack(spacing: 0) {
                GroupMomentHeader(
                    tabLabel: tabLabel,
                    options: switcherOptions,
                    selectedTypeCode: selectedMomentType,
                    onSelect: { option in
                        selectedMomentType = option.typeCode
                        GroupMomentSelectionHolder.store.apply(typeCode: option.typeCode, momentId: option.momentId)
                    },
                    onManageClick: manageContext != nil ? { showManageSheet = true } : nil,
                    onInviteMoment: { option in
                        selectedMomentType = option.typeCode
                        GroupMomentSelectionHolder.store.apply(typeCode: option.typeCode, momentId: option.momentId)
                        inviteMomentId = option.momentId
                        inviteMomentLabel = option.label
                    },
                    onDeleteMoment: { option in
                        switcherArchiveOption = option
                    },
                    onLeaveMoment: { option in
                        switcherLeaveOption = option
                    }
                )
                content()
            }
        }
    }

    private var activePlaceholder: some View {
        VStack(spacing: 12) {
            Text("Group moment is active")
                .font(GroupTypography.heading(size: 18))
                .foregroundStyle(GroupTheme.onSurface)
            Text("Active Trip, Shared Purchase, and Shared Living dashboards ship in a later phase. Your moment is saved and ready.")
                .font(GroupTypography.body())
                .foregroundStyle(GroupTheme.onSurfaceVariant)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 24)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(GroupTheme.background)
    }

    @ViewBuilder
    private func activeExperienceBody(for tab: GroupBottomTab) -> some View {
        switch tab {
        case .pulse:
            ExperiencePulse(
                momentId: activeExperienceMomentId,
                reloadKey: tripMomentsReloadKey,
                onQuickAdd: { openQuickAdd($0) },
                onViewAllActivity: { showLivingActivity = true },
                onEditActivity: { id, _ in editingLivingActivityId = id },
                onOpenSettlement: { showTripSettlement = true }
            )
        case .moments:
            ExperienceMoments(
                momentId: activeExperienceMomentId,
                reloadKey: tripMomentsReloadKey,
                onQuickAdd: { openQuickAdd() }
            )
        case .memory:
            ExperienceMemory(
                momentId: activeExperienceMomentId,
                reloadKey: tripMomentsReloadKey,
                onQuickAdd: { openQuickAdd() }
            )
        case .life:
            GroupLifeCommandCenter(onCreateMomentType: handleCreateTypeSelect)
        default:
            ExperiencePulse(
                momentId: activeExperienceMomentId,
                reloadKey: tripMomentsReloadKey,
                onQuickAdd: { openQuickAdd($0) },
                onViewAllActivity: { showLivingActivity = true },
                onEditActivity: { id, _ in editingLivingActivityId = id },
                onOpenSettlement: { showTripSettlement = true }
            )
        }
    }

    @ViewBuilder
    private func activePurchaseBody(for tab: GroupBottomTab) -> some View {
        switch tab {
        case .pulse:
            PurchasePulse(
                reloadKey: tripMomentsReloadKey,
                onQuickAdd: { openQuickAdd($0) },
                onOpenSettlement: { showTripSettlement = true }
            )
        case .moments:
            PurchaseMoments(momentId: activePurchaseMomentId, onQuickAdd: { openQuickAdd() })
        case .memory:
            PurchaseMemory(momentId: activePurchaseMomentId, onQuickAdd: { openQuickAdd() })
        case .life:
            GroupLifeCommandCenter(onCreateMomentType: handleCreateTypeSelect)
        default:
            PurchasePulse(
                reloadKey: tripMomentsReloadKey,
                onQuickAdd: { openQuickAdd($0) },
                onOpenSettlement: { showTripSettlement = true }
            )
        }
    }

    @ViewBuilder
    private func activeLivingBody(for tab: GroupBottomTab) -> some View {
        switch tab {
        case .pulse:
            LivingPulse(
                reloadToken: livingActivityReloadToken + tripMomentsReloadKey,
                onQuickAdd: { openQuickAdd($0) },
                onViewAllActivity: { showLivingActivity = true },
                onEditActivity: { id, _ in editingLivingActivityId = id },
                onOpenSettlement: { showTripSettlement = true }
            )
        case .moments:
            LivingMoments(momentId: activeLivingMomentId, onQuickAdd: { openQuickAdd() })
        case .memory:
            LivingMemory(momentId: activeLivingMomentId, onQuickAdd: { openQuickAdd() })
        case .life:
            GroupLifeCommandCenter(onCreateMomentType: handleCreateTypeSelect)
        default:
            LivingPulse(
                reloadToken: livingActivityReloadToken + tripMomentsReloadKey,
                onQuickAdd: { openQuickAdd($0) },
                onViewAllActivity: { showLivingActivity = true },
                onEditActivity: { id, _ in editingLivingActivityId = id },
                onOpenSettlement: { showTripSettlement = true }
            )
        }
    }

    @ViewBuilder
    private func tabBody<Empty: View>(
        for tab: GroupBottomTab,
        @ViewBuilder empty: () -> Empty
    ) -> some View {
        // Empty switcher inventory wins over stale ACTIVE bootstrap (archive-all) — web parity.
        // Pin content to the owning Tab so Pulse/Moments survive tab switches.
        if !switcherOptions.isEmpty {
            if tab == .life {
                groupTabWithHeader(tabLabel: tabLabel(for: tab)) {
                    GroupLifeCommandCenter(onCreateMomentType: handleCreateTypeSelect)
                }
            } else if activeMomentTypeForUI == "SHARED_EXPERIENCE" {
                groupTabWithHeader(tabLabel: tabLabel(for: tab)) {
                    activeExperienceBody(for: tab)
                }
            } else if activeMomentTypeForUI == "SHARED_PURCHASE" {
                groupTabWithHeader(tabLabel: tabLabel(for: tab)) {
                    activePurchaseBody(for: tab)
                }
            } else if activeMomentTypeForUI == "SHARED_LIVING" {
                groupTabWithHeader(tabLabel: tabLabel(for: tab)) {
                    activeLivingBody(for: tab)
                }
            } else {
                activePlaceholder
            }
        } else {
            VStack(spacing: 0) {
                setupResumeBanner()
                empty()
            }
        }
    }

    private func tabLabel(for tab: GroupBottomTab) -> String {
        switch tab {
        case .pulse: return "Pulse"
        case .moments: return "Moments"
        case .memory: return "Memory"
        case .life: return "Life"
        default: return "Pulse"
        }
    }

    @ViewBuilder
    private var setupCover: some View {
        if let setupMoment = createViewModel.setupMoment {
            let type = setupMoment.momentTypeCode ?? "SHARED_EXPERIENCE"
            Group {
                switch type {
                case "SHARED_PURCHASE":
                    GroupPurchaseSetupView(
                        setupViewModel: createViewModel.setupViewModel,
                        momentId: setupMoment.momentId,
                        onClose: { createViewModel.dismissSetup() },
                        onActivated: handleSetupActivated
                    )
                case "SHARED_LIVING":
                    GroupLivingSetupView(
                        setupViewModel: createViewModel.setupViewModel,
                        momentId: setupMoment.momentId,
                        onClose: { createViewModel.dismissSetup() },
                        onActivated: handleSetupActivated
                    )
                default:
                    GroupTripSetupView(
                        setupViewModel: createViewModel.setupViewModel,
                        momentId: setupMoment.momentId,
                        onClose: { createViewModel.dismissSetup() },
                        onActivated: handleSetupActivated
                    )
                }
            }
        }
    }

    var body: some View {
        tabViewWithLifecycle
            .momentraToastHost(context: .group)
            .sheet(isPresented: $showActionCenter) {
                actionCenterSheet
            }
            .fullScreenCover(isPresented: $showLivingActivity) {
                if let momentId = activityListMomentId {
                    LivingActivityScreen(
                        momentId: momentId,
                        reloadToken: livingActivityReloadToken,
                        source: activityListSource,
                        onBack: { showLivingActivity = false },
                        onEditActivity: { id, _ in editingLivingActivityId = id }
                    )
                }
            }
            .fullScreenCover(isPresented: $showTripSettlement) {
                TripSettlementView(
                    momentId: settlementMomentId,
                    onBack: {
                        showTripSettlement = false
                        tripMomentsReloadKey += 1
                    }
                )
            }
            .sheet(isPresented: Binding(
                get: { editingLivingActivityId != nil },
                set: { if !$0 { editingLivingActivityId = nil } }
            )) {
                if let momentId = activityListMomentId, let eventId = editingLivingActivityId {
                    LivingActivityEditSheet(
                        momentId: momentId,
                        eventId: eventId,
                        source: activityListSource,
                        onDismiss: { editingLivingActivityId = nil },
                        onSaved: {
                            livingActivityReloadToken += 1
                            tripMomentsReloadKey += 1
                        }
                    )
                    .presentationDetents([.medium, .large])
                }
            }
            .onChange(of: showActionCenter) { wasShown, isShown in
                if wasShown && !isShown {
                    quickAddActionId = nil
                    tripMomentsReloadKey += 1
                }
            }
            .onChange(of: activeMomentTypeForUI) { _, _ in
                showActionCenter = false
            }

            .sheet(isPresented: $showManageSheet) {
                manageSheet
            }
            .sheet(isPresented: Binding(
                get: { inviteMomentId != nil },
                set: { if !$0 { inviteMomentId = nil; inviteMomentLabel = nil } }
            )) {
                if let inviteMomentId {
                    MomentInviteSheet(
                        momentId: inviteMomentId,
                        momentLabel: inviteMomentLabel,
                        variant: .group,
                        onDismiss: {
                            self.inviteMomentId = nil
                            inviteMomentLabel = nil
                        }
                    )
                }
            }
            .alert("Archive moment", isPresented: Binding(
                get: { switcherArchiveOption != nil },
                set: { if !$0 { switcherArchiveOption = nil } }
            )) {
                Button("Cancel", role: .cancel) { switcherArchiveOption = nil }
                Button("Archive", role: .destructive) {
                    guard let option = switcherArchiveOption else { return }
                    switcherArchiveOption = nil
                    selectedMomentType = option.typeCode
                    GroupMomentSelectionHolder.store.apply(typeCode: option.typeCode, momentId: option.momentId)
                    Task {
                        do {
                            let inventory = MomentLifecycleCoordinator.groupInventory(
                                moments: groupSession.bootstrap?.sessionMoments ?? []
                            )
                            let result = try await MomentLifecycleCoordinator.run(
                                contextType: .group,
                                momentId: option.momentId,
                                momentTypeCode: option.typeCode,
                                action: .archive,
                                inventory: inventory,
                                selectedMomentId: option.momentId,
                                previousStatus: "ACTIVE"
                            )
                            await refreshAfterGroupManage(
                                replacementMomentId: result.replacementMomentId,
                                replacementMomentTypeCode: result.replacementMomentTypeCode ?? option.typeCode,
                                useExplicitSelection: result.replacementMomentId != nil
                            )
                        } catch let err as MomentLifecycleError {
                            MomentraToastCenter.shared.error(err.userMessage)
                        } catch {
                            MomentraToastCenter.shared.error(error.localizedDescription)
                        }
                    }
                }
            } message: {
                Text("Archive \(switcherArchiveOption?.label ?? "this moment")? This removes it from your active list.")
            }
            .alert("Leave moment", isPresented: Binding(
                get: { switcherLeaveOption != nil },
                set: { if !$0 { switcherLeaveOption = nil } }
            )) {
                Button("Cancel", role: .cancel) { switcherLeaveOption = nil }
                Button("Leave", role: .destructive) {
                    guard let option = switcherLeaveOption else { return }
                    switcherLeaveOption = nil
                    selectedMomentType = option.typeCode
                    GroupMomentSelectionHolder.store.apply(typeCode: option.typeCode, momentId: option.momentId)
                    Task {
                        do {
                            let inventory = MomentLifecycleCoordinator.groupInventory(
                                moments: groupSession.bootstrap?.sessionMoments ?? []
                            )
                            let result = try await MomentLifecycleCoordinator.run(
                                contextType: .group,
                                momentId: option.momentId,
                                momentTypeCode: option.typeCode,
                                action: .leave,
                                inventory: inventory,
                                selectedMomentId: option.momentId,
                                previousStatus: "ACTIVE"
                            )
                            await refreshAfterGroupManage(
                                replacementMomentId: result.replacementMomentId,
                                replacementMomentTypeCode: result.replacementMomentTypeCode ?? option.typeCode,
                                useExplicitSelection: result.replacementMomentId != nil
                            )
                        } catch let err as MomentLifecycleError {
                            MomentraToastCenter.shared.error(err.userMessage)
                        } catch {
                            MomentraToastCenter.shared.error(error.localizedDescription)
                        }
                    }
                }
            } message: {
                Text("Leave \(switcherLeaveOption?.label ?? "this moment")? You will lose access. The moment stays for others.")
            }
            .sheet(isPresented: $showFallbackSheet) {
                GroupQuickAddFallbackSheet(onDismiss: { showFallbackSheet = false })
            }
            .fullScreenCover(isPresented: $showCreateOverlay) {
                createOverlay
            }
            .fullScreenCover(isPresented: setupCoverBinding) {
                setupCover
            }
    }

    private var tabViewWithLifecycle: some View {
        Group {
            if groupSession.isLoading && groupSession.bootstrap == nil {
                MomentraLoadingIndicator(label: "Loading moments…")
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                mainTabView
            }
        }
            .contextTabBarAppearance()
            .onAppear {
                ShellActionRouter.groupNewMomentHandler = { showCreateOverlay = true }
                ShellActionRouter.groupSelectLifeHandler = { selectedTab = .life }
                GroupMomentAccessGate.handler = { momentId in
                    await groupSession.handleMomentInaccessible(momentId)
                    tripMomentStream.stop()
                }
                ShellActionRouter.registerGroupOpenMomentHandler { momentId, momentType in
                    Task {
                        MomentraAnalytics.logEvent("invite_group_selected")
                        let id = momentId.uuidString
                        let inInventory = await groupSession.refreshAndSelectMoment(
                            momentId: id,
                            momentType: momentType
                        )
                        createViewModel.syncDraftFromSession(groupSession.bootstrap)
                        let options = resolveGroupMomentSwitcherOptions(bootstrap: groupSession.bootstrap)
                        if let option = options.first(where: {
                            $0.momentId.caseInsensitiveCompare(id) == .orderedSame
                                || $0.momentId == momentId.uuidString
                        }) {
                            selectedMomentType = option.typeCode
                            GroupMomentSelectionHolder.store.apply(
                                typeCode: option.typeCode,
                                momentId: option.momentId
                            )
                            ShellActionRouter.clearPinnedGroupMomentId()
                            MomentraAnalytics.logEvent("invite_destination_opened")
                        } else {
                            let type = momentType ?? selectedMomentType
                            selectedMomentType = type.isEmpty ? "SHARED_EXPERIENCE" : type
                            GroupMomentSelectionHolder.store.apply(
                                typeCode: selectedMomentType,
                                momentId: id
                            )
                            if inInventory {
                                ShellActionRouter.clearPinnedGroupMomentId()
                            }
                        }
                        selectedTab = .pulse
                    }
                }
                startTripMomentStreamIfNeeded()
            }
            .onChange(of: activeExperienceMomentId) { _, _ in
                startTripMomentStreamIfNeeded()
            }
            .onChange(of: activePurchaseMomentId) { _, _ in
                startTripMomentStreamIfNeeded()
            }
            .onChange(of: activeLivingMomentId) { _, _ in
                startTripMomentStreamIfNeeded()
            }
            .onDisappear {
                tripMomentStream.stop()
            }
            .task(id: shouldLoadSession) {
                await loadSessionIfNeeded()
            }
            .onChange(of: groupSession.bootstrap) { _, bootstrap in
                createViewModel.syncDraftFromSession(bootstrap)
                syncSelectionFromBootstrap()
            }
            .onChange(of: switcherOptions.map(\.typeCode)) { _, _ in
                syncSelectionFromBootstrap()
            }
            .onChange(of: scenePhase) { _, phase in
                // Cross-client archive sync: refresh inventory when returning to foreground.
                guard phase == .active else { return }
                Task {
                    await groupSession.softRefreshGroupSession()
                    createViewModel.syncDraftFromSession(groupSession.bootstrap)
                    syncSelectionFromBootstrap()
                }
            }
            .onChange(of: selectedTab) { _, newTab in
                handleSelectedTabChange(newTab)
            }
            .onDisappear {
                ShellActionRouter.groupNewMomentHandler = nil
                ShellActionRouter.groupSelectLifeHandler = nil
                ShellActionRouter.unregisterGroupOpenMomentHandler()
                GroupMomentAccessGate.handler = nil
                tripMomentStream.stop()
            }
            .onChange(of: currentScreenName) { _, screenName in
                MomentraAnalytics.logScreen(screenName, appContext: appContext)
            }
            .onAppear {
                MomentraAnalytics.logScreen(currentScreenName, appContext: appContext)
            }
    }

    private func handleSelectedTabChange(_ newTab: GroupBottomTab) {
        if newTab == .add {
            handleQuickAdd()
            selectedTab = previousTab
        } else {
            MomentraAnalytics.logEvent(
                "tab_select",
                params: ["app_context": appContext, "tab": AnalyticsScreens.groupTabSlug(newTab)]
            )
            previousTab = newTab
        }
    }

    private var setupCoverBinding: Binding<Bool> {
        Binding(
            get: { createViewModel.setupMoment != nil },
            set: { if !$0 { createViewModel.dismissSetup() } }
        )
    }

    @ViewBuilder
    private var mainTabView: some View {
        TabView(selection: $selectedTab) {
            Tab(GroupBottomTab.pulse.label, systemImage: GroupBottomTab.pulse.systemImage, value: .pulse) {
                pulseTabContent
            }
            Tab(GroupBottomTab.moments.label, systemImage: GroupBottomTab.moments.systemImage, value: .moments) {
                momentsTabContent
            }
            Tab("Add", systemImage: GroupBottomTab.add.systemImage, value: .add) {
                Color.clear
            }
            Tab(GroupBottomTab.life.label, systemImage: GroupBottomTab.life.systemImage, value: .life) {
                lifeTabContent
            }
            Tab(GroupBottomTab.memory.label, systemImage: GroupBottomTab.memory.systemImage, value: .memory) {
                memoryTabContent
            }
        }
    }

    private var pulseContinueSetup: (() -> Void)? {
        createViewModel.hasDraft ? { resumeDraftSetup() } : nil
    }

    @ViewBuilder
    private var pulseTabContent: some View {
        tabBody(for: .pulse) {
            GroupPulseEmptyView(
                onCreateMoment: openCreateOverlay,
                resumeDraft: createViewModel.hasDraft,
                onContinueSetup: pulseContinueSetup
            )
        }
    }

    @ViewBuilder
    private var momentsTabContent: some View {
        tabBody(for: .moments) {
            GroupMomentsEmptyView(onCreateMoment: openCreateOverlay)
        }
    }

    @ViewBuilder
    private var lifeTabContent: some View {
        tabBody(for: .life) {
            GroupLifeEmptyView(onCreateMoment: openCreateOverlay)
        }
    }

    @ViewBuilder
    private var memoryTabContent: some View {
        tabBody(for: .memory) {
            GroupMemoryEmptyView(onCreateMoment: openCreateOverlay)
        }
    }

    @ViewBuilder
    private var actionCenterSheet: some View {
        if let momentId = actionCenterMomentId,
           let momentType = activeMomentTypeForUI ?? sessionManager.activeMomentType {
            GroupMomentQuickAddRouter(
                isPresented: $showActionCenter,
                momentId: momentId,
                momentTypeCode: momentType,
                onSuccess: {
                    tripMomentsReloadKey += 1
                    MomentraToastCenter.shared.success("Quick Add saved")
                    Task { await refreshAfterGroupManage() }
                },
                momentName: manageContext?.momentName.nilIfBlank
                    ?? switcherOptions.first(where: { $0.momentId == momentId })?.label,
                stageLabel: nil,
                initialActionId: quickAddActionId
            )
        }
    }

    @ViewBuilder
    private var manageSheet: some View {
        if let manageContext {
            MomentManageSheet(
                context: manageContext.asSharedContext,
                theme: .group,
                onEditSetup: {
                    Task {
                        await createViewModel.openSetupForActiveMoment(
                            momentId: manageContext.momentId,
                            typeCode: manageContext.typeCode
                        )
                    }
                },
                onEditName: { name in
                    Task {
                        try? await APIClient.shared.patchGroupMoment(
                            momentId: manageContext.momentId,
                            body: GroupMomentUpdateRequest(momentName: name, status: nil)
                        )
                        await refreshAfterGroupManage()
                    }
                },
                onPause: { runGroupLifecycle(action: .pause) },
                onResume: { runGroupLifecycle(action: .resume) },
                onComplete: { runGroupLifecycle(action: .complete) },
                onArchive: { runGroupLifecycle(action: .archive) },
                onDeletePermanently: { runGroupLifecycle(action: .delete) },
                isOwner: manageContext.isOwned,
                onLeave: { runGroupLifecycle(action: .leave) }
            )
        }
    }

    @ViewBuilder
    private var createOverlay: some View {
        GroupCreateEmptyView(
            onSelectType: handleCreateTypeSelect,
            onCreateMoment: {},
            onClose: { showCreateOverlay = false }
        )
        .overlay(alignment: .bottom) {
            if let error = createViewModel.createError {
                Text(error)
                    .font(GroupTypography.caption(size: 13))
                    .foregroundStyle(GroupTheme.error)
                    .padding()
            } else if createViewModel.creatingTypeCode != nil {
                ProgressView()
                    .tint(GroupTheme.primary)
                    .padding()
            }
        }
    }

    private func startTripMomentStreamIfNeeded() {
        let mid = activeExperienceMomentId
            ?? activePurchaseMomentId
            ?? activeLivingMomentId
        guard let mid, !mid.isEmpty else {
            tripMomentStream.stop()
            return
        }
        if GroupMomentAccessGate.wasCleared(mid) {
            tripMomentStream.stop()
            return
        }
        tripMomentStream.start(
            momentId: mid,
            onInvalidate: {
                tripMomentsReloadKey += 1
            },
            onTerminalFailure: { momentId, _ in
                Task { await GroupMomentAccessGate.onInaccessible(momentId) }
            }
        )
    }
}

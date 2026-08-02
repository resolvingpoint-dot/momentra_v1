import Foundation
import Observation

@MainActor
@Observable
final class PersonalSessionStore {
    private var pulseFetcher: KeyedCachedFetcher<PersonalPulseResponse>!
    private var momentsFetcher: KeyedCachedFetcher<PersonalMomentsHomeResponse>!
    private var memoryFetcher: KeyedCachedFetcher<PersonalMemoryResponse>!
    private var lifeFetcher: CachedFetcher<PersonalLifeResponse>!
    private var templateMomentsFetcher: KeyedCachedFetcher<TemplateMomentsResponse>!
    private var templateLifeFetcher: KeyedCachedFetcher<TemplateLifeResponse>!
    private var templateMemoryFetcher: KeyedCachedFetcher<TemplateMemoryResponse>!
    private var bootstrapFetcher: KeyedCachedFetcher<APIClient.PersonalSessionBootstrapResponse>!
    private var masterExpenseOptionsFetcher: CachedFetcher<PersonalMasterExpenseOptionsResponse>!
    private let defaults = UserDefaults.standard
    private let jsonEncoder = JSONEncoder()
    private let jsonDecoder = JSONDecoder()
    private(set) var hasPendingQuickAddDraft = QuickAddDraftStore.hasPending
    private var isRetryingDraft = false

    init() {
        pulseFetcher = KeyedCachedFetcher(key: { PersonalMomentSelectionHolder.store.selectedMomentTypeCode }) { typeCode, force in
            try await APIClient.shared.fetchPersonalPulse(forceRefresh: force, momentTypeCode: typeCode)
        }
        momentsFetcher = KeyedCachedFetcher(key: { PersonalMomentSelectionHolder.store.selectedMomentTypeCode }) { typeCode, force in
            try await APIClient.shared.fetchPersonalMomentsHome(forceRefresh: force, momentTypeCode: typeCode)
        }
        memoryFetcher = KeyedCachedFetcher(key: { PersonalMomentSelectionHolder.store.selectedMomentTypeCode }) { typeCode, force in
            try await APIClient.shared.fetchPersonalMemory(forceRefresh: force, momentTypeCode: typeCode)
        }
        lifeFetcher = CachedFetcher { force in
            try await APIClient.shared.fetchPersonalLife(forceRefresh: force)
        }
        templateMomentsFetcher = KeyedCachedFetcher(key: { PersonalMomentSelectionHolder.store.selectedMomentTypeCode }) { typeCode, _ in
            try await APIClient.shared.fetchTemplateMoments(momentType: typeCode ?? "LIFE_OPERATIONS")
        }
        templateLifeFetcher = KeyedCachedFetcher(key: { PersonalMomentSelectionHolder.store.selectedMomentTypeCode }) { typeCode, _ in
            try await APIClient.shared.fetchTemplateLife(momentType: typeCode ?? "LIFE_OPERATIONS")
        }
        templateMemoryFetcher = KeyedCachedFetcher(key: { PersonalMomentSelectionHolder.store.selectedMomentTypeCode }) { typeCode, _ in
            try await APIClient.shared.fetchTemplateMemory(momentType: typeCode ?? "LIFE_OPERATIONS")
        }
        bootstrapFetcher = KeyedCachedFetcher(key: { PersonalMomentSelectionHolder.store.selectedMomentTypeCode }) { typeCode, force in
            let bootstrap = try await APIClient.shared.fetchPersonalSessionBootstrap(
                forceRefresh: force,
                momentTypeCode: typeCode
            )
            self.pulseFetcher.seed(bootstrap.pulse)
            self.momentsFetcher.seed(bootstrap.momentsHome)
            return bootstrap
        }
        masterExpenseOptionsFetcher = CachedFetcher { _ in
            try await APIClient.shared.fetchMasterExpenseOptions()
        }

        NetworkMonitor.shared.onConnectivityRestored { [weak self] in
            Task { @MainActor in
                await self?.retryPendingQuickAddDraft()
            }
        }
    }

    func setSelectedMoment(typeCode: String?, momentId: String?) {
        if let typeCode {
            PersonalMomentSelectionHolder.store.apply(typeCode: typeCode, momentId: momentId)
        } else {
            PersonalMomentSelectionHolder.store.selectedMomentTypeCode = nil
            PersonalMomentSelectionHolder.store.selectedMomentId = nil
        }
    }

    func peekPulse() -> PersonalPulseResponse? { pulseFetcher.peek() }

    func isPulseFresh() -> Bool { pulseFetcher.isFresh() }

    func peekMomentsHome() -> PersonalMomentsHomeResponse? { momentsFetcher.peek() }

    func isMomentsHomeFresh() -> Bool { momentsFetcher.isFresh() }

    func peekMemory() -> PersonalMemoryResponse? { memoryFetcher.peek() }

    func isMemoryFresh() -> Bool { memoryFetcher.isFresh() }

    func peekLife() -> PersonalLifeResponse? { lifeFetcher.peek() }

    func isLifeFresh() -> Bool { lifeFetcher.isFresh() }

    func warmUpFromDisk() {
        if let pulse: PersonalPulseResponse = loadDisk(key: pulseDiskKey()) {
            pulseFetcher.seed(pulse)
        }
        if let moments: PersonalMomentsHomeResponse = loadDisk(key: momentsDiskKey()) {
            momentsFetcher.seed(moments)
        }
        if let memory: PersonalMemoryResponse = loadDisk(key: memoryDiskKey()) {
            memoryFetcher.seed(memory)
        }
        if let life: PersonalLifeResponse = loadDisk(key: Self.lifeDiskKey) {
            lifeFetcher.seed(life)
        }
        if let templateMoments: TemplateMomentsResponse = loadDisk(key: templateMomentsDiskKey()) {
            templateMomentsFetcher.seed(templateMoments)
        }
        if let templateMemory: TemplateMemoryResponse = loadDisk(key: templateMemoryDiskKey()) {
            templateMemoryFetcher.seed(templateMemory)
        }
        refreshPendingDraftState()
    }

    func peekTemplateMoments() -> TemplateMomentsResponse? { templateMomentsFetcher.peek() }

    func isTemplateMomentsFresh() -> Bool { templateMomentsFetcher.isFresh() }

    func peekTemplateLife() -> TemplateLifeResponse? { templateLifeFetcher.peek() }

    func isTemplateLifeFresh() -> Bool { templateLifeFetcher.isFresh() }

    func peekTemplateMemory() -> TemplateMemoryResponse? { templateMemoryFetcher.peek() }

    func isTemplateMemoryFresh() -> Bool { templateMemoryFetcher.isFresh() }

    func warmStart(force: Bool = false) async {
        if !force, pulseFetcher.isFresh(), momentsFetcher.isFresh() { return }
        guard let bootstrap = try? await bootstrapFetcher.get(force: force) else { return }
        persistDisk(bootstrap.pulse, key: pulseDiskKey())
        persistDisk(bootstrap.momentsHome, key: momentsDiskKey())
    }

    func pulse(force: Bool = false) async throws -> PersonalPulseResponse {
        let data = try await pulseFetcher.get(force: force)
        persistDisk(data, key: pulseDiskKey())
        return data
    }

    func momentsHome(force: Bool = false) async throws -> PersonalMomentsHomeResponse {
        let data = try await momentsFetcher.get(force: force)
        persistDisk(data, key: momentsDiskKey())
        return data
    }

    func memory(force: Bool = false) async throws -> PersonalMemoryResponse {
        let data = try await memoryFetcher.get(force: force)
        persistDisk(data, key: memoryDiskKey())
        return data
    }

    func life(force: Bool = false) async throws -> PersonalLifeResponse {
        let data = try await lifeFetcher.get(force: force)
        persistDisk(data, key: Self.lifeDiskKey)
        return data
    }

    func invalidatePulse() { pulseFetcher.invalidateAll() }

    func invalidateMomentsHome() { momentsFetcher.invalidateAll() }

    func invalidateMemory() { memoryFetcher.invalidateAll() }

    func invalidateLife() { lifeFetcher.invalidate() }

    func invalidateAfterSetup() {
        invalidatePulse()
        invalidateMomentsHome()
        invalidateMemory()
        invalidateLife()
        invalidateTemplateProjections()
        bootstrapFetcher.invalidateActive()
    }

    func invalidateAfterQuickAdd() {
        invalidatePulse()
        invalidateMomentsHome()
        invalidateMemory()
        invalidateLife()
        invalidateTemplateProjections()
    }

    /// Narrow invalidation for Build Momentum — skip life + bootstrap.
    func invalidateAfterFutureBuildingQuickAdd() {
        invalidatePulse()
        invalidateMomentsHome()
        invalidateMemory()
        invalidateTemplateProjections()
    }

    /// Narrow invalidation for Capture Lifestyle — skip life + bootstrap.
    func invalidateAfterLifestyleQuickAdd() {
        invalidatePulse()
        invalidateMomentsHome()
        invalidateMemory()
        invalidateTemplateProjections()
    }

    /// Narrow invalidation for Capture Relationships — skip life + bootstrap.
    func invalidateAfterRelationshipsQuickAdd() {
        invalidatePulse()
        invalidateMomentsHome()
        invalidateMemory()
        invalidateTemplateProjections()
    }

    func invalidateAfterMasterExpense(includeRelationships: Bool) {
        invalidatePulse()
        invalidateMomentsHome()
        invalidateMemory()
        invalidateLife()
        invalidateTemplateProjections()
        bootstrapFetcher.invalidateActive()
    }

    func invalidateTemplateProjections() {
        templateMomentsFetcher.invalidateActive()
        templateLifeFetcher.invalidateActive()
        templateMemoryFetcher.invalidateActive()
    }

    func templateMoments(force: Bool = false) async throws -> TemplateMomentsResponse {
        let data = try await templateMomentsFetcher.get(force: force)
        persistDisk(data, key: templateMomentsDiskKey())
        return data
    }

    func templateLife(force: Bool = false) async throws -> TemplateLifeResponse {
        try await templateLifeFetcher.get(force: force)
    }

    func templateMemory(force: Bool = false) async throws -> TemplateMemoryResponse {
        let data = try await templateMemoryFetcher.get(force: force)
        persistDisk(data, key: templateMemoryDiskKey())
        return data
    }

    func archiveTemplateMoment(momentType: String, momentId: String) async throws -> PersonalMomentResponse {
        try await APIClient.shared.archiveTemplateMoment(momentType: momentType, momentId: momentId)
    }

    func completeTemplateMoment(momentType: String, momentId: String) async throws -> PersonalMomentResponse {
        try await APIClient.shared.completeTemplateMoment(momentType: momentType, momentId: momentId)
    }

    func getMasterExpenseOptions(force: Bool = false) async throws -> PersonalMasterExpenseOptionsResponse {
        try await masterExpenseOptionsFetcher.get(force: force)
    }

    func peekMasterExpenseOptions() -> PersonalMasterExpenseOptionsResponse? {
        masterExpenseOptionsFetcher.peek()
    }

    func invalidateMasterExpenseOptions() {
        masterExpenseOptionsFetcher.invalidate()
    }

    func createMasterExpense(_ body: PersonalMasterExpenseRequest) async throws -> PersonalMasterExpenseResponse {
        try await APIClient.shared.createMasterExpense(body)
    }

    func getQuickAddOptions(momentId: String? = nil) async throws -> PersonalQuickAddOptionsResponse {
        try await APIClient.shared.fetchPersonalQuickAddOptions(momentId: momentId)
    }

    func submitQuickAdd(
        _ request: PersonalQuickAddRequest,
        tabKey: String = "default",
        clientRequestId: String? = nil
    ) async throws {
        let requestId = clientRequestId ?? UUID().uuidString.lowercased()
        let body = requestWithClientRequestId(request, clientRequestId: requestId)

        do {
            _ = try await APIClient.shared.createPersonalQuickAdd(body)
            QuickAddDraftStore.clear()
            refreshPendingDraftState()
            if request.futureBuilding != nil {
                invalidateAfterFutureBuildingQuickAdd()
            } else if request.lifestyle != nil {
                invalidateAfterLifestyleQuickAdd()
            } else if request.emotionalSecurity != nil {
                invalidateAfterRelationshipsQuickAdd()
            } else {
                invalidateAfterQuickAdd()
            }
        } catch {
            let apiError = APIClient.mapTransportError(error)
            if apiError.isIdempotentSuccess {
                QuickAddDraftStore.clear()
                refreshPendingDraftState()
                if request.futureBuilding != nil {
                    invalidateAfterFutureBuildingQuickAdd()
                } else if request.lifestyle != nil {
                    invalidateAfterLifestyleQuickAdd()
                } else if request.emotionalSecurity != nil {
                    invalidateAfterRelationshipsQuickAdd()
                } else {
                    invalidateAfterQuickAdd()
                }
                return
            }
            if apiError.isRetryable || !NetworkMonitor.shared.isConnected {
                QuickAddDraftStore.save(
                    clientRequestId: requestId,
                    momentId: request.momentId,
                    tabKey: tabKey,
                    request: body
                )
                refreshPendingDraftState()
            }
            throw apiError
        }
    }

    func retryPendingQuickAddDraft() async -> Bool {
        guard !isRetryingDraft, let draft = QuickAddDraftStore.load() else { return false }
        guard NetworkMonitor.shared.isConnected else { return false }

        isRetryingDraft = true
        defer { isRetryingDraft = false }

        do {
            try await submitQuickAdd(
                draft.request,
                tabKey: draft.tabKey,
                clientRequestId: draft.clientRequestId
            )
            return true
        } catch {
            return false
        }
    }

    func discardPendingQuickAddDraft() {
        QuickAddDraftStore.clear()
        refreshPendingDraftState()
    }

    func listAccounts(includeArchived: Bool = false) async throws -> [PersonalAccountResponse] {
        try await APIClient.shared.fetchPersonalAccounts(includeArchived: includeArchived)
    }

    func getAccount(accountId: String) async throws -> PersonalAccountResponse {
        try await APIClient.shared.fetchPersonalAccount(accountId: accountId)
    }

    func patchAccount(accountId: String, body: PersonalAccountPatchRequest) async throws -> PersonalAccountResponse {
        try await APIClient.shared.patchPersonalAccount(accountId: accountId, body: body)
    }

    func archiveAccount(accountId: String) async throws -> PersonalAccountResponse {
        try await APIClient.shared.archivePersonalAccount(accountId: accountId)
    }

    func deleteAccount(accountId: String) async throws {
        try await APIClient.shared.deletePersonalAccount(accountId: accountId)
    }

    private func requestWithClientRequestId(
        _ request: PersonalQuickAddRequest,
        clientRequestId: String
    ) -> PersonalQuickAddRequest {
        PersonalQuickAddRequest(
            momentId: request.momentId,
            eventType: request.eventType,
            eventTitle: request.eventTitle,
            eventSummary: request.eventSummary,
            clientRequestId: clientRequestId,
            recovery: request.recovery,
            reflection: request.reflection,
            rhythm: request.rhythm,
            expense: request.expense,
            commitment: request.commitment,
            futureBuilding: request.futureBuilding,
            lifestyle: request.lifestyle,
            emotionalSecurity: request.emotionalSecurity
        )
    }

    private func refreshPendingDraftState() {
        hasPendingQuickAddDraft = QuickAddDraftStore.hasPending
    }

    private static let lifeDiskKey = "personal_life:v1"

    private func diskTypeSlug() -> String {
        PersonalMomentSelectionHolder.store.selectedMomentTypeCode?.lowercased() ?? "life_operations"
    }

    private func pulseDiskKey() -> String { "personal_pulse:\(diskTypeSlug())" }

    private func momentsDiskKey() -> String { "personal_moments:\(diskTypeSlug())" }

    private func memoryDiskKey() -> String { "personal_memory:\(diskTypeSlug()):v2" }

    private func templateMomentsDiskKey() -> String { "personal_template_moments:\(diskTypeSlug())" }

    private func templateMemoryDiskKey() -> String { "personal_template_memory:\(diskTypeSlug())" }

    private func persistDisk<T: Encodable>(_ value: T, key: String) {
        guard let data = try? jsonEncoder.encode(value) else { return }
        defaults.set(data, forKey: key)
    }

    private func loadDisk<T: Decodable>(key: String) -> T? {
        guard let data = defaults.data(forKey: key) else { return nil }
        return try? jsonDecoder.decode(T.self, from: data)
    }

    // MARK: - Authoritative session snapshot

    private(set) var session: APIClient.PersonalSessionBootstrapResponse?
    private(set) var sessionLoading = false
    private(set) var sessionError: String?
    private(set) var generation: Int = 0
    private var sessionLastLoadedAt: Date?
    private var sessionLoadTask: Task<Void, Never>?

    @discardableResult
    func bumpGeneration() -> Int {
        generation += 1
        return generation
    }

    func setPersonalMomentType(_ typeCode: String) {
        bumpGeneration()
        PersonalMomentSelectionHolder.store.selectedMomentTypeCode = typeCode
    }

    private func applySession(_ session: APIClient.PersonalSessionBootstrapResponse) {
        self.session = session
        pulseFetcher.seed(session.pulse)
        // Inventory/bootstrap moments home is card-only (no domain details). Keep cards for
        // switcher, but mark stale so Moments tab fetches full /moments/home + templates.
        momentsFetcher.seedStale(session.momentsHome)
        persistDisk(session.pulse, key: pulseDiskKey())
        persistDisk(session.momentsHome, key: momentsDiskKey())
        sessionLastLoadedAt = Date()
        sessionError = nil
    }

    /// Shell entry — prefer thin session + inventory; fall back to bootstrap.
    func ensurePersonalSession(force: Bool = false) async {
        if !force,
           session != nil,
           sessionError == nil,
           let at = sessionLastLoadedAt,
           CacheTTL.isSessionFresh(fetchedAt: at) {
            return
        }
        if sessionLoadTask != nil, !force { return }

        sessionLoadTask = Task {
            defer { sessionLoadTask = nil }
            sessionLoading = session == nil
            sessionError = nil
            let code = PersonalMomentSelectionHolder.store.selectedMomentTypeCode
            do {
                let fresh: APIClient.PersonalSessionBootstrapResponse
                do {
                    _ = try? await APIClient.shared.fetchPersonalSession()
                    let inventory = try await APIClient.shared.fetchPersonalInventory(momentTypeCode: code)
                    fresh = APIClient.PersonalSessionBootstrapResponse(
                        pulse: inventory.pulse,
                        momentsHome: inventory.momentsHome
                    )
                } catch {
                    fresh = try await APIClient.shared.fetchPersonalSessionBootstrap(
                        forceRefresh: force,
                        momentTypeCode: code
                    )
                }
                applySession(fresh)
                sessionLoading = false
            } catch {
                sessionLoading = false
                sessionError = error.localizedDescription
            }
        }
        await sessionLoadTask?.value
    }

    /// Soft background refresh via split inventory + session endpoints.
    func softRefreshPersonalSession() async {
        let gen = generation
        do {
            _ = try? await APIClient.shared.fetchPersonalSession()
            let code = PersonalMomentSelectionHolder.store.selectedMomentTypeCode
            let inventory = try await APIClient.shared.fetchPersonalInventory(momentTypeCode: code)
            if gen != generation { return }
            applySession(
                APIClient.PersonalSessionBootstrapResponse(
                    pulse: inventory.pulse,
                    momentsHome: inventory.momentsHome
                )
            )
        } catch {
            await ensurePersonalSession(force: false)
        }
    }

    func refreshPersonalSessionInventory(force: Bool = false) async {
        if force {
            await ensurePersonalSession(force: true)
            return
        }
        await softRefreshPersonalSession()
    }
}

@MainActor
enum PersonalSessionHolder {
    static let store = PersonalSessionStore()
}

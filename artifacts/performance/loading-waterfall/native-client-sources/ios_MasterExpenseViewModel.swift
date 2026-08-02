import Foundation
import Observation

@MainActor
@Observable
final class MasterExpenseViewModel {
    var options: PersonalMasterExpenseOptionsResponse?
    var loading = false
    var saving = false
    var error: String?

    var title = ""
    var amount = ""
    var money = MoneyValue(amountMinor: 0, currencyCode: "INR")
    var accountId = ""
    var categoryCode = ""
    var subcategoryCode = ""
    var occurredAt = Date()
    var feeling = ""
    var meaningfulness = ""
    var memorability = ""
    var sharedEnabled = true
    var sharedWith: Set<String> = []
    var relationshipImpact = ""
    var contextReason = ""
    var notes = ""
    var moreDetailsExpanded = false

    private var activeSaveRequestId: String?

    var currencies: [CurrencyReference] {
        ReferenceDataStore.shared.data?.currencies ?? []
    }

    var isDirty: Bool {
        !title.trimmingCharacters(in: .whitespaces).isEmpty
            || !amount.trimmingCharacters(in: .whitespaces).isEmpty
            || money.amountMinor > 0
            || !subcategoryCode.isEmpty
            || !feeling.isEmpty
            || !meaningfulness.isEmpty
            || !memorability.isEmpty
            || !sharedWith.isEmpty
            || !relationshipImpact.isEmpty
            || !contextReason.isEmpty
            || !notes.isEmpty
    }

    var canSave: Bool {
        guard options?.lifeOperationsMomentId != nil else { return false }
        guard options?.lifestyleMomentId != nil else { return false }
        let minorUnit = currencies.first(where: { $0.code == money.currencyCode })?.minorUnit ?? 2
        let amountMinor = MoneyFormatter.parseUserInputToMinor(amount, minorUnit: minorUnit)
        return !title.trimmingCharacters(in: .whitespaces).isEmpty
            && amountMinor > 0
            && !accountId.isEmpty
            && !categoryCode.isEmpty
    }

    var selectedCategoryChildren: [PersonalQuickAddCategoryResponse] {
        options?.categories.first(where: { $0.categoryId == categoryCode })?.children ?? []
    }

    func load() async {
        error = nil
        if let peek = PersonalSessionHolder.store.peekMasterExpenseOptions() {
            options = peek
            loading = false
            if accountId.isEmpty, let first = peek.accounts.first {
                accountId = first.accountId
                money.currencyCode = first.currencyCode
            }
        } else {
            loading = true
        }
        defer { loading = false }
        do {
            let data = try await PersonalSessionHolder.store.getMasterExpenseOptions()
            options = data
            if accountId.isEmpty, let first = data.accounts.first {
                accountId = first.accountId
                money.currencyCode = first.currencyCode
            }
            // Do not auto-select category.
        } catch {
            if options == nil {
                self.error = error.localizedDescription
            }
        }
    }

    func selectCategory(_ code: String) {
        categoryCode = code
        subcategoryCode = Self.resolveSubcategory(
            categories: options?.categories ?? [],
            categoryCode: code,
            current: subcategoryCode
        )
    }

    func selectSubcategory(_ code: String) {
        subcategoryCode = code
    }

    func clearAll() {
        title = ""
        amount = ""
        money = MoneyValue(amountMinor: 0, currencyCode: money.currencyCode)
        subcategoryCode = ""
        categoryCode = ""
        feeling = ""
        meaningfulness = ""
        memorability = ""
        sharedWith = []
        relationshipImpact = ""
        contextReason = ""
        notes = ""
        occurredAt = Date()
    }

    func toggleSharedWith(_ value: String) {
        if sharedWith.contains(value) {
            sharedWith.remove(value)
        } else {
            sharedWith.insert(value)
        }
    }

    func save() async -> Bool {
        guard canSave, !saving else { return false }
        saving = true
        error = nil
        defer {
            if activeSaveRequestId != nil {
                saving = false
                activeSaveRequestId = nil
            }
        }
        let requestId = UUID().uuidString.lowercased()
        activeSaveRequestId = requestId
        let categoryName = options?.categories.first(where: { $0.categoryId == categoryCode })?.categoryName
        let resolvedSub = Self.resolveSubcategory(
            categories: options?.categories ?? [],
            categoryCode: categoryCode,
            current: subcategoryCode
        )
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let minorUnit = currencies.first(where: { $0.code == money.currencyCode })?.minorUnit ?? 2
        let amountMinor = MoneyFormatter.parseUserInputToMinor(amount, minorUnit: minorUnit)
        let body = PersonalMasterExpenseRequest(
            clientRequestId: requestId,
            expense: PersonalMasterExpenseTransactionRequest(
                title: title.trimmingCharacters(in: .whitespaces),
                amount: MoneyFormatter.minorToDisplayInput(amountMinor, minorUnit: minorUnit),
                accountId: accountId,
                categoryName: categoryName,
                categoryId: categoryCode,
                categoryCode: categoryCode,
                subcategoryCode: resolvedSub.isEmpty ? nil : resolvedSub,
                currencyCode: money.currencyCode,
                amountMinor: Int(amountMinor),
                pressureImpact: nil,
                description: title.trimmingCharacters(in: .whitespaces),
                transactionDate: formatter.string(from: occurredAt)
            ),
            experience: PersonalMasterExpenseExperienceRequest(
                feeling: feeling.isEmpty ? nil : feeling,
                meaningfulness: meaningfulness.isEmpty ? nil : meaningfulness,
                memorability: memorability.isEmpty ? nil : memorability
            ),
            sharedExperience: PersonalMasterExpenseSharedRequest(
                enabled: sharedEnabled,
                sharedWith: Array(sharedWith),
                relationshipImpact: relationshipImpact.isEmpty ? [] : [relationshipImpact]
            ),
            context: PersonalMasterExpenseContextRequest(reason: contextReason.isEmpty ? nil : contextReason),
            notes: notes.trimmingCharacters(in: .whitespaces).isEmpty ? nil : notes.trimmingCharacters(in: .whitespaces)
        )
        do {
            _ = try await PersonalSessionHolder.store.createMasterExpense(body)
            PersonalSessionHolder.store.invalidateAfterMasterExpense(includeRelationships: sharedEnabled)
            return true
        } catch {
            self.error = error.localizedDescription
            return false
        }
    }

    static func resolveSubcategory(
        categories: [PersonalQuickAddCategoryResponse],
        categoryCode: String,
        current: String
    ) -> String {
        guard !categoryCode.isEmpty, !current.isEmpty else { return "" }
        let children = categories.first(where: { $0.categoryId == categoryCode })?.children ?? []
        return children.contains(where: { $0.categoryId == current }) ? current : ""
    }
}

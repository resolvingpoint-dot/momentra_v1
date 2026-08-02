import Combine
import SwiftUI

@MainActor
final class BusinessActionCenterViewModel: ObservableObject {
    let momentId: String
    let momentTypeCode: String

    @Published private(set) var catalog: BusinessActionCatalogResponse?
    @Published private(set) var hubActions: [BusinessActionCenterAction] = []
    @Published private(set) var catalogCategories: [BusinessCatalogCategory] = []
    @Published private(set) var members: [BusinessCatalogMember] = []
    @Published private(set) var vendors: [BusinessCatalogVendor] = []
    @Published var catalogLoading = false
    @Published var catalogError: String?

    /// Renderer fields for the currently selected action (source of truth for SchemaForm).
    @Published private(set) var rendererFields: [BusinessCatalogField] = []
    @Published var rendererLoading = false
    @Published var rendererError: String?

    init(momentId: String, momentTypeCode: String) {
        self.momentId = momentId
        self.momentTypeCode = momentTypeCode
    }

    var templateId: String {
        catalog?.templateId ?? BusinessActionCenterMeta.templateId(forMomentType: momentTypeCode)
    }

    var resolvedActions: [BusinessActionCenterAction] {
        if !hubActions.isEmpty { return hubActions }
        return BusinessActionCenterMeta.fallbackActions(for: templateId)
    }

    var resolvedCategories: [BusinessCatalogCategory] {
        if !catalogCategories.isEmpty { return catalogCategories }
        return BusinessActionCenterMeta.fallbackCategories(for: templateId)
    }

    func loadCatalog() async {
        catalogLoading = true
        catalogError = nil
        defer { catalogLoading = false }
        do {
            let response = try await BusinessActionRepository.fetchActionCatalog(momentId: momentId)
            catalog = response
            let template = response.templateId
            hubActions = response.actions.map { BusinessActionCenterMeta.enrich($0, templateId: template) }
            catalogCategories = response.categories
            members = response.members
            vendors = response.vendors
            BusinessQuickAddDiagnostics.record(
                actionCode: "catalog",
                momentTypeCode: momentTypeCode,
                stage: "catalog_ok",
                fieldCount: hubActions.reduce(0) { $0 + $1.fields.count }
            )
        } catch {
            catalogError = error.localizedDescription
            hubActions = []
            catalogCategories = []
            members = []
            vendors = []
            BusinessQuickAddDiagnostics.record(
                actionCode: "catalog",
                momentTypeCode: momentTypeCode,
                stage: "catalog_error",
                decodeFailureStage: "catalog_fetch"
            )
        }
    }

    /// Prefer fields embedded in action-catalog (no second /renderer RTT).
    func loadRendererFields(actionKey: String) async {
        rendererLoading = true
        rendererError = nil
        defer { rendererLoading = false }

        if let embedded = hubActions.first(where: { $0.actionId == actionKey })?.fields, !embedded.isEmpty {
            rendererFields = embedded
            BusinessQuickAddDiagnostics.record(
                actionCode: actionKey,
                momentTypeCode: momentTypeCode,
                stage: "renderer_from_catalog",
                fieldCount: embedded.count
            )
            return
        }

        do {
            let meta = try await BusinessActionRepository.fetchRendererMeta(
                momentId: momentId,
                actionKey: actionKey
            )
            if !meta.fields.isEmpty {
                rendererFields = meta.fields.enumerated().map { index, field in
                    BusinessCatalogField(
                        fieldKey: field.fieldKey,
                        fieldType: BusinessActivityPayloadBuilder.normalizeFieldType(field.fieldType),
                        label: field.label,
                        placeholder: field.placeholder,
                        required: field.required || (meta.requiredFields?.contains(field.fieldKey) ?? false),
                        options: field.options,
                        defaultValue: field.defaultValue,
                        displayOrder: field.displayOrder > 0 ? field.displayOrder : index,
                        visibleWhen: field.visibleWhen,
                        allowCustom: field.allowCustom
                    )
                }
                BusinessQuickAddDiagnostics.record(
                    actionCode: actionKey,
                    momentTypeCode: momentTypeCode,
                    stage: "renderer_ok",
                    fieldCount: rendererFields.count
                )
            } else if let offline = BusinessActionSchemaLibrary.fields(forActionId: actionKey), !offline.isEmpty {
                rendererFields = offline
                BusinessQuickAddDiagnostics.record(
                    actionCode: actionKey,
                    momentTypeCode: momentTypeCode,
                    stage: "renderer_empty_used_offline",
                    fieldCount: offline.count
                )
            } else {
                rendererFields = []
                if BusinessActionSchemaLibrary.isKnownAction(actionId: actionKey) {
                    rendererError = "Renderer returned no fields for a known action."
                    BusinessQuickAddDiagnostics.record(
                        actionCode: actionKey,
                        momentTypeCode: momentTypeCode,
                        stage: "renderer_empty_known",
                        decodeFailureStage: "renderer_fields_empty"
                    )
                }
            }
        } catch {
            rendererFields = BusinessActionSchemaLibrary.fields(forActionId: actionKey) ?? []
            if rendererFields.isEmpty {
                rendererError = error.localizedDescription
            }
            BusinessQuickAddDiagnostics.record(
                actionCode: actionKey,
                momentTypeCode: momentTypeCode,
                stage: "renderer_error",
                decodeFailureStage: "renderer_fetch",
                fieldCount: rendererFields.count
            )
        }
    }

    func clearRendererFields() {
        rendererFields = []
        rendererError = nil
    }

    /// Backward-compatible name used by shell.
    func loadRendererContext(actionKey: String) async {
        await loadRendererFields(actionKey: actionKey)
    }

    func submit(action: BusinessActionCenterAction, fields: [String: String]) async throws {
        try await BusinessActionRepository.submit(momentId: momentId, action: action, fields: fields)
    }
}

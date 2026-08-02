import Foundation

// MARK: - Schema field definition from catalog API

struct BusinessCatalogFieldOption: Codable, Equatable {
    let value: String
    let label: String
}

struct BusinessCatalogVisibleWhen: Codable, Equatable {
    let field: String
    let equals: String
}

struct BusinessCatalogField: Decodable, Equatable, Identifiable {
    var id: String { fieldKey }
    let fieldKey: String
    let fieldType: String
    let label: String
    let placeholder: String?
    let required: Bool
    let options: [BusinessCatalogFieldOption]?
    let defaultValue: String?
    let displayOrder: Int
    let visibleWhen: BusinessCatalogVisibleWhen?
    let allowCustom: Bool

    private enum CodingKeys: String, CodingKey {
        case key
        case fieldKey = "field_key"
        case fieldType = "field_type"
        case label, placeholder, required, options
        case defaultValue = "default_value"
        case defaultAlias = "default"
        case displayOrder = "display_order"
        case visibleWhen = "visible_when"
        case allowCustom = "allow_custom"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        // Backend catalog uses "key"; older clients used "field_key".
        if let k = try c.decodeIfPresent(String.self, forKey: .key), !k.isEmpty {
            fieldKey = k
        } else if let k = try c.decodeIfPresent(String.self, forKey: .fieldKey), !k.isEmpty {
            fieldKey = k
        } else {
            throw DecodingError.keyNotFound(
                CodingKeys.key,
                .init(codingPath: c.codingPath, debugDescription: "Missing field key")
            )
        }
        fieldType = BusinessActivityPayloadBuilder.normalizeFieldType(
            try c.decodeIfPresent(String.self, forKey: .fieldType) ?? "text"
        )
        label = try c.decodeIfPresent(String.self, forKey: .label) ?? fieldKey
        placeholder = try c.decodeIfPresent(String.self, forKey: .placeholder)
        required = try c.decodeIfPresent(Bool.self, forKey: .required) ?? false
        options = try c.decodeIfPresent([BusinessCatalogFieldOption].self, forKey: .options)
        if let dv = try c.decodeIfPresent(String.self, forKey: .defaultValue) {
            defaultValue = dv
        } else if let boolDefault = try c.decodeIfPresent(Bool.self, forKey: .defaultAlias) {
            defaultValue = boolDefault ? "true" : "false"
        } else if let strDefault = try c.decodeIfPresent(String.self, forKey: .defaultAlias) {
            defaultValue = strDefault
        } else {
            defaultValue = nil
        }
        displayOrder = try c.decodeIfPresent(Int.self, forKey: .displayOrder) ?? 0
        visibleWhen = try c.decodeIfPresent(BusinessCatalogVisibleWhen.self, forKey: .visibleWhen)
        allowCustom = try c.decodeIfPresent(Bool.self, forKey: .allowCustom) ?? (fieldType == "vendor_picker")
    }

    init(fieldKey: String, fieldType: String, label: String, placeholder: String? = nil,
         required: Bool = false, options: [BusinessCatalogFieldOption]? = nil,
         defaultValue: String? = nil, displayOrder: Int = 0,
         visibleWhen: BusinessCatalogVisibleWhen? = nil, allowCustom: Bool = false) {
        self.fieldKey = fieldKey
        self.fieldType = fieldType
        self.label = label
        self.placeholder = placeholder
        self.required = required
        self.options = options
        self.defaultValue = defaultValue
        self.displayOrder = displayOrder
        self.visibleWhen = visibleWhen
        self.allowCustom = allowCustom || fieldType == "vendor_picker"
    }
}

/// Typed renderer metadata from GET .../actions/{key}/renderer
struct BusinessActionRendererMeta: Decodable, Equatable {
    let actionId: String
    let actionType: String
    let label: String
    let rendererId: String
    let ctaLabel: String?
    let fields: [BusinessCatalogField]
    let requiredFields: [String]?

    enum CodingKeys: String, CodingKey {
        case actionId = "action_id"
        case actionType = "action_type"
        case label
        case rendererId = "renderer_id"
        case ctaLabel = "cta_label"
        case fields
        case requiredFields = "required_fields"
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        actionId = try c.decodeIfPresent(String.self, forKey: .actionId) ?? ""
        actionType = try c.decodeIfPresent(String.self, forKey: .actionType) ?? ""
        label = try c.decodeIfPresent(String.self, forKey: .label) ?? ""
        rendererId = try c.decodeIfPresent(String.self, forKey: .rendererId) ?? "schema.generic"
        ctaLabel = try c.decodeIfPresent(String.self, forKey: .ctaLabel)
        fields = Self.decodeFieldsFlexibly(from: c) ?? []
        requiredFields = try c.decodeIfPresent([String].self, forKey: .requiredFields)
    }

    private static func decodeFieldsFlexibly(from c: KeyedDecodingContainer<CodingKeys>) -> [BusinessCatalogField]? {
        guard var arr = try? c.nestedUnkeyedContainer(forKey: .fields) else {
            return try? c.decodeIfPresent([BusinessCatalogField].self, forKey: .fields)
        }
        var out: [BusinessCatalogField] = []
        var index = 0
        while !arr.isAtEnd {
            if let field = try? arr.decode(BusinessCatalogField.self) {
                out.append(
                    BusinessCatalogField(
                        fieldKey: field.fieldKey,
                        fieldType: BusinessActivityPayloadBuilder.normalizeFieldType(field.fieldType),
                        label: field.label,
                        placeholder: field.placeholder,
                        required: field.required,
                        options: field.options,
                        defaultValue: field.defaultValue,
                        displayOrder: field.displayOrder > 0 ? field.displayOrder : index,
                        visibleWhen: field.visibleWhen,
                        allowCustom: field.allowCustom
                    )
                )
            } else {
                _ = try? arr.decode(DiscardedField.self)
            }
            index += 1
        }
        return out
    }

    private struct DiscardedField: Decodable {}
}

struct BusinessCatalogAction: Decodable, Equatable {
    let actionId: String
    let actionType: String
    let label: String
    let subtitle: String?
    let icon: String
    let rendererId: String
    let categoryId: String
    let ctaLabel: String
    let displayOrder: Int
    let supports: [String: Bool]?
    let fields: [BusinessCatalogField]?

    enum CodingKeys: String, CodingKey {
        case actionId = "action_id"
        case actionType = "action_type"
        case label, subtitle, icon
        case rendererId = "renderer_id"
        case categoryId = "category_id"
        case ctaLabel = "cta_label"
        case displayOrder = "display_order"
        case supports, fields
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        actionId = try c.decode(String.self, forKey: .actionId)
        actionType = try c.decode(String.self, forKey: .actionType)
        label = try c.decode(String.self, forKey: .label)
        subtitle = try c.decodeIfPresent(String.self, forKey: .subtitle)
        icon = try c.decodeIfPresent(String.self, forKey: .icon) ?? "bolt"
        rendererId = try c.decodeIfPresent(String.self, forKey: .rendererId) ?? "schema.generic"
        categoryId = try c.decodeIfPresent(String.self, forKey: .categoryId) ?? "core"
        ctaLabel = try c.decodeIfPresent(String.self, forKey: .ctaLabel) ?? "Save"
        displayOrder = try c.decodeIfPresent(Int.self, forKey: .displayOrder) ?? 0
        supports = try c.decodeIfPresent([String: Bool].self, forKey: .supports)
        fields = Self.decodeFieldsFlexibly(from: c)
    }

    /// Decode fields one-by-one so a single bad field does not wipe the list.
    private static func decodeFieldsFlexibly(from c: KeyedDecodingContainer<CodingKeys>) -> [BusinessCatalogField]? {
        guard let arr = try? c.nestedUnkeyedContainer(forKey: .fields) else {
            return try? c.decodeIfPresent([BusinessCatalogField].self, forKey: .fields)
        }
        var container = arr
        var out: [BusinessCatalogField] = []
        var index = 0
        while !container.isAtEnd {
            if let field = try? container.decode(BusinessCatalogField.self) {
                out.append(
                    BusinessCatalogField(
                        fieldKey: field.fieldKey,
                        fieldType: BusinessActivityPayloadBuilder.normalizeFieldType(field.fieldType),
                        label: field.label,
                        placeholder: field.placeholder,
                        required: field.required,
                        options: field.options,
                        defaultValue: field.defaultValue,
                        displayOrder: field.displayOrder > 0 ? field.displayOrder : index,
                        visibleWhen: field.visibleWhen,
                        allowCustom: field.allowCustom
                    )
                )
            } else {
                _ = try? container.decode(DiscardedField.self)
            }
            index += 1
        }
        return out
    }

    private struct DiscardedField: Decodable {}
}

struct BusinessCatalogCategory: Codable, Equatable, Identifiable {
    let id: String
    let label: String
    let actions: [BusinessCatalogCategoryActionRef]?

    struct BusinessCatalogCategoryActionRef: Codable, Equatable {
        let actionId: String
        let actionType: String
        let label: String
        let icon: String
        let rendererId: String
        let ctaLabel: String
        let displayOrder: Int

        enum CodingKeys: String, CodingKey {
            case actionId = "action_id"
            case actionType = "action_type"
            case label, icon
            case rendererId = "renderer_id"
            case ctaLabel = "cta_label"
            case displayOrder = "display_order"
        }
    }
}

struct BusinessCatalogMember: Codable, Equatable, Identifiable {
    let memberId: String
    let name: String
    let role: String?
    let userId: String?

    var id: String { memberId }
    var displayName: String { name }

    enum CodingKeys: String, CodingKey {
        case memberId = "member_id"
        case name, role
        case userId = "user_id"
    }
}

struct BusinessCatalogVendor: Codable, Equatable, Identifiable {
    let value: String
    let label: String
    let dueMinor: Int?

    var id: String { value }

    enum CodingKeys: String, CodingKey {
        case value, label
        case dueMinor = "due_minor"
    }
}

struct BusinessActionCatalogResponse: Decodable, Equatable {
    static let expectedSchemaVersion = 2

    let momentId: String
    let momentType: String
    let templateId: String
    let schemaVersion: Int
    let categories: [BusinessCatalogCategory]
    let actions: [BusinessCatalogAction]
    let members: [BusinessCatalogMember]
    let vendors: [BusinessCatalogVendor]

    enum CodingKeys: String, CodingKey {
        case momentId = "moment_id"
        case momentType = "moment_type"
        case templateId = "template_id"
        case schemaVersion = "schema_version"
        case categories, actions, members, vendors
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        momentId = try c.decodeIfPresent(String.self, forKey: .momentId) ?? ""
        momentType = try c.decodeIfPresent(String.self, forKey: .momentType) ?? ""
        templateId = try c.decodeIfPresent(String.self, forKey: .templateId) ?? ""
        schemaVersion = try c.decodeIfPresent(Int.self, forKey: .schemaVersion) ?? 0
        categories = try c.decodeIfPresent([BusinessCatalogCategory].self, forKey: .categories) ?? []
        actions = try c.decodeIfPresent([BusinessCatalogAction].self, forKey: .actions) ?? []
        members = try c.decodeIfPresent([BusinessCatalogMember].self, forKey: .members) ?? []
        vendors = try c.decodeIfPresent([BusinessCatalogVendor].self, forKey: .vendors) ?? []
    }

    var schemaCompatible: Bool {
        schemaVersion == 0 || schemaVersion == Self.expectedSchemaVersion
    }
}

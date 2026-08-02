package com.example.momentra.data.business.actioncenter

import com.example.momentra.data.actioncenter.ActionCapabilities
import com.example.momentra.data.actioncenter.ActionCenterAction
import com.example.momentra.data.actioncenter.RendererConfig
import com.example.momentra.data.actioncenter.SimpleField
import com.example.momentra.data.actioncenter.SimpleFieldType
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.booleanOrNull
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.intOrNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

@Serializable
data class BusinessCatalogSupportsDto(
    val drafts: Boolean = true,
    val favorites: Boolean = true,
    val review: Boolean = true,
)

@Serializable
data class BusinessCatalogActionDto(
    @SerialName("action_id") val actionId: String,
    @SerialName("action_type") val actionType: String,
    val label: String,
    val subtitle: String? = null,
    val icon: String = "bolt",
    @SerialName("renderer_id") val rendererId: String,
    @SerialName("category_id") val categoryId: String? = null,
    @SerialName("cta_label") val ctaLabel: String? = null,
    @SerialName("display_order") val displayOrder: Int = 100,
    val supports: BusinessCatalogSupportsDto = BusinessCatalogSupportsDto(),
    val fields: List<BusinessRendererFieldDto> = emptyList(),
    @SerialName("required_fields") val requiredFields: List<String> = emptyList(),
)

@Serializable
data class BusinessCatalogCategoryDto(
    val id: String,
    val label: String,
    val actions: List<BusinessCatalogActionDto> = emptyList(),
)

@Serializable
data class BusinessCatalogMemberDto(
    @SerialName("member_id") val memberId: String,
    val name: String,
    val role: String? = null,
    @SerialName("user_id") val userId: String? = null,
)

@Serializable
data class BusinessCatalogVendorDto(
    val value: String,
    val label: String,
    @SerialName("due_minor") val dueMinor: Long? = null,
)

@Serializable
data class BusinessActionCatalogDto(
    @SerialName("moment_id") val momentId: String,
    @SerialName("moment_type") val momentType: String,
    @SerialName("template_id") val templateId: String,
    @SerialName("schema_version") val schemaVersion: Int = 0,
    val categories: List<BusinessCatalogCategoryDto> = emptyList(),
    val actions: List<BusinessCatalogActionDto> = emptyList(),
    val members: List<BusinessCatalogMemberDto> = emptyList(),
    val vendors: List<BusinessCatalogVendorDto> = emptyList(),
) {
    companion object {
        const val EXPECTED_SCHEMA_VERSION = 2
    }
}

@Serializable
data class BusinessRendererFieldOptionDto(
    val value: String,
    val label: String,
)

@Serializable
data class BusinessRendererVisibleWhenDto(
    val field: String,
    val equals: String,
)

@Serializable
data class BusinessRendererFieldDto(
    val key: String,
    val label: String,
    @SerialName("field_type") val fieldType: String = "text",
    val required: Boolean = false,
    val options: List<BusinessRendererFieldOptionDto> = emptyList(),
    /** String or bool from catalog — coerce in mapper. */
    val default: JsonElement? = null,
    @SerialName("default_value") val defaultValue: JsonElement? = null,
    @SerialName("visible_when") val visibleWhen: BusinessRendererVisibleWhenDto? = null,
    @SerialName("allow_custom") val allowCustom: Boolean = false,
)

@Serializable
data class BusinessActionRendererDto(
    @SerialName("moment_id") val momentId: String? = null,
    @SerialName("moment_type") val momentType: String? = null,
    @SerialName("action_id") val actionId: String,
    @SerialName("action_type") val actionType: String,
    val label: String,
    @SerialName("renderer_id") val rendererId: String,
    @SerialName("cta_label") val ctaLabel: String? = null,
    val fields: List<BusinessRendererFieldDto> = emptyList(),
    @SerialName("required_fields") val requiredFields: List<String> = emptyList(),
)

object BusinessCatalogMapper {
    fun templateIdFromMomentType(momentTypeCode: String): String =
        BusinessActionCenterMeta.templateIdForMomentType(momentTypeCode)

    fun toActions(catalog: BusinessActionCatalogDto): List<ActionCenterAction> {
        val templateId = catalog.templateId.substringAfter("business.", catalog.templateId)
            .ifBlank { templateIdFromMomentType(catalog.momentType) }
        return catalog.actions
            .sortedBy { it.displayOrder }
            .map { dto -> dto.toActionCenterAction(templateId) }
    }

    fun BusinessCatalogActionDto.toActionCenterAction(templateId: String): ActionCenterAction {
        val meta = BusinessActionCenterMeta.metaForRendererId(rendererId)
        val apiFields = fields.map { it.toSimpleField() }
        val resolvedFields = apiFields.ifEmpty { meta?.fallbackFields.orEmpty() }
        val supports = ActionCapabilities(
            drafts = supports.drafts,
            favorites = supports.favorites,
        )
        return ActionCenterAction(
            templateId = templateId,
            actionId = actionId,
            actionType = actionType,
            label = label,
            subtitle = subtitle?.takeIf { it.isNotBlank() }
                ?: ctaLabel
                ?: meta?.ctaLabel
                ?: "",
            category = BusinessActionCenterMeta.categoryForId(categoryId ?: meta?.categoryId ?: "core"),
            estimatedTimeSec = 20,
            tags = listOf(actionId, actionType),
            rendererType = meta?.rendererType ?: BusinessActionCenterMeta.rendererTypeFor(rendererId),
            rendererConfig = RendererConfig.SimpleFormConfig(resolvedFields),
            analyticsId = rendererId,
            priority = displayOrder,
            icon = icon,
            supports = supports,
            ctaLabel = ctaLabel ?: meta?.ctaLabel ?: "Save",
        )
    }

    fun rendererFieldsFromDto(dto: BusinessActionRendererDto): List<SimpleField> =
        dto.fields.map { it.toSimpleField() }

    fun rendererFieldsFromJson(json: JsonObject): List<SimpleField> {
        val arr = json["fields"]?.jsonArray ?: return emptyList()
        return arr.mapNotNull { el -> parseFieldElement(el) }
    }

    private fun parseFieldElement(el: JsonElement): SimpleField? {
        val obj = el.jsonObject
        val key = obj["key"]?.jsonPrimitive?.contentOrNull ?: return null
        val label = obj["label"]?.jsonPrimitive?.contentOrNull ?: key
        val required = obj["required"]?.jsonPrimitive?.contentOrNull?.toBooleanStrictOrNull() ?: false
        val fieldType = obj["field_type"]?.jsonPrimitive?.contentOrNull ?: "text"
        val options = parseOptions(obj["options"])
        val defaultValue = obj["default_value"]?.jsonPrimitive?.contentOrNull
            ?: obj["default"]?.jsonPrimitive?.contentOrNull
        val visible = obj["visible_when"]?.jsonObject
        val allowCustom = obj["allow_custom"]?.jsonPrimitive?.contentOrNull?.toBooleanStrictOrNull()
            ?: (fieldType == "vendor_picker")
        return SimpleField(
            key = key,
            label = label,
            type = fieldTypeToSimple(fieldType),
            required = required,
            options = options.map { it.first },
            optionPairs = options,
            defaultValue = defaultValue,
            visibleWhenField = visible?.get("field")?.jsonPrimitive?.contentOrNull,
            visibleWhenEquals = visible?.get("equals")?.jsonPrimitive?.contentOrNull,
            allowCustom = allowCustom,
        )
    }

    private fun parseOptions(el: JsonElement?): List<Pair<String, String>> {
        if (el == null) return emptyList()
        return when (el) {
            is JsonArray -> el.mapNotNull { optEl ->
                val opt = optEl.jsonObject
                val value = opt["value"]?.jsonPrimitive?.contentOrNull ?: return@mapNotNull null
                val label = opt["label"]?.jsonPrimitive?.contentOrNull ?: value
                value to label
            }
            else -> emptyList()
        }
    }

    private fun jsonScalarToString(el: JsonElement?): String? {
        val prim = el as? JsonPrimitive ?: return null
        prim.booleanOrNull?.let { return if (it) "true" else "false" }
        return prim.contentOrNull
    }

    private fun BusinessRendererFieldDto.toSimpleField(): SimpleField {
        val pairs = options.map { it.value to it.label }
        return SimpleField(
            key = key,
            label = label,
            type = fieldTypeToSimple(fieldType),
            required = required,
            options = pairs.map { it.first },
            optionPairs = pairs,
            defaultValue = jsonScalarToString(defaultValue) ?: jsonScalarToString(default),
            visibleWhenField = visibleWhen?.field,
            visibleWhenEquals = visibleWhen?.equals,
            allowCustom = allowCustom || fieldType == "vendor_picker",
        )
    }

    private fun fieldTypeToSimple(fieldType: String): SimpleFieldType = when (fieldType) {
        "textarea" -> SimpleFieldType.TEXTAREA
        "date" -> SimpleFieldType.DATE
        "amount" -> SimpleFieldType.AMOUNT
        "member_picker" -> SimpleFieldType.MEMBER_PICKER
        "member_multi_select" -> SimpleFieldType.MEMBER_MULTI_SELECT
        "searchable_select" -> SimpleFieldType.SEARCHABLE_SELECT
        "segmented" -> SimpleFieldType.SEGMENTED
        "single_select" -> SimpleFieldType.SELECT
        "toggle" -> SimpleFieldType.TOGGLE
        "attachment" -> SimpleFieldType.ATTACHMENT
        "vendor_picker", "vendor" -> SimpleFieldType.VENDOR_PICKER
        else -> SimpleFieldType.TEXT
    }

    fun membersToOptions(members: List<BusinessCatalogMemberDto>): List<Pair<String, String>> =
        members.map { it.memberId to it.name }

    fun vendorsToOptions(vendors: List<BusinessCatalogVendorDto>): List<Pair<String, String>> =
        vendors.map { it.value to it.label }
}

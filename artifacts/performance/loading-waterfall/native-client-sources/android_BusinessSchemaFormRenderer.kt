package com.example.momentra.ui.business.actioncenter.renderers

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import com.example.momentra.data.actioncenter.ActionCenterAction
import com.example.momentra.data.actioncenter.RendererConfig
import com.example.momentra.data.actioncenter.SimpleField
import com.example.momentra.data.actioncenter.SimpleFieldType
import com.example.momentra.data.business.actioncenter.BusinessActivitySubmit
import com.example.momentra.data.business.actioncenter.BusinessCatalogMapper
import com.example.momentra.data.business.actioncenter.BusinessCatalogMemberDto
import com.example.momentra.data.business.actioncenter.BusinessCatalogVendorDto
import com.example.momentra.data.repository.BusinessActionRepository
import com.example.momentra.ui.business.actioncenter.BusinessProgressiveActionForm
import com.example.momentra.ui.business.actioncenter.BusinessProgressiveStep
import com.example.momentra.ui.business.actioncenter.fields.BizAttachmentField
import com.example.momentra.ui.business.actioncenter.fields.BizChipSelector
import com.example.momentra.ui.business.actioncenter.fields.BizMaterialDateField
import com.example.momentra.ui.business.actioncenter.fields.BizMemberPickerField
import com.example.momentra.ui.business.actioncenter.fields.BizMoneyField
import com.example.momentra.ui.business.actioncenter.fields.BizMultiMemberPickerField
import com.example.momentra.ui.business.actioncenter.fields.BizNotesField
import com.example.momentra.ui.business.actioncenter.fields.BizSearchableSelectField
import com.example.momentra.ui.business.actioncenter.fields.BizTextInputField
import com.example.momentra.ui.business.actioncenter.fields.BizToggleField
import com.example.momentra.ui.business.actioncenter.ui.BusinessFormChrome
import com.example.momentra.ui.business.actioncenter.ui.BusinessSectionTitle
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.Locale

private const val SEGMENTED_THRESHOLD = 4

@Composable
fun BusinessSchemaFormRenderer(
    action: ActionCenterAction,
    momentId: String,
    members: List<BusinessCatalogMemberDto> = emptyList(),
    vendors: List<BusinessCatalogVendorDto> = emptyList(),
    onClose: () -> Unit,
    onSuccess: () -> Unit,
) {
    val fallback = (action.rendererConfig as? RendererConfig.SimpleFormConfig)?.fields.orEmpty()
    var fields by remember(action.actionId) { mutableStateOf(fallback) }
    // Catalog already embeds fields — skip second /renderer RTT when present.
    var loadingRenderer by remember(action.actionId) { mutableStateOf(fallback.isEmpty()) }

    LaunchedEffect(momentId, action.actionId) {
        if (fallback.isNotEmpty()) {
            fields = fallback
            loadingRenderer = false
            return@LaunchedEffect
        }
        loadingRenderer = true
        runCatching {
            BusinessActionRepository.getActionRenderer(momentId, action.actionId)
        }.onSuccess { dto ->
            val apiFields = BusinessCatalogMapper.rendererFieldsFromDto(dto)
            if (apiFields.isNotEmpty()) fields = apiFields
        }
        loadingRenderer = false
    }

    val memberOptions = remember(members) { BusinessCatalogMapper.membersToOptions(members) }
    val vendorOptions = remember(vendors) { BusinessCatalogMapper.vendorsToOptions(vendors) }

    BusinessProgressiveActionForm(
        action = action,
        momentId = momentId,
        initialState = buildInitialState(fields),
        formChrome = { BusinessFormChrome(actionLabel = action.label) },
        saveLabel = action.ctaLabel,
        reviewEnabled = true,
        steps = listOf(
            BusinessProgressiveStep(
                id = "content",
                title = action.label,
                validate = { state -> validateFields(fields, state) },
            ) { state, set, errors ->
                if (loadingRenderer) {
                    BusinessSectionTitle("Loading form…")
                } else {
                    BusinessSectionTitle("Core")
                    fields.forEach { field ->
                        if (!isFieldVisible(field, state)) return@forEach
                        renderField(field, state, set, errors, memberOptions, vendorOptions)
                    }
                }
            },
        ),
        buildReviewRows = { s ->
            val rows = fields.mapNotNull { f ->
                if (!isFieldVisible(f, s)) return@mapNotNull null
                val v = s[f.key].orEmpty()
                if (v.isNotBlank()) {
                    val display = resolveDisplayValue(f, v, memberOptions, vendorOptions)
                    f.label to display
                } else null
            }.toMutableList()
            val due = computeDueMinor(s)
            if (due > 0) {
                rows.add("Due to vendor" to formatDueLabel(due))
            }
            rows
        },
        draftTitleKey = fields.firstOrNull { it.key == "title" }?.key
            ?: fields.firstOrNull()?.key
            ?: "title",
        onSubmit = { formFields ->
            withContext(Dispatchers.IO) {
                BusinessActivitySubmit.post(momentId, action, formFields)
            }
        },
        onClose = onClose,
        onSuccess = onSuccess,
    )
}

private fun isFieldVisible(field: SimpleField, state: Map<String, String>): Boolean {
    val f = field.visibleWhenField ?: return true
    val expected = field.visibleWhenEquals ?: return true
    return state[f].orEmpty() == expected
}

private fun buildInitialState(fields: List<SimpleField>): Map<String, String> {
    val map = mutableMapOf<String, String>()
    fields.forEach { f ->
        when {
            !f.defaultValue.isNullOrBlank() -> map[f.key] = f.defaultValue
            f.type == SimpleFieldType.TOGGLE -> map[f.key] = "false"
            f.type == SimpleFieldType.AMOUNT -> {
                map[f.key] = ""
                map["currency_code"] = "INR"
            }
            f.type == SimpleFieldType.DATE -> map[f.key] = java.time.LocalDate.now().toString()
            else -> map[f.key] = ""
        }
    }
    return map
}

private fun majorToMinor(raw: String): Long {
    val n = raw.replace(",", "").toDoubleOrNull() ?: return 0L
    return (n * 100).toLong()
}

private fun computeDueMinor(state: Map<String, String>): Long {
    val total = majorToMinor(state["amount_minor"].orEmpty())
    return when (state["payment_status"].orEmpty()) {
        "paid_full", "" -> 0L
        "unpaid" -> total
        "paid_partial" -> {
            val paid = majorToMinor(state["amount_paid_minor"].orEmpty()).coerceIn(0L, total)
            (total - paid).coerceAtLeast(0L)
        }
        else -> 0L
    }
}

private fun formatDueLabel(dueMinor: Long): String {
    return if (dueMinor % 100L == 0L) {
        "₹${String.format(Locale.US, "%,d", dueMinor / 100)}"
    } else {
        "₹${String.format(Locale.US, "%,.2f", dueMinor / 100.0)}"
    }
}

private fun resolveDisplayValue(
    field: SimpleField,
    raw: String,
    memberOptions: List<Pair<String, String>>,
    vendorOptions: List<Pair<String, String>>,
): String = when (field.type) {
    SimpleFieldType.SELECT, SimpleFieldType.SEGMENTED, SimpleFieldType.SEARCHABLE_SELECT -> {
        field.optionPairs.firstOrNull { it.first == raw }?.second ?: raw
    }
    SimpleFieldType.VENDOR_PICKER -> {
        vendorOptions.firstOrNull { it.first == raw }?.second ?: raw
    }
    SimpleFieldType.MEMBER_PICKER -> {
        memberOptions.firstOrNull { it.first == raw }?.second ?: raw
    }
    SimpleFieldType.MEMBER_MULTI_SELECT -> {
        raw.split(",").filter { it.isNotBlank() }
            .joinToString { id -> memberOptions.firstOrNull { it.first == id }?.second ?: id }
            .ifBlank { raw }
    }
    SimpleFieldType.TOGGLE -> if (raw == "true") "Yes" else "No"
    SimpleFieldType.ATTACHMENT -> {
        val count = raw.split(",").filter { it.isNotBlank() }.size
        "$count file(s)"
    }
    else -> raw
}

@Composable
private fun renderField(
    field: SimpleField,
    state: Map<String, String>,
    set: (String, String) -> Unit,
    errors: Map<String, String>,
    memberOptions: List<Pair<String, String>>,
    vendorOptions: List<Pair<String, String>>,
) {
    when (field.type) {
        SimpleFieldType.TEXT -> BizTextInputField(
            label = field.label,
            value = state[field.key].orEmpty(),
            onChange = { set(field.key, it) },
            required = field.required,
            error = errors[field.key],
        )
        SimpleFieldType.TEXTAREA -> BizNotesField(
            value = state[field.key].orEmpty(),
            onChange = { set(field.key, it) },
            label = field.label,
        )
        SimpleFieldType.DATE -> BizMaterialDateField(
            label = field.label,
            value = state[field.key].orEmpty(),
            onChange = { set(field.key, it) },
            required = field.required,
            error = errors[field.key],
        )
        SimpleFieldType.AMOUNT -> BizMoneyField(
            label = field.label,
            value = state[field.key].orEmpty(),
            onChange = { set(field.key, it) },
            error = errors[field.key],
        )
        SimpleFieldType.MEMBER_PICKER -> BizMemberPickerField(
            label = field.label,
            value = state[field.key].orEmpty(),
            options = memberOptions,
            onChange = { set(field.key, it) },
            required = field.required,
            error = errors[field.key],
        )
        SimpleFieldType.MEMBER_MULTI_SELECT -> {
            val selected = state[field.key].orEmpty().split(",")
                .map { it.trim() }.filter { it.isNotEmpty() }
            BizMultiMemberPickerField(
                label = field.label,
                selectedIds = selected,
                options = memberOptions,
                onChange = { set(field.key, it.joinToString(",")) },
                required = field.required,
                error = errors[field.key],
            )
        }
        SimpleFieldType.SEGMENTED -> {
            val pairs = field.optionPairs.ifEmpty {
                field.options.map { it to it.replaceFirstChar { c -> c.uppercaseChar() } }
            }
            BizChipSelector(field.label, state[field.key].orEmpty(), pairs) { set(field.key, it) }
        }
        SimpleFieldType.SEARCHABLE_SELECT -> {
            val pairs = field.optionPairs.ifEmpty {
                field.options.map { it to it.replaceFirstChar { c -> c.uppercaseChar() } }
            }
            BizSearchableSelectField(
                label = field.label,
                value = state[field.key].orEmpty(),
                options = pairs,
                onChange = { set(field.key, it) },
                required = field.required,
                error = errors[field.key],
            )
        }
        SimpleFieldType.VENDOR_PICKER -> BizSearchableSelectField(
            label = field.label,
            value = state[field.key].orEmpty(),
            options = vendorOptions,
            onChange = { set(field.key, it) },
            required = field.required,
            error = errors[field.key],
            allowCustom = true,
            placeholder = "Search or type vendor…",
        )
        SimpleFieldType.SELECT -> {
            val pairs = field.optionPairs.ifEmpty {
                field.options.map { it to it.replaceFirstChar { c -> c.uppercaseChar() } }
            }
            if (pairs.size <= SEGMENTED_THRESHOLD) {
                BizChipSelector(field.label, state[field.key].orEmpty(), pairs) { set(field.key, it) }
            } else {
                BizSearchableSelectField(
                    label = field.label,
                    value = state[field.key].orEmpty(),
                    options = pairs,
                    onChange = { set(field.key, it) },
                    required = field.required,
                    error = errors[field.key],
                )
            }
        }
        SimpleFieldType.TOGGLE -> BizToggleField(
            label = field.label,
            checked = state[field.key] == "true",
            onChange = { set(field.key, if (it) "true" else "false") },
        )
        SimpleFieldType.ATTACHMENT -> BizAttachmentField(
            label = field.label,
            value = state[field.key].orEmpty(),
            onChange = { set(field.key, it) },
            error = errors[field.key],
        )
    }
}

private fun validateFields(fields: List<SimpleField>, state: Map<String, String>): Map<String, String> {
    val errs = linkedMapOf<String, String>()
    fields.filter { it.required && isFieldVisible(it, state) && state[it.key].isNullOrBlank() }
        .forEach { errs[it.key] = "${it.label} is required" }
    fields.filter { it.type == SimpleFieldType.AMOUNT && isFieldVisible(it, state) }.forEach { f ->
        if (!f.required && state[f.key].isNullOrBlank()) return@forEach
        val v = state[f.key].orEmpty()
        if (v.isBlank() && f.required) {
            errs[f.key] = "Enter a valid amount greater than 0"
            return@forEach
        }
        if (v.isBlank()) return@forEach
        val n = v.toDoubleOrNull()
        if (n == null || (f.key == "amount_minor" && n <= 0)) {
            errs[f.key] = "Enter a valid amount greater than 0"
        }
        if (f.key == "amount_paid_minor") {
            val total = state["amount_minor"].orEmpty().toDoubleOrNull() ?: 0.0
            if (n != null && n > total) errs[f.key] = "Amount paid cannot exceed spend amount"
        }
    }
    return errs
}

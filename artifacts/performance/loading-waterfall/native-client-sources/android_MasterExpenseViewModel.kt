package com.example.momentra.ui.personal.master_expense

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.momentra.data.models.PersonalMasterExpenseContextRequestDto
import com.example.momentra.data.models.PersonalMasterExpenseExperienceRequestDto
import com.example.momentra.data.models.PersonalMasterExpenseOptionsDto
import com.example.momentra.data.models.PersonalMasterExpenseRequestDto
import com.example.momentra.data.models.PersonalMasterExpenseSharedRequestDto
import com.example.momentra.data.models.PersonalMasterExpenseTransactionRequestDto
import com.example.momentra.data.models.PersonalQuickAddCategoryDto
import com.example.momentra.data.repository.PersonalSessionHolder
import com.example.momentra.ui.personal.quickadd.PersonalLoadState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import java.util.UUID

data class MasterExpenseFormState(
    val title: String = "",
    val amountMinor: Long = 0,
    val currencyCode: String = "INR",
    val accountId: String = "",
    val categoryCode: String = "",
    val subcategoryCode: String = "",
    val occurredAt: String = defaultOccurredAt(),
    val feeling: String = "",
    val meaningfulness: String = "",
    val memorability: String = "",
    val sharedEnabled: Boolean = true,
    val sharedWith: Set<String> = emptySet(),
    val relationshipImpact: Set<String> = emptySet(),
    val contextReason: String = "",
    val notes: String = "",
    val moreDetailsExpanded: Boolean = false,
)

fun MasterExpenseFormState.isDirty(): Boolean =
    title.isNotBlank() ||
        amountMinor > 0 ||
        subcategoryCode.isNotBlank() ||
        feeling.isNotBlank() ||
        meaningfulness.isNotBlank() ||
        memorability.isNotBlank() ||
        sharedWith.isNotEmpty() ||
        relationshipImpact.isNotEmpty() ||
        contextReason.isNotBlank() ||
        notes.isNotBlank()

fun resolveSubcategoryForCategory(
    categories: List<PersonalQuickAddCategoryDto>,
    categoryCode: String,
    currentSubcategory: String,
): String {
    if (categoryCode.isBlank() || currentSubcategory.isBlank()) return ""
    val children = categories.firstOrNull { it.categoryId == categoryCode }?.children.orEmpty()
    return if (children.any { it.categoryId == currentSubcategory }) currentSubcategory else ""
}

class MasterExpenseViewModel : ViewModel() {
    private val _options = MutableStateFlow<PersonalLoadState<PersonalMasterExpenseOptionsDto>>(PersonalLoadState.Idle)
    val options: StateFlow<PersonalLoadState<PersonalMasterExpenseOptionsDto>> = _options.asStateFlow()

    private val _form = MutableStateFlow(MasterExpenseFormState())
    val form: StateFlow<MasterExpenseFormState> = _form.asStateFlow()

    private val _saving = MutableStateFlow(false)
    val saving: StateFlow<Boolean> = _saving.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()

    private var activeSaveRequestId: String? = null

    fun loadOptions() {
        viewModelScope.launch {
            val peek = PersonalSessionHolder.repository.peekMasterExpenseOptions()
            if (peek != null) {
                val resolved = peek.withDefaults()
                _options.value = PersonalLoadState.Loaded(resolved)
                _form.update { current ->
                    current.copy(
                        accountId = current.accountId.ifEmpty { resolved.accounts.firstOrNull()?.accountId.orEmpty() },
                        currencyCode = resolved.accounts.firstOrNull()?.currencyCode ?: current.currencyCode,
                    )
                }
            } else {
                _options.value = PersonalLoadState.Loading
            }
            runCatching { PersonalSessionHolder.repository.getMasterExpenseOptions() }
                .onSuccess { data ->
                    val resolved = data.withDefaults()
                    _options.value = PersonalLoadState.Loaded(resolved)
                    _form.update { current ->
                        current.copy(
                            accountId = current.accountId.ifEmpty { resolved.accounts.firstOrNull()?.accountId.orEmpty() },
                            // Do not auto-select category — user confirms explicitly.
                            currencyCode = resolved.accounts.firstOrNull()?.currencyCode ?: current.currencyCode,
                        )
                    }
                }
                .onFailure {
                    if (_options.value !is PersonalLoadState.Loaded) {
                        _options.value = PersonalLoadState.Error(it.message ?: "Failed to load options")
                    }
                }
        }
    }

    fun updateForm(transform: (MasterExpenseFormState) -> MasterExpenseFormState) {
        _form.update(transform)
    }

    fun selectCategory(code: String) {
        val categories = (_options.value as? PersonalLoadState.Loaded)?.data?.categories.orEmpty()
        _form.update { state ->
            state.copy(
                categoryCode = code,
                subcategoryCode = resolveSubcategoryForCategory(categories, code, state.subcategoryCode),
            )
        }
    }

    fun selectSubcategory(code: String) {
        _form.update { it.copy(subcategoryCode = code) }
    }

    fun clearAll() {
        _form.value = MasterExpenseFormState(
            accountId = _form.value.accountId,
            currencyCode = _form.value.currencyCode,
            moreDetailsExpanded = _form.value.moreDetailsExpanded,
        )
    }

    fun toggleSharedWith(value: String) {
        _form.update { state ->
            val next = state.sharedWith.toMutableSet()
            if (next.contains(value)) next.remove(value) else next.add(value)
            state.copy(sharedWith = next)
        }
    }

    fun toggleRelationshipImpact(value: String) {
        _form.update { state ->
            val next = state.relationshipImpact.toMutableSet()
            if (next.contains(value)) next.remove(value) else next.add(value)
            state.copy(relationshipImpact = next)
        }
    }

    fun canSave(optionsData: PersonalMasterExpenseOptionsDto?, form: MasterExpenseFormState): Boolean {
        if (optionsData?.lifeOperationsMomentId.isNullOrBlank()) return false
        if (optionsData.lifestyleMomentId.isNullOrBlank()) return false
        return form.title.isNotBlank() &&
            form.amountMinor > 0 &&
            form.accountId.isNotBlank() &&
            form.categoryCode.isNotBlank()
    }

    fun save(onSuccess: () -> Unit) {
        val optionsData = (_options.value as? PersonalLoadState.Loaded)?.data ?: return
        val form = _form.value
        if (!canSave(optionsData, form)) return
        if (_saving.value) return
        viewModelScope.launch {
            _saving.value = true
            _error.value = null
            val requestId = UUID.randomUUID().toString()
            activeSaveRequestId = requestId
            val category = optionsData.categories.firstOrNull { it.categoryId == form.categoryCode }
            val subcategory = resolveSubcategoryForCategory(
                optionsData.categories,
                form.categoryCode,
                form.subcategoryCode,
            )
            val amountMajor = form.amountMinor / 100.0
            val body = PersonalMasterExpenseRequestDto(
                clientRequestId = requestId,
                expense = PersonalMasterExpenseTransactionRequestDto(
                    title = form.title.trim(),
                    amount = if (amountMajor % 1.0 == 0.0) amountMajor.toLong().toString() else amountMajor.toString(),
                    accountId = form.accountId,
                    categoryName = category?.categoryName,
                    categoryId = form.categoryCode,
                    categoryCode = form.categoryCode,
                    subcategoryCode = subcategory.ifBlank { null },
                    currencyCode = form.currencyCode,
                    amountMinor = form.amountMinor,
                    description = form.title.trim(),
                    transactionDate = form.occurredAt.ifBlank { null },
                ),
                experience = PersonalMasterExpenseExperienceRequestDto(
                    feeling = form.feeling.ifBlank { null },
                    meaningfulness = form.meaningfulness.ifBlank { null },
                    memorability = form.memorability.ifBlank { null },
                ),
                sharedExperience = PersonalMasterExpenseSharedRequestDto(
                    enabled = form.sharedEnabled,
                    sharedWith = form.sharedWith.toList(),
                    relationshipImpact = form.relationshipImpact.toList(),
                ),
                context = PersonalMasterExpenseContextRequestDto(
                    reason = form.contextReason.ifBlank { null },
                ),
                notes = form.notes.trim().ifBlank { null },
            )
            runCatching {
                PersonalSessionHolder.repository.createMasterExpense(body)
            }
                .onSuccess {
                    if (activeSaveRequestId == requestId) {
                        PersonalSessionHolder.repository.invalidateAfterMasterExpense(form.sharedEnabled)
                        onSuccess()
                    }
                }
                .onFailure {
                    _error.value = it.message ?: "Failed to save expense"
                }
            if (activeSaveRequestId == requestId) {
                _saving.value = false
                activeSaveRequestId = null
            }
        }
    }
}

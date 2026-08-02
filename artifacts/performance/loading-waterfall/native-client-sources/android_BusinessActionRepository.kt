package com.example.momentra.data.repository

import com.example.momentra.data.api.ApiClient
import com.example.momentra.data.business.actioncenter.BusinessActionCatalogDto
import com.example.momentra.data.business.actioncenter.BusinessActionRendererDto
import com.example.momentra.data.cache.KeyedCachedFetcher
import kotlinx.serialization.json.JsonObject

object BusinessActionRepository {
    private val api = ApiClient.getApiService()

    private var catalogMomentKey: String = ""
    private val catalogFetcher = KeyedCachedFetcher(
        keyProvider = { catalogMomentKey },
    ) { momentId, _ ->
        api.getBusinessActionCatalog(momentId)
    }

    suspend fun getActionCatalog(momentId: String, force: Boolean = false): BusinessActionCatalogDto {
        catalogMomentKey = momentId
        val cached = if (!force) catalogFetcher.peek() else null
        if (cached != null &&
            cached.schemaVersion == BusinessActionCatalogDto.EXPECTED_SCHEMA_VERSION &&
            catalogFetcher.isFresh()
        ) {
            return cached
        }
        val data = catalogFetcher.get(force)
        if (data.schemaVersion != 0 &&
            data.schemaVersion != BusinessActionCatalogDto.EXPECTED_SCHEMA_VERSION
        ) {
            // Schema mismatch — force one more network pull without using stale shape.
            return catalogFetcher.get(force = true)
        }
        return data
    }

    fun peekActionCatalog(momentId: String): BusinessActionCatalogDto? {
        catalogMomentKey = momentId
        val peek = catalogFetcher.peek() ?: return null
        if (peek.schemaVersion != 0 &&
            peek.schemaVersion != BusinessActionCatalogDto.EXPECTED_SCHEMA_VERSION
        ) {
            return null
        }
        return peek
    }

    fun invalidateActionCatalog() {
        catalogFetcher.invalidateAll()
    }

    suspend fun getActionRenderer(momentId: String, actionKey: String): BusinessActionRendererDto =
        api.getBusinessActionRenderer(momentId, actionKey)

    suspend fun postActivity(momentId: String, body: JsonObject): JsonObject =
        api.postBusinessActivity(momentId, body)

    suspend fun patchActivity(momentId: String, eventId: String, body: JsonObject): JsonObject =
        api.patchBusinessActivity(momentId, eventId, body)

    suspend fun deleteActivity(momentId: String, eventId: String): JsonObject =
        api.deleteBusinessActivity(momentId, eventId)

    suspend fun getNotifications(momentId: String): JsonObject =
        api.getBusinessNotifications(momentId)

    suspend fun getAttachmentUploadUrl(momentId: String, body: JsonObject): JsonObject =
        api.getBusinessAttachmentUploadUrl(momentId, body)

    suspend fun confirmAttachment(momentId: String, body: JsonObject): JsonObject =
        api.confirmBusinessAttachment(momentId, body)
}

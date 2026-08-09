package com.example.momentra.data.stream

import android.util.Log
import com.example.momentra.data.api.ApiClient
import com.example.momentra.ui.group.shared.isGroupMomentAccessDeniedStatus
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.Call
import okhttp3.Request
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.nio.charset.StandardCharsets
import kotlin.math.min

/**
 * Thin OkHttp SSE reader for `GET api/v1/group/moments/{id}/stream`.
 * Auth via Authorization Bearer (ApiClient SSE client).
 * Reconnects with exponential backoff; stops permanently on 401/403/404.
 */
object TripMomentSseClient {
    private const val TAG = "TripMomentSse"
    private const val MAX_BACKOFF_MS = 30_000L

    fun start(
        scope: CoroutineScope,
        momentId: String,
        onInvalidate: () -> Unit,
        onTerminalFailure: ((String, Int) -> Unit)? = null,
    ): Job {
        var activeCall: Call? = null
        val job = scope.launch(Dispatchers.IO) {
            var backoffMs = 1_000L
            while (isActive) {
                try {
                    val base = ApiClient.getBaseUrl().trimEnd('/')
                    val url = "$base/api/v1/group/moments/$momentId/stream"
                    val request = Request.Builder()
                        .url(url)
                        .header("Accept", "text/event-stream")
                        .get()
                        .build()
                    val call = ApiClient.getSseOkHttpClient().newCall(request)
                    activeCall = call
                    call.execute().use { response ->
                        if (isGroupMomentAccessDeniedStatus(response.code)) {
                            Log.w(TAG, "SSE terminal HTTP ${response.code} for $momentId")
                            withContext(Dispatchers.Main) {
                                onTerminalFailure?.invoke(momentId, response.code)
                            }
                            return@launch
                        }
                        if (!response.isSuccessful) {
                            Log.w(TAG, "SSE HTTP ${response.code} for $momentId")
                            delay(backoffMs)
                            backoffMs = min(backoffMs * 2, MAX_BACKOFF_MS)
                            return@use
                        }
                        val body = response.body ?: return@use
                        backoffMs = 1_000L
                        BufferedReader(
                            InputStreamReader(body.byteStream(), StandardCharsets.UTF_8),
                        ).use { reader ->
                            var eventName = "message"
                            val dataLines = mutableListOf<String>()
                            while (isActive) {
                                ensureActive()
                                val line = reader.readLine() ?: break
                                when {
                                    line.startsWith(":") -> Unit // heartbeat comment
                                    line.startsWith("event:") -> {
                                        eventName = line.removePrefix("event:").trim()
                                    }
                                    line.startsWith("data:") -> {
                                        dataLines += line.removePrefix("data:").removePrefix(" ")
                                    }
                                    line.isEmpty() -> {
                                        if (eventName == "invalidate" && dataLines.isNotEmpty()) {
                                            try {
                                                JSONObject(dataLines.joinToString("\n"))
                                                withContext(Dispatchers.Main) {
                                                    onInvalidate()
                                                }
                                            } catch (e: Exception) {
                                                Log.w(TAG, "Bad invalidate payload", e)
                                            }
                                        }
                                        eventName = "message"
                                        dataLines.clear()
                                    }
                                }
                            }
                        }
                    }
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    if (!isActive) break
                    Log.w(TAG, "SSE stream failed for $momentId; retry in ${backoffMs}ms", e)
                    delay(backoffMs)
                    backoffMs = min(backoffMs * 2, MAX_BACKOFF_MS)
                } finally {
                    activeCall = null
                }
            }
        }
        job.invokeOnCompletion {
            activeCall?.cancel()
        }
        return job
    }
}

package com.example.momentra.ui.group.pulse.purchase

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.TrendingUp
import androidx.compose.material.icons.filled.*
import androidx.compose.material.icons.outlined.ShoppingBag
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.momentra.data.models.ParticipationBreakdownDto
import com.example.momentra.data.models.PulseDashboardRecentItemDto
import com.example.momentra.data.models.PulseInsightDto
import com.example.momentra.data.models.PulseNextBestActionDto
import com.example.momentra.data.models.PurchasePulseAttentionItemDto
import com.example.momentra.data.models.PurchasePulseResponseDto
import com.example.momentra.monetisation.model.RecommendationPlacementId
import com.example.momentra.monetisation.ui.RecommendationSlot
import com.example.momentra.ui.group.actioncenter.AttentionActionMapper
import com.example.momentra.ui.group.settlement.GroupSettlementCard
import com.example.momentra.ui.group.shared.GroupAtmosphericOrbs
import com.example.momentra.ui.group.shared.GroupExplainerEyebrow
import com.example.momentra.ui.group.shared.GroupGlassCard
import com.example.momentra.ui.group.shared.GroupTabLoadingSkeleton
import com.example.momentra.ui.group.shared.GroupWidgetInfoButton
import com.example.momentra.ui.group.shared.TripStitchTypography
import com.example.momentra.ui.group.shared.rememberPurchaseStitchPalette

@Composable
fun PurchasePulseScreen(
    modifier: Modifier = Modifier,
    momentId: String? = null,
    reloadKey: Int = 0,
    onQuickAdd: ((String?) -> Unit)? = null,
    onViewAllActivity: (() -> Unit)? = null,
    onOpenSettlement: (() -> Unit)? = null,
    viewModel: PurchasePulseViewModel = viewModel(),
) {
    val palette = rememberPurchaseStitchPalette()
    val state by viewModel.state.collectAsState()

    LaunchedEffect(momentId) {
        if (!momentId.isNullOrBlank()) viewModel.load(momentId)
    }

    LaunchedEffect(reloadKey) {
        if (reloadKey > 0 && !momentId.isNullOrBlank()) viewModel.load(momentId, force = false)
    }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(palette.background),
    ) {
        GroupAtmosphericOrbs()

        if (state is PurchasePulseUiState.Error) {
            val message = (state as PurchasePulseUiState.Error).message
            Column(
                Modifier.fillMaxSize().padding(24.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Text(message, color = palette.onSurfaceVariant)
                Spacer(Modifier.height(12.dp))
                Button(onClick = { momentId?.let { viewModel.load(it, force = true) } }) {
                    Text("Retry")
                }
            }
        }

        if (state is PurchasePulseUiState.Loading) {
            GroupTabLoadingSkeleton()
        }

        val pulse = (state as? PurchasePulseUiState.Loaded)?.data

        AnimatedVisibility(
            visible = pulse != null,
            enter = fadeIn(tween(600)) + slideInVertically(initialOffsetY = { 40 }, animationSpec = tween(600)),
            modifier = Modifier.fillMaxSize(),
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp),
            ) {
                SummaryCard(palette, pulse)
                RecommendationSlot(
                    placement = RecommendationPlacementId.GROUP_PULSE_AFTER_SUMMARY,
                    meaningfulContentLoaded = pulse != null,
                    contentCount = if (pulse != null) 2 else 0,
                )
                HealthSection(palette, pulse)
                AttentionSection(
                    palette = palette,
                    items = pulse?.attentionItems.orEmpty(),
                    onViewAllActivity = onViewAllActivity,
                    onQuickAdd = onQuickAdd,
                )
                FundingSection(palette, pulse)
                ParticipationSection(palette, pulse)
                GroupSettlementCard(
                    palette = palette,
                    widget = pulse?.settlementWidget,
                    onViewDetails = onOpenSettlement,
                    currencyCode = pulse?.currencyCode ?: "INR",
                )
                RecentActivitySection(palette, pulse?.dashboardCard?.recentItems.orEmpty())
                NextActionCard(
                    palette = palette,
                    action = pulse?.nextBestAction,
                    onViewAllActivity = onViewAllActivity,
                    onQuickAdd = onQuickAdd,
                )
                InsightsSection(palette, pulse?.insights.orEmpty())
                if (onQuickAdd != null) {
                    Button(
                        onClick = { onQuickAdd(null) },
                        modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = palette.primary),
                    ) {
                        Text("Quick Add", color = palette.onPrimary)
                    }
                }
                Spacer(Modifier.height(100.dp))
            }
        }
    }
}

@Composable
private fun SummaryCard(
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    pulse: PurchasePulseResponseDto?,
) {
    val name = pulse?.momentName?.takeIf { it.isNotBlank() } ?: "Purchase"
    val contributors = (pulse?.contributorCount ?: pulse?.stats?.contributorsJoined ?: 0).toString()
    val currency = pulse?.currencyCode
    val target = pulse?.targetAmountMinor?.let { formatMinor(it, currency) } ?: "—"
    val collected = pulse?.fundedAmountMinor?.let { formatMinor(it, currency) } ?: "—"
    val remaining = pulse?.amountRemainingMinor?.let { formatMinor(it, currency) }
        ?: pulse?.let {
            val t = it.targetAmountMinor ?: return@let "—"
            formatMinor((t - it.fundedAmountMinor).coerceAtLeast(0), currency)
        }
        ?: "—"

    GroupGlassCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                Box(
                    modifier = Modifier.size(40.dp).clip(CircleShape).background(palette.primary.copy(alpha = 0.1f)),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(Icons.Outlined.ShoppingBag, contentDescription = null, tint = palette.primary, modifier = Modifier.size(24.dp))
                }
                Column {
                    Text(
                        "SHARED PURCHASE",
                        style = TripStitchTypography.eyebrow,
                        color = palette.primary,
                    )
                    Text(name, style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold), color = palette.onSurface)
                }
            }
            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                verticalArrangement = Arrangement.spacedBy(12.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier.height(180.dp),
                userScrollEnabled = false,
            ) {
                item { StatItem("Contributors", contributors, palette) }
                item { StatItem("Target", target, palette) }
                item { StatItem("Collected", collected, palette, highlight = true) }
                item { StatItem("Remaining", remaining, palette) }
            }
        }
    }
}

@Composable
private fun StatItem(
    label: String,
    value: String,
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    highlight: Boolean = false,
) {
    Column(modifier = Modifier.background(palette.surfaceContainerHigh, RoundedCornerShape(12.dp)).padding(12.dp)) {
        Text(label.uppercase(), style = TripStitchTypography.eyebrow, color = palette.onSurfaceVariant)
        Text(
            value,
            style = TripStitchTypography.statValue,
            color = if (highlight) palette.primary else palette.onSurface,
        )
    }
}

@Composable
private fun HealthSection(
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    pulse: PurchasePulseResponseDto?,
) {
    val healthPct = ((pulse?.experienceHealthPercent ?: pulse?.readinessScore ?: 0.0) / 100.0).toFloat().coerceIn(0f, 1f)
    val healthLabel = "${((pulse?.experienceHealthPercent ?: pulse?.readinessScore ?: 0.0).toInt())}%"
    GroupGlassCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Row(modifier = Modifier.fillMaxWidth()) {
                GroupExplainerEyebrow(
                    text = "PURCHASE HEALTH",
                    palette = palette,
                    explainerId = "PULSE-001",
                    momentTypeCode = "SHARED_PURCHASE",
                )
            }
            Box(modifier = Modifier.size(140.dp), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(progress = { 1f }, modifier = Modifier.fillMaxSize(), color = palette.surfaceContainerHigh, strokeWidth = 10.dp, trackColor = Color.Transparent)
                CircularProgressIndicator(progress = { healthPct }, modifier = Modifier.fillMaxSize(), color = palette.primary, strokeWidth = 10.dp, trackColor = Color.Transparent)
                Column(horizontalAlignment = Alignment.CenterHorizontally) {
                    Text(healthLabel, style = MaterialTheme.typography.headlineMedium.copy(fontWeight = FontWeight.Bold), color = palette.onSurface)
                    Text(pulse?.readinessTitle ?: "Getting started", style = MaterialTheme.typography.labelSmall, color = palette.onSurfaceVariant)
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp, Alignment.CenterHorizontally)) {
                pulse?.healthDimensions.orEmpty().forEach { dim ->
                    Box(modifier = Modifier.background(palette.surfaceContainerHigh, CircleShape).padding(horizontal = 10.dp, vertical = 6.dp)) {
                        Text(
                            "${dim.label} ${dim.status ?: ""}".uppercase().trim(),
                            style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp, fontWeight = FontWeight.Bold),
                            color = palette.onSurfaceVariant,
                        )
                    }
                }
            }
        }
    }
}

private fun attentionSignalClick(
    action: String?,
    momentTypeCode: String,
    onViewAllActivity: (() -> Unit)?,
    onQuickAdd: ((String?) -> Unit)?,
): (() -> Unit)? {
    if (AttentionActionMapper.opensActivity(action)) {
        return onViewAllActivity ?: onQuickAdd?.let { { it.invoke(null) } }
    }
    if (onQuickAdd == null) return onViewAllActivity
    val actionId = AttentionActionMapper.mapToQuickAddId(action, momentTypeCode)
    return { onQuickAdd(actionId) }
}

@Composable
private fun AttentionSection(
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    items: List<PurchasePulseAttentionItemDto>,
    onViewAllActivity: (() -> Unit)? = null,
    onQuickAdd: ((String?) -> Unit)? = null,
) {
    if (items.isEmpty()) return
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Icon(Icons.Default.Warning, contentDescription = null, tint = palette.error, modifier = Modifier.size(18.dp))
            Text("ATTENTION SIGNALS", style = TripStitchTypography.eyebrow, color = palette.onSurfaceVariant)
            GroupWidgetInfoButton(
                explainerId = "PULSE-006",
                momentTypeCode = "SHARED_PURCHASE",
                palette = palette,
            )
        }
        items.forEach { item ->
            val color = when (item.accent.lowercase()) {
                "error" -> palette.error
                "tertiary" -> palette.tertiary
                else -> palette.primary
            }
            val onClick = attentionSignalClick(item.action, "SHARED_PURCHASE", onViewAllActivity, onQuickAdd)
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .background(color.copy(alpha = 0.08f), RoundedCornerShape(12.dp))
                    .border(1.dp, color.copy(alpha = 0.1f), RoundedCornerShape(12.dp))
                    .clickable(enabled = onClick != null) { onClick?.invoke() }
                    .padding(14.dp),
            ) {
                Icon(Icons.Default.Warning, contentDescription = null, tint = color, modifier = Modifier.size(20.dp))
                Text(item.title, style = MaterialTheme.typography.bodyMedium, color = palette.onSurface, modifier = Modifier.weight(1f))
                Icon(Icons.Default.ChevronRight, contentDescription = null, tint = palette.onSurfaceVariant, modifier = Modifier.size(18.dp))
            }
        }
    }
}

@Composable
private fun FundingSection(
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    pulse: PurchasePulseResponseDto?,
) {
    val score = pulse?.fundingPercent ?: pulse?.readinessScore ?: 0.0
    GroupGlassCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            GroupExplainerEyebrow(
                text = "FUNDING PROGRESS",
                palette = palette,
                explainerId = "PULSE-004",
                momentTypeCode = "SHARED_PURCHASE",
            )
            Text("${score.toInt()}%", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold), color = palette.onSurface)
            LinearProgressIndicator(
                progress = { (score / 100f).toFloat().coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth().height(6.dp),
                color = palette.primary,
                trackColor = palette.surfaceContainerHigh,
            )
            Text(pulse?.readinessNarrative ?: "Funding in progress", style = MaterialTheme.typography.labelSmall, color = palette.onSurfaceVariant)
        }
    }
}

@Composable
private fun ParticipationSection(
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    pulse: PurchasePulseResponseDto?,
) {
    val breakdown = pulse?.participationBreakdown ?: ParticipationBreakdownDto()
    val percent = pulse?.participationPercent ?: 0.0
    GroupGlassCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            GroupExplainerEyebrow(
                text = "PARTICIPATION",
                palette = palette,
                explainerId = "PULSE-005",
                momentTypeCode = "SHARED_PURCHASE",
            )
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("${percent.toInt()}%", style = MaterialTheme.typography.headlineSmall.copy(fontWeight = FontWeight.Bold), color = palette.onSurface)
                if (pulse?.avatars?.isNotEmpty() == true) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .clip(CircleShape)
                            .background(palette.surfaceContainerHigh)
                            .border(2.dp, palette.background, CircleShape),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text("+${pulse.avatars.size}", style = MaterialTheme.typography.labelSmall.copy(fontWeight = FontWeight.Bold), color = palette.onSurfaceVariant)
                    }
                }
            }
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                ParticipationCount("Active", breakdown.active.toString(), palette)
                ParticipationCount("Pending", breakdown.pending.toString(), palette)
                ParticipationCount("Inactive", breakdown.inactive.toString(), palette)
            }
        }
    }
}

@Composable
private fun ParticipationCount(label: String, value: String, palette: com.example.momentra.ui.group.shared.GroupPalette) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label.uppercase(), style = MaterialTheme.typography.labelSmall, color = palette.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Bold), color = palette.onSurface)
    }
}

@Composable
private fun RecentActivitySection(
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    items: List<PulseDashboardRecentItemDto>,
) {
    if (items.isEmpty()) return
    GroupGlassCard(modifier = Modifier.fillMaxWidth()) {
        Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
            GroupExplainerEyebrow(
                text = "RECENT ACTIVITY",
                palette = palette,
                explainerId = "PULSE-007",
                momentTypeCode = "SHARED_PURCHASE",
            )
            items.take(5).forEach { item ->
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    Box(modifier = Modifier.size(36.dp).clip(CircleShape).background(palette.surfaceContainerHigh), contentAlignment = Alignment.Center) {
                        Icon(Icons.Default.History, contentDescription = null, tint = palette.primary, modifier = Modifier.size(18.dp))
                    }
                    Column(modifier = Modifier.weight(1f)) {
                        Text(item.title, style = MaterialTheme.typography.bodySmall, color = palette.onSurface)
                        Text(item.relativeTime, style = MaterialTheme.typography.labelSmall.copy(fontSize = 9.sp), color = palette.onSurfaceVariant)
                    }
                }
            }
        }
    }
}

@Composable
private fun NextActionCard(
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    action: PulseNextBestActionDto?,
    onViewAllActivity: (() -> Unit)? = null,
    onQuickAdd: ((String?) -> Unit)? = null,
) {
    if (action == null) return
    val onClick = attentionSignalClick(action.action, "SHARED_PURCHASE", onViewAllActivity, onQuickAdd)
    GroupGlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(enabled = onClick != null) { onClick?.invoke() },
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Icon(Icons.Default.Bolt, contentDescription = null, tint = palette.primary, modifier = Modifier.size(16.dp))
                GroupExplainerEyebrow(
                    text = "NEXT BEST ACTION",
                    palette = palette,
                    explainerId = "PULSE-008",
                    momentTypeCode = "SHARED_PURCHASE",
                )
            }
            Text(action.title, style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold), color = palette.onSurface)
            if (action.subtitle.isNotBlank()) {
                Text(action.subtitle, style = MaterialTheme.typography.bodySmall, color = palette.onSurfaceVariant)
            }
        }
    }
}

@Composable
private fun InsightsSection(
    palette: com.example.momentra.ui.group.shared.GroupPalette,
    insights: List<PulseInsightDto>,
) {
    if (insights.isEmpty()) return
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        GroupExplainerEyebrow(
            text = "AI Insights",
            palette = palette,
            explainerId = "PULSE-009",
            momentTypeCode = "SHARED_PURCHASE",
        )
        insights.forEach { insight ->
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .background(palette.surfaceContainer, RoundedCornerShape(16.dp))
                    .border(1.dp, palette.primary.copy(alpha = 0.1f), RoundedCornerShape(16.dp))
                    .padding(16.dp),
            ) {
                Icon(Icons.Default.AutoAwesome, contentDescription = null, tint = palette.primary, modifier = Modifier.size(20.dp))
                Text(insight.title, style = MaterialTheme.typography.bodySmall, color = palette.onSurface)
            }
        }
    }
}

private fun formatMinor(minor: Int, currencyCode: String? = null): String =
    com.example.momentra.data.money.AppMoneyDisplay.formatMinor(minor, currencyCode)

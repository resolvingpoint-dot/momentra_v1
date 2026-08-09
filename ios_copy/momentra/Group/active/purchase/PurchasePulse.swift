import SwiftUI
import Combine

struct PurchasePulse: View {
    var reloadKey: Int = 0
    var onQuickAdd: ((String?) -> Void)? = nil
    var onOpenSettlement: (() -> Void)? = nil
    @ObservedObject private var session = GroupSessionManager.shared
    @State private var pulse: PurchasePulseResponse?
    @State private var isRefreshing = false

    private var resolvedMomentId: String? { session.activeMomentId }
    private var isLoading: Bool { pulse == nil }

    var body: some View {
        ScrollView(.vertical, showsIndicators: false) {
            VStack(spacing: GroupTheme.spacingSectionGap) {
                if isLoading {
                    pulseSkeleton
                } else {
                    pulseContent
                }
            }
            .padding(.horizontal, GroupTheme.screenHorizontal)
            .padding(.bottom, GroupSpacing.card)
        }
        .background(GroupTheme.background)
        .refreshable { await loadPulse(force: true) }
        .task(id: resolvedMomentId) { await loadPulse(force: false) }
        .onChange(of: reloadKey) { _, _ in
            Task { await loadPulse(force: false) }
        }
        .animation(.easeOut(duration: 0.35), value: pulse?.momentId)
    }

    private var pulseSkeleton: some View {
        VStack(spacing: GroupTheme.spacingSectionGap) {
            GroupSkeletonBox(height: 180, radius: GroupRadius.large)
            GroupSkeletonBox(height: 160, radius: GroupRadius.large)
            GroupSkeletonBox(height: 200, radius: GroupRadius.large)
            GroupSkeletonBox(height: 140, radius: GroupRadius.large)
        }
    }

    private var pulseContent: some View {
        VStack(spacing: GroupTheme.spacingSectionGap) {
            headerSection.groupStaggeredCardEnter(index: 0)
            RecommendationSlot(
                placement: .groupPulseAfterSummary,
                contentCount: 3
            )
            .groupStaggeredCardEnter(index: 1)
            healthSection.groupStaggeredCardEnter(index: 2)
            attentionSection.groupStaggeredCardEnter(index: 3)
            fundingSection.groupStaggeredCardEnter(index: 4)
            participationSection.groupStaggeredCardEnter(index: 5)
            settlementSection.groupStaggeredCardEnter(index: 6)
            recentActivitySection.groupStaggeredCardEnter(index: 7)
            GroupCta(
                eyebrow: "Next Best Action",
                title: pulse?.nextBestAction?.title.nilIfBlank
                    ?? pulse?.readinessTitle.nilIfBlank
                    ?? "Keep funding moving",
                subtitle: pulse?.nextBestAction?.subtitle.nilIfBlank
                    ?? pulse?.readinessNarrative.nilIfBlank,
                impacts: ["Funding", "Progress", "Participation"],
                action: { handleNextBestAction() }
            )
            .overlay(alignment: .topTrailing) {
                GroupWidgetInfoButton(explainerId: "PULSE-008", momentTypeCode: "SHARED_PURCHASE")
                    .padding(GroupSpacing.inner)
            }
            .groupStaggeredCardEnter(index: 8)
            insightsSection.groupStaggeredCardEnter(index: 9)
        }
    }

    private func loadPulse(force: Bool = false) async {
        guard let momentId = resolvedMomentId else { return }
        let cacheKey = "group_purchase_pulse:\(momentId)"
        if pulse == nil, let cached = DiskCacheStore.loadCodable(PurchasePulseResponse.self, key: cacheKey) {
            pulse = cached
        }
        isRefreshing = pulse != nil
        defer { isRefreshing = false }
        _ = force
        if let loaded = try? await APIClient.shared.fetchPurchasePulse(momentId: momentId) {
            pulse = loaded
            DiskCacheStore.saveCodable(loaded, key: cacheKey)
        }
    }

    private var headerSection: some View {
        GroupGlassCard(accentLeft: true, glow: true) {
            VStack(alignment: .leading, spacing: GroupSpacing.stack) {
                HStack(spacing: GroupSpacing.sm) {
                    Image(systemName: "cart.fill")
                        .foregroundStyle(GroupTheme.primary)
                    Text(pulse?.momentName.nilIfBlank ?? "Purchase Pulse")
                        .font(GroupTypography.heading())
                        .foregroundStyle(GroupTheme.onSurface)
                }
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: GroupSpacing.stack) {
                    GroupMetricTile(
                        label: "Contributors",
                        value: "\(max(pulse?.contributorCount ?? 0, pulse?.stats.contributorsJoined ?? 0))"
                    )
                    GroupMetricTile(label: "Target", value: moneyLabel(pulse?.targetAmountMinor ?? 0))
                    GroupMetricTile(label: "Collected", value: moneyLabel(pulse?.fundedAmountMinor ?? 0), valueColor: GroupTheme.primary)
                    GroupMetricTile(label: "Remaining", value: moneyLabel(pulse?.amountRemainingMinor ?? 0))
                }
            }
        }
    }

    private var healthSection: some View {
        let health = Int(pulse?.experienceHealthPercent ?? pulse?.readinessScore ?? 0)
        return GroupGlassCard {
            VStack(spacing: GroupSpacing.inner) {
                GroupSectionHeader(
                    title: "Purchase Health",
                    explainerId: "PULSE-001",
                    momentTypeCode: "SHARED_PURCHASE"
                )
                GroupHealthRing(value: health, label: pulse?.readinessTitle ?? "Getting started")
                if let dims = pulse?.healthDimensions, !dims.isEmpty {
                    GroupChipRow(chips: dims.map { "\($0.label) \($0.status ?? "\(Int($0.percent))%")" })
                }
            }
        }
    }

    @ViewBuilder
    private var attentionSection: some View {
        let items = pulse?.attentionItems ?? []
        if !items.isEmpty {
            VStack(alignment: .leading, spacing: GroupSpacing.inner) {
                GroupSectionHeader(
                    title: "Attention Signals",
                    icon: "exclamationmark.triangle.fill",
                    explainerId: "PULSE-006",
                    momentTypeCode: "SHARED_PURCHASE"
                )
                ForEach(items) { item in
                    let color: Color = {
                        switch (item.accent ?? "").lowercased() {
                        case "error": return GroupTheme.error
                        case "tertiary": return GroupTheme.tertiary
                        default: return GroupTheme.primary
                        }
                    }()
                    Button(action: {
                        let actionId = AttentionActionMapper.mapToQuickAddId(
                            action: item.action,
                            momentTypeCode: "SHARED_PURCHASE"
                        )
                        onQuickAdd?(actionId)
                    }) {
                        HStack(spacing: GroupSpacing.inner) {
                            Image(systemName: "exclamationmark.circle.fill")
                                .foregroundStyle(color)
                            Text(item.title)
                                .font(GroupTypography.body())
                                .foregroundStyle(GroupTheme.onSurface)
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundStyle(GroupTheme.onSurfaceVariant)
                        }
                        .padding(14)
                        .background(color.opacity(0.08))
                        .clipShape(RoundedRectangle(cornerRadius: GroupRadius.medium, style: .continuous))
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private func handleNextBestAction() {
        let action = pulse?.nextBestAction?.action
        if AttentionActionMapper.opensActivity(action) {
            onQuickAdd?(nil)
            return
        }
        let actionId = AttentionActionMapper.mapToQuickAddId(action: action, momentTypeCode: "SHARED_PURCHASE")
            ?? "CONTRIBUTOR"
        onQuickAdd?(actionId)
    }

    private var fundingSection: some View {
        let ratio = min(max((pulse?.fundingPercent ?? 0) / 100, 0), 1)
        return GroupGlassCard {
            VStack(alignment: .leading, spacing: GroupSpacing.inner) {
                GroupSectionHeader(
                    title: "Funding Progress",
                    icon: "chart.pie.fill",
                    explainerId: "PULSE-004",
                    momentTypeCode: "SHARED_PURCHASE"
                )
                HStack {
                    Text(moneyLabel(pulse?.fundedAmountMinor ?? 0))
                        .font(GroupTypography.body())
                        .foregroundStyle(GroupTheme.onSurface)
                    Spacer()
                    Text("\(Int(pulse?.fundingPercent ?? 0))%")
                        .font(GroupTypography.body())
                        .foregroundStyle(GroupTheme.onSurfaceVariant)
                }
                GeometryReader { geo in
                    ZStack(alignment: .leading) {
                        Capsule().fill(GroupTheme.surfaceContainerHigh).frame(height: 10)
                        Capsule()
                            .fill(LinearGradient(colors: [GroupTheme.primaryContainer, GroupTheme.primary], startPoint: .leading, endPoint: .trailing))
                            .frame(width: geo.size.width * ratio, height: 10)
                    }
                }
                .frame(height: 10)
                if let narrative = pulse?.readinessNarrative.nilIfBlank {
                    Text(narrative)
                        .font(GroupTypography.caption())
                        .foregroundStyle(GroupTheme.onSurfaceVariant)
                }
            }
        }
    }

    private var participationSection: some View {
        let breakdown = pulse?.participationBreakdown
        return GroupGlassCard {
            VStack(alignment: .leading, spacing: GroupSpacing.inner) {
                Text("PARTICIPATION")
                    .font(GroupTypography.label(size: 11))
                    .foregroundStyle(GroupTheme.onSurfaceVariant)
                Text("\(Int(pulse?.participationPercent ?? 0))%")
                    .font(GroupTypography.data())
                    .foregroundStyle(GroupTheme.primary)
                HStack {
                    participationStat("Active", "\(breakdown?.active ?? 0)")
                    participationStat("Pending", "\(breakdown?.pending ?? 0)")
                    participationStat("Inactive", "\(breakdown?.inactive ?? 0)")
                }
            }
        }
    }

    private func participationStat(_ label: String, _ value: String) -> some View {
        VStack {
            Text(label.uppercased())
                .font(GroupTypography.label(size: 9, weight: .medium))
                .foregroundStyle(GroupTheme.onSurfaceVariant)
            Text(value)
                .font(GroupTypography.subhead())
                .foregroundStyle(GroupTheme.onSurface)
        }
        .frame(maxWidth: .infinity)
    }

    // MARK: - Group Settlement

    private var settlementWidgetOrPlaceholder: TripSettlementWidget {
        pulse?.settlementWidget
            ?? .placeholder(currencyCode: pulse?.currencyCode ?? "INR")
    }

    @ViewBuilder
    private var settlementSection: some View {
        let widget = settlementWidgetOrPlaceholder
        GroupGlassCard {
            VStack(alignment: .leading, spacing: GroupSpacing.stack) {
                GroupSectionHeader(
                    title: "Group Settlement",
                    action: "View Details",
                    onAction: onOpenSettlement
                )
                LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: GroupSpacing.inner) {
                    settlementMetric(
                        label: "Total Paid",
                        value: AppMoneyDisplay.formatMinor(
                            widget.totalPaidMinor,
                            currencyCode: widget.currencyCode
                        ),
                        valueColor: GroupTheme.onSurface
                    )
                    settlementMetric(
                        label: "Pending Settlement",
                        value: AppMoneyDisplay.formatMinor(
                            widget.pendingSettlementMinor,
                            currencyCode: widget.currencyCode
                        ),
                        valueColor: GroupTheme.tertiary
                    )
                }
                Text(
                    widget.statusLine.nilIfBlank
                        ?? (widget.membersNeedingSettlement == 0
                            ? "All balances are settled."
                            : "\(widget.membersNeedingSettlement) members need settlement")
                )
                .font(GroupTypography.caption())
                .foregroundStyle(GroupTheme.onSurfaceVariant)

                ForEach(Array(widget.previewMembers.prefix(3))) { member in
                    settlementPreviewRow(member, currency: widget.currencyCode)
                }

                Button(action: { onOpenSettlement?() }) {
                    HStack {
                        Text("View Settlement")
                            .font(GroupTypography.subhead())
                        Spacer()
                        Image(systemName: "arrow.right")
                    }
                    .foregroundStyle(GroupTheme.primary)
                }
                .buttonStyle(.plain)
                .accessibilityLabel("View settlement")
                .padding(.top, GroupSpacing.xs)
            }
        }
    }

    private func settlementMetric(label: String, value: String, valueColor: Color) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(GroupTypography.label(size: 11, weight: .medium))
                .foregroundStyle(GroupTheme.onSurfaceVariant)
            Text(value)
                .font(MomentraFont.heading(size: 20))
                .foregroundStyle(valueColor)
                .lineLimit(1)
                .minimumScaleFactor(0.7)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(GroupSpacing.inner)
        .background(GroupTheme.surfaceContainerLow)
        .clipShape(RoundedRectangle(cornerRadius: GroupRadius.medium, style: .continuous))
    }

    private func settlementPreviewRow(
        _ member: TripSettlementWidgetPreviewMember,
        currency: String
    ) -> some View {
        let receives = member.status.lowercased() == "will_receive"
        let chipTone: Color = receives ? GroupTheme.primary : GroupTheme.tertiary
        let chipBackground = receives
            ? GroupTheme.primary.opacity(0.12)
            : GroupTheme.tertiary.opacity(0.18)
        let amount = AppMoneyDisplay.formatMinor(
            member.amountMinor,
            currencyCode: member.currencyCode.isEmpty ? currency : member.currencyCode
        )
        let chipText: String = {
            let label = member.chipLabel.nilIfBlank
                ?? (receives ? "Receives" : "Needs to pay")
            return "\(label) \(amount)"
        }()
        return HStack(spacing: GroupSpacing.inner) {
            UserAvatarView(photoUrl: member.photoUrl, displayName: member.displayName, size: 32)
            Text(member.displayName)
                .font(GroupTypography.body())
                .foregroundStyle(GroupTheme.onSurface)
            Spacer(minLength: 0)
            Text(chipText)
                .font(GroupTypography.label(size: 10, weight: .medium))
                .foregroundStyle(chipTone)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(chipBackground)
                .clipShape(Capsule())
        }
        .padding(GroupSpacing.inner)
        .background(GroupTheme.surfaceContainerHigh)
        .clipShape(RoundedRectangle(cornerRadius: GroupRadius.medium, style: .continuous))
        .accessibilityElement(children: .combine)
        .accessibilityLabel("\(member.displayName), \(chipText)")
    }

    @ViewBuilder
    private var recentActivitySection: some View {
        let items = pulse?.recentActivity ?? []
        if !items.isEmpty {
            GroupGlassCard {
                VStack(alignment: .leading, spacing: GroupSpacing.stack) {
                    GroupSectionHeader(
                        title: "Recent Activity",
                        action: "View All",
                        explainerId: "PULSE-007",
                        momentTypeCode: "SHARED_PURCHASE"
                    )
                    ForEach(items) { item in
                        HStack(spacing: GroupSpacing.inner) {
                            Image(systemName: "clock.fill")
                                .foregroundStyle(GroupTheme.primary)
                            VStack(alignment: .leading, spacing: 2) {
                                Text(item.title)
                                    .font(GroupTypography.body())
                                    .foregroundStyle(GroupTheme.onSurface)
                                if !item.relativeTime.isEmpty {
                                    Text(item.relativeTime)
                                        .font(GroupTypography.caption())
                                        .foregroundStyle(GroupTheme.onSurfaceVariant)
                                }
                            }
                            Spacer()
                        }
                    }
                }
            }
        }
    }

    @ViewBuilder
    private var insightsSection: some View {
        let insights = pulse?.insights ?? []
        if !insights.isEmpty {
            VStack(spacing: GroupSpacing.stack) {
                GroupSectionHeader(
                    title: "AI Insights",
                    explainerId: "PULSE-009",
                    momentTypeCode: "SHARED_PURCHASE"
                )
                ForEach(insights) { insight in
                    GroupGlassCard {
                        VStack(alignment: .leading, spacing: GroupSpacing.xs) {
                            Text(insight.title)
                                .font(GroupTypography.subhead())
                                .foregroundStyle(GroupTheme.onSurface)
                            if !insight.subtitle.isEmpty {
                                Text(insight.subtitle)
                                    .font(GroupTypography.caption())
                                    .foregroundStyle(GroupTheme.onSurfaceVariant)
                            }
                        }
                    }
                }
            }
        }
    }

    private func moneyLabel(_ minor: Int) -> String {
        AppMoneyDisplay.formatMinor(minor, currencyCode: pulse?.currencyCode)
    }
}

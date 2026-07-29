"use client";

/**
 * Presentational Team Ops Pulse widgets — no fetch / mapping / invent.
 */
import type { TeamOpsEventItem, TeamOpsPulseResponse } from "@/lib/api/businessActive";
import { TEAM_OPS } from "../shared/teamOpsTheme";
import {
  HealthBandBadge,
  TeamOpsEmptyLine,
  TeamOpsEventRows,
  TeamOpsKpiChip,
  TeamOpsSectionCard,
  TeamOpsSectionTitle,
} from "../shared/shared";

type Pulse = TeamOpsPulseResponse;

export function PulseHero({ data }: { data: Pulse }) {
  const health = data.hero.overall_team_health ?? data.kpis.overall_team_health;
  return (
    <TeamOpsSectionCard gradient>
      <div className="mb-2 flex items-start justify-between gap-3">
        <p className="text-sm font-medium" style={{ color: TEAM_OPS.onVariant }}>
          Team Health
        </p>
        <HealthBandBadge band={health?.band} label={health?.label} />
      </div>
      <h2
        className="mb-1 text-2xl font-bold tracking-tight"
        style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}
      >
        {data.hero.title}
      </h2>
      <p className="mb-3 text-sm" style={{ color: TEAM_OPS.onVariant }}>
        {data.hero.subtitle || "Team Operations"}
      </p>
      {health?.inputs ? (
        <p className="text-[10px]" style={{ color: TEAM_OPS.onVariant }}>
          Inputs: {health.inputs.members ?? 0} members · {health.inputs.open_issues ?? 0} issues ·{" "}
          {health.inputs.pending_approvals ?? 0} approvals · {health.inputs.escalations ?? 0}{" "}
          escalations
        </p>
      ) : null}
    </TeamOpsSectionCard>
  );
}

export function PulseKpis({ data }: { data: Pulse }) {
  return (
    <section>
      <TeamOpsSectionTitle>KPIs</TeamOpsSectionTitle>
      <div className="flex gap-2 overflow-x-auto pb-1">
        <TeamOpsKpiChip label="Members" value={data.kpis.members} />
        <TeamOpsKpiChip label="Open issues" value={data.kpis.open_issues} />
        <TeamOpsKpiChip label="Pending approvals" value={data.kpis.pending_approvals} />
        <TeamOpsKpiChip label="Recognition" value={data.kpis.recognitions} />
        <TeamOpsKpiChip label="Meetings" value={data.kpis.meetings} />
        <TeamOpsKpiChip label="Escalations" value={data.kpis.escalations} />
        <TeamOpsKpiChip label="Participation" value={data.kpis.participation} />
      </div>
    </section>
  );
}

export function PulseApprovals({ data }: { data: Pulse }) {
  return (
    <section>
      <TeamOpsSectionTitle>Approvals</TeamOpsSectionTitle>
      <p className="mb-2 text-xs" style={{ color: TEAM_OPS.onVariant }}>
        Pending: {data.approvals.pending_count}
      </p>
      <TeamOpsEventRows items={data.approvals.items} emptyLabel="No approval activity yet." />
    </section>
  );
}

export function PulseParticipation({ data }: { data: Pulse }) {
  return (
    <section>
      <TeamOpsSectionTitle>Participation</TeamOpsSectionTitle>
      <TeamOpsEventRows items={data.participation.items} emptyLabel="No participation logged yet." />
    </section>
  );
}

export function PulseIssues({ data }: { data: Pulse }) {
  return (
    <section>
      <TeamOpsSectionTitle>Issues</TeamOpsSectionTitle>
      <p className="mb-2 text-xs" style={{ color: TEAM_OPS.onVariant }}>
        Open {data.issues.open_count} · Escalations {data.issues.escalation_count}
      </p>
      <TeamOpsEventRows items={data.issues.items} emptyLabel="No open issues." />
    </section>
  );
}

export function PulseRecognition({ data }: { data: Pulse }) {
  return (
    <section>
      <TeamOpsSectionTitle>Recognition</TeamOpsSectionTitle>
      <TeamOpsEventRows items={data.recognition.items} emptyLabel="No recognition yet." />
    </section>
  );
}

export function PulseRecentActivity({
  data,
  onViewActivity,
  onSelectActivity,
}: {
  data: Pulse;
  onViewActivity?: () => void;
  onSelectActivity?: (item: TeamOpsEventItem) => void;
}) {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between gap-2">
        <TeamOpsSectionTitle>Recent activity</TeamOpsSectionTitle>
        {onViewActivity ? (
          <button
            type="button"
            className="text-xs font-semibold"
            style={{ color: TEAM_OPS.primaryContainer }}
            onClick={onViewActivity}
          >
            View all
          </button>
        ) : null}
      </div>
      <TeamOpsEventRows
        items={data.recent_activity.items.slice(0, 12)}
        emptyLabel="No activity yet — use Action Center to record the first update."
        onSelect={onSelectActivity}
      />
    </section>
  );
}

export function PulseAttention({ data }: { data: Pulse }) {
  return (
    <section>
      <TeamOpsSectionTitle>Attention</TeamOpsSectionTitle>
      {data.attention.items.length === 0 ? (
        <TeamOpsEmptyLine label="Nothing needs attention." />
      ) : (
        <ul className="space-y-2">
          {data.attention.items.map((a) => (
            <li
              key={a.kind}
              className="rounded-xl px-3 py-2 text-sm"
              style={{ background: TEAM_OPS.surfaceLow, color: TEAM_OPS.tertiary }}
            >
              {a.label}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function PulseSignals({ data }: { data: Pulse }) {
  return (
    <section>
      <TeamOpsSectionTitle>Signals</TeamOpsSectionTitle>
      {data.signals.items.length === 0 ? (
        <TeamOpsEmptyLine label="No signals yet." />
      ) : (
        <ul className="space-y-2">
          {data.signals.items.map((s, i) => (
            <li
              key={s.signal_id || s.signal_type || `${s.label}-${i}`}
              className="rounded-xl px-3 py-2 text-sm"
              style={{ background: TEAM_OPS.surfaceLow, color: TEAM_OPS.onSurface }}
            >
              {s.label || s.title || s.signal_type || "Signal"}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function PulseNextAction({ data, onQuickAdd }: { data: Pulse; onQuickAdd?: () => void }) {
  return (
    <TeamOpsSectionCard>
      <TeamOpsSectionTitle>Next action</TeamOpsSectionTitle>
      {data.next_action.item ? (
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold" style={{ color: TEAM_OPS.onSurface }}>
              {data.next_action.item.label}
            </p>
            <p className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
              {data.next_action.item.reason}
            </p>
          </div>
          {onQuickAdd ? (
            <button
              type="button"
              className="rounded-xl px-4 py-2 text-sm font-semibold"
              style={{ background: TEAM_OPS.primaryContainer, color: "#0d0096" }}
              onClick={onQuickAdd}
            >
              Open Action Center
            </button>
          ) : null}
        </div>
      ) : (
        <TeamOpsEmptyLine label="No recommended next step." />
      )}
    </TeamOpsSectionCard>
  );
}

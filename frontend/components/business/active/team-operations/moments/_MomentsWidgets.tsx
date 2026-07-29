"use client";

import type { TeamOpsMomentsResponse } from "@/lib/api/businessActive";
import { TEAM_OPS } from "../shared/teamOpsTheme";
import {
  TeamOpsEventRows,
  TeamOpsSectionCard,
  TeamOpsSectionTitle,
} from "../shared/shared";

type Moments = TeamOpsMomentsResponse;

export function MomentsHero({ data }: { data: Moments }) {
  return (
    <TeamOpsSectionCard gradient>
      <p className="mb-1 text-xs uppercase tracking-widest" style={{ color: TEAM_OPS.primary }}>
        Journey
      </p>
      <h2
        className="text-2xl font-bold"
        style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}
      >
        {data.journey_hero.title}
      </h2>
      <p className="mt-1 text-sm" style={{ color: TEAM_OPS.onVariant }}>
        {data.journey_hero.subtitle || "Team journey"}
      </p>
      <p className="mt-3 text-xs" style={{ color: TEAM_OPS.onVariant }}>
        {data.journey_hero.member_count ?? 0} members · {data.journey_hero.activity_count ?? 0}{" "}
        activities
      </p>
    </TeamOpsSectionCard>
  );
}

export function MomentsMilestones({ data }: { data: Moments }) {
  return (
    <section>
      <TeamOpsSectionTitle>Milestones</TeamOpsSectionTitle>
      <TeamOpsEventRows items={data.milestones.items} emptyLabel="No milestones yet." />
    </section>
  );
}

export function MomentsMeetings({ data }: { data: Moments }) {
  return (
    <section>
      <TeamOpsSectionTitle>Meetings</TeamOpsSectionTitle>
      <TeamOpsEventRows items={data.meetings.items} emptyLabel="No meetings logged." />
    </section>
  );
}

export function MomentsApprovals({ data }: { data: Moments }) {
  return (
    <section>
      <TeamOpsSectionTitle>Approvals</TeamOpsSectionTitle>
      <TeamOpsEventRows items={data.approvals.items} emptyLabel="No approval moments." />
    </section>
  );
}

export function MomentsRecognition({ data }: { data: Moments }) {
  return (
    <section>
      <TeamOpsSectionTitle>Recognition</TeamOpsSectionTitle>
      <TeamOpsEventRows items={data.recognition.items} emptyLabel="No recognition moments." />
    </section>
  );
}

export function MomentsIssues({ data }: { data: Moments }) {
  return (
    <section>
      <TeamOpsSectionTitle>Issues</TeamOpsSectionTitle>
      <TeamOpsEventRows items={data.issues.items} emptyLabel="No issue moments." />
    </section>
  );
}

export function MomentsTeamChanges({ data }: { data: Moments }) {
  return (
    <section>
      <TeamOpsSectionTitle>Team changes</TeamOpsSectionTitle>
      <TeamOpsEventRows items={data.team_changes.items} emptyLabel="No team changes yet." />
    </section>
  );
}

export function MomentsTimeline({ data }: { data: Moments }) {
  return (
    <section>
      <TeamOpsSectionTitle>Timeline</TeamOpsSectionTitle>
      <TeamOpsEventRows
        items={data.timeline.items}
        emptyLabel="Timeline is empty until activities are recorded."
      />
    </section>
  );
}

export function MomentsRecentActivity({ data }: { data: Moments }) {
  return (
    <section>
      <TeamOpsSectionTitle>Recent activity</TeamOpsSectionTitle>
      <TeamOpsEventRows
        items={data.recent_activity.items}
        emptyLabel="No recent activity window yet."
      />
    </section>
  );
}

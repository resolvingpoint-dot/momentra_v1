"use client";

/**
 * Presentational Team Operations Moments — stitch layout, backend-driven.
 */
import { motion } from "framer-motion";
import type { TeamOpsMomentsResponse } from "@/lib/api/businessActive";
import { cardEntranceVariants, staggerContainerVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { hasAnimatedOnce, markAnimatedOnce } from "@/lib/motion/useHasAnimatedOnce";
import {
  TeamOpsEmptyLine,
  TeamOpsScrollShell,
  TeamOpsStatusBanner,
} from "../shared/shared";
import {
  StitchContinueManaging,
  StitchHighlights,
  StitchMomentsHero,
  StitchProgressSnapshot,
  StitchTimelineSection,
} from "../shared/TeamOpsStitchComponents";
import { TeamOpsMomentsSkeleton } from "./TeamOpsMomentsSkeleton";

type Props = {
  data: TeamOpsMomentsResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  motionKey?: string;
  onRetry: () => void;
  onQuickAdd?: () => void;
};

export function TeamOperationsMoments({
  data,
  loading,
  refreshing,
  error,
  bottomPadding = 0,
  motionKey = "team-ops-moments",
  onRetry,
  onQuickAdd,
}: Props) {
  const reduced = useReducedMotion();
  const skipEnter = hasAnimatedOnce(motionKey);
  if (!skipEnter && data) markAnimatedOnce(motionKey);

  if (loading && !data) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsMomentsSkeleton />
      </TeamOpsScrollShell>
    );
  }
  if (error && !data) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsStatusBanner loading={false} error={error} onRetry={onRetry} />
      </TeamOpsScrollShell>
    );
  }
  if (!data) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsEmptyLine label="No data" />
      </TeamOpsScrollShell>
    );
  }

  const hub = data.operations_hub ?? {};
  const variants = skipEnter ? { hidden: {}, show: {} } : staggerContainerVariants(reduced);
  const card = skipEnter
    ? { hidden: { opacity: 1, y: 0 }, show: { opacity: 1, y: 0 } }
    : cardEntranceVariants(reduced);

  return (
    <TeamOpsScrollShell bottomPadding={bottomPadding}>
      {refreshing ? (
        <TeamOpsStatusBanner loading={false} refreshing error={null} onRetry={onRetry} />
      ) : null}
      <motion.div
        className="flex flex-col gap-6"
        variants={variants}
        initial="hidden"
        animate="show"
      >
        <motion.div variants={card}>
          <StitchMomentsHero
            title={data.journey_hero.title}
            memberCount={hub.member_count ?? data.journey_hero.member_count ?? 0}
            pendingApprovals={hub.pending_approvals ?? 0}
            openIssues={hub.open_issues ?? 0}
            activityCount={data.journey_hero.activity_count ?? 0}
            isActive={data.journey_hero.is_active}
          />
        </motion.div>
        <motion.div variants={card}>
          <StitchTimelineSection items={data.timeline.items} />
        </motion.div>
        <motion.div variants={card}>
          <StitchProgressSnapshot items={data.progress_snapshot.items} />
        </motion.div>
        <motion.div variants={card}>
          <StitchHighlights items={data.highlights.items} />
        </motion.div>
        <motion.div variants={card}>
          <StitchContinueManaging onQuickAdd={onQuickAdd} />
        </motion.div>
      </motion.div>
    </TeamOpsScrollShell>
  );
}

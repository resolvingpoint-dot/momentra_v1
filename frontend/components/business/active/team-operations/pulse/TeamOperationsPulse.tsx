"use client";

/**
 * Presentational Team Operations Pulse — stitch layout, backend-driven.
 */
import { motion } from "framer-motion";
import type { TeamOpsEventItem, TeamOpsPulseResponse } from "@/lib/api/businessActive";
import { cardEntranceVariants, staggerContainerVariants } from "@/lib/motion/variants";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { hasAnimatedOnce, markAnimatedOnce } from "@/lib/motion/useHasAnimatedOnce";
import {
  TeamOpsScrollShell,
  TeamOpsStatusBanner,
} from "../shared/shared";
import {
  StitchActivityFeed,
  StitchAttentionCards,
  StitchHealthDrivers,
  StitchHealthHero,
  StitchNextAction,
  StitchSignalsGrid,
} from "../shared/TeamOpsStitchComponents";
import { TeamOpsPulseSkeleton } from "./TeamOpsPulseSkeleton";

type Props = {
  data: TeamOpsPulseResponse | null;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  bottomPadding?: number;
  motionKey?: string;
  onRetry: () => void;
  onQuickAdd?: () => void;
  onViewActivity?: () => void;
  onSelectActivity?: (item: TeamOpsEventItem) => void;
};

export function TeamOperationsPulse({
  data,
  loading,
  refreshing,
  error,
  bottomPadding = 0,
  motionKey = "team-ops-pulse",
  onRetry,
  onQuickAdd,
  onViewActivity,
}: Props) {
  const reduced = useReducedMotion();
  const skipEnter = hasAnimatedOnce(motionKey);
  if (!skipEnter && data) markAnimatedOnce(motionKey);

  if (loading && !data) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsPulseSkeleton />
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
        <TeamOpsStatusBanner
          loading={false}
          error="This moment is unavailable. Retry or create a new moment."
          onRetry={onRetry}
        />
      </TeamOpsScrollShell>
    );
  }

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
        aria-busy={refreshing || undefined}
      >
        <motion.div variants={card}>
          <StitchHealthHero data={data} />
        </motion.div>
        <motion.div variants={card}>
          <StitchHealthDrivers drivers={data.health_drivers.items} />
        </motion.div>
        <motion.div variants={card}>
          <StitchAttentionCards items={data.attention.items} onViewAll={onViewActivity} />
        </motion.div>
        <motion.div variants={card}>
          <StitchSignalsGrid items={data.signals.items} />
        </motion.div>
        <motion.div variants={card}>
          <StitchActivityFeed
            items={data.recent_activity.items}
            onViewAll={onViewActivity}
          />
        </motion.div>
        <motion.div variants={card}>
          <StitchNextAction item={data.next_action.item} onQuickAdd={onQuickAdd} />
        </motion.div>
      </motion.div>
    </TeamOpsScrollShell>
  );
}

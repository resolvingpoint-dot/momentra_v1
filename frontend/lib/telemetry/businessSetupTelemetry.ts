/**
 * Business setup open latency marks — plan metrics.
 * Development console via performanceTelemetry; Personal/Group untouched.
 */
import { endSpan, startSpan, type PerformanceSpanName } from "@/lib/telemetry/performanceTelemetry";

const SESSION_KEY = "business_setup_open";

type OpenSession = {
  totalSpanId: string;
  createSpanId: string | null;
  getSpanId: string | null;
  firstPaintSpanId: string | null;
  bootstrapSpanId: string | null;
  createEndedAt: number | null;
  firstPaintAt: number | null;
  momentId: string | null;
};

let session: OpenSession | null = null;

function mark(name: string) {
  if (typeof performance !== "undefined" && performance.mark) {
    try {
      performance.mark(name);
    } catch {
      /* ignore */
    }
  }
}

export function beginBusinessSetupOpen(metadata?: Record<string, unknown>) {
  if (session) {
    endSpan(session.totalSpanId);
  }
  const totalSpanId = startSpan("business_setup_total_open" as PerformanceSpanName, {
    ...metadata,
    metric: "business_setup_total_open_ms",
  });
  const createSpanId = startSpan("business_setup_create" as PerformanceSpanName, {
    metric: "business_setup_create_ms",
  });
  mark("business_setup_create_start");
  session = {
    totalSpanId,
    createSpanId,
    getSpanId: null,
    firstPaintSpanId: null,
    bootstrapSpanId: null,
    createEndedAt: null,
    firstPaintAt: null,
    momentId: null,
  };
}

export function markBusinessSetupCreateDone(momentId: string) {
  if (!session?.createSpanId) return;
  endSpan(session.createSpanId, { metadata: { momentId, metric: "business_setup_create_ms" } });
  mark("business_setup_create_end");
  session.createSpanId = null;
  session.createEndedAt = performance.now();
  session.momentId = momentId;
  session.firstPaintSpanId = startSpan("business_setup_first_paint" as PerformanceSpanName, {
    momentId,
    metric: "business_setup_first_paint_ms",
  });
  mark("business_setup_overlay_mounted");
  session.getSpanId = startSpan("business_setup_get" as PerformanceSpanName, {
    momentId,
    metric: "business_setup_get_ms",
  });
}

/** Overlay mounted / shell first paint (skeleton counts as usable). */
export function markBusinessSetupFirstPaint() {
  if (!session?.firstPaintSpanId) return;
  endSpan(session.firstPaintSpanId, {
    metadata: { momentId: session.momentId, metric: "business_setup_first_paint_ms" },
  });
  session.firstPaintSpanId = null;
  session.firstPaintAt = performance.now();
  endSpan(session.totalSpanId, {
    metadata: { momentId: session.momentId, metric: "business_setup_total_open_ms" },
  });
  mark("business_setup_first_usable_paint");
  session.bootstrapSpanId = startSpan("business_setup_bootstrap_refresh" as PerformanceSpanName, {
    momentId: session.momentId,
    metric: "business_setup_bootstrap_refresh_ms",
  });
}

export function markBusinessSetupGetDone(metadata?: Record<string, unknown>) {
  if (!session?.getSpanId) return;
  endSpan(session.getSpanId, {
    metadata: {
      momentId: session.momentId,
      metric: "business_setup_get_ms",
      ...metadata,
    },
  });
  session.getSpanId = null;
  mark("business_setup_get_end");
}

export function markBusinessSetupBootstrapDone() {
  if (!session?.bootstrapSpanId) return;
  endSpan(session.bootstrapSpanId, {
    metadata: { momentId: session.momentId, metric: "business_setup_bootstrap_refresh_ms" },
  });
  session.bootstrapSpanId = null;
  mark("business_setup_bootstrap_end");
  session = null;
}

export function clearBusinessSetupOpenSession() {
  if (!session) return;
  if (session.createSpanId) endSpan(session.createSpanId);
  if (session.getSpanId) endSpan(session.getSpanId);
  if (session.firstPaintSpanId) endSpan(session.firstPaintSpanId);
  if (session.bootstrapSpanId) endSpan(session.bootstrapSpanId);
  endSpan(session.totalSpanId);
  session = null;
}

export { SESSION_KEY as BUSINESS_SETUP_OPEN_SESSION_KEY };

/** Debug performance spans — not product analytics. */

export type PerformanceSpanName =
  | "bootstrap.load"
  | "login.to_pulse"
  | "context.switch"
  | "quick_add.save"
  | "pulse.refresh"
  | "pulse.time_to_visible"
  | "template.moments.load"
  | "template.pulse.load"
  | "template.life.load"
  | "template.memory.load"
  | "template.moment.archive"
  | "template.moment.complete"
  | "business_setup_create"
  | "business_setup_get"
  | "business_setup_first_paint"
  | "business_setup_bootstrap_refresh"
  | "business_setup_total_open";

export type PerformanceSpan = {
  id: string;
  name: PerformanceSpanName;
  startedAt: number;
  endedAt?: number;
  durationMs?: number;
  requestId?: string;
  serverDurationMs?: number;
  serverCacheHit?: boolean;
  projectionVersion?: number;
  metadata?: Record<string, unknown>;
};

const activeSpans = new Map<string, PerformanceSpan>();
const completedSpans: PerformanceSpan[] = [];
const MAX_COMPLETED = 100;

let loginToPulseSpanId: string | null = null;
let quickAddSaveSpanId: string | null = null;

function pushCompleted(span: PerformanceSpan): void {
  completedSpans.unshift(span);
  if (completedSpans.length > MAX_COMPLETED) {
    completedSpans.length = MAX_COMPLETED;
  }
}

export function startSpan(
  name: PerformanceSpanName,
  metadata?: Record<string, unknown>,
): string {
  const id =
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : `span-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  activeSpans.set(id, {
    id,
    name,
    startedAt: performance.now(),
    metadata,
  });
  return id;
}

export function endSpan(
  spanId: string,
  extra?: Partial<Pick<PerformanceSpan, "requestId" | "serverDurationMs" | "metadata">>,
): PerformanceSpan | null {
  const span = activeSpans.get(spanId);
  if (!span) return null;
  activeSpans.delete(spanId);
  const endedAt = performance.now();
  const completed: PerformanceSpan = {
    ...span,
    ...extra,
    metadata: { ...span.metadata, ...extra?.metadata },
    endedAt,
    durationMs: endedAt - span.startedAt,
  };
  pushCompleted(completed);
  if (process.env.NODE_ENV === "development") {
    console.debug("[PerformanceTelemetry]", completed.name, {
      durationMs: Math.round(completed.durationMs ?? 0),
      serverDurationMs: completed.serverDurationMs,
      requestId: completed.requestId,
      metadata: completed.metadata,
    });
  }
  return completed;
}

export function recordResponseHeaders(res: Response, spanId?: string): void {
  const requestId = res.headers.get("X-Request-ID") ?? undefined;
  const durationHeader = res.headers.get("X-Duration-Ms");
  const serverDurationMs =
    durationHeader !== null && durationHeader !== "" ? Number(durationHeader) : undefined;
  const cacheHitHeader = res.headers.get("X-Cache-Hit");
  const serverCacheHit =
    cacheHitHeader === "true" ? true : cacheHitHeader === "false" ? false : undefined;
  const versionHeader = res.headers.get("X-Projection-Version");
  const projectionVersion =
    versionHeader !== null && versionHeader !== ""
      ? Number(versionHeader)
      : undefined;

  if (!spanId) return;
  const span = activeSpans.get(spanId);
  if (!span) return;
  span.requestId = requestId;
  if (serverDurationMs !== undefined && !Number.isNaN(serverDurationMs)) {
    span.serverDurationMs = serverDurationMs;
  }
  if (serverCacheHit !== undefined) {
    span.serverCacheHit = serverCacheHit;
  }
  if (projectionVersion !== undefined && !Number.isNaN(projectionVersion)) {
    span.projectionVersion = projectionVersion;
  }
}

export function getServerCacheHitRatio(spans: PerformanceSpan[]): {
  hits: number;
  total: number;
  ratio: number | null;
} {
  const withHeader = spans.filter((span) => span.serverCacheHit !== undefined);
  const hits = withHeader.filter((span) => span.serverCacheHit).length;
  return {
    hits,
    total: withHeader.length,
    ratio: withHeader.length > 0 ? hits / withHeader.length : null,
  };
}

export function startLoginToPulseSpan(): void {
  if (loginToPulseSpanId) return;
  loginToPulseSpanId = startSpan("login.to_pulse");
}

export function endLoginToPulseSpan(): PerformanceSpan | null {
  if (!loginToPulseSpanId) return null;
  const spanId = loginToPulseSpanId;
  loginToPulseSpanId = null;
  return endSpan(spanId);
}

/** Mark first paint of usable pulse data (cached or network). */
export function markPulseTimeToVisible(metadata?: Record<string, unknown>): void {
  if (typeof performance === "undefined" || typeof performance.mark !== "function") {
    return;
  }
  try {
    performance.mark("pulse-visible");
    const startExists = performance
      .getEntriesByName("pulse-load-start", "mark")
      .some((e) => e.entryType === "mark");
    if (startExists) {
      performance.measure("pulse-time-to-visible", "pulse-load-start", "pulse-visible");
    } else {
      performance.mark("pulse-load-start");
      performance.measure("pulse-time-to-visible", "pulse-load-start", "pulse-visible");
    }
  } catch {
    /* ignore mark collisions */
  }
  const id = startSpan("pulse.time_to_visible", metadata);
  endSpan(id, { metadata });
}

export function markPulseLoadStart(): void {
  if (typeof performance === "undefined" || typeof performance.mark !== "function") {
    return;
  }
  try {
    performance.mark("pulse-load-start");
  } catch {
    /* ignore */
  }
}

/** Mark shell first paint (cached session path). */
export function markShellPaint(): void {
  if (typeof performance === "undefined" || typeof performance.mark !== "function") {
    return;
  }
  try {
    performance.mark("shell-paint");
  } catch {
    /* ignore */
  }
}

/** Mark selected tab content visible (cached or network). */
export function markSelectedTabVisible(metadata?: Record<string, unknown>): void {
  if (typeof performance === "undefined" || typeof performance.mark !== "function") {
    return;
  }
  try {
    performance.mark("selected-tab-visible");
  } catch {
    /* ignore */
  }
  const id = startSpan("pulse.time_to_visible", {
    ...metadata,
    mark: "selected-tab-visible",
  });
  endSpan(id, { metadata });
}

/** Mark auth /me validation complete. */
export function markAuthValidated(): void {
  if (typeof performance === "undefined" || typeof performance.mark !== "function") {
    return;
  }
  try {
    performance.mark("auth-validated");
  } catch {
    /* ignore */
  }
}

export function startQuickAddSaveSpan(): void {
  if (quickAddSaveSpanId) return;
  quickAddSaveSpanId = startSpan("quick_add.save");
}

export function endQuickAddSaveSpan(): PerformanceSpan | null {
  if (!quickAddSaveSpanId) return null;
  const spanId = quickAddSaveSpanId;
  quickAddSaveSpanId = null;
  return endSpan(spanId);
}

export function getActiveSpans(): PerformanceSpan[] {
  return Array.from(activeSpans.values());
}

export function getRecentSpans(limit = 50): PerformanceSpan[] {
  return completedSpans.slice(0, limit);
}

export function clearPerformanceTelemetry(): void {
  activeSpans.clear();
  completedSpans.length = 0;
  loginToPulseSpanId = null;
  quickAddSaveSpanId = null;
}

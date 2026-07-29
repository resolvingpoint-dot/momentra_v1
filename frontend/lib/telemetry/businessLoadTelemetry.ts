/** BusinessLoad client telemetry — no PII or full payloads. */

export type BusinessLoadFields = {
  platform: "web" | "android" | "ios";
  userHash?: string;
  momentId?: string | null;
  momentType?: string | null;
  tab?: string | null;
  requestKey?: string;
  reason?: string;
  cacheSource?: "memory" | "disk" | "network" | "redis" | "none";
  isStale?: boolean;
  durationMs?: number;
  generation?: number;
  success?: boolean;
  errorCode?: string | null;
};

/** In-session counters for Performance Freeze measurement (dev / tests). */
export type BusinessLoadMetricsSnapshot = {
  bootstrapNetwork: number;
  createOptionsNetwork: number;
  pulseNetwork: number;
  momentsNetwork: number;
  lifeNetwork: number;
  memoryNetwork: number;
  pulseMemoryHit: number;
  momentsMemoryHit: number;
  generationDrops: number;
  durationsMs: {
    bootstrap: number[];
    pulse: number[];
    moments: number[];
    createOptions: number[];
  };
};

const metrics: BusinessLoadMetricsSnapshot = {
  bootstrapNetwork: 0,
  createOptionsNetwork: 0,
  pulseNetwork: 0,
  momentsNetwork: 0,
  lifeNetwork: 0,
  memoryNetwork: 0,
  pulseMemoryHit: 0,
  momentsMemoryHit: 0,
  generationDrops: 0,
  durationsMs: {
    bootstrap: [],
    pulse: [],
    moments: [],
    createOptions: [],
  },
};

function pushDuration(bucket: number[], ms: number | undefined) {
  if (ms == null || !Number.isFinite(ms)) return;
  bucket.push(ms);
  if (bucket.length > 200) bucket.shift();
}

function recordMetrics(fields: BusinessLoadFields): void {
  const key = (fields.requestKey ?? "").toLowerCase();
  const tab = (fields.tab ?? "").toLowerCase();
  const source = fields.cacheSource;
  const reason = fields.reason ?? "";

  if (reason === "generation_mismatch" || fields.errorCode === "stale_generation") {
    metrics.generationDrops += 1;
  }

  if (source === "network") {
    if (key.includes("session_bootstrap") || tab === "session") {
      metrics.bootstrapNetwork += 1;
      pushDuration(metrics.durationsMs.bootstrap, fields.durationMs);
    } else if (key.includes("create_options") || tab === "create") {
      metrics.createOptionsNetwork += 1;
      pushDuration(metrics.durationsMs.createOptions, fields.durationMs);
    } else if (tab === "pulse") {
      metrics.pulseNetwork += 1;
      pushDuration(metrics.durationsMs.pulse, fields.durationMs);
    } else if (tab === "moments") {
      metrics.momentsNetwork += 1;
      pushDuration(metrics.durationsMs.moments, fields.durationMs);
    } else if (tab === "life") {
      metrics.lifeNetwork += 1;
    } else if (tab === "memory") {
      metrics.memoryNetwork += 1;
    }
  } else if (source === "memory" || source === "disk") {
    if (tab === "pulse") metrics.pulseMemoryHit += 1;
    if (tab === "moments") metrics.momentsMemoryHit += 1;
  }
}

export function getBusinessLoadMetricsSnapshot(): BusinessLoadMetricsSnapshot {
  return {
    ...metrics,
    durationsMs: {
      bootstrap: [...metrics.durationsMs.bootstrap],
      pulse: [...metrics.durationsMs.pulse],
      moments: [...metrics.durationsMs.moments],
      createOptions: [...metrics.durationsMs.createOptions],
    },
  };
}

export function resetBusinessLoadMetrics(): void {
  metrics.bootstrapNetwork = 0;
  metrics.createOptionsNetwork = 0;
  metrics.pulseNetwork = 0;
  metrics.momentsNetwork = 0;
  metrics.lifeNetwork = 0;
  metrics.memoryNetwork = 0;
  metrics.pulseMemoryHit = 0;
  metrics.momentsMemoryHit = 0;
  metrics.generationDrops = 0;
  metrics.durationsMs.bootstrap = [];
  metrics.durationsMs.pulse = [];
  metrics.durationsMs.moments = [];
  metrics.durationsMs.createOptions = [];
}

export function percentile(sortedAsc: number[], p: number): number | null {
  if (sortedAsc.length === 0) return null;
  const idx = Math.min(
    sortedAsc.length - 1,
    Math.max(0, Math.ceil((p / 100) * sortedAsc.length) - 1),
  );
  return sortedAsc[idx] ?? null;
}

function hashUserId(userId: string | null | undefined): string | undefined {
  if (!userId) return undefined;
  let h = 0;
  for (let i = 0; i < userId.length; i++) {
    h = (h * 31 + userId.charCodeAt(i)) | 0;
  }
  return `u${(h >>> 0).toString(16)}`;
}

export function logBusinessLoad(
  fields: Omit<BusinessLoadFields, "platform"> & {
    platform?: BusinessLoadFields["platform"];
    userId?: string | null;
  },
): void {
  const payload: BusinessLoadFields = {
    platform: fields.platform ?? "web",
    userHash: fields.userHash ?? hashUserId(fields.userId),
    momentId: fields.momentId,
    momentType: fields.momentType,
    tab: fields.tab,
    requestKey: fields.requestKey,
    reason: fields.reason,
    cacheSource: fields.cacheSource,
    isStale: fields.isStale,
    durationMs: fields.durationMs,
    generation: fields.generation,
    success: fields.success,
    errorCode: fields.errorCode,
  };
  recordMetrics(payload);
  if (process.env.NODE_ENV === "development") {
    console.debug("[BusinessLoad]", payload);
  }
  console.info(
    "BusinessLoad",
    JSON.stringify({
      event: "BusinessLoad",
      ...payload,
    }),
  );
}

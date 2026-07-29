"use client";

import { useCallback, useState } from "react";
import { requestWithRetry } from "@/lib/api/client";
import { getRecentSpans, getServerCacheHitRatio } from "@/lib/telemetry/performanceTelemetry";

type DomainEvent = {
  event_id?: string;
  name: string;
  user_id?: string;
  moment_id?: string;
  context?: string;
  moment_type?: string;
  payload?: Record<string, unknown>;
  created_at?: string;
};

export default function DebugEventsPage() {
  const [momentId, setMomentId] = useState("");
  const [events, setEvents] = useState<DomainEvent[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const loadEvents = useCallback(async () => {
    if (!momentId.trim()) {
      setError("Enter a moment ID.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const qs = new URLSearchParams({ moment_id: momentId.trim() });
      const data = await requestWithRetry<{ events?: DomainEvent[] } | DomainEvent[]>(
        `api/v1/debug/events?${qs.toString()}`,
        { method: "GET" },
      );
      setEvents(Array.isArray(data) ? data : (data.events ?? []));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load events");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, [momentId]);

  if (process.env.NODE_ENV === "production") {
    return (
      <main className="mx-auto max-w-3xl p-6">
        <p className="text-sm opacity-70">Event timeline is only available in development.</p>
      </main>
    );
  }

  const spans = getRecentSpans().slice(0, 20);
  const cacheStats = getServerCacheHitRatio(getRecentSpans());

  return (
    <main className="mx-auto max-w-4xl space-y-8 p-6 font-mono text-sm">
      <header>
        <h1 className="text-xl font-semibold">Event Timeline</h1>
        <p className="mt-1 opacity-70">Domain events and recent client performance spans.</p>
      </header>

      <section className="space-y-3 rounded-xl border border-white/10 p-4">
        <label className="block space-y-2">
          <span className="opacity-80">Moment ID</span>
          <input
            value={momentId}
            onChange={(e) => setMomentId(e.target.value)}
            className="w-full rounded-lg border border-white/15 bg-black/20 px-3 py-2"
            placeholder="uuid"
          />
        </label>
        <button
          type="button"
          onClick={() => void loadEvents()}
          disabled={loading}
          className="rounded-lg bg-violet-600 px-4 py-2 font-semibold text-white disabled:opacity-50"
        >
          {loading ? "Loading…" : "Load events"}
        </button>
        {error ? <p className="text-red-400">{error}</p> : null}
      </section>

      <section className="space-y-2">
        <h2 className="text-base font-semibold">Domain events</h2>
        {events.length === 0 ? (
          <p className="opacity-60">No events loaded.</p>
        ) : (
          <ol className="space-y-2">
            {events.map((event, index) => (
              <li
                key={event.event_id ?? `${event.name}-${index}`}
                className="rounded-lg border border-white/10 p-3"
              >
                <p className="font-semibold">{event.name}</p>
                <p className="opacity-70">{event.created_at ?? "—"}</p>
                {event.context ? <p>context: {event.context}</p> : null}
                {event.moment_type ? <p>template: {event.moment_type}</p> : null}
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="space-y-2">
        <h2 className="text-base font-semibold">Recent performance spans</h2>
        {cacheStats.total > 0 ? (
          <p className="opacity-80">
            Server cache hit ratio: {cacheStats.hits}/{cacheStats.total} (
            {Math.round((cacheStats.ratio ?? 0) * 100)}%)
          </p>
        ) : null}
        {spans.length === 0 ? (
          <p className="opacity-60">No spans recorded yet.</p>
        ) : (
          <ul className="space-y-2">
            {spans.map((span) => (
              <li key={span.id} className="rounded-lg border border-white/10 p-3">
                <p>
                  {span.name} — {span.durationMs !== undefined ? `${Math.round(span.durationMs)}ms` : "active"}
                </p>
                {span.requestId ? <p className="opacity-70">request: {span.requestId}</p> : null}
                {span.serverDurationMs !== undefined ? (
                  <p className="opacity-70">server: {span.serverDurationMs}ms</p>
                ) : null}
                {span.serverCacheHit !== undefined ? (
                  <p className="opacity-70">
                    X-Cache-Hit: {span.serverCacheHit ? "true" : "false"}
                  </p>
                ) : null}
                {span.projectionVersion !== undefined ? (
                  <p className="opacity-70">X-Projection-Version: {span.projectionVersion}</p>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

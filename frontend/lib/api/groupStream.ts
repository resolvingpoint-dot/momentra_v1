/**
 * SSE client for Group Trip projection invalidate push.
 * Uses fetch + ReadableStream so Authorization Bearer can be set
 * (EventSource cannot set custom headers).
 */
import { refreshAccessToken } from "@/lib/api/client";
import { clearTokens, getAccessToken } from "@/lib/auth/tokens";

const baseUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.mallaapp.org"
).replace(/\/$/, "");

export type TripInvalidatePayload = {
  moment_id: string;
  slices: string[];
  reason: string;
};

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal?.aborted) {
      reject(new DOMException("Aborted", "AbortError"));
      return;
    }
    const t = window.setTimeout(resolve, ms);
    signal?.addEventListener(
      "abort",
      () => {
        window.clearTimeout(t);
        reject(new DOMException("Aborted", "AbortError"));
      },
      { once: true },
    );
  });
}

async function authHeaders(): Promise<Headers> {
  let token = getAccessToken();
  if (!token) {
    try {
      await refreshAccessToken();
    } catch {
      clearTokens();
      throw new Error("Not signed in");
    }
    token = getAccessToken();
  }
  if (!token) throw new Error("Not signed in");
  const headers = new Headers({
    Accept: "text/event-stream",
    Authorization: `Bearer ${token}`,
  });
  if (baseUrl.includes("ngrok")) {
    headers.set("ngrok-skip-browser-warning", "true");
  }
  return headers;
}

/**
 * Subscribe to `GET /api/v1/group/trips/{momentId}/stream`.
 * Returns an unsubscribe function. Reconnects with exponential backoff.
 */
export function subscribeTripMomentStream(
  momentId: string,
  onInvalidate: (payload: TripInvalidatePayload) => void,
): () => void {
  const ac = new AbortController();
  let stopped = false;

  const stop = () => {
    stopped = true;
    ac.abort();
  };

  void (async () => {
    let backoffMs = 1_000;
    while (!stopped) {
      try {
        const headers = await authHeaders();
        const res = await fetch(
          `${baseUrl}/api/v1/group/trips/${encodeURIComponent(momentId)}/stream`,
          { method: "GET", headers, signal: ac.signal, cache: "no-store" },
        );

        if (res.status === 401) {
          try {
            await refreshAccessToken();
          } catch {
            clearTokens();
            break;
          }
          continue;
        }

        if (!res.ok || !res.body) {
          await sleep(backoffMs, ac.signal);
          backoffMs = Math.min(backoffMs * 2, 30_000);
          continue;
        }

        backoffMs = 1_000;
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let eventName = "message";
        let dataLines: string[] = [];

        while (!stopped) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split(/\r?\n/);
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (line.startsWith(":")) {
              continue;
            }
            if (line.trim() === "") {
              if (dataLines.length > 0 && eventName === "invalidate") {
                try {
                  const payload = JSON.parse(dataLines.join("\n")) as TripInvalidatePayload;
                  onInvalidate(payload);
                } catch {
                  /* ignore malformed */
                }
              }
              eventName = "message";
              dataLines = [];
              continue;
            }
            if (line.startsWith("event:")) {
              eventName = line.slice(6).trim();
            } else if (line.startsWith("data:")) {
              dataLines.push(line.slice(5).replace(/^ /, ""));
            }
          }
        }
      } catch (err) {
        if (stopped || (err instanceof DOMException && err.name === "AbortError")) {
          break;
        }
        try {
          await sleep(backoffMs, ac.signal);
        } catch {
          break;
        }
        backoffMs = Math.min(backoffMs * 2, 30_000);
      }
    }
  })();

  return stop;
}

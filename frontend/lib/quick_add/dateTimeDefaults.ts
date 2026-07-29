/** Local-time Quick Add date/time defaults (not UTC). */

function pad(n: number): string {
  return String(n).padStart(2, "0");
}

/** Local calendar date as `yyyy-MM-dd`. */
export function todayISODate(now: Date = new Date()): string {
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

/** Local clock time as `HH:mm`. */
export function nowISOTime(now: Date = new Date()): string {
  return `${pad(now.getHours())}:${pad(now.getMinutes())}`;
}

/** Local datetime for `datetime-local` / occurred_at as `yyyy-MM-dd'T'HH:mm`. */
export function defaultOccurredAt(now: Date = new Date()): string {
  return `${todayISODate(now)}T${nowISOTime(now)}`;
}

/** Compose occurred_at from separate date + time fields. */
export function composeOccurredAt(
  date: string | null | undefined,
  time: string | null | undefined,
): string | undefined {
  const d = String(date ?? "").trim();
  const t = String(time ?? "").trim();
  if (d && t) return `${d}T${t}`;
  if (d) return d;
  return undefined;
}

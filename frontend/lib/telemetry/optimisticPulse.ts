import type { PersonalPulseResponse } from "@/lib/api/personal";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";

export type OptimisticPatch = {
  clientRequestId: string;
  momentTypeCode: PersonalMomentTypeCode;
  previous: PersonalPulseResponse | null;
  patch: Partial<PersonalPulseResponse>;
};

const pending = new Map<string, OptimisticPatch>();

type PulseListener = (
  momentTypeCode: PersonalMomentTypeCode,
  pulse: PersonalPulseResponse | null,
) => void;

const listeners = new Set<PulseListener>();

function mergePulse(
  current: PersonalPulseResponse,
  patch: Partial<PersonalPulseResponse>,
): PersonalPulseResponse {
  return { ...current, ...patch };
}

function notify(momentTypeCode: PersonalMomentTypeCode, pulse: PersonalPulseResponse | null): void {
  listeners.forEach((listener) => listener(momentTypeCode, pulse));
}

export function subscribeOptimisticPulse(listener: PulseListener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function applyOptimisticPatch(
  momentTypeCode: PersonalMomentTypeCode,
  clientRequestId: string,
  current: PersonalPulseResponse | null,
  patch: Partial<PersonalPulseResponse>,
): PersonalPulseResponse | null {
  pending.set(clientRequestId, {
    clientRequestId,
    momentTypeCode,
    previous: current,
    patch,
  });
  if (!current) return null;
  const merged = mergePulse(current, patch);
  notify(momentTypeCode, merged);
  return merged;
}

export function reconcilePatch(
  clientRequestId: string,
  serverPulse: PersonalPulseResponse,
): PersonalPulseResponse {
  const entry = pending.get(clientRequestId);
  pending.delete(clientRequestId);
  if (entry) {
    notify(entry.momentTypeCode, serverPulse);
  }
  return serverPulse;
}

export function rollbackPatch(clientRequestId: string): PersonalPulseResponse | null {
  const entry = pending.get(clientRequestId);
  if (!entry) return null;
  pending.delete(clientRequestId);
  notify(entry.momentTypeCode, entry.previous);
  return entry.previous;
}

export function getPendingOptimisticPatches(): OptimisticPatch[] {
  return Array.from(pending.values());
}

export function hasPendingPatch(clientRequestId: string): boolean {
  return pending.has(clientRequestId);
}

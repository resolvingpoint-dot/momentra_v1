"use client";

export type GroupMomentTypeCode =
  | "SHARED_EXPERIENCE"
  | "SHARED_PURCHASE"
  | "SHARED_LIVING";

const VALID_TYPES = new Set<string>([
  "SHARED_EXPERIENCE",
  "SHARED_PURCHASE",
  "SHARED_LIVING",
]);

const STORAGE_KEY = "momentra:group:selectedMomentType";

let selectedMomentTypeCode: GroupMomentTypeCode = "SHARED_EXPERIENCE";
const listeners = new Set<() => void>();

export function isGroupMomentTypeCode(
  code: string | null | undefined,
): code is GroupMomentTypeCode {
  return !!code && VALID_TYPES.has(code);
}

export function normalizeGroupMomentTypeCode(
  code: string | null | undefined,
): GroupMomentTypeCode | null {
  if (!code || !VALID_TYPES.has(code)) return null;
  return code as GroupMomentTypeCode;
}

function readStored(): GroupMomentTypeCode | null {
  if (typeof window === "undefined") return null;
  return normalizeGroupMomentTypeCode(window.localStorage.getItem(STORAGE_KEY));
}

function notify() {
  listeners.forEach((fn) => fn());
}

export function getSelectedGroupMomentTypeCode(): GroupMomentTypeCode {
  return selectedMomentTypeCode;
}

export function setSelectedGroupMomentTypeCode(code: GroupMomentTypeCode) {
  const canonical = normalizeGroupMomentTypeCode(code) ?? code;
  if (selectedMomentTypeCode === canonical) return;
  selectedMomentTypeCode = canonical;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, canonical);
  }
  notify();
}

export function hydrateGroupMomentSession() {
  const stored = readStored();
  if (stored) {
    selectedMomentTypeCode = stored;
  }
}

export function subscribeGroupMomentSession(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function groupMomentTypeLabel(code: GroupMomentTypeCode): string {
  switch (code) {
    case "SHARED_PURCHASE":
      return "Shared Purchase";
    case "SHARED_LIVING":
      return "Shared Living";
    default:
      return "Shared Experience";
  }
}

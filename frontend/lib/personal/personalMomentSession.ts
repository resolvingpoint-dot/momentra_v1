"use client";

export type PersonalMomentTypeCode =
  | "LIFE_OPERATIONS"
  | "FUTURE_BUILDING"
  | "LIFESTYLE"
  | "RELATIONSHIPS";

export const MY_MONEY_TEMPLATE_CODES: readonly PersonalMomentTypeCode[] = [
  "LIFE_OPERATIONS",
  "FUTURE_BUILDING",
  "LIFESTYLE",
  "RELATIONSHIPS",
] as const;

const LEGACY_MOMENT_TYPE_ALIASES: Record<string, PersonalMomentTypeCode> = {
  EMOTIONAL_SECURITY: "RELATIONSHIPS",
};

const VALID_MOMENT_TYPES = new Set<string>([
  "LIFE_OPERATIONS",
  "FUTURE_BUILDING",
  "LIFESTYLE",
  "RELATIONSHIPS",
  "EMOTIONAL_SECURITY",
]);

const STORAGE_KEY = "momentra:personal:selectedMomentType";

let selectedMomentTypeCode: PersonalMomentTypeCode = "LIFE_OPERATIONS";
const listeners = new Set<() => void>();

/** Canonical moment type — maps legacy EMOTIONAL_SECURITY to RELATIONSHIPS. */
export function normalizePersonalMomentTypeCode(
  code: string | null | undefined,
): PersonalMomentTypeCode | null {
  if (!code || !VALID_MOMENT_TYPES.has(code)) return null;
  if (code in LEGACY_MOMENT_TYPE_ALIASES) {
    return LEGACY_MOMENT_TYPE_ALIASES[code];
  }
  return code as PersonalMomentTypeCode;
}

export function isMyMoneyTemplateCode(
  code: string | null | undefined,
): code is PersonalMomentTypeCode {
  const normalized = normalizePersonalMomentTypeCode(code);
  return normalized !== null && MY_MONEY_TEMPLATE_CODES.includes(normalized);
}

function readStored(): PersonalMomentTypeCode | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  return normalizePersonalMomentTypeCode(raw);
}

function notify() {
  listeners.forEach((fn) => fn());
}

export function getSelectedMomentTypeCode(): PersonalMomentTypeCode {
  return selectedMomentTypeCode;
}

export function setSelectedMomentTypeCode(code: PersonalMomentTypeCode) {
  const canonical = normalizePersonalMomentTypeCode(code) ?? code;
  if (selectedMomentTypeCode === canonical) return;
  selectedMomentTypeCode = canonical;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, canonical);
  }
  notify();
}

export function hydratePersonalMomentSession() {
  const stored = readStored();
  if (stored) {
    selectedMomentTypeCode = stored;
    if (typeof window !== "undefined") {
      window.localStorage.setItem(STORAGE_KEY, stored);
    }
  }
}

export function subscribePersonalMomentSession(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function momentTypeLabel(code: PersonalMomentTypeCode): string {
  switch (code) {
    case "FUTURE_BUILDING":
      return "Future Building";
    case "LIFESTYLE":
      return "Lifestyle";
    case "RELATIONSHIPS":
      return "Relationships";
    default:
      return "Life Operations";
  }
}

export function momentTypeBadge(code: PersonalMomentTypeCode): string {
  switch (code) {
    case "FUTURE_BUILDING":
      return "FUTURE BUILDING";
    case "LIFESTYLE":
      return "LIFESTYLE";
    case "RELATIONSHIPS":
      return "RELATIONSHIPS";
    default:
      return "LIFE OPERATIONS";
  }
}

export function momentTypeCodesEqual(a: string, b: string): boolean {
  const na = normalizePersonalMomentTypeCode(a);
  const nb = normalizePersonalMomentTypeCode(b);
  return na != null && nb != null && na === nb;
}

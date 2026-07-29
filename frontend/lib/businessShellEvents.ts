export const BUSINESS_CREATE_OPEN_EVENT = "momentra:open-business-create";
export const BUSINESS_OPEN_MOMENT_EVENT = "momentra:business-open-moment";
export const BUSINESS_SELECT_PULSE_EVENT = "momentra:business-select-pulse";

export function openBusinessCreateOverlay(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(BUSINESS_CREATE_OPEN_EVENT));
  }
}

export function openBusinessMomentAndPulse(momentId: string, typeCode: string): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent(BUSINESS_OPEN_MOMENT_EVENT, {
      detail: { momentId, typeCode },
    }),
  );
}

export function selectBusinessPulseTab(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(BUSINESS_SELECT_PULSE_EVENT));
  }
}

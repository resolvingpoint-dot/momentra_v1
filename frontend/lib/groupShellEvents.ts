export const GROUP_CREATE_OPEN_EVENT = "momentra:open-group-create";
export const GROUP_OPEN_MOMENT_EVENT = "momentra:group-open-moment";

export function openGroupCreateOverlay(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(GROUP_CREATE_OPEN_EVENT));
  }
}

export function openGroupMomentAndPulse(detail: {
  moment_id: string;
  moment_type?: string | null;
}): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(GROUP_OPEN_MOMENT_EVENT, { detail }));
  }
}

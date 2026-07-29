export const PERSONAL_CREATE_OPEN_EVENT = "momentra:open-personal-create";

export function openPersonalCreateOverlay(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(PERSONAL_CREATE_OPEN_EVENT));
  }
}

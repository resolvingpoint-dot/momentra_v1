export const LIFE360_SELECT_LIFE_TAB_EVENT = "momentra:select-life-tab";

export function openLifeTabFromLife360(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new CustomEvent(LIFE360_SELECT_LIFE_TAB_EVENT));
  }
}

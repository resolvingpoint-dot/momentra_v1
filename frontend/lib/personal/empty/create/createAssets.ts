/** Local images from docs/screens/personal/choose a moment-personal */

export const PERSONAL_CREATE_HERO_IMAGE = "/personal/create/hero.webp";

export const PERSONAL_CREATE_CARD_IMAGES: Record<string, string> = {
  LIFE_OPERATIONS: "/personal/create/life-ops.webp",
  FUTURE_BUILDING: "/personal/create/future-building.webp",
  LIFESTYLE: "/personal/create/lifestyle.webp",
  RELATIONSHIPS: "/personal/create/relationship.webp",
};

export function createCardImageForType(momentTypeCode: string): string {
  const key =
    momentTypeCode.toUpperCase() === "EMOTIONAL_SECURITY"
      ? "RELATIONSHIPS"
      : momentTypeCode.toUpperCase();
  return (
    PERSONAL_CREATE_CARD_IMAGES[key] ??
    PERSONAL_CREATE_CARD_IMAGES.FUTURE_BUILDING
  );
}

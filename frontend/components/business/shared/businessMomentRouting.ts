import type {
  BusinessCreateOptionCard,
  BusinessMomentResponse,
  BusinessMomentTypeCard,
} from "@/lib/api/business";

export type BusinessMomentManageContext = {
  momentId: string;
  typeCode: string;
  momentName: string;
  status: string;
};

export type BusinessMomentSwitcherOption = {
  typeCode: string;
  label: string;
  momentId: string | null;
  displayOrder?: number;
};

/** Same ACTIVE-family as Personal (`ACTIVE` / `PAUSED` / `COMPLETED`). */
export const ACTIVE_BUSINESS_MOMENT_STATUSES = new Set(["ACTIVE", "PAUSED", "COMPLETED"]);

export function isActiveBusinessMomentStatus(status: string | null | undefined): boolean {
  return ACTIVE_BUSINESS_MOMENT_STATUSES.has((status ?? "").toUpperCase());
}

function isSwitcherEligible(
  linkedMomentId: string | null | undefined,
  linkedMomentStatus: string | null | undefined,
): boolean {
  if (!linkedMomentId) return false;
  const status = (linkedMomentStatus ?? "").trim();
  if (!status) return true;
  return isActiveBusinessMomentStatus(status);
}

function isHomeCardSwitcherEligible(card: BusinessMomentTypeCard): boolean {
  if (!card.linked_moment_id) return false;
  if (card.is_active === true) return true;
  return isSwitcherEligible(card.linked_moment_id, card.linked_moment_status);
}

function isCreateCardSwitcherEligible(card: BusinessCreateOptionCard): boolean {
  if (!card.linked_moment_id) return false;
  if (card.is_active === true) return true;
  return isSwitcherEligible(card.linked_moment_id, card.linked_moment_status);
}

export function resolveBusinessMomentManageContext(
  typeCode: string,
  createCards: BusinessCreateOptionCard[],
  homeCards: BusinessMomentTypeCard[] = [],
  moments: BusinessMomentResponse[] = [],
): BusinessMomentManageContext | null {
  // Group parity: prefer inventory moment of this type when ACTIVE-family.
  const fromMoments = moments.find((m) => {
    const code = (m.moment_type_code ?? "").toUpperCase();
    if (code !== typeCode.toUpperCase()) return false;
    const status = (m.status ?? "").trim();
    if (!status) return true;
    return isActiveBusinessMomentStatus(status);
  });
  if (fromMoments?.moment_id) {
    return {
      momentId: fromMoments.moment_id,
      typeCode,
      momentName: fromMoments.moment_name?.trim() || typeCode,
      status: (fromMoments.status ?? "").trim() || "ACTIVE",
    };
  }

  const card = createCards.find((item) => item.moment_type_code === typeCode);
  const homeCard = homeCards.find((item) => item.moment_type_code === typeCode);

  if (homeCard && isHomeCardSwitcherEligible(homeCard) && homeCard.linked_moment_id) {
    return {
      momentId: homeCard.linked_moment_id,
      typeCode,
      momentName: homeCard.moment_type_name?.trim() || card?.moment_type_name?.trim() || typeCode,
      status: (homeCard.linked_moment_status ?? "").trim() || "ACTIVE",
    };
  }
  if (card && isCreateCardSwitcherEligible(card) && card.linked_moment_id) {
    return {
      momentId: card.linked_moment_id,
      typeCode,
      momentName: card.moment_type_name?.trim() || homeCard?.moment_type_name?.trim() || typeCode,
      status: (card.linked_moment_status ?? "").trim() || "ACTIVE",
    };
  }

  const momentId = card?.linked_moment_id ?? homeCard?.linked_moment_id ?? null;
  if (!momentId) return null;
  const status = card?.linked_moment_status ?? homeCard?.linked_moment_status ?? "ACTIVE";
  const momentName =
    card?.moment_type_name?.trim() ||
    homeCard?.moment_type_name?.trim() ||
    typeCode;
  return { momentId, typeCode, momentName, status };
}

/**
 * Group-first: build from bootstrap.moments; fallback to Personal-style home/create merge.
 */
export function resolveBusinessMomentSwitcherOptions(
  homeCards: BusinessMomentTypeCard[],
  createCards: BusinessCreateOptionCard[],
  moments: BusinessMomentResponse[] = [],
): BusinessMomentSwitcherOption[] {
  const byType = new Map<string, BusinessMomentSwitcherOption>();

  const push = (
    typeCode: string,
    label: string,
    momentId: string | null,
    displayOrder: number,
  ) => {
    byType.set(typeCode, { typeCode, label, momentId, displayOrder });
  };

  // Group parity: real moment inventory first.
  for (const item of moments) {
    const typeCode = (item.moment_type_code ?? "").trim();
    if (!typeCode || !item.moment_id) continue;
    const status = (item.status ?? "").trim();
    if (status && !isActiveBusinessMomentStatus(status)) continue;
    push(typeCode, item.moment_name || typeCode, item.moment_id, byType.size);
  }

  if (byType.size > 0) {
    return [...byType.values()].sort(
      (a, b) => (a.displayOrder ?? 0) - (b.displayOrder ?? 0),
    );
  }

  // Personal-style fallback: create then home (home wins).
  for (const item of createCards) {
    if (!isCreateCardSwitcherEligible(item)) continue;
    push(
      item.moment_type_code,
      item.moment_type_name,
      item.linked_moment_id ?? null,
      item.display_order,
    );
  }
  for (const item of homeCards) {
    if (!isHomeCardSwitcherEligible(item)) continue;
    push(
      item.moment_type_code,
      item.moment_type_name,
      item.linked_moment_id ?? null,
      item.display_order,
    );
  }

  return [...byType.values()].sort(
    (a, b) => (a.displayOrder ?? 0) - (b.displayOrder ?? 0),
  );
}

export function reconcileSelectedBusinessMomentType(
  options: BusinessMomentSwitcherOption[],
  current: string,
): string {
  if (options.length === 0) return current;
  if (options.some((item) => item.typeCode === current)) return current;
  return options[0]?.typeCode ?? current;
}

/** Group parity: resolve type + momentId from switcher options. */
export function resolveSelectedBusinessMoment(
  options: BusinessMomentSwitcherOption[],
  currentType: string,
  currentMomentId: string | null = null,
): { typeCode: string; momentId: string | null } {
  if (options.length === 0) {
    return { typeCode: currentType, momentId: currentMomentId };
  }
  const typeCode = reconcileSelectedBusinessMomentType(options, currentType);
  const match =
    options.find((o) => o.typeCode === typeCode && o.momentId === currentMomentId) ??
    options.find((o) => o.typeCode === typeCode) ??
    options[0];
  return {
    typeCode: match?.typeCode ?? typeCode,
    momentId: match?.momentId ?? null,
  };
}

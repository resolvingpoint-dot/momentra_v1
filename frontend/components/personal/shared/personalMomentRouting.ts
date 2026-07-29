import type { BootstrapResponse } from "@/lib/api/bootstrapTypes";
import type { PersonalCreateOptionCard, PersonalMomentHomeCard } from "@/lib/api/personal";
import type {
  PersonalMemoryResponse,
  PersonalMomentsHomeResponse,
  PersonalPulseResponse,
} from "@/lib/api/personal";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import {
  momentTypeBadge,
  momentTypeLabel,
  momentTypeCodesEqual,
  normalizePersonalMomentTypeCode,
} from "@/lib/personal/personalMomentSession";
import {
  contextStateFromBootstrap,
  moduleStateFromBootstrap,
  resolveScreen,
  type ResolvedScreen,
} from "@/lib/screenResolver";

export type PersonalMomentSwitcherOption = {
  typeCode: PersonalMomentTypeCode;
  label: string;
  momentId: string | null;
};

export type PersonalMomentManageContext = {
  momentId: string;
  typeCode: PersonalMomentTypeCode;
  momentName: string;
  status: "DRAFT" | "ACTIVE" | "PAUSED" | "COMPLETED" | "ARCHIVED";
};

function asMomentTypeCode(code: string): PersonalMomentTypeCode | null {
  return normalizePersonalMomentTypeCode(code);
}

export function activeMomentSwitcherOptionsFromHomeCards(
  cards: PersonalMomentHomeCard[],
): PersonalMomentSwitcherOption[] {
  return cards
    .filter((c) => c.is_active && c.moment_type_code !== "CUSTOM")
    .sort((a, b) => a.display_order - b.display_order)
    .map((c) => {
      const typeCode = asMomentTypeCode(c.moment_type_code);
      if (!typeCode) return null;
      return {
        typeCode,
        label: c.moment_type_name?.trim() || momentTypeLabel(typeCode),
        momentId: c.linked_moment_id ?? null,
      };
    })
    .filter((o): o is PersonalMomentSwitcherOption => o != null);
}

export function activeMomentSwitcherOptionsFromCreateCards(
  cards: PersonalCreateOptionCard[],
): PersonalMomentSwitcherOption[] {
  return cards
    .filter((c) => isActiveMoment(c) && c.moment_type_code !== "CUSTOM")
    .sort((a, b) => a.display_order - b.display_order)
    .map((c) => {
      const typeCode = asMomentTypeCode(c.moment_type_code);
      if (!typeCode) return null;
      return {
        typeCode,
        label: c.moment_type_name?.trim() || momentTypeLabel(typeCode),
        momentId: c.linked_moment_id ?? null,
      };
    })
    .filter((o): o is PersonalMomentSwitcherOption => o != null);
}

export function resolveMomentSwitcherOptions(
  momentsHome: PersonalMomentsHomeResponse | null | undefined,
  createOptions: PersonalCreateOptionCard[] | undefined,
): PersonalMomentSwitcherOption[] {
  const fromHome = momentsHome?.cards?.length
    ? activeMomentSwitcherOptionsFromHomeCards(momentsHome.cards)
    : [];
  const fromCreate = activeMomentSwitcherOptionsFromCreateCards(createOptions ?? []);

  const byType = new Map<PersonalMomentTypeCode, PersonalMomentSwitcherOption>();
  for (const option of fromCreate) {
    byType.set(option.typeCode, option);
  }
  for (const option of fromHome) {
    byType.set(option.typeCode, option);
  }

  const displayOrder = new Map<PersonalMomentTypeCode, number>();
  for (const card of momentsHome?.cards ?? []) {
    const typeCode = asMomentTypeCode(card.moment_type_code);
    if (typeCode) displayOrder.set(typeCode, card.display_order);
  }
  for (const card of createOptions ?? []) {
    const typeCode = asMomentTypeCode(card.moment_type_code);
    if (typeCode && !displayOrder.has(typeCode)) {
      displayOrder.set(typeCode, card.display_order);
    }
  }

  return Array.from(byType.values()).sort(
    (a, b) => (displayOrder.get(a.typeCode) ?? 999) - (displayOrder.get(b.typeCode) ?? 999),
  );
}

export function reconcileSelectedMomentType(
  options: PersonalMomentSwitcherOption[],
  current: PersonalMomentTypeCode,
  holdTypeCode?: PersonalMomentTypeCode | null,
): PersonalMomentTypeCode {
  if (options.length === 0) return current;
  if (options.some((o) => o.typeCode === current)) return current;
  if (holdTypeCode && holdTypeCode === current) return current;
  return options[0].typeCode;
}

export const ACTIVE_MOMENT_STATUSES = new Set(["ACTIVE", "PAUSED", "COMPLETED"]);

export function isActiveMomentStatus(status: string | null | undefined): boolean {
  return status != null && ACTIVE_MOMENT_STATUSES.has(status);
}

export function isDraftMoment(card: PersonalCreateOptionCard | null | undefined): boolean {
  return card?.linked_moment_status === "DRAFT" && card.linked_moment_id != null;
}

export function isActiveMoment(card: PersonalCreateOptionCard | null | undefined): boolean {
  return isActiveMomentStatus(card?.linked_moment_status);
}

export function activeCardForType(
  cards: PersonalCreateOptionCard[],
  typeCode: PersonalMomentTypeCode,
): PersonalCreateOptionCard | undefined {
  return cards.find((c) => momentTypeCodesEqual(c.moment_type_code, typeCode));
}

export function activeHomeCardForType(
  cards: PersonalMomentHomeCard[] | undefined,
  typeCode: PersonalMomentTypeCode,
): PersonalMomentHomeCard | undefined {
  return cards?.find((c) => momentTypeCodesEqual(c.moment_type_code, typeCode));
}

export type QuickAddGateSnapshot = {
  hasActiveMoment: boolean;
  momentId: string | null;
  resolverState: ResolvedScreen;
  bootstrapPulseState: string;
  bootstrapContextState: string;
};

export function resolveQuickAddGate(params: {
  momentTypeCode: PersonalMomentTypeCode;
  bootstrap: BootstrapResponse | null;
  createCards: PersonalCreateOptionCard[];
  homeCards?: PersonalMomentHomeCard[];
  pulse: PersonalPulseResponse | null;
  switcherOptions: PersonalMomentSwitcherOption[];
  lifeOpsDetailMomentId?: string | null;
}): QuickAddGateSnapshot {
  const {
    momentTypeCode,
    bootstrap,
    createCards,
    homeCards,
    pulse,
    switcherOptions,
    lifeOpsDetailMomentId,
  } = params;

  const createCard = activeCardForType(createCards, momentTypeCode);
  const homeCard = activeHomeCardForType(homeCards, momentTypeCode);
  const switcher = switcherOptions.find((o) => o.typeCode === momentTypeCode);
  const resolverState = resolveScreen("personal", "pulse", bootstrap);
  const bootstrapPulseState = moduleStateFromBootstrap(bootstrap, "pulse");
  const bootstrapContextState = contextStateFromBootstrap(bootstrap, "personal");

  const hasPulsePayload =
    pulse != null && !pulse.is_empty && pulseHasTypePayload(pulse, momentTypeCode);
  const hasActiveCreate = isActiveMoment(createCard);
  const hasActiveHome =
    homeCard?.is_active === true || isActiveMomentStatus(homeCard?.linked_moment_status);
  const hasActiveScreen =
    resolverState === "active_pulse" &&
    (hasPulsePayload || bootstrapPulseState === "ACTIVE");
  const hasBootstrapActive =
    bootstrapPulseState === "ACTIVE" &&
    bootstrapContextState === "ACTIVE" &&
    momentTypeCode === "LIFE_OPERATIONS";

  const hasActiveMoment =
    hasActiveCreate ||
    hasActiveHome ||
    hasPulsePayload ||
    hasActiveScreen ||
    (hasBootstrapActive && (hasPulsePayload || resolverState === "active_pulse"));

  const momentId =
    createCard?.linked_moment_id ??
    homeCard?.linked_moment_id ??
    switcher?.momentId ??
    (momentTypeCode === "LIFE_OPERATIONS" ? lifeOpsDetailMomentId ?? null : null) ??
    null;

  return {
    hasActiveMoment,
    momentId,
    resolverState,
    bootstrapPulseState,
    bootstrapContextState,
  };
}

export function logQuickAddGateBlocked(
  selectedType: PersonalMomentTypeCode,
  gate: QuickAddGateSnapshot,
): void {
  if (process.env.NODE_ENV !== "development") return;
  console.debug("QuickAddGate blocked:", {
    selectedType,
    resolverState: gate.resolverState,
    activeMomentId: gate.momentId,
    bootstrapState: {
      pulse: gate.bootstrapPulseState,
      context: gate.bootstrapContextState,
    },
  });
}

export function resolvePersonalMomentManageContext(
  typeCode: PersonalMomentTypeCode,
  createCards: PersonalCreateOptionCard[],
  homeCards?: PersonalMomentHomeCard[],
): PersonalMomentManageContext | null {
  const card = activeCardForType(createCards, typeCode);
  const homeCard = homeCards?.find((c) => momentTypeCodesEqual(c.moment_type_code, typeCode));
  const momentId = card?.linked_moment_id ?? homeCard?.linked_moment_id ?? null;
  if (!momentId) return null;
  const status = (card?.linked_moment_status ??
    homeCard?.linked_moment_status ??
    "ACTIVE") as PersonalMomentManageContext["status"];
  const momentName =
    card?.moment_type_name?.trim() ||
    homeCard?.moment_name?.trim() ||
    homeCard?.moment_type_name?.trim() ||
    momentTypeLabel(typeCode);
  return { momentId, typeCode, momentName, status };
}

export function pulseHasTypePayload(
  pulse: PersonalPulseResponse,
  typeCode: PersonalMomentTypeCode,
): boolean {
  switch (typeCode) {
    case "FUTURE_BUILDING":
      return pulse.future_building != null;
    case "LIFESTYLE":
      return pulse.lifestyle?.metrics != null;
    case "RELATIONSHIPS":
      return pulse.emotional_security != null;
    default:
      return pulse.life_operations != null;
  }
}

export function memoryHasTypePayload(
  memory: PersonalMemoryResponse,
  typeCode: PersonalMomentTypeCode,
): boolean {
  switch (typeCode) {
    case "FUTURE_BUILDING":
      return memory.future_building != null;
    case "LIFESTYLE":
      return memory.lifestyle?.metrics != null;
    case "RELATIONSHIPS":
      return memory.emotional_security != null;
    default:
      return memory.life_operations?.metrics != null;
  }
}

export function momentsHasTypePayload(
  moments: PersonalMomentsHomeResponse,
  typeCode: PersonalMomentTypeCode,
): boolean {
  switch (typeCode) {
    case "FUTURE_BUILDING":
      return moments.future_building_detail != null;
    case "LIFESTYLE":
      return moments.lifestyle_detail?.metrics != null;
    case "RELATIONSHIPS":
      return moments.emotional_security_detail != null;
    default:
      return moments.life_operations_detail?.metrics != null;
  }
}

export function templateMomentsEnabled(typeCode: PersonalMomentTypeCode): boolean {
  return (
    typeCode === "LIFE_OPERATIONS" ||
    typeCode === "FUTURE_BUILDING" ||
    typeCode === "LIFESTYLE" ||
    typeCode === "RELATIONSHIPS"
  );
}

export { momentTypeBadge, momentTypeLabel };

export function momentTypeActivatedMessage(typeCode: PersonalMomentTypeCode): string {
  return `${momentTypeLabel(typeCode)} activated`;
}

export function momentTypeOpenPulseMessage(typeCode: PersonalMomentTypeCode): string {
  return `${momentTypeLabel(typeCode)} is active — opening your Pulse`;
}

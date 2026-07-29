import type { SessionBootstrapResponse } from "@/lib/api/group";
import type { GroupMomentTypeCode } from "@/lib/group/groupMomentSession";
import { groupMomentTypeLabel, isGroupMomentTypeCode } from "@/lib/group/groupMomentSession";

export type GroupMomentSwitcherOption = {
  typeCode: GroupMomentTypeCode;
  label: string;
  momentId: string;
};

export type GroupMomentManageContext = {
  momentId: string;
  typeCode: GroupMomentTypeCode;
  momentName: string;
  status: string;
};

const ACTIVE_STATUSES = new Set(["ACTIVE", "PAUSED", "LIVE"]);

function normalizeStatus(value: string | null | undefined): string {
  return (value ?? "").trim().toUpperCase();
}

function isSwitcherEligible(status: string | null | undefined): boolean {
  const normalized = normalizeStatus(status);
  return ACTIVE_STATUSES.has(normalized) || normalized === "COMPLETED";
}

function typeDisplayOrder(typeCode: string): number {
  switch (typeCode) {
    case "SHARED_EXPERIENCE":
      return 1;
    case "SHARED_PURCHASE":
      return 2;
    case "SHARED_LIVING":
      return 3;
    default:
      return 99;
  }
}

function momentLabel(
  typeCode: string,
  name: string | null | undefined,
): string {
  const trimmed = name?.trim();
  if (trimmed && trimmed.length > 0) return trimmed;
  if (isGroupMomentTypeCode(typeCode)) return groupMomentTypeLabel(typeCode);
  return typeCode.replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function collectMomentItems(session: SessionBootstrapResponse) {
  const seen = new Set<string>();
  const items: Array<{
    id: string;
    moment_type?: string | null;
    lifecycle_status?: string | null;
    name?: string;
  }> = [];

  for (const source of [
    ...(session.live_overview?.live_cards ?? []),
    ...(session.moments ?? []),
  ]) {
    if (!source.id || seen.has(source.id)) continue;
    seen.add(source.id);
    items.push(source);
  }
  return items;
}

export function resolveGroupMomentSwitcherOptions(
  session: SessionBootstrapResponse | null | undefined,
): GroupMomentSwitcherOption[] {
  if (!session) return [];

  const byType = new Map<string, GroupMomentSwitcherOption>();

  for (const item of collectMomentItems(session)) {
    const typeCode = item.moment_type ?? "";
    if (!isGroupMomentTypeCode(typeCode)) continue;
    if (!isSwitcherEligible(item.lifecycle_status)) continue;

    byType.set(typeCode, {
      typeCode,
      label: momentLabel(typeCode, item.name),
      momentId: item.id,
    });
  }

  return Array.from(byType.values()).sort(
    (a, b) => typeDisplayOrder(a.typeCode) - typeDisplayOrder(b.typeCode),
  );
}

export function resolveGroupMomentManageContext(
  typeCode: GroupMomentTypeCode,
  session: SessionBootstrapResponse | null | undefined,
): GroupMomentManageContext | null {
  if (!session) return null;

  const option = resolveGroupMomentSwitcherOptions(session).find(
    (item) => item.typeCode === typeCode,
  );
  if (!option) return null;

  const item = collectMomentItems(session).find(
    (entry) => entry.id === option.momentId,
  );

  return {
    momentId: option.momentId,
    typeCode: option.typeCode,
    momentName: momentLabel(option.typeCode, item?.name ?? option.label),
    status: normalizeStatus(item?.lifecycle_status) || "ACTIVE",
  };
}

export function reconcileSelectedGroupMomentType(
  options: GroupMomentSwitcherOption[],
  current: GroupMomentTypeCode | "",
): GroupMomentTypeCode {
  if (options.length === 0) {
    // Keep create-default preference only; callers must not route ACTIVE on empty inventory.
    return (current || "SHARED_EXPERIENCE") as GroupMomentTypeCode;
  }
  if (current && options.some((item) => item.typeCode === current)) {
    return current;
  }
  return options[0]!.typeCode;
}

export function switcherOptionForType(
  options: GroupMomentSwitcherOption[],
  typeCode: GroupMomentTypeCode,
): GroupMomentSwitcherOption | null {
  return options.find((item) => item.typeCode === typeCode) ?? null;
}

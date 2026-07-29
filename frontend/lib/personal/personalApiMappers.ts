import type {
  PersonalMemoryResponse,
  PersonalMomentsHomeResponse,
  PersonalPulseResponse,
  TemplateMemoryResponse,
  TemplateMomentsResponse,
} from "@/lib/api/personal";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asRecord(value: unknown): Record<string, unknown> {
  return isRecord(value) ? value : {};
}

function asBoolean(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function asArray<T>(value: unknown): T[] {
  return Array.isArray(value) ? (value as T[]) : [];
}

function optionalRecord(value: unknown): Record<string, unknown> | undefined {
  return isRecord(value) ? value : undefined;
}

export function parsePersonalPulseResponse(raw: unknown): PersonalPulseResponse {
  const obj = asRecord(raw);
  return {
    overall_rhythm_state: asString(obj.overall_rhythm_state, "EMPTY"),
    active_moment_count: asNumber(obj.active_moment_count),
    is_empty: asBoolean(obj.is_empty, true),
    hero_title: typeof obj.hero_title === "string" ? obj.hero_title : null,
    hero_subtitle: typeof obj.hero_subtitle === "string" ? obj.hero_subtitle : null,
    journey_title: typeof obj.journey_title === "string" ? obj.journey_title : null,
    journey_subtitle: typeof obj.journey_subtitle === "string" ? obj.journey_subtitle : null,
    cta_label: typeof obj.cta_label === "string" ? obj.cta_label : null,
    life_operations: optionalRecord(obj.life_operations) as PersonalPulseResponse["life_operations"],
    future_building: optionalRecord(obj.future_building) as PersonalPulseResponse["future_building"],
    lifestyle: optionalRecord(obj.lifestyle) as PersonalPulseResponse["lifestyle"],
    emotional_security: optionalRecord(obj.emotional_security) as PersonalPulseResponse["emotional_security"],
  };
}

export function parsePersonalMomentsHomeResponse(raw: unknown): PersonalMomentsHomeResponse {
  const obj = asRecord(raw);
  return {
    active_moment_count: asNumber(obj.active_moment_count),
    is_empty: asBoolean(obj.is_empty, true),
    subtitle: asString(obj.subtitle),
    cards: asArray(obj.cards),
    life_operations_detail: optionalRecord(obj.life_operations_detail) as PersonalMomentsHomeResponse["life_operations_detail"],
    future_building_detail: optionalRecord(obj.future_building_detail) as PersonalMomentsHomeResponse["future_building_detail"],
    lifestyle_detail: optionalRecord(obj.lifestyle_detail) as PersonalMomentsHomeResponse["lifestyle_detail"],
    emotional_security_detail: optionalRecord(obj.emotional_security_detail) as PersonalMomentsHomeResponse["emotional_security_detail"],
  };
}

export function parsePersonalMemoryResponse(raw: unknown): PersonalMemoryResponse {
  const obj = asRecord(raw);
  return {
    is_empty: asBoolean(obj.is_empty, true),
    life_operations: optionalRecord(obj.life_operations) as PersonalMemoryResponse["life_operations"],
    future_building: optionalRecord(obj.future_building) as PersonalMemoryResponse["future_building"],
    lifestyle: optionalRecord(obj.lifestyle) as PersonalMemoryResponse["lifestyle"],
    emotional_security: optionalRecord(obj.emotional_security) as PersonalMemoryResponse["emotional_security"],
  };
}

export function parseTemplateMomentsResponse(raw: unknown): TemplateMomentsResponse {
  const obj = asRecord(raw);
  const setup = asRecord(obj.setup_summary);
  const accounts = asRecord(obj.accounts_summary);
  const progress = asRecord(obj.progress);
  return {
    projection_version: typeof obj.projection_version === "number" ? obj.projection_version : undefined,
    generated_at: typeof obj.generated_at === "string" ? obj.generated_at : undefined,
    moment_type_code: asString(obj.moment_type_code),
    status: asString(obj.status, "EMPTY") as TemplateMomentsResponse["status"],
    moment: (optionalRecord(obj.moment) ?? null) as TemplateMomentsResponse["moment"],
    moment_projection: optionalRecord(obj.moment_projection) as unknown as TemplateMomentsResponse["moment_projection"],
    setup_summary: {
      pressure_sources: asArray<string>(setup.pressure_sources),
      recovery_supports: asArray<string>(setup.recovery_supports),
      runtime_priorities: asArray<string>(setup.runtime_priorities),
      identity_chips: asArray<string>(setup.identity_chips),
    },
    recent_events: asArray(obj.recent_events),
    accounts_summary: {
      total_accounts: asNumber(accounts.total_accounts),
      active_accounts: asNumber(accounts.active_accounts),
      accounts: asArray(accounts.accounts),
    },
    timeline_count: asNumber(obj.timeline_count),
    last_activity_at: typeof obj.last_activity_at === "string" ? obj.last_activity_at : null,
    progress: {
      label: asString(progress.label),
      subtitle: asString(progress.subtitle),
      blocks: asArray(progress.blocks),
    },
  };
}

export function parseTemplateMemoryResponse(raw: unknown): TemplateMemoryResponse {
  const obj = asRecord(raw);
  return {
    projection_version: typeof obj.projection_version === "number" ? obj.projection_version : undefined,
    generated_at: typeof obj.generated_at === "string" ? obj.generated_at : undefined,
    moment_type_code: asString(obj.moment_type_code),
    status: asString(obj.status, "EMPTY"),
    memory_projection: optionalRecord(obj.memory_projection) as unknown as TemplateMemoryResponse["memory_projection"],
    memories: asArray(obj.memories),
    patterns: asArray(obj.patterns),
    insights: asArray(obj.insights),
    timeline: asArray(obj.timeline),
  };
}

export function parseTemplatePulseResponse(raw: unknown): Record<string, unknown> {
  return asRecord(raw);
}

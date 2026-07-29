import type { GroupLifeSatelliteScore } from "@/lib/api/groupLife";
import { requestWithRetry } from "@/lib/api/client";

// Setup endpoints
export type ProfileOption = {
  profile_code: string;
  profile_name: string;
  profile_description: string | null;
  display_order: number;
};

export type Step1Response = {
  moment_id: string;
  moment_type: string;
  moment_profile: string;
};

export type Step2Input = {
  moment_name: string;
  detail_fields: Record<string, any>;
};

export type MemberInput = {
  display_name: string;
  role_code: string;
};

export type Step3Input = {
  members: MemberInput[];
};

export type Step4Input = {
  activate: boolean;
};

export type SetupStatus = {
  moment_id: string;
  moment_type: string;
  moment_profile: string;
  moment_name: string;
  status: string;
  stage: string;
  setup_step: string;
};

// QuickAdd endpoints
export type QuickAddSectionModule = {
  module_code: string;
  module_label: string;
  category: string | null;
  display_order: number;
};

export type QuickAddResponse = {
  moment_id: string;
  moment_type: string;
  moment_profile: string;
  sections: Record<string, QuickAddSectionModule[]>;
};

// Active endpoints
export type ActivePulseResponse = {
  moment_id: string;
  moment_type: string;
  moment_profile: string;
  moment_name: string;
  status: string;
  stage: string;
  pulse_data: Record<string, any>;
  health_data: Record<string, any>;
  signals: Array<{
    signal_id: string;
    signal_type: string;
    signal_category: string;
    signal_title: string;
    signal_description: string | null;
    priority: string;
    signal_score: number | null;
  }>;
  recommendations: Array<{
    recommendation_id: string;
    recommendation_type: string;
    recommendation_category: string;
    title: string;
    description: string | null;
    priority: string;
    recommendation_score: number | null;
  }>;
  recent_events: Array<{
    event_id: string;
    module_code: string;
    event_action: string;
    event_time: string | null;
  }>;
};

export type ActiveMomentsResponse = {
  moment_id: string;
  moment_type: string;
  moment_profile: string;
  moment_name: string;
  status: string;
  stage: string;
  memories: Array<{
    memory_id: string;
    memory_type: string;
    category: string;
    title: string;
    description: string | null;
    memory_date: string | null;
    created_at: string | null;
    highlight_score: number | null;
  }>;
  recent_events: Array<{
    event_id: string;
    module_code: string;
    event_action: string;
    event_time: string | null;
  }>;
  updates: Array<{
    update_id: string;
    category: string;
    title: string;
    description: string;
    status: string;
    created_at: string | null;
  }>;
};

export type GroupMomentsStatTile = {
  label: string;
  value: string;
  highlight?: boolean;
};

export type TripMomentsMemoryHero = {
  eyebrow: string;
  title: string;
  subtitle: string;
  cover_image_url?: string | null;
  primary_cta_label?: string;
  secondary_cta_label?: string;
};

export type GroupMomentsOperationsHub = {
  core_summary: {
    eyebrow: string;
    eyebrow_icon?: string;
    moment_name: string;
    stage_badge: string;
    stat_tiles?: GroupMomentsStatTile[];
  };
  people_roles?: {
    primary?: {
      display_name: string;
      role_label: string;
      avatar_url?: string | null;
    } | null;
    role_counts?: Array<{ label: string; count: number }>;
  };
  money_status?: {
    progress_label: string;
    progress_percent: number;
    columns?: Array<{ label: string; value: string; highlight?: boolean }>;
  };
  activity_ops?: Array<{ tile_id?: string; label: string; value: string; icon?: string }>;
  assets?: Array<{ asset_id?: string; label: string; count: number; icon?: string }>;
  decisions?: Array<{ decision_id?: string; title: string; status_label: string; icon?: string; is_active?: boolean }>;
  current_state?: {
    stage_label: string;
    focus_items?: Array<{ label: string; is_complete?: boolean }>;
    cta_label?: string;
  };
};

export type GroupMemoryHub = {
  hero: {
    moment_name: string;
    cover_image_url?: string | null;
    chips?: Array<{ icon: string; label: string }>;
  };
  timeline?: Array<{ event_id?: string; title: string; date_label?: string; is_complete?: boolean }>;
  milestone_wall?: Array<{ milestone_id?: string; label: string; icon?: string }>;
  people_impact?: Array<{ display_name: string; impact_label: string; avatar_url?: string | null }>;
  gallery?: Array<{ memory_id?: string; title: string; image_url?: string | null }>;
  lessons_pattern?: string;
  group_identity?: string;
  highlights?: Array<{ highlight_id?: string; label: string; icon?: string }>;
  intelligence?: { metrics?: Array<{ label: string; value: string }>; insight?: string };
  budget_reflection?: {
    planned_budget: string;
    actual_spend: string;
    budget_accuracy: string;
    summary?: string;
  } | null;
};

export type TripMomentsViewResponse = {
  moment_id: string;
  trip_name: string;
  stage_badge: string;
  status_badge: string;
  memory_hero: TripMomentsMemoryHero;
  operations_hub: GroupMomentsOperationsHub;
  memory_hub: GroupMemoryHub;
  captured_memories?: Array<{
    id: string;
    card_type?: string;
    title: string;
    body?: string;
    image_url?: string | null;
  }>;
  memory_feed?: Array<{
    id: string;
    timestamp_label?: string;
    icon?: string;
    accent?: string;
    title: string;
    subtitle?: string;
    activity_type?: string;
  }>;
};

export type TripPulseStats = {
  participants_joined?: number;
  members_joined?: number;
  guests_joined?: number;
  participants_expected?: number | null;
  active_plan_items?: number;
  confirmed_bookings?: number;
  total_expenses_minor?: number;
  total_expenses_currency?: string;
  total_budget_minor?: number;
  contributions_minor?: number;
  contributions_currency?: string;
  corpus_balance_minor?: number;
  open_polls?: number;
  memories_count?: number;
  updated_at_display?: { label?: string; minutes_ago?: number };
};

export type TripPulseResponse = {
  moment_id: string;
  trip_name: string;
  stage_badge: string;
  status_badge?: string;
  readiness_score?: number;
  readiness_title?: string;
  readiness_narrative?: string;
  experience_health_percent?: number;
  participation_percent?: number;
  days_remaining?: number | null;
  attention_items?: Array<{ id: string; title: string; icon: string; accent: string; action: string }>;
  health_dimensions?: Array<{ label: string; percent: number; status?: string }>;
  insights?: Array<{ id: string; title: string; subtitle?: string; icon?: string }>;
  next_best_action?: { title: string; subtitle: string; action: string; impact_labels?: string[] } | null;
  dashboard_card?: {
    recent_items?: Array<{
      id: string;
      title: string;
      subtitle?: string;
      relative_time?: string;
      activity_type?: string;
    }>;
  } | null;
  participation_breakdown?: { active: number; pending: number; inactive: number };
  stats: TripPulseStats;
};

export type ActiveMemoryResponse = {
  moment_id: string;
  moment_type: string;
  moment_profile: string;
  moment_name: string;
  status: string;
  stage: string;
  memories: Array<{
    memory_id: string;
    memory_type: string;
    category: string;
    title: string;
    description: string | null;
    memory_date: string | null;
    created_at: string | null;
    highlight_score: number | null;
  }>;
  patterns: Array<{
    pattern_id: string;
    pattern_type: string;
    pattern_category: string;
    insight_title: string;
    insight_text: string | null;
    confidence_score: number;
    trend_direction: string | null;
  }>;
  insights: Array<{
    insight_id: string;
    insight_layer: string;
    insight_type: string;
    insight_title: string;
    insight_body: string;
    confidence_level: string | null;
    created_at: string | null;
  }>;
};

export type ActiveLifeResponse = {
  is_empty: boolean;
  active_moment_count: number;
  moments: Array<{
    moment_id: string;
    moment_type: string;
    moment_profile: string;
    moment_name: string;
    status: string;
    stage: string;
    health_data: Record<string, any>;
    journey_data: Record<string, any>;
  }>;
  insights: Array<{
    insight_id: string;
    moment_id: string | null;
    insight_layer: string;
    insight_type: string;
    insight_title: string;
    insight_body: string;
    confidence_level: string | null;
    created_at: string | null;
  }>;
};

// Session endpoints
export type GroupSessionMomentItem = {
  id: string;
  name?: string;
  moment_type?: string | null;
  lifecycle_status?: string | null;
};

export type GroupSessionTypeCard = {
  moment_type_code?: string;
  linked_moment_id?: string | null;
  linked_moment_status?: string | null;
};

export type SessionBootstrapResponse = {
  is_empty: boolean;
  active_moment_count: number;
  active_moment_id: string | null;
  moment_type: string | null;
  moment_profile: string | null;
  setup_step: string;
  create_options: Array<{
    moment_type_id: string;
    moment_type_code: string;
    moment_type_name: string;
    create_tagline: string | null;
    description: string | null;
    icon_name: string | null;
    image_url: string | null;
    accent_main: string | null;
    accent_soft_tint: string | null;
    card_layout: string | null;
    display_order: number;
    coming_soon: boolean;
  }>;
  pulse_data: Record<string, any> | null;
  moments_data: Record<string, any> | null;
  memory_data: Record<string, any> | null;
  draft_moment_id?: string | null;
  draft_moment_type?: string | null;
  has_draft?: boolean;
  linked_moment_status?: string | null;
  focus_moment_id?: string | null;
  moments?: GroupSessionMomentItem[];
  live_overview?: {
    live_cards?: GroupSessionMomentItem[];
  };
  pulse?: {
    type_cards?: GroupSessionTypeCard[];
  };
};

export type GroupSessionResponse = {
  is_empty: boolean;
  active_moment_count: number;
  focus_moment_id?: string | null;
  active_moment_id?: string | null;
  moment_type?: string | null;
  draft_moment_id?: string | null;
  draft_moment_type?: string | null;
  has_draft?: boolean;
  linked_moment_status?: string | null;
};

export type GroupInventoryResponse = {
  pulse: NonNullable<SessionBootstrapResponse["pulse"]>;
  moments: GroupSessionMomentItem[];
  live_overview?: SessionBootstrapResponse["live_overview"];
};

export type GroupSharedCategory = "experience" | "purchase" | "living";

export type GroupDraftCreateResponse = {
  moment_id: string;
  moment_type_code: string;
  lifecycle_status?: string;
};

export type GroupSharedSetupState = {
  moment_id: string;
  moment_type_code: string;
  moment_name?: string;
  living_name?: string;
  status?: string;
  lifecycle_status?: string;
  saved_answers?: Record<string, unknown> | null;
  fields?: unknown[];
  title?: string | null;
  subtitle?: string | null;
  background_image_url?: string | null;
  mission?: { badge_label: string; title: string; body: string } | null;
  cta_label?: string | null;
  footer_note?: string | null;
  [key: string]: unknown;
};

export type GroupSharedPreview = {
  insight_text?: string;
  narrative?: string;
  preview_blocks?: Array<{ label: string; value: string | null }>;
  identity_chips?: string[];
  runtime_priorities?: string[];
  [key: string]: unknown;
};

function sharedBase(category: GroupSharedCategory): string {
  return `api/v1/group/shared-${category}`;
}

export async function createGroupSharedDraft(
  category: GroupSharedCategory,
  body: Record<string, string>,
): Promise<GroupDraftCreateResponse> {
  return requestWithRetry<GroupDraftCreateResponse>(`${sharedBase(category)}/moments`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function getGroupSharedSetup(
  category: GroupSharedCategory,
  momentId: string,
): Promise<GroupSharedSetupState> {
  return requestWithRetry<GroupSharedSetupState>(
    `${sharedBase(category)}/moments/${momentId}/setup`,
    { method: "GET" },
  );
}

export async function saveGroupSharedDraft(
  category: GroupSharedCategory,
  momentId: string,
  answers: Record<string, unknown>,
): Promise<GroupSharedSetupState> {
  return requestWithRetry<GroupSharedSetupState>(
    `${sharedBase(category)}/moments/${momentId}/setup/draft`,
    { method: "PUT", body: JSON.stringify(answers) },
  );
}

export async function previewGroupSharedSetup(
  category: GroupSharedCategory,
  momentId: string,
): Promise<GroupSharedPreview> {
  return requestWithRetry<GroupSharedPreview>(
    `${sharedBase(category)}/moments/${momentId}/setup/preview`,
    { method: "GET" },
  );
}

export async function activateGroupSharedSetup(
  category: GroupSharedCategory,
  momentId: string,
): Promise<{ moment_id: string; lifecycle_status: string }> {
  return requestWithRetry(`${sharedBase(category)}/moments/${momentId}/setup/activate`, {
    method: "POST",
  });
}

export type InviteDraft = {
  invite_link: string;
  invite_code: string;
  qr_payload: string;
  email_subject: string;
  email_body: string;
  whatsapp_text: string;
  sms_text: string;
  experience_name?: string | null;
  expires_at?: string | null;
  invite_id?: string | null;
  participant_id?: string | null;
  status?: string | null;
};

export type EmailInviteResult = {
  id: string;
  moment_id: string;
  invitee_email: string;
  status: string;
  expires_at: string;
  created_at: string;
  sent: boolean;
  invite_link?: string | null;
  email_subject?: string | null;
  email_body?: string | null;
  send_error?: string | null;
};

export async function getInviteDraft(
  momentId: string,
  participantId?: string | null,
): Promise<InviteDraft> {
  const qs = participantId ? `?participant_id=${encodeURIComponent(participantId)}` : "";
  return requestWithRetry<InviteDraft>(`api/v1/moments/${momentId}/invite-draft${qs}`, {
    method: "GET",
  });
}

export async function refreshInviteDraft(
  momentId: string,
  participantId?: string | null,
): Promise<InviteDraft> {
  return requestWithRetry<InviteDraft>(`api/v1/moments/${momentId}/invite-draft/refresh`, {
    method: "POST",
    body: JSON.stringify({ participant_id: participantId ?? null }),
  });
}

export async function recordInviteChannel(
  momentId: string,
  channel: string,
  opts?: { participantId?: string | null; inviteId?: string | null },
): Promise<{ ok: boolean; invite_id?: string; channel?: string }> {
  return requestWithRetry(`api/v1/moments/${momentId}/invite-channel`, {
    method: "POST",
    body: JSON.stringify({
      channel,
      participant_id: opts?.participantId ?? null,
      invite_id: opts?.inviteId ?? null,
    }),
  });
}

export async function createEmailInvite(
  momentId: string,
  email: string,
  participantId?: string | null,
): Promise<EmailInviteResult> {
  return requestWithRetry<EmailInviteResult>(`api/v1/moments/${momentId}/email-invites`, {
    method: "POST",
    body: JSON.stringify({ email, participant_id: participantId ?? null }),
  });
}

export type InviteAcceptResult = {
  moment_id: string;
  moment_name: string;
  moment_type?: string | null;
  already_member?: boolean;
  participant_id?: string | null;
};

export async function acceptInvite(token: string): Promise<InviteAcceptResult> {
  return requestWithRetry<InviteAcceptResult>(
    `api/v1/invites/${encodeURIComponent(token)}/accept`,
    { method: "POST" },
  );
}

// Setup API functions
export async function getSetupProfiles(momentType: string): Promise<ProfileOption[]> {
   return requestWithRetry<ProfileOption[]>(`/api/v1/group/setup/profiles`);
}

export async function setupBasics(
   momentType: string,
   body: Step2Input
 ): Promise<Step1Response> {
   return requestWithRetry<Step1Response>(`/api/v1/group/setup/${momentType}/basics`, {
     method: "POST",
     body: JSON.stringify(body),
   });
 }

 export async function setupPeople(
   momentType: string,
   momentId: string,
   body: Step3Input
 ): Promise<SetupStatus> {
   return requestWithRetry<SetupStatus>(`/api/v1/group/setup/${momentType}/people/${momentId}`, {
     method: "POST",
     body: JSON.stringify(body),
   });
 }

 export async function getSetupReview(momentId: string): Promise<SetupStatus> {
   return requestWithRetry<SetupStatus>(`/api/v1/group/setup/review/${momentId}`);
 }

 export async function activateMoment(
   momentId: string,
   body: Step4Input
 ): Promise<SetupStatus> {
   return requestWithRetry<SetupStatus>(`/api/v1/group/setup/activate/${momentId}`, {
     method: "POST",
     body: JSON.stringify(body),
   });
 }

 // Active API functions
 export async function getActivePulse(
  momentId: string,
  forceRefresh = false,
): Promise<ActivePulseResponse> {
   const qs = forceRefresh ? "?force_refresh=true" : "";
   return requestWithRetry<ActivePulseResponse>(
     `/api/v1/group/active/pulse/${momentId}${qs}`,
   );
 }

 export async function getActiveMoments(
  momentId: string,
  forceRefresh = false,
): Promise<ActiveMomentsResponse> {
   const qs = forceRefresh ? "?force_refresh=true" : "";
   return requestWithRetry<ActiveMomentsResponse>(
     `/api/v1/group/active/moments/${momentId}${qs}`,
   );
 }

 export async function getTripMomentsView(
  momentId: string,
  forceRefresh = false,
): Promise<TripMomentsViewResponse> {
   const qs = forceRefresh ? "?force_refresh=true" : "";
   return requestWithRetry<TripMomentsViewResponse>(
     `/api/v1/group/trips/${momentId}/moments-view${qs}`,
   );
 }

 export async function getTripPulse(
  momentId: string,
  forceRefresh = false,
): Promise<TripPulseResponse> {
   const qs = forceRefresh ? "?force_refresh=true" : "";
   return requestWithRetry<TripPulseResponse>(
     `/api/v1/group/trips/${momentId}/pulse${qs}`,
   );
 }

export type PurchasePulseResponse = {
  moment_id: string;
  moment_name: string;
  profile_badge: string;
  stage_badge: string;
  status_badge?: string;
  funding_percent: number;
  funded_amount_minor: number;
  target_amount_minor?: number;
  amount_remaining_minor?: number;
  currency_code?: string;
  readiness_score?: number;
  readiness_title?: string;
  readiness_narrative?: string;
  contributor_count?: number;
  experience_health_percent?: number;
  participation_percent?: number;
  attention_items?: Array<{ id: string; title: string; subtitle?: string; icon: string; accent: string; action: string }>;
  health_dimensions?: Array<{ label: string; percent: number; status?: string }>;
  insights?: Array<{ id: string; title: string; subtitle?: string; icon?: string }>;
  next_best_action?: { title: string; subtitle: string; action: string; impact_labels?: string[] } | null;
  metric_tiles?: Array<{ label: string; value: string }>;
  recent_activity?: Array<{ id: string; title: string; subtitle?: string; relative_time?: string }>;
  participation_breakdown?: { active: number; pending: number; inactive: number };
  dashboard_card?: {
    recent_items?: Array<{ id: string; title: string; subtitle?: string; relative_time?: string }>;
  } | null;
  stats: {
    contributors_joined?: number;
    vendors?: number;
    items_finalized?: number;
    contributions_minor?: number;
    ownership_status?: string;
    updated_at_display?: { label?: string; minutes_ago?: number };
  };
};

export type PurchaseMomentsViewResponse = {
  moment_id: string;
  moment_name: string;
  profile_badge: string;
  stage_badge: string;
  status_badge: string;
  funding_percent?: number;
  funded_amount_minor?: number;
  contributor_count?: number;
  memory_hero_title?: string;
  memory_hero_subtitle?: string;
  operations_hub: GroupMomentsOperationsHub;
  memory_hub: GroupMemoryHub;
};

export async function getPurchasePulse(
  momentId: string,
  forceRefresh = false,
): Promise<PurchasePulseResponse> {
  const qs = forceRefresh ? "?force_refresh=true" : "";
  return requestWithRetry<PurchasePulseResponse>(
    `/api/v1/group/shared-purchase/moments/${momentId}/pulse${qs}`,
  );
}

export async function getPurchaseMomentsView(
  momentId: string,
  forceRefresh = false,
): Promise<PurchaseMomentsViewResponse> {
  const qs = forceRefresh ? "?force_refresh=true" : "";
  return requestWithRetry<PurchaseMomentsViewResponse>(
    `/api/v1/group/shared-purchase/moments/${momentId}/moments-view${qs}`,
  );
}

export type LivingPulseResponse = {
  moment_id: string;
  moment_name: string;
  profile_badge: string;
  stage_badge: string;
  status_badge?: string;
  health_percent?: number;
  expenses_total_minor?: number;
  contributions_total_minor?: number;
  outstanding_minor?: number;
  currency_code?: string;
  readiness_score?: number;
  readiness_title?: string;
  readiness_narrative?: string;
  resident_count?: number;
  experience_health_percent?: number;
  participation_percent?: number;
  attention_items?: Array<{ id: string; title: string; subtitle?: string; icon: string; accent: string; action: string }>;
  health_dimensions?: Array<{ label: string; percent: number; status?: string }>;
  insights?: Array<{ id: string; title: string; subtitle?: string; icon?: string }>;
  next_best_action?: { title: string; subtitle: string; action: string; impact_labels?: string[] } | null;
  metric_tiles?: Array<{ label: string; value: string }>;
  recent_activity?: Array<{
    id: string;
    title: string;
    subtitle?: string;
    relative_time?: string;
    activity_type?: string;
    icon?: string;
  }>;
  participation_breakdown?: { active: number; pending: number; inactive: number };
  dashboard_card?: {
    recent_items?: Array<{
      id: string;
      title: string;
      subtitle?: string;
      relative_time?: string;
      activity_type?: string;
      icon?: string;
    }>;
  } | null;
  operations_progress?: { label?: string; percent?: number; subtitle?: string } | null;
  stats: {
    residents_joined?: number;
    expenses_logged?: number;
    total_expenses_minor?: number;
    contributions_minor?: number;
    tasks_open?: number;
    open_polls?: number;
    rules_count?: number;
    assets_count?: number;
  };
};

export type LivingMomentsViewResponse = {
  moment_id: string;
  moment_name: string;
  profile_badge: string;
  stage_badge: string;
  status_badge: string;
  health_percent?: number;
  expenses_total_minor?: number;
  resident_count?: number;
  memory_hero_title?: string;
  memory_hero_subtitle?: string;
  operations_hub: GroupMomentsOperationsHub;
  memory_hub: GroupMemoryHub;
};

export async function getLivingPulse(
  momentId: string,
  forceRefresh = false,
): Promise<LivingPulseResponse> {
  const qs = forceRefresh ? "?force_refresh=true" : "";
  return requestWithRetry<LivingPulseResponse>(
    `/api/v1/group/shared-living/moments/${momentId}/pulse${qs}`,
  );
}

export type LivingActivityItem = {
  id: string;
  activity_type: string;
  ref_id?: string | null;
  title: string;
  subtitle: string;
  icon: string;
  occurred_at: string;
  relative_time?: string;
  edit_event_type: string;
  can_edit: boolean;
  can_delete: boolean;
};

export type LivingActivityListResponse = {
  moment_id: string;
  items: LivingActivityItem[];
  summary?: { total?: number };
};

export async function listLivingActivity(momentId: string): Promise<LivingActivityListResponse> {
  return requestWithRetry<LivingActivityListResponse>(
    `/api/v1/group/shared-living/moments/${momentId}/activity`,
  );
}

export async function getLivingActivityDetail(
  momentId: string,
  eventId: string,
): Promise<LivingActivityItem> {
  return requestWithRetry<LivingActivityItem>(
    `/api/v1/group/shared-living/moments/${momentId}/activity/${eventId}`,
  );
}

export async function patchLivingActivity(
  momentId: string,
  eventId: string,
  body: { title?: string; subtitle?: string; occurred_at?: string },
): Promise<LivingActivityItem> {
  return requestWithRetry<LivingActivityItem>(
    `/api/v1/group/shared-living/moments/${momentId}/activity/${eventId}`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export async function deleteLivingActivity(momentId: string, eventId: string): Promise<{ status: string }> {
  return requestWithRetry<{ status: string }>(
    `/api/v1/group/shared-living/moments/${momentId}/activity/${eventId}`,
    { method: "DELETE" },
  );
}

/** Shared Experience / trip activity — same shape as living. */
export async function listTripActivity(momentId: string): Promise<LivingActivityListResponse> {
  return requestWithRetry<LivingActivityListResponse>(
    `/api/v1/group/trips/${momentId}/activity`,
  );
}

export async function getTripActivityDetail(
  momentId: string,
  eventId: string,
): Promise<LivingActivityItem> {
  return requestWithRetry<LivingActivityItem>(
    `/api/v1/group/trips/${momentId}/activity/${eventId}`,
  );
}

export async function patchTripActivity(
  momentId: string,
  eventId: string,
  body: { title?: string; subtitle?: string; occurred_at?: string },
): Promise<LivingActivityItem> {
  return requestWithRetry<LivingActivityItem>(
    `/api/v1/group/trips/${momentId}/activity/${eventId}`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export async function deleteTripActivity(momentId: string, eventId: string): Promise<{ status: string }> {
  return requestWithRetry<{ status: string }>(
    `/api/v1/group/trips/${momentId}/activity/${eventId}`,
    { method: "DELETE" },
  );
}

export async function getLivingMomentsView(
  momentId: string,
  forceRefresh = false,
): Promise<LivingMomentsViewResponse> {
  const qs = forceRefresh ? "?force_refresh=true" : "";
  return requestWithRetry<LivingMomentsViewResponse>(
    `/api/v1/group/shared-living/moments/${momentId}/moments-view${qs}`,
  );
}

 export async function getActiveMemory(
  momentId: string,
  forceRefresh = false,
): Promise<ActiveMemoryResponse> {
   const qs = forceRefresh ? "?force_refresh=true" : "";
   return requestWithRetry<ActiveMemoryResponse>(
     `/api/v1/group/active/memory/${momentId}${qs}`,
   );
 }

 export async function getActiveLife(): Promise<ActiveLifeResponse> {
   return requestWithRetry<ActiveLifeResponse>(`/api/v1/group/active/life`);
 }

 // QuickAdd API functions
 export async function getQuickAddConfig(momentId: string): Promise<QuickAddResponse> {
   return requestWithRetry<QuickAddResponse>(`/api/v1/group/quickadd/${momentId}`);
 }

 // Session API functions
 export async function getGroupSession(): Promise<GroupSessionResponse> {
   return requestWithRetry<GroupSessionResponse>(`/api/v1/group/session`);
 }

 export async function getGroupInventory(): Promise<GroupInventoryResponse> {
   return requestWithRetry<GroupInventoryResponse>(`/api/v1/group/inventory`);
 }

 export async function getSessionBootstrap(): Promise<SessionBootstrapResponse> {
   return requestWithRetry<SessionBootstrapResponse>(`/api/v1/group/session/bootstrap`);
 }

// Settlement API
export type SettlementPreview = {
  moment_id: string;
  currency_code: string;
  total_expenses_minor: number;
  member_balances: Array<{ member_id: string; display_name: string; paid_minor: number; owed_minor: number; net_minor: number; currency_code: string }>;
  suggestions: Array<{ from_member_id: string; to_member_id: string; from_display_name: string; to_display_name: string; amount_minor: number; currency_code: string; reason?: string }>;
  harmony_label: string;
  balance_insight: string;
  status: string;
};

export type SettlementRecord = {
  id: string;
  moment_id: string;
  from_member_id: string;
  to_member_id: string;
  amount_minor: number;
  currency_code: string;
  status: string;
  description?: string | null;
  created_at: string;
  updated_at: string;
  settled_at?: string | null;
};

export async function getSettlementPreview(momentId: string): Promise<SettlementPreview> {
  return requestWithRetry<SettlementPreview>(`/api/v1/group/moments/${momentId}/settlements/preview`);
}

export async function listSettlements(momentId: string): Promise<{ moment_id: string; currency_code: string; settlements: SettlementRecord[] }> {
  return requestWithRetry(`/api/v1/group/moments/${momentId}/settlements`);
}

export async function markSettlementSettled(momentId: string, settlementId: string): Promise<SettlementRecord> {
  return requestWithRetry<SettlementRecord>(`/api/v1/group/moments/${momentId}/settlements/${settlementId}/mark-settled`, {
    method: "POST",
  });
}

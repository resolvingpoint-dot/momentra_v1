export type BusinessMomentTypeCard = {
  moment_type_id: string;
  moment_type_code: string;
  moment_type_name: string;
  description?: string | null;
  create_tagline?: string | null;
  badge_label?: string | null;
  icon_name?: string | null;
  accent_main?: string | null;
  accent_soft_tint?: string | null;
  card_layout?: string | null;
  display_order: number;
  linked_moment_id?: string | null;
  linked_moment_status?: string | null;
  /** Personal parity: ACTIVE / PAUSED / COMPLETED linked moment. */
  is_active?: boolean;
  cover_image_url?: string | null;
  action_label: string;
  action_style?: string;
};

export type BusinessCreateOptionCard = {
  moment_type_id: string;
  moment_type_code: string;
  moment_type_name: string;
  create_tagline?: string | null;
  description?: string | null;
  icon_name?: string | null;
  accent_main?: string | null;
  accent_soft_tint?: string | null;
  badge_label?: string | null;
  cover_image_url?: string | null;
  card_layout?: string | null;
  display_order: number;
  linked_moment_id?: string | null;
  linked_moment_status?: string | null;
  is_active?: boolean;
  is_selected?: boolean;
  is_available?: boolean;
  implementation_status?: string;
};

export type BusinessMomentResponse = {
  moment_id: string;
  moment_type_id: string;
  moment_type_code?: string | null;
  moment_name: string;
  moment_description?: string | null;
  status: string;
  cover_image_url?: string | null;
  workspace_id?: string | null;
};

export type BusinessWorkspaceSummary = {
  id: string;
  name: string;
  logo?: string | null;
  role: string;
  currency?: string;
  timezone?: string;
  industry?: string | null;
  status?: string;
};

export type BusinessModuleTile = {
  key: string;
  label: string;
  status: string;
  description?: string | null;
};

export type BusinessDashboardSummary = {
  open_moments: number;
  pending_approvals: number;
  member_count: number;
  revenue_today?: number | null;
  cash_balance?: number | null;
};

export type BusinessMomentsHomeResponse = {
  is_empty: boolean;
  active_moment_count: number;
  cards: BusinessMomentTypeCard[];
};

export type BusinessCreateOptionsResponse = {
  is_empty: boolean;
  active_moment_count: number;
  cards: BusinessCreateOptionCard[];
};

export type BusinessSessionBootstrapResponse = {
  moments_home: BusinessMomentsHomeResponse;
  /** Workspace-scoped visible BUSINESS moments. */
  moments?: BusinessMomentResponse[];
  selected_workspace?: BusinessWorkspaceSummary | null;
  workspaces?: BusinessWorkspaceSummary[];
  module_tiles?: BusinessModuleTile[];
  dashboard?: BusinessDashboardSummary;
};

export type BusinessSessionResponse = {
  selected_workspace?: BusinessWorkspaceSummary | null;
  workspaces?: BusinessWorkspaceSummary[];
  module_tiles?: BusinessModuleTile[];
};

export type BusinessWorkspaceOverviewResponse = {
  workspace_id: string;
  dashboard?: BusinessDashboardSummary;
  recent_moments?: BusinessMomentResponse[];
};

export type BusinessWorkspaceMomentsResponse = {
  workspace_id: string;
  moments_home?: BusinessMomentsHomeResponse;
  moments?: BusinessMomentResponse[];
};

export type BusinessSetupProgress = {
  current_step: number;
  completed_steps: number[];
};

export type BusinessSetupState = {
  moment_id: string;
  moment_type_code: string;
  status: string;
  template_id: string;
  template_version: string;
  setup_version: string;
  answers: Record<string, unknown>;
  progress: BusinessSetupProgress;
  membership?: Array<{
    user_id: string;
    role: string;
    status: string;
    invitation_status: string;
  }>;
  updated_at?: string | null;
};

export type BusinessSetupPreview = {
  template_id?: string | null;
  moment_type_code?: string | null;
  summary_blocks: Array<{
    block_id: string;
    title: string;
    body?: string | null;
    items?: Array<{ label: string; value?: unknown }>;
  }>;
  warnings: string[];
  blocking_errors?: string[];
  activation_ready: boolean;
};

export type BusinessMomentCreateResponse = BusinessSetupState & {
  moment_type_id: string;
  moment_name: string;
  moment_description?: string | null;
  cover_image_url?: string | null;
};

export type BusinessActivateResponse = {
  moment_id: string;
  moment_type_code: string;
  status: string;
  activated_at?: string | null;
  membership?: BusinessSetupState["membership"];
  projection_status?: "READY" | "REFRESHING";
};

export type BusinessSetupInviteDraft = {
  invite_id: string;
  local_id: string;
  channel: string;
  invite_link: string;
  invite_code: string;
  qr_payload: string;
  email_subject?: string | null;
  email_body?: string | null;
  whatsapp_text?: string | null;
  sms_text?: string | null;
  expires_at?: string | null;
};

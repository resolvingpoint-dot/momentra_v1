CREATE TABLE business_moments (
																    moment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    moment_type VARCHAR(50) NOT NULL,
																
																    moment_name VARCHAR(255) NOT NULL,
																
																    status VARCHAR(30) NOT NULL DEFAULT 'draft',
																
																    created_by UUID NOT NULL,
																
																    activated_at TIMESTAMP NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_business_moment_type
																    CHECK (
																        moment_type IN (
																            'team_operations',
																            'project_operations',
																            'event_operations',
																            'department_operations',
																            'business_runway',
																            'vendor_operations',
																            'custom_operational_moment'
																        )
																    ),
																
																    CONSTRAINT chk_business_moment_status
																    CHECK (
																        status IN (
																            'draft',
																            'configured',
																            'active',
																            'completed',
																            'archived'
																        )
																    )
																);
-- >>>STMT<<<
CREATE INDEX idx_business_moments_workspace
																ON business_moments(workspace_id);
-- >>>STMT<<<
CREATE INDEX idx_business_moments_status
																ON business_moments(status);
-- >>>STMT<<<
CREATE INDEX idx_business_moments_type
																ON business_moments(moment_type);
-- >>>STMT<<<
CREATE TABLE business_moment_setup (
																
																    setup_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    purpose VARCHAR(100) NOT NULL,
																
																    custom_purpose VARCHAR(255),
																
																    team_size VARCHAR(50) NOT NULL,
																
																    budget_enabled BOOLEAN NOT NULL DEFAULT FALSE,
																
																    monthly_budget NUMERIC(18,2),
																
																    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
																
																    work_style VARCHAR(50) NOT NULL,
																
																    visibility VARCHAR(50) NOT NULL,
																
																    team_owner_user_id UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_setup_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_team_size
																    CHECK (
																        team_size IN (
																            'just_me',
																            '2_5',
																            '6_15',
																            '16_50',
																            '50_plus'
																        )
																    ),
																
																    CONSTRAINT chk_work_style
																    CHECK (
																        work_style IN (
																            'planned',
																            'mixed',
																            'fast_response'
																        )
																    ),
																
																    CONSTRAINT chk_visibility
																    CHECK (
																        visibility IN (
																            'team_only',
																            'leadership',
																            'organization'
																        )
																    ),
																
																    CONSTRAINT chk_budget
																    CHECK (
																        monthly_budget IS NULL
																        OR monthly_budget >= 0
																    )
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_moment_setup
																ON business_moment_setup(moment_id);
-- >>>STMT<<<
CREATE TABLE business_moment_structure (
																
																    structure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    roles_supported JSONB NOT NULL,
																
																    approver_role VARCHAR(100) NOT NULL,
																
																    custom_approver_user_id UUID,
																
																    approval_threshold NUMERIC(18,2) NOT NULL,
																
																    approval_threshold_label VARCHAR(100),
																
																    escalation_contact_role VARCHAR(100) NOT NULL,
																
																    custom_escalation_user_id UUID,
																
																    coordination_style VARCHAR(50) NOT NULL,
																
																    monitoring_level VARCHAR(50) NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_structure_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_approval_threshold
																    CHECK (
																        approval_threshold >= 0
																    ),
																
																    CONSTRAINT chk_coordination_style
																    CHECK (
																        coordination_style IN (
																            'independent',
																            'cross_functional',
																            'leadership_driven',
																            'shared_ownership'
																        )
																    ),
																
																    CONSTRAINT chk_monitoring_level
																    CHECK (
																        monitoring_level IN (
																            'basic',
																            'standard',
																            'high_visibility'
																        )
																    )
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_moment_structure
																ON business_moment_structure(moment_id);
-- >>>STMT<<<
CREATE TABLE business_moment_members (
																
																    member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    user_id UUID,
																
																    name VARCHAR(255) NOT NULL,
																
																    email VARCHAR(255),
																
																    mobile VARCHAR(50),
																
																    username VARCHAR(100),
																
																    role VARCHAR(100) NOT NULL,
																
																    member_status VARCHAR(50) NOT NULL DEFAULT 'configured',
																
																    is_team_lead BOOLEAN NOT NULL DEFAULT FALSE,
																
																    is_budget_owner BOOLEAN NOT NULL DEFAULT FALSE,
																
																    can_edit_own_entries BOOLEAN NOT NULL DEFAULT TRUE,
																
																    can_edit_team_entries BOOLEAN NOT NULL DEFAULT FALSE,
																
																    can_edit_expense_entries BOOLEAN NOT NULL DEFAULT FALSE,
																
																    added_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_member_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_member_role
																    CHECK (
																        role IN (
																            'Team Member',
																            'Team Lead',
																            'Budget Owner',
																            'Approver',
																            'Observer'
																        )
																    ),
																
																    CONSTRAINT chk_member_status
																    CHECK (
																        member_status IN (
																            'configured',
																            'invited',
																            'active',
																            'removed'
																        )
																    )
																);
-- >>>STMT<<<
CREATE INDEX idx_business_members_moment
																ON business_moment_members(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_business_members_role
																ON business_moment_members(role);
-- >>>STMT<<<
CREATE INDEX idx_business_members_status
																ON business_moment_members(member_status);
-- >>>STMT<<<
CREATE TABLE business_moment_invitations (
																
																    invite_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    member_id UUID,
																
																    invite_method VARCHAR(50) NOT NULL,
																
																    invite_status VARCHAR(50) NOT NULL DEFAULT 'pending',
																
																    invite_target VARCHAR(255) NOT NULL,
																
																    qr_token VARCHAR(500),
																
																    send_on_activation BOOLEAN NOT NULL DEFAULT TRUE,
																
																    sent_at TIMESTAMP,
																
																    accepted_at TIMESTAMP,
																
																    expires_at TIMESTAMP,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_invitation_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT fk_invitation_member
																        FOREIGN KEY(member_id)
																        REFERENCES business_moment_members(member_id),
																
																    CONSTRAINT chk_invite_method
																    CHECK (
																        invite_method IN (
																            'email',
																            'mobile',
																            'username',
																            'qr'
																        )
																    ),
																
																    CONSTRAINT chk_invite_status
																    CHECK (
																        invite_status IN (
																            'pending',
																            'sent',
																            'accepted',
																            'expired',
																            'cancelled'
																        )
																    )
																);
-- >>>STMT<<<
CREATE INDEX idx_business_invitation_moment
																ON business_moment_invitations(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_business_invitation_status
																ON business_moment_invitations(invite_status);
-- >>>STMT<<<
CREATE TABLE business_moment_governance (
																
																    governance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    send_invites_on_activation BOOLEAN NOT NULL DEFAULT TRUE,
																
																    operational_visibility VARCHAR(50) NOT NULL,
																
																    notify_approvals BOOLEAN NOT NULL DEFAULT TRUE,
																
																    notify_spending_activity BOOLEAN NOT NULL DEFAULT TRUE,
																
																    notify_issues_risks BOOLEAN NOT NULL DEFAULT TRUE,
																
																    notify_team_updates BOOLEAN NOT NULL DEFAULT TRUE,
																
																    approval_enabled BOOLEAN NOT NULL DEFAULT FALSE,
																
																    activation_ready BOOLEAN NOT NULL DEFAULT FALSE,
																
																    activation_ready_reason TEXT,
																
																    activated_by UUID,
																
																    activated_at TIMESTAMP,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_governance_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_operational_visibility
																    CHECK (
																        operational_visibility IN (
																            'private',
																            'leadership',
																            'organization'
																        )
																    )
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_moment_governance
																ON business_moment_governance(moment_id);
-- >>>STMT<<<
CREATE TABLE team_activities (
																
																    activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    activity_title VARCHAR(255) NOT NULL,
																
																    category VARCHAR(100) NOT NULL,
																
																    description TEXT,
																
																    activity_status VARCHAR(50) NOT NULL DEFAULT 'planned',
																
																    activity_owner_id UUID,
																
																    has_spend BOOLEAN NOT NULL DEFAULT FALSE,
																
																    amount NUMERIC(18,2),
																
																    vendor_name VARCHAR(255),
																
																    receipt_file_id UUID,
																
																    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
																
																    created_by UUID NOT NULL,
																
																    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_activity_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_activity_status
																        CHECK (
																            activity_status IN (
																                'planned',
																                'in_progress',
																                'completed'
																            )
																        ),
																
																    CONSTRAINT chk_activity_priority
																        CHECK (
																            priority IN (
																                'low',
																                'medium',
																                'high'
																            )
																        ),
																
																    CONSTRAINT chk_activity_amount
																        CHECK (
																            amount IS NULL
																            OR amount >= 0
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_team_activities_moment
																ON team_activities(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_team_activities_status
																ON team_activities(activity_status);
-- >>>STMT<<<
CREATE INDEX idx_team_activities_owner
																ON team_activities(activity_owner_id);
-- >>>STMT<<<
CREATE INDEX idx_team_activities_recorded
																ON team_activities(recorded_at DESC);
-- >>>STMT<<<
CREATE TABLE team_approval_requests (
																
																    approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    request_title VARCHAR(255) NOT NULL,
																
																    amount NUMERIC(18,2) NOT NULL,
																
																    approval_type VARCHAR(100) NOT NULL,
																
																    reason TEXT NOT NULL,
																
																    priority VARCHAR(20) NOT NULL DEFAULT 'normal',
																
																    requested_by UUID NOT NULL,
																
																    approver_id UUID NOT NULL,
																
																    needed_by TIMESTAMP,
																
																    approval_status VARCHAR(50) NOT NULL DEFAULT 'pending',
																
																    decision_note TEXT,
																
																    decided_by UUID,
																
																    decided_at TIMESTAMP,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_approval_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_approval_amount
																        CHECK (
																            amount >= 0
																        ),
																
																    CONSTRAINT chk_approval_priority
																        CHECK (
																            priority IN (
																                'normal',
																                'urgent'
																            )
																        ),
																
																    CONSTRAINT chk_approval_status
																        CHECK (
																            approval_status IN (
																                'pending',
																                'approved',
																                'rejected',
																                'cancelled',
																                'expired'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_team_approval_moment
																ON team_approval_requests(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_team_approval_status
																ON team_approval_requests(approval_status);
-- >>>STMT<<<
CREATE INDEX idx_team_approval_approver
																ON team_approval_requests(approver_id);
-- >>>STMT<<<
CREATE TABLE team_updates (
																
																    update_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    update_type VARCHAR(100) NOT NULL,
																
																    update_title VARCHAR(255) NOT NULL,
																
																    people_involved JSONB,
																
																    description TEXT,
																
																    visibility VARCHAR(50) NOT NULL DEFAULT 'team_only',
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_team_update_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_update_visibility
																        CHECK (
																            visibility IN (
																                'team_only',
																                'leadership',
																                'everyone'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_team_updates_moment
																ON team_updates(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_team_updates_created
																ON team_updates(created_at DESC);
-- >>>STMT<<<
CREATE TABLE team_issue_risks (
																
																    issue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    issue_title VARCHAR(255) NOT NULL,
																
																    issue_type VARCHAR(100) NOT NULL,
																
																    severity VARCHAR(50) NOT NULL,
																
																    current_impact VARCHAR(50) NOT NULL,
																
																    owner_id UUID,
																
																    target_resolution_date TIMESTAMP,
																
																    resolution_status VARCHAR(50) NOT NULL DEFAULT 'open',
																
																    description TEXT,
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    resolved_at TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_issue_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_issue_severity
																        CHECK (
																            severity IN (
																                'low',
																                'medium',
																                'high',
																                'critical'
																            )
																        ),
																
																    CONSTRAINT chk_issue_impact
																        CHECK (
																            current_impact IN (
																                'none_yet',
																                'minor',
																                'moderate',
																                'major'
																            )
																        ),
																
																    CONSTRAINT chk_issue_status
																        CHECK (
																            resolution_status IN (
																                'open',
																                'investigating',
																                'resolved'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_team_risks_moment
																ON team_issue_risks(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_team_risks_status
																ON team_issue_risks(resolution_status);
-- >>>STMT<<<
CREATE INDEX idx_team_risks_severity
																ON team_issue_risks(severity);
-- >>>STMT<<<
CREATE INDEX idx_team_risks_owner
																ON team_issue_risks(owner_id);
-- >>>STMT<<<
CREATE TABLE business_live_feed (
																
																    feed_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    source_table VARCHAR(100) NOT NULL,
																
																    source_record_id UUID NOT NULL,
																
																    event_type VARCHAR(100) NOT NULL,
																
																    actor_user_id UUID NOT NULL,
																
																    actor_name VARCHAR(255) NOT NULL,
																
																    headline VARCHAR(500) NOT NULL,
																
																    detail_message TEXT,
																
																    amount NUMERIC(18,2),
																
																    priority VARCHAR(20),
																
																    event_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    visibility VARCHAR(50) NOT NULL DEFAULT 'team_only',
																
																    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
																
																    CONSTRAINT fk_live_feed_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_live_visibility
																        CHECK (
																            visibility IN (
																                'team_only',
																                'leadership',
																                'organization'
																            )
																        ),
																
																    CONSTRAINT chk_live_priority
																        CHECK (
																            priority IS NULL
																            OR priority IN (
																                'low',
																                'medium',
																                'high',
																                'critical'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_live_feed_moment_business_live_feed
																ON business_live_feed(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_live_feed_timestamp
																ON business_live_feed(event_timestamp DESC);
-- >>>STMT<<<
CREATE INDEX idx_live_feed_source
																ON business_live_feed(source_table, source_record_id);
-- >>>STMT<<<
CREATE INDEX idx_live_feed_event_type
																ON business_live_feed(event_type);
-- >>>STMT<<<
CREATE TABLE business_audit_history (
																
																    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    source_table VARCHAR(100) NOT NULL,
																
																    source_record_id UUID NOT NULL,
																
																    field_name VARCHAR(255) NOT NULL,
																
																    old_value TEXT,
																
																    new_value TEXT NOT NULL,
																
																    change_type VARCHAR(50) NOT NULL,
																
																    changed_by UUID NOT NULL,
																
																    changed_by_name VARCHAR(255) NOT NULL,
																
																    change_reason TEXT,
																
																    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_audit_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_audit_change_type
																        CHECK (
																            change_type IN (
																                'create',
																                'edit',
																                'delete',
																                'restore',
																                'approve',
																                'reject',
																                'resolve'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_audit_moment
																ON business_audit_history(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_audit_source
																ON business_audit_history(source_table, source_record_id);
-- >>>STMT<<<
CREATE INDEX idx_audit_changed_at
																ON business_audit_history(changed_at DESC);
-- >>>STMT<<<
CREATE TABLE business_transaction_permissions (
																
																    permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    source_table VARCHAR(100) NOT NULL,
																
																    source_record_id UUID NOT NULL,
																
																    role_name VARCHAR(100) NOT NULL,
																
																    can_view BOOLEAN NOT NULL DEFAULT TRUE,
																
																    can_edit BOOLEAN NOT NULL DEFAULT FALSE,
																
																    can_delete BOOLEAN NOT NULL DEFAULT FALSE,
																
																    permission_reason VARCHAR(255) NOT NULL,
																
																    granted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    active_flag BOOLEAN NOT NULL DEFAULT TRUE,
																
																    CONSTRAINT fk_permission_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_permission_moment
																ON business_transaction_permissions(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_permission_source
																ON business_transaction_permissions(source_table, source_record_id);
-- >>>STMT<<<
CREATE INDEX idx_permission_role
																ON business_transaction_permissions(role_name);
-- >>>STMT<<<
CREATE TABLE business_notifications (
																
																    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    recipient_user_id UUID NOT NULL,
																
																    notification_type VARCHAR(100) NOT NULL,
																
																    source_table VARCHAR(100) NOT NULL,
																
																    source_record_id UUID NOT NULL,
																
																    title VARCHAR(500) NOT NULL,
																
																    message TEXT NOT NULL,
																
																    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
																
																    delivery_channel VARCHAR(50) NOT NULL,
																
																    notification_status VARCHAR(50) NOT NULL DEFAULT 'queued',
																
																    read_at TIMESTAMP,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    expires_at TIMESTAMP,
																
																    CONSTRAINT fk_notification_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_notification_priority
																        CHECK (
																            priority IN (
																                'low',
																                'medium',
																                'high',
																                'critical'
																            )
																        ),
																
																    CONSTRAINT chk_delivery_channel
																        CHECK (
																            delivery_channel IN (
																                'in_app',
																                'email',
																                'push'
																            )
																        ),
																
																    CONSTRAINT chk_notification_status
																        CHECK (
																            notification_status IN (
																                'queued',
																                'sent',
																                'read',
																                'failed',
																                'archived'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_notification_recipient
																ON business_notifications(recipient_user_id);
-- >>>STMT<<<
CREATE INDEX idx_notification_status
																ON business_notifications(notification_status);
-- >>>STMT<<<
CREATE INDEX idx_notification_created
																ON business_notifications(created_at DESC);
-- >>>STMT<<<
CREATE TABLE business_pulse_snapshots (
																
																    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    snapshot_date DATE NOT NULL,
																
																    activities_count INTEGER NOT NULL DEFAULT 0,
																
																    completed_activities INTEGER NOT NULL DEFAULT 0,
																
																    in_progress_activities INTEGER NOT NULL DEFAULT 0,
																
																    planned_activities INTEGER NOT NULL DEFAULT 0,
																
																    pending_approvals INTEGER NOT NULL DEFAULT 0,
																
																    open_risks INTEGER NOT NULL DEFAULT 0,
																
																    critical_risks INTEGER NOT NULL DEFAULT 0,
																
																    monthly_spend NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    top_spend_category VARCHAR(255),
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_pulse_snapshot_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_pulse_snapshot_moment
																ON business_pulse_snapshots(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_pulse_snapshot_date
																ON business_pulse_snapshots(snapshot_date DESC);
-- >>>STMT<<<
CREATE TABLE business_moment_metrics (
																
																    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    members_count INTEGER NOT NULL DEFAULT 0,
																
																    activities_count INTEGER NOT NULL DEFAULT 0,
																
																    pending_approvals INTEGER NOT NULL DEFAULT 0,
																
																    open_risks INTEGER NOT NULL DEFAULT 0,
																
																    spend_amount NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    last_activity_at TIMESTAMP,
																
																    last_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_moment_metrics_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id)
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_moment_metrics
																ON business_moment_metrics(moment_id);
-- >>>STMT<<<
CREATE TABLE business_memory_patterns (
																
																    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    pattern_type VARCHAR(100) NOT NULL,
																
																    pattern_title VARCHAR(255) NOT NULL,
																
																    observation_text TEXT NOT NULL,
																
																    source_metric VARCHAR(255),
																
																    confidence_level NUMERIC(5,2),
																
																    first_observed_at TIMESTAMP NOT NULL,
																
																    last_observed_at TIMESTAMP NOT NULL,
																
																    pattern_status VARCHAR(50) NOT NULL DEFAULT 'active',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_memory_pattern_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_pattern_status
																        CHECK (
																            pattern_status IN (
																                'active',
																                'archived'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_memory_pattern_moment
																ON business_memory_patterns(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_memory_pattern_type
																ON business_memory_patterns(pattern_type);
-- >>>STMT<<<
CREATE TABLE business_quick_add_drafts (
																
																    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    user_id UUID NOT NULL,
																
																    tab_type VARCHAR(50) NOT NULL,
																
																    draft_payload JSONB NOT NULL,
																
																    draft_status VARCHAR(50) NOT NULL DEFAULT 'active',
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_draft_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_draft_status
																        CHECK (
																            draft_status IN (
																                'active',
																                'submitted',
																                'discarded',
																                'expired'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_draft_moment
																ON business_quick_add_drafts(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_draft_user
																ON business_quick_add_drafts(user_id);
-- >>>STMT<<<
CREATE TABLE business_attachment_files (
																
																    file_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    source_table VARCHAR(100) NOT NULL,
																
																    source_record_id UUID NOT NULL,
																
																    file_name VARCHAR(500) NOT NULL,
																
																    file_type VARCHAR(100) NOT NULL,
																
																    file_size_bytes BIGINT NOT NULL,
																
																    storage_path TEXT NOT NULL,
																
																    uploaded_by UUID NOT NULL,
																
																    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_attachment_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_attachment_moment
																ON business_attachment_files(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_attachment_source
																ON business_attachment_files(source_table, source_record_id);
-- >>>STMT<<<
CREATE TABLE business_vendor_directory (
																
																    vendor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    vendor_name VARCHAR(255) NOT NULL,
																
																    vendor_category VARCHAR(100),
																
																    vendor_status VARCHAR(50) NOT NULL DEFAULT 'active',
																
																    total_spend NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    last_transaction_at TIMESTAMP,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_vendor_status
																        CHECK (
																            vendor_status IN (
																                'active',
																                'inactive',
																                'archived'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_vendor_workspace
																ON business_vendor_directory(workspace_id);
-- >>>STMT<<<
CREATE INDEX idx_vendor_name
																ON business_vendor_directory(vendor_name);
-- >>>STMT<<<
CREATE TABLE business_orchestration_jobs (
																
																    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    job_type VARCHAR(100) NOT NULL,
																
																    source_table VARCHAR(100),
																
																    source_record_id UUID,
																
																    job_status VARCHAR(50) NOT NULL DEFAULT 'queued',
																
																    attempts INTEGER NOT NULL DEFAULT 0,
																
																    error_message TEXT,
																
																    queued_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    completed_at TIMESTAMP,
																
																    CONSTRAINT fk_job_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_job_status
																        CHECK (
																            job_status IN (
																                'queued',
																                'processing',
																                'completed',
																                'failed'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_job_status
																ON business_orchestration_jobs(job_status);
-- >>>STMT<<<
CREATE INDEX idx_job_moment
																ON business_orchestration_jobs(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_job_type
																ON business_orchestration_jobs(job_type);
-- >>>STMT<<<
CREATE TABLE ai_signals (
    signal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    moment_id UUID NOT NULL,

    signal_scope VARCHAR(50) NOT NULL DEFAULT 'team_operations',
    signal_type VARCHAR(100) NOT NULL,
    signal_title VARCHAR(255) NOT NULL,
    signal_message TEXT NOT NULL,

    source_table VARCHAR(100),
    source_record_id UUID,

    severity VARCHAR(30) NOT NULL DEFAULT 'info',
    confidence_score NUMERIC(5,2),

    recommended_action TEXT,
    target_screen VARCHAR(50),

    signal_status VARCHAR(50) NOT NULL DEFAULT 'active',

    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,

    CONSTRAINT fk_ai_signal_moment
        FOREIGN KEY(moment_id)
        REFERENCES business_moments(moment_id),

    CONSTRAINT chk_ai_signal_severity
        CHECK (
            severity IN (
                'info',
                'low',
                'medium',
                'high',
                'critical'
            )
        ),

    CONSTRAINT chk_ai_signal_status
        CHECK (
            signal_status IN (
                'active',
                'dismissed',
                'resolved',
                'expired',
                'archived'
            )
        ),

    CONSTRAINT chk_ai_signal_target_screen
        CHECK (
            target_screen IS NULL
            OR target_screen IN (
                'pulse',
                'moments',
                'live',
                'memory',
                'quick_add'
            )
        )
);
-- >>>STMT<<<
CREATE INDEX idx_ai_signals_moment
ON ai_signals(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_ai_signals_type
ON ai_signals(signal_type);
-- >>>STMT<<<
CREATE INDEX idx_ai_signals_status
ON ai_signals(signal_status);
-- >>>STMT<<<
CREATE INDEX idx_ai_signals_generated
ON ai_signals(generated_at DESC);
-- >>>STMT<<<
ALTER TABLE business_pulse_snapshots
ADD COLUMN IF NOT EXISTS health_score NUMERIC(5,2) NOT NULL DEFAULT 100,
ADD COLUMN IF NOT EXISTS health_status VARCHAR(50) NOT NULL DEFAULT 'stable',
ADD COLUMN IF NOT EXISTS health_reason TEXT;
-- >>>STMT<<<
ALTER TABLE business_pulse_snapshots
ADD CONSTRAINT chk_business_pulse_health_status
CHECK (
    health_status IN (
        'stable',
        'attention',
        'at_risk',
        'critical'
    )
);
-- >>>STMT<<<
ALTER TABLE team_activities
ADD CONSTRAINT fk_team_activity_owner_member
FOREIGN KEY(activity_owner_id)
REFERENCES business_moment_members(member_id);
-- >>>STMT<<<
ALTER TABLE team_approval_requests
ADD CONSTRAINT fk_team_approval_approver_member
FOREIGN KEY(approver_id)
REFERENCES business_moment_members(member_id);
-- >>>STMT<<<
ALTER TABLE team_approval_requests
ADD CONSTRAINT fk_team_approval_requested_by_member
FOREIGN KEY(requested_by)
REFERENCES business_moment_members(member_id);
-- >>>STMT<<<
ALTER TABLE team_issue_risks
ADD CONSTRAINT fk_team_issue_owner_member
FOREIGN KEY(owner_id)
REFERENCES business_moment_members(member_id);
-- >>>STMT<<<
ALTER TABLE team_approval_requests
ADD COLUMN IF NOT EXISTS converted_activity_id UUID,
ADD COLUMN IF NOT EXISTS converted_to_spend BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS converted_at TIMESTAMP;
-- >>>STMT<<<
CREATE TABLE business_runway_setup (
																    runway_setup_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    business_stage VARCHAR(50) NOT NULL,
																
																    cash_available NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    monthly_burn NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    monthly_revenue NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    operating_currency VARCHAR(10) NOT NULL DEFAULT 'INR',
																
																    estimated_runway_months NUMERIC(10,2) NOT NULL DEFAULT 0,
																
																    runway_goal VARCHAR(100) NOT NULL,
																
																    runway_owner_id UUID,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_runway_setup_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_runway_business_stage
																        CHECK (
																            business_stage IN (
																                'idea',
																                'mvp',
																                'growth',
																                'smb',
																                'custom'
																            )
																        ),
																
																    CONSTRAINT chk_runway_cash_available
																        CHECK (cash_available >= 0),
																
																    CONSTRAINT chk_runway_monthly_burn
																        CHECK (monthly_burn >= 0),
																
																    CONSTRAINT chk_runway_monthly_revenue
																        CHECK (monthly_revenue >= 0),
																
																    CONSTRAINT chk_runway_goal
																        CHECK (
																            runway_goal IN (
																                'extend_runway',
																                'control_burn',
																                'plan_hiring',
																                'track_funding',
																                'reach_profitability',
																                'custom'
																            )
																        )
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_runway_setup
																ON business_runway_setup(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_business_runway_setup_owner
																ON business_runway_setup(runway_owner_id);
-- >>>STMT<<<
CREATE TABLE business_runway_structure (
																    structure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    burn_categories JSONB NOT NULL,
																
																    revenue_model VARCHAR(100) NOT NULL,
																
																    alert_threshold_months NUMERIC(10,2) NOT NULL DEFAULT 6,
																
																    hiring_intent VARCHAR(100),
																
																    funding_structure VARCHAR(100) NOT NULL,
																
																    runway_philosophy VARCHAR(100) NOT NULL,
																
																    monitoring_level VARCHAR(50) NOT NULL DEFAULT 'standard',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_runway_structure_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_runway_revenue_model
																        CHECK (
																            revenue_model IN (
																                'product_sales',
																                'service_revenue',
																                'subscription_revenue',
																                'project_revenue',
																                'commission_revenue',
																                'mixed',
																                'custom'
																            )
																        ),
																
																    CONSTRAINT chk_runway_alert_threshold
																        CHECK (alert_threshold_months > 0),
																
																    CONSTRAINT chk_runway_funding_structure
																        CHECK (
																            funding_structure IN (
																                'owner_funded',
																                'revenue_funded',
																                'bank_loan',
																                'credit_line',
																                'investor_funded',
																                'government_grant',
																                'mixed',
																                'custom'
																            )
																        ),
																
																    CONSTRAINT chk_runway_philosophy
																        CHECK (
																            runway_philosophy IN (
																                'conservative',
																                'balanced',
																                'growth_focused',
																                'aggressive_expansion'
																            )
																        ),
																
																    CONSTRAINT chk_runway_monitoring_level
																        CHECK (
																            monitoring_level IN (
																                'basic',
																                'standard',
																                'high_visibility'
																            )
																        )
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_runway_structure
																ON business_runway_structure(moment_id);
-- >>>STMT<<<
CREATE TABLE business_runway_governance_rules (
																    governance_rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    visibility_roles JSONB NOT NULL,
																
																    alert_recipient_roles JSONB NOT NULL,
																
																    alert_conditions JSONB NOT NULL,
																
																    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
																
																    approval_rules JSONB,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_runway_governance_rules_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id)
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_runway_governance_rules
																ON business_runway_governance_rules(moment_id);
-- >>>STMT<<<
CREATE TABLE runway_cash_inflows (
																    cash_inflow_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    inflow_type VARCHAR(100) NOT NULL,
																
																    amount NUMERIC(18,2) NOT NULL,
																
																    currency VARCHAR(10) NOT NULL,
																
																    exchange_rate_to_operating_currency NUMERIC(18,6) NOT NULL DEFAULT 1,
																
																    amount_in_operating_currency NUMERIC(18,2) NOT NULL,
																
																    inflow_date DATE NOT NULL,
																
																    reference VARCHAR(255),
																
																    description TEXT,
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_runway_cash_inflow_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_runway_cash_inflow_type
																        CHECK (
																            inflow_type IN (
																                'revenue_collected',
																                'investor_funding',
																                'owner_contribution',
																                'bank_loan',
																                'government_grant',
																                'customer_advance',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_runway_cash_inflow_amount
																        CHECK (amount > 0),
																
																    CONSTRAINT chk_runway_cash_inflow_fx
																        CHECK (exchange_rate_to_operating_currency > 0),
																
																    CONSTRAINT chk_runway_cash_inflow_converted_amount
																        CHECK (amount_in_operating_currency >= 0)
																);
-- >>>STMT<<<
CREATE INDEX idx_runway_cash_inflows_moment
																ON runway_cash_inflows(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_runway_cash_inflows_date
																ON runway_cash_inflows(inflow_date DESC);
-- >>>STMT<<<
CREATE INDEX idx_runway_cash_inflows_type
																ON runway_cash_inflows(inflow_type);
-- >>>STMT<<<
CREATE TABLE runway_expense_burns (
																    expense_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    expense_category VARCHAR(100) NOT NULL,
																
																    amount NUMERIC(18,2) NOT NULL,
																
																    currency VARCHAR(10) NOT NULL,
																
																    exchange_rate_to_operating_currency NUMERIC(18,6) NOT NULL DEFAULT 1,
																
																    amount_in_operating_currency NUMERIC(18,2) NOT NULL,
																
																    vendor_name VARCHAR(255),
																
																    expense_date DATE NOT NULL,
																
																    description TEXT,
																
																    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
																
																    approval_status VARCHAR(50) NOT NULL DEFAULT 'not_required',
																
																    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_runway_expense_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_runway_expense_category
																        CHECK (
																            expense_category IN (
																                'salaries',
																                'marketing',
																                'technology',
																                'operations',
																                'vendor',
																                'inventory',
																                'taxes',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_runway_expense_amount
																        CHECK (amount > 0),
																
																    CONSTRAINT chk_runway_expense_fx
																        CHECK (exchange_rate_to_operating_currency > 0),
																
																    CONSTRAINT chk_runway_expense_converted_amount
																        CHECK (amount_in_operating_currency >= 0),
																
																    CONSTRAINT chk_runway_expense_approval_status
																        CHECK (
																            approval_status IN (
																                'not_required',
																                'pending',
																                'approved',
																                'rejected'
																            )
																        ),
																
																    CONSTRAINT chk_runway_expense_priority
																        CHECK (
																            priority IN (
																                'low',
																                'medium',
																                'high'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_runway_expenses_moment
																ON runway_expense_burns(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_runway_expenses_date
																ON runway_expense_burns(expense_date DESC);
-- >>>STMT<<<
CREATE INDEX idx_runway_expenses_category
																ON runway_expense_burns(expense_category);
-- >>>STMT<<<
CREATE INDEX idx_runway_expenses_approval
																ON runway_expense_burns(approval_status);
-- >>>STMT<<<
CREATE TABLE runway_risks (
																    risk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    risk_title VARCHAR(255) NOT NULL,
																
																    risk_type VARCHAR(100) NOT NULL,
																
																    severity VARCHAR(50) NOT NULL,
																
																    expected_impact VARCHAR(50) NOT NULL,
																
																    owner_id UUID,
																
																    target_resolution_date DATE,
																
																    description TEXT,
																
																    risk_status VARCHAR(50) NOT NULL DEFAULT 'open',
																
																    adjustment_required BOOLEAN NOT NULL DEFAULT FALSE,
																
																    affected_metric VARCHAR(100),
																
																    current_value NUMERIC(18,2),
																
																    new_value NUMERIC(18,2),
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    resolved_at TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_runway_risk_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_runway_risk_type
																        CHECK (
																            risk_type IN (
																                'funding_delay',
																                'revenue_drop',
																                'cost_increase',
																                'customer_loss',
																                'loan_risk',
																                'vendor_dependency',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_runway_risk_severity
																        CHECK (
																            severity IN (
																                'low',
																                'medium',
																                'high',
																                'critical'
																            )
																        ),
																
																    CONSTRAINT chk_runway_risk_expected_impact
																        CHECK (
																            expected_impact IN (
																                'lt_1_month',
																                '1_3_months',
																                '3_6_months',
																                '6_plus_months'
																            )
																        ),
																
																    CONSTRAINT chk_runway_risk_status
																        CHECK (
																            risk_status IN (
																                'open',
																                'investigating',
																                'resolved',
																                'archived'
																            )
																        ),
																
																    CONSTRAINT chk_runway_risk_affected_metric
																        CHECK (
																            affected_metric IS NULL
																            OR affected_metric IN (
																                'cash_available',
																                'revenue',
																                'monthly_burn',
																                'runway_threshold'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_runway_risks_moment
																ON runway_risks(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_runway_risks_status
																ON runway_risks(risk_status);
-- >>>STMT<<<
CREATE INDEX idx_runway_risks_severity
																ON runway_risks(severity);
-- >>>STMT<<<
CREATE INDEX idx_runway_risks_owner
																ON runway_risks(owner_id);
-- >>>STMT<<<
CREATE TABLE runway_strategic_decisions (
																    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    decision_type VARCHAR(100) NOT NULL,
																
																    decision_title VARCHAR(255) NOT NULL,
																
																    decision_owner_id UUID,
																
																    expected_impact VARCHAR(50) NOT NULL,
																
																    description TEXT,
																
																    decision_status VARCHAR(50) NOT NULL DEFAULT 'active',
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_runway_decision_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_runway_decision_type
																        CHECK (
																            decision_type IN (
																                'hiring',
																                'expansion',
																                'funding',
																                'cost_reduction',
																                'pricing',
																                'operations',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_runway_decision_impact
																        CHECK (
																            expected_impact IN (
																                'increase_runway',
																                'reduce_runway',
																                'neutral',
																                'unknown'
																            )
																        ),
																
																    CONSTRAINT chk_runway_decision_status
																        CHECK (
																            decision_status IN (
																                'active',
																                'edited',
																                'archived'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_runway_decisions_moment
																ON runway_strategic_decisions(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_runway_decisions_type
																ON runway_strategic_decisions(decision_type);
-- >>>STMT<<<
CREATE INDEX idx_runway_decisions_created
																ON runway_strategic_decisions(created_at DESC);
-- >>>STMT<<<
CREATE TABLE runway_financial_updates (
																    financial_update_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    update_type VARCHAR(100) NOT NULL,
																
																    current_value NUMERIC(18,2) NOT NULL,
																
																    new_value NUMERIC(18,2) NOT NULL,
																
																    currency VARCHAR(10),
																
																    exchange_rate_to_operating_currency NUMERIC(18,6),
																
																    new_value_in_operating_currency NUMERIC(18,2),
																
																    reason TEXT NOT NULL,
																
																    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
																
																    approval_status VARCHAR(50) NOT NULL DEFAULT 'not_required',
																
																    applied_status VARCHAR(50) NOT NULL DEFAULT 'pending',
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    applied_at TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_runway_financial_update_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_runway_financial_update_type
																        CHECK (
																            update_type IN (
																                'cash_available',
																                'monthly_burn',
																                'revenue_estimate',
																                'runway_threshold',
																                'funding_expectation'
																            )
																        ),
																
																    CONSTRAINT chk_runway_financial_update_new_value
																        CHECK (new_value >= 0),
																
																    CONSTRAINT chk_runway_financial_update_approval_status
																        CHECK (
																            approval_status IN (
																                'not_required',
																                'pending',
																                'approved',
																                'rejected'
																            )
																        ),
																
																    CONSTRAINT chk_runway_financial_update_applied_status
																        CHECK (
																            applied_status IN (
																                'pending',
																                'applied',
																                'rejected'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_runway_financial_updates_moment
																ON runway_financial_updates(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_runway_financial_updates_type
																ON runway_financial_updates(update_type);
-- >>>STMT<<<
CREATE INDEX idx_runway_financial_updates_status
																ON runway_financial_updates(applied_status);
-- >>>STMT<<<
CREATE TABLE business_runway_snapshots (
																    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    snapshot_date DATE NOT NULL,
																
																    cash_available NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    total_cash_inflow NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    total_expense_burn NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    net_burn NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    estimated_runway_months NUMERIC(10,2) NOT NULL DEFAULT 0,
																
																    open_risks INTEGER NOT NULL DEFAULT 0,
																
																    decision_count INTEGER NOT NULL DEFAULT 0,
																
																    operating_currency VARCHAR(10) NOT NULL DEFAULT 'INR',
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_runway_snapshot_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id)
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_runway_snapshot_day
																ON business_runway_snapshots(moment_id, snapshot_date);
-- >>>STMT<<<
CREATE INDEX idx_runway_snapshot_moment
																ON business_runway_snapshots(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_runway_snapshot_date
																ON business_runway_snapshots(snapshot_date DESC);
-- >>>STMT<<<
ALTER TABLE business_moment_members
																DROP CONSTRAINT IF EXISTS chk_member_role;
-- >>>STMT<<<
ALTER TABLE business_moment_members
																ADD CONSTRAINT chk_member_role
																CHECK (
																    role IN (
																        'Team Member',
																        'Team Lead',
																        'Budget Owner',
																        'Approver',
																        'Observer',
																
																        'Runway Owner',
																        'Finance Lead',
																        'Operations Lead',
																        'Financial Contributor',
																        'Viewer'
																    )
																);
-- >>>STMT<<<
ALTER TABLE business_moment_members
																ADD COLUMN IF NOT EXISTS can_add_runway_transactions BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS can_edit_financial_entries BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS can_manage_runway_settings BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS can_approve_runway_changes BOOLEAN NOT NULL DEFAULT FALSE;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_apply_runway_member_permissions
																ON business_moment_members;
-- >>>STMT<<<
ALTER TABLE business_moment_governance
																ADD COLUMN IF NOT EXISTS runway_visibility_roles JSONB,
																ADD COLUMN IF NOT EXISTS runway_alert_roles JSONB,
																ADD COLUMN IF NOT EXISTS runway_alert_conditions JSONB,
																ADD COLUMN IF NOT EXISTS runway_approval_required BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS runway_approval_rules JSONB;
-- >>>STMT<<<
ALTER TABLE business_pulse_snapshots
																ADD COLUMN IF NOT EXISTS cash_available NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS estimated_runway_months NUMERIC(10,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS cash_inflow_total NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS expense_burn_total NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS net_burn NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS runway_alert_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS runway_risk_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS operating_currency VARCHAR(10) DEFAULT 'INR';
-- >>>STMT<<<
ALTER TABLE business_moment_metrics
																ADD COLUMN IF NOT EXISTS cash_available NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS estimated_runway_months NUMERIC(10,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS cash_inflow_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS expense_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS risk_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS decision_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS net_burn NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS operating_currency VARCHAR(10) DEFAULT 'INR';
-- >>>STMT<<<
ALTER TABLE business_memory_patterns
																DROP CONSTRAINT IF EXISTS chk_business_memory_pattern_type;
-- >>>STMT<<<
ALTER TABLE business_memory_patterns
																ADD CONSTRAINT chk_business_memory_pattern_type
																CHECK (
																    pattern_type IN (
																        'vendor',
																        'vendor_pattern',
																        'spend_pattern',
																        'approval_pattern',
																        'risk_pattern',
																        'ownership_pattern',
																
																        'cash_inflow_pattern',
																        'burn_pattern',
																        'runway_risk_pattern',
																        'decision_pattern',
																        'financial_update_pattern',
																        'net_burn_pattern'
																    )
																);
-- >>>STMT<<<
ALTER TABLE business_live_feed
																DROP CONSTRAINT IF EXISTS chk_live_visibility;
-- >>>STMT<<<
ALTER TABLE business_live_feed
																ADD CONSTRAINT chk_live_visibility
																CHECK (
																    visibility IN (
																        'team_only',
																        'leadership',
																        'organization',
																
																        'runway_roles',
																        'runway_owners',
																        'finance_leads',
																        'all_runway_participants'
																    )
																);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_runway_risk_member_refs
																ON runway_risks;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_runway_decision_member_refs
																ON runway_strategic_decisions;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_pulse_runway_snapshot
																ON business_pulse_snapshots(moment_id, snapshot_date DESC);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_moment_metrics_runway
																ON business_moment_metrics(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_memory_patterns_runway_type
																ON business_memory_patterns(moment_id, pattern_type);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_live_feed_runway_source
																ON business_live_feed(source_table, source_record_id);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_risk_updated
ON runway_risks;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_financial_update_updated
ON runway_financial_updates;
-- >>>STMT<<<
CREATE TABLE business_operations_setup (
																    operations_setup_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    operations_type VARCHAR(100) NOT NULL,
																
																    operating_model VARCHAR(100) NOT NULL,
																
																    operational_owner_role VARCHAR(100) NOT NULL,
																
																    operating_currency VARCHAR(10) NOT NULL DEFAULT 'INR',
																
																    monthly_operating_budget NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_business_operations_setup_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_business_operations_type
																        CHECK (
																            operations_type IN (
																                'store',
																                'branch',
																                'department',
																                'warehouse',
																                'restaurant',
																                'clinic',
																                'factory',
																                'custom'
																            )
																        ),
																
																    CONSTRAINT chk_business_operations_model
																        CHECK (
																            operating_model IN (
																                'budget_driven',
																                'vendor_driven',
																                'performance_driven',
																                'compliance_driven',
																                'balanced_operations'
																            )
																        ),
																
																    CONSTRAINT chk_business_operations_owner_role
																        CHECK (
																            operational_owner_role IN (
																                'Business Owner',
																                'Operations Manager',
																                'Department Head',
																                'Branch Manager',
																                'Store Manager',
																                'Custom'
																            )
																        ),
																
																    CONSTRAINT chk_business_operations_monthly_budget
																        CHECK (monthly_operating_budget >= 0)
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_operations_setup
																ON business_operations_setup(moment_id);
-- >>>STMT<<<
CREATE TABLE business_operations_budget_categories (
																    budget_category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    category_name VARCHAR(100) NOT NULL,
																
																    custom_category_name VARCHAR(255),
																
																    allocated_budget NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
																
																    category_status VARCHAR(50) NOT NULL DEFAULT 'active',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_operations_budget_category_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_operations_budget_category_name
																        CHECK (
																            category_name IN (
																                'inventory',
																                'payroll',
																                'marketing',
																                'operations',
																                'utilities',
																                'maintenance',
																                'vendor_services',
																                'travel',
																                'technology',
																                'custom'
																            )
																        ),
																
																    CONSTRAINT chk_operations_budget_allocated
																        CHECK (allocated_budget >= 0),
																
																    CONSTRAINT chk_operations_budget_category_status
																        CHECK (
																            category_status IN (
																                'active',
																                'archived'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_operations_budget_categories_moment
																ON business_operations_budget_categories(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_budget_categories_status
																ON business_operations_budget_categories(category_status);
-- >>>STMT<<<
CREATE TABLE business_operations_structure (
																    operations_structure_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    vendor_dependency VARCHAR(50) NOT NULL,
																
																    approval_model VARCHAR(100) NOT NULL,
																
																    kpi_tracking JSONB,
																
																    issue_sensitivity VARCHAR(100) NOT NULL,
																
																    performance_review_cycle VARCHAR(50) NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_business_operations_structure_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_operations_vendor_dependency
																        CHECK (
																            vendor_dependency IN (
																                'low',
																                'moderate',
																                'high',
																                'critical'
																            )
																        ),
																
																    CONSTRAINT chk_operations_approval_model
																        CHECK (
																            approval_model IN (
																                'open_approval',
																                'manager_approval',
																                'multi_level_approval',
																                'owner_approval'
																            )
																        ),
																
																    CONSTRAINT chk_operations_issue_sensitivity
																        CHECK (
																            issue_sensitivity IN (
																                'monitor_only',
																                'normal',
																                'high_visibility',
																                'critical_operations'
																            )
																        ),
																
																    CONSTRAINT chk_operations_review_cycle
																        CHECK (
																            performance_review_cycle IN (
																                'weekly',
																                'bi_weekly',
																                'monthly',
																                'quarterly'
																            )
																        )
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_operations_structure
																ON business_operations_structure(moment_id);
-- >>>STMT<<<
CREATE TABLE business_operations_governance_rules (
																    operations_governance_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    visibility_roles JSONB NOT NULL,
																
																    alert_conditions JSONB NOT NULL,
																
																    alert_recipient_roles JSONB NOT NULL,
																
																    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
																
																    approval_rules JSONB,
																
																    monitoring_level VARCHAR(50) NOT NULL DEFAULT 'standard',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_business_operations_governance_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_operations_monitoring_level
																        CHECK (
																            monitoring_level IN (
																                'basic',
																                'standard',
																                'high_visibility',
																                'owner_oversight'
																            )
																        )
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_operations_governance
																ON business_operations_governance_rules(moment_id);
-- >>>STMT<<<
CREATE TABLE operations_spend_entries (
																    spend_entry_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    spend_name VARCHAR(255) NOT NULL,
																
																    budget_category_id UUID NOT NULL,
																
																    spend_category VARCHAR(100) NOT NULL,
																
																    currency VARCHAR(10) NOT NULL,
																
																    amount NUMERIC(18,2) NOT NULL,
																
																    exchange_rate_to_operating_currency NUMERIC(18,6) NOT NULL DEFAULT 1,
																
																    amount_in_operating_currency NUMERIC(18,2) NOT NULL,
																
																    spend_date DATE NOT NULL,
																
																    vendor_name VARCHAR(255),
																
																    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
																
																    description TEXT,
																
																    approval_required BOOLEAN NOT NULL DEFAULT FALSE,
																
																    approval_status VARCHAR(50) NOT NULL DEFAULT 'not_required',
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_operations_spend_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT fk_operations_spend_budget_category
																        FOREIGN KEY(budget_category_id)
																        REFERENCES business_operations_budget_categories(budget_category_id),
																
																    CONSTRAINT chk_operations_spend_category
																        CHECK (
																            spend_category IN (
																                'purchase',
																                'vendor_payment',
																                'staff_cost',
																                'utility_bill',
																                'maintenance',
																                'marketing_spend',
																                'inventory_refill',
																                'service_charge',
																                'travel_expense',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_operations_spend_amount
																        CHECK (amount > 0),
																
																    CONSTRAINT chk_operations_spend_fx
																        CHECK (exchange_rate_to_operating_currency > 0),
																
																    CONSTRAINT chk_operations_spend_amount_operating
																        CHECK (amount_in_operating_currency >= 0),
																
																    CONSTRAINT chk_operations_spend_priority
																        CHECK (
																            priority IN (
																                'low',
																                'medium',
																                'high',
																                'critical'
																            )
																        ),
																
																    CONSTRAINT chk_operations_spend_approval_status
																        CHECK (
																            approval_status IN (
																                'not_required',
																                'pending',
																                'approved',
																                'rejected'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_operations_spend_moment
																ON operations_spend_entries(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_spend_budget_category
																ON operations_spend_entries(budget_category_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_spend_date
																ON operations_spend_entries(spend_date DESC);
-- >>>STMT<<<
CREATE INDEX idx_operations_spend_approval
																ON operations_spend_entries(approval_status);
-- >>>STMT<<<
CREATE TABLE operations_vendor_updates (
																    vendor_update_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    vendor_event_type VARCHAR(100) NOT NULL,
																
																    vendor_name VARCHAR(255) NOT NULL,
																
																    vendor_category VARCHAR(100) NOT NULL,
																
																    vendor_status VARCHAR(100) NOT NULL,
																
																    impact_level VARCHAR(50) NOT NULL DEFAULT 'medium',
																
																    description TEXT,
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_operations_vendor_update_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_operations_vendor_event_type
																        CHECK (
																            vendor_event_type IN (
																                'new_vendor',
																                'vendor_evaluation',
																                'vendor_issue',
																                'contract_renewal',
																                'payment_status',
																                'contract_change',
																                'vendor_suspension',
																                'vendor_reactivation',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_operations_vendor_category
																        CHECK (
																            vendor_category IN (
																                'inventory_vendor',
																                'technology_vendor',
																                'marketing_vendor',
																                'service_vendor',
																                'facility_vendor',
																                'logistics_vendor',
																                'professional_services',
																                'equipment_supplier',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_operations_vendor_status
																        CHECK (
																            vendor_status IN (
																                'active',
																                'preferred_vendor',
																                'under_review',
																                'on_hold',
																                'blocked',
																                'terminated'
																            )
																        ),
																
																    CONSTRAINT chk_operations_vendor_impact
																        CHECK (
																            impact_level IN (
																                'low',
																                'medium',
																                'high',
																                'critical'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_operations_vendor_updates_moment
																ON operations_vendor_updates(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_vendor_updates_vendor
																ON operations_vendor_updates(vendor_name);
-- >>>STMT<<<
CREATE INDEX idx_operations_vendor_updates_event
																ON operations_vendor_updates(vendor_event_type);
-- >>>STMT<<<
CREATE INDEX idx_operations_vendor_updates_status
																ON operations_vendor_updates(vendor_status);
-- >>>STMT<<<
CREATE TABLE operations_approval_requests (
																    operations_approval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    request_type VARCHAR(100) NOT NULL,
																
																    request_title VARCHAR(255) NOT NULL,
																
																    amount NUMERIC(18,2),
																
																    currency VARCHAR(10),
																
																    linked_spend_entry_id UUID,
																
																    approver_id UUID,
																
																    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
																
																    description TEXT NOT NULL,
																
																    approval_status VARCHAR(50) NOT NULL DEFAULT 'pending',
																
																    decision_note TEXT,
																
																    decided_by UUID,
																
																    decided_at TIMESTAMP,
																
																    requested_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_operations_approval_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT fk_operations_approval_spend
																        FOREIGN KEY(linked_spend_entry_id)
																        REFERENCES operations_spend_entries(spend_entry_id),
																
																    CONSTRAINT chk_operations_approval_request_type
																        CHECK (
																            request_type IN (
																                'expense_approval',
																                'vendor_approval',
																                'budget_change',
																                'policy_exception',
																                'operational_request'
																            )
																        ),
																
																    CONSTRAINT chk_operations_approval_amount
																        CHECK (
																            amount IS NULL
																            OR amount >= 0
																        ),
																
																    CONSTRAINT chk_operations_approval_priority
																        CHECK (
																            priority IN (
																                'low',
																                'medium',
																                'high',
																                'critical'
																            )
																        ),
																
																    CONSTRAINT chk_operations_approval_status
																        CHECK (
																            approval_status IN (
																                'pending',
																                'approved',
																                'rejected',
																                'cancelled',
																                'archived'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_operations_approval_moment
																ON operations_approval_requests(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_approval_status
																ON operations_approval_requests(approval_status);
-- >>>STMT<<<
CREATE INDEX idx_operations_approval_approver
																ON operations_approval_requests(approver_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_approval_spend
																ON operations_approval_requests(linked_spend_entry_id);
-- >>>STMT<<<
CREATE TABLE operations_issues (
																    operations_issue_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    issue_category VARCHAR(100) NOT NULL,
																
																    issue_title VARCHAR(255) NOT NULL,
																
																    severity VARCHAR(50) NOT NULL,
																
																    impact_area VARCHAR(100) NOT NULL,
																
																    owner_id UUID,
																
																    target_resolution_date DATE,
																
																    description TEXT,
																
																    issue_status VARCHAR(50) NOT NULL DEFAULT 'open',
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    resolved_at TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_operations_issue_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_operations_issue_category
																        CHECK (
																            issue_category IN (
																                'operations',
																                'inventory',
																                'vendor',
																                'compliance',
																                'customer',
																                'technology',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_operations_issue_severity
																        CHECK (
																            severity IN (
																                'low',
																                'medium',
																                'high',
																                'critical'
																            )
																        ),
																
																    CONSTRAINT chk_operations_issue_impact
																        CHECK (
																            impact_area IN (
																                'budget',
																                'operations',
																                'vendor',
																                'customer',
																                'compliance',
																                'technology'
																            )
																        ),
																
																    CONSTRAINT chk_operations_issue_status
																        CHECK (
																            issue_status IN (
																                'open',
																                'investigating',
																                'resolved',
																                'archived'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_operations_issues_moment
																ON operations_issues(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_issues_status
																ON operations_issues(issue_status);
-- >>>STMT<<<
CREATE INDEX idx_operations_issues_severity
																ON operations_issues(severity);
-- >>>STMT<<<
CREATE INDEX idx_operations_issues_owner
																ON operations_issues(owner_id);
-- >>>STMT<<<
CREATE TABLE operations_improvements (
																    improvement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    improvement_type VARCHAR(100) NOT NULL,
																
																    improvement_title VARCHAR(255) NOT NULL,
																
																    impact_area VARCHAR(100) NOT NULL,
																
																    expected_impact VARCHAR(100) NOT NULL,
																
																    owner_id UUID,
																
																    effective_date DATE NOT NULL,
																
																    description TEXT,
																
																    follow_up_required BOOLEAN NOT NULL DEFAULT FALSE,
																
																    follow_up_owner_id UUID,
																
																    follow_up_date DATE,
																
																    improvement_status VARCHAR(50) NOT NULL DEFAULT 'recorded',
																
																    created_by UUID NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    completed_at TIMESTAMP,
																
																    archived_at TIMESTAMP,
																
																    CONSTRAINT fk_operations_improvement_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_operations_improvement_type
																        CHECK (
																            improvement_type IN (
																                'process_improvement',
																                'budget_control_improvement',
																                'customer_experience_improvement',
																                'inventory_improvement',
																                'compliance_improvement',
																                'staffing_scheduling_improvement',
																                'approval_flow_improvement',
																                'service_quality_improvement',
																                'operational_control_improvement',
																                'other'
																            )
																        ),
																
																    CONSTRAINT chk_operations_improvement_impact_area
																        CHECK (
																            impact_area IN (
																                'budget',
																                'operations',
																                'customer',
																                'compliance',
																                'inventory',
																                'staff',
																                'approval_flow'
																            )
																        ),
																
																    CONSTRAINT chk_operations_improvement_expected_impact
																        CHECK (
																            expected_impact IN (
																                'reduce_cost',
																                'improve_speed',
																                'reduce_issues',
																                'improve_service',
																                'improve_control',
																                'improve_visibility'
																            )
																        ),
																
																    CONSTRAINT chk_operations_improvement_status
																        CHECK (
																            improvement_status IN (
																                'recorded',
																                'in_follow_up',
																                'completed',
																                'archived'
																            )
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_operations_improvements_moment
																ON operations_improvements(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_improvements_type
																ON operations_improvements(improvement_type);
-- >>>STMT<<<
CREATE INDEX idx_operations_improvements_owner
																ON operations_improvements(owner_id);
-- >>>STMT<<<
CREATE INDEX idx_operations_improvements_status
																ON operations_improvements(improvement_status);
-- >>>STMT<<<
CREATE TABLE business_operations_snapshots (
																    operations_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    snapshot_date DATE NOT NULL,
																
																    monthly_budget NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    allocated_budget NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    budget_used NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    budget_remaining NUMERIC(18,2) NOT NULL DEFAULT 0,
																
																    budget_alert_count INTEGER NOT NULL DEFAULT 0,
																
																    vendor_activity_count INTEGER NOT NULL DEFAULT 0,
																
																    open_approval_count INTEGER NOT NULL DEFAULT 0,
																
																    active_issue_count INTEGER NOT NULL DEFAULT 0,
																
																    critical_issue_count INTEGER NOT NULL DEFAULT 0,
																
																    improvement_count INTEGER NOT NULL DEFAULT 0,
																
																    operations_health_status VARCHAR(50) NOT NULL DEFAULT 'healthy',
																
																    operating_currency VARCHAR(10) NOT NULL DEFAULT 'INR',
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_business_operations_snapshot_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES business_moments(moment_id),
																
																    CONSTRAINT chk_business_operations_health_status
																        CHECK (
																            operations_health_status IN (
																                'healthy',
																                'attention',
																                'at_risk'
																            )
																        )
																);
-- >>>STMT<<<
CREATE UNIQUE INDEX uq_business_operations_snapshot_day
																ON business_operations_snapshots(moment_id, snapshot_date);
-- >>>STMT<<<
CREATE INDEX idx_business_operations_snapshot_moment
																ON business_operations_snapshots(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_business_operations_snapshot_date
																ON business_operations_snapshots(snapshot_date DESC);
-- >>>STMT<<<
ALTER TABLE business_moments
																DROP CONSTRAINT IF EXISTS chk_business_moment_type;
-- >>>STMT<<<
ALTER TABLE business_moments
																ADD CONSTRAINT chk_business_moment_type
																CHECK (
																    moment_type IN (
																        'team_operations',
																        'business_runway',
																        'business_operations',
																        'project_operations',
																        'event_operations',
																        'department_operations',
																        'vendor_operations',
																        'custom_operational_moment'
																    )
																);
-- >>>STMT<<<
ALTER TABLE business_moment_members
																DROP CONSTRAINT IF EXISTS chk_member_role;
-- >>>STMT<<<
ALTER TABLE business_moment_members
																ADD CONSTRAINT chk_member_role
																CHECK (
																    role IN (
																        'Team Member',
																        'Team Lead',
																        'Budget Owner',
																        'Approver',
																        'Observer',
																
																        'Runway Owner',
																        'Finance Lead',
																        'Operations Lead',
																        'Financial Contributor',
																        'Viewer',
																
																        'Operations Owner',
																        'Budget Controller',
																        'Contributor'
																    )
																);
-- >>>STMT<<<
ALTER TABLE business_moment_members
																ADD COLUMN IF NOT EXISTS can_add_operations_records BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS can_edit_operations_records BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS can_edit_own_operations_records BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS can_approve_operations_requests BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS can_delete_operations_records BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS can_manage_operations_settings BOOLEAN NOT NULL DEFAULT FALSE;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_apply_operations_member_permissions
																ON business_moment_members;
-- >>>STMT<<<
ALTER TABLE business_moment_governance
																ADD COLUMN IF NOT EXISTS operations_visibility_roles JSONB,
																ADD COLUMN IF NOT EXISTS operations_alert_roles JSONB,
																ADD COLUMN IF NOT EXISTS operations_alert_conditions JSONB,
																ADD COLUMN IF NOT EXISTS operations_approval_required BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS operations_approval_rules JSONB,
																ADD COLUMN IF NOT EXISTS operations_monitoring_level VARCHAR(50);
-- >>>STMT<<<
ALTER TABLE business_pulse_snapshots
																ADD COLUMN IF NOT EXISTS operations_health_status VARCHAR(50) DEFAULT 'healthy',
																ADD COLUMN IF NOT EXISTS active_issue_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS open_approval_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS budget_alert_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS improvement_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS budget_used_total NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS budget_remaining_total NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS vendor_activity_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS operations_operating_currency VARCHAR(10) DEFAULT 'INR';
-- >>>STMT<<<
ALTER TABLE business_pulse_snapshots
																DROP CONSTRAINT IF EXISTS chk_business_pulse_operations_health_status;
-- >>>STMT<<<
ALTER TABLE business_pulse_snapshots
																ADD CONSTRAINT chk_business_pulse_operations_health_status
																CHECK (
																    operations_health_status IS NULL
																    OR operations_health_status IN (
																        'healthy',
																        'attention',
																        'at_risk'
																    )
																);
-- >>>STMT<<<
ALTER TABLE business_moment_metrics
																ADD COLUMN IF NOT EXISTS budget_category_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS operations_budget_used_total NUMERIC(18,2) NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS operations_active_issue_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS operations_approval_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS operations_improvement_count INTEGER NOT NULL DEFAULT 0,
																ADD COLUMN IF NOT EXISTS last_operations_activity_at TIMESTAMP,
																ADD COLUMN IF NOT EXISTS latest_spend_title VARCHAR(255),
																ADD COLUMN IF NOT EXISTS latest_issue_title VARCHAR(255),
																ADD COLUMN IF NOT EXISTS latest_approval_status VARCHAR(50),
																ADD COLUMN IF NOT EXISTS latest_improvement_title VARCHAR(255),
																ADD COLUMN IF NOT EXISTS operations_operating_currency VARCHAR(10) DEFAULT 'INR';
-- >>>STMT<<<
ALTER TABLE business_memory_patterns
																DROP CONSTRAINT IF EXISTS chk_business_memory_pattern_type;
-- >>>STMT<<<
ALTER TABLE business_memory_patterns
																ADD CONSTRAINT chk_business_memory_pattern_type
																CHECK (
																    pattern_type IN (
																        'vendor',
																        'vendor_pattern',
																        'spend_pattern',
																        'approval_pattern',
																        'risk_pattern',
																        'ownership_pattern',
																
																        'cash_inflow_pattern',
																        'burn_pattern',
																        'runway_risk_pattern',
																        'decision_pattern',
																        'financial_update_pattern',
																        'net_burn_pattern',
																
																        'operations_budget_pattern',
																        'operations_vendor_pattern',
																        'operations_approval_pattern',
																        'operations_issue_pattern',
																        'operations_improvement_pattern'
																    )
																);
-- >>>STMT<<<
ALTER TABLE business_live_feed
																DROP CONSTRAINT IF EXISTS chk_live_visibility;
-- >>>STMT<<<
ALTER TABLE business_live_feed
																ADD CONSTRAINT chk_live_visibility
																CHECK (
																    visibility IN (
																        'team_only',
																        'leadership',
																        'organization',
																
																        'runway_roles',
																        'runway_owners',
																        'finance_leads',
																        'all_runway_participants',
																
																        'operations_roles',
																        'operations_owners',
																        'operations_leads',
																        'budget_controllers',
																        'all_operations_participants'
																    )
																);
-- >>>STMT<<<
ALTER TABLE business_transaction_permissions
																ADD COLUMN IF NOT EXISTS can_approve BOOLEAN NOT NULL DEFAULT FALSE;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_operations_approval_member_refs
																ON operations_approval_requests;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_operations_issue_member_refs
																ON operations_issues;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_operations_improvement_member_refs
																ON operations_improvements;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_pulse_operations_snapshot
																ON business_pulse_snapshots(moment_id, snapshot_date DESC);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_moment_metrics_operations
																ON business_moment_metrics(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_memory_patterns_operations_type
																ON business_memory_patterns(moment_id, pattern_type);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_live_feed_operations_source
																ON business_live_feed(source_table, source_record_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_business_transaction_permissions_operations
																ON business_transaction_permissions(moment_id, source_table, source_record_id, role_name);
-- >>>STMT<<<
CREATE TABLE business_health_driver_scores (
																    score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES business_moments(moment_id),
																
																    driver_code VARCHAR(100) NOT NULL,
																    driver_name VARCHAR(255) NOT NULL,
																
																    driver_score NUMERIC(5,2) NOT NULL DEFAULT 0,
																
																    driver_status VARCHAR(50) NOT NULL DEFAULT 'stable',
																
																    score_delta NUMERIC(5,2),
																
																    trend_direction VARCHAR(30),
																
																    source_table VARCHAR(100),
																    source_record_id UUID,
																
																    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_health_driver_moment
																ON business_health_driver_scores(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_health_driver_code
																ON business_health_driver_scores(driver_code);
-- >>>STMT<<<
CREATE TABLE business_attention_items (
																    attention_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES business_moments(moment_id),
																
																    attention_type VARCHAR(100) NOT NULL,
																
																    severity VARCHAR(30) NOT NULL,
																
																    title VARCHAR(255) NOT NULL,
																
																    description TEXT,
																
																    due_date TIMESTAMP,
																
																    status VARCHAR(50) NOT NULL DEFAULT 'open',
																
																    source_table VARCHAR(100),
																    source_record_id UUID,
																
																    generated_by VARCHAR(50) DEFAULT 'system',
																
																    resolved_at TIMESTAMP,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_attention_moment
																ON business_attention_items(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_attention_status
																ON business_attention_items(status);
-- >>>STMT<<<
CREATE TABLE business_signal_insights (
																    signal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES business_moments(moment_id),
																
																    signal_type VARCHAR(100) NOT NULL,
																
																    signal_title VARCHAR(255) NOT NULL,
																
																    signal_summary TEXT NOT NULL,
																
																    impact_level VARCHAR(50) NOT NULL,
																
																    change_percent NUMERIC(8,2),
																
																    lookback_days INTEGER DEFAULT 7,
																
																    source_table VARCHAR(100),
																    source_record_id UUID,
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    expires_at TIMESTAMP,
																
																    signal_status VARCHAR(50) DEFAULT 'active'
																);
-- >>>STMT<<<
CREATE INDEX idx_signal_moment
																ON business_signal_insights(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_signal_status
																ON business_signal_insights(signal_status);
-- >>>STMT<<<
CREATE TABLE business_recommended_actions (
																    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES business_moments(moment_id),
																
																    action_title VARCHAR(255) NOT NULL,
																
																    action_reason TEXT NOT NULL,
																
																    priority VARCHAR(30) NOT NULL,
																
																    cta_label VARCHAR(100) NOT NULL,
																
																    target_screen VARCHAR(100),
																
																    target_payload JSONB,
																
																    expected_health_impact NUMERIC(5,2),
																
																    source_rule VARCHAR(255),
																
																    status VARCHAR(50) DEFAULT 'active',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    completed_at TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_recommended_action_moment
																ON business_recommended_actions(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_recommended_action_status
																ON business_recommended_actions(status);
-- >>>STMT<<<
CREATE TABLE business_moment_highlights (
																    highlight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES business_moments(moment_id),
																
																    highlight_type VARCHAR(100) NOT NULL,
																
																    highlight_title VARCHAR(255) NOT NULL,
																
																    highlight_summary TEXT,
																
																    source_table VARCHAR(100),
																
																    source_record_id UUID,
																
																    impact_level VARCHAR(50),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    highlight_status VARCHAR(50) DEFAULT 'active'
																);
-- >>>STMT<<<
CREATE INDEX idx_moment_highlight_moment
																ON business_moment_highlights(moment_id);
-- >>>STMT<<<
CREATE TABLE business_progress_snapshots (
																    progress_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES business_moments(moment_id),
																
																    metric_code VARCHAR(100) NOT NULL,
																
																    metric_name VARCHAR(255) NOT NULL,
																
																    metric_score NUMERIC(5,2) NOT NULL,
																
																    metric_delta NUMERIC(5,2),
																
																    metric_status VARCHAR(50),
																
																    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_progress_snapshot_moment
																ON business_progress_snapshots(moment_id);
-- >>>STMT<<<
CREATE TABLE business_life_dimensions (
																    dimension_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    dimension_type VARCHAR(100) NOT NULL,
																
																    dimension_name VARCHAR(255) NOT NULL,
																
																    dimension_score NUMERIC(5,2) NOT NULL,
																
																    dimension_status VARCHAR(50),
																
																    trend_direction VARCHAR(30),
																
																    trend_delta NUMERIC(5,2),
																
																    active_moment_count INTEGER DEFAULT 0,
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_life_dimension_workspace
																ON business_life_dimensions(workspace_id);
-- >>>STMT<<<
CREATE TABLE business_life_connections (
																    connection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    source_dimension VARCHAR(100),
																
																    source_label VARCHAR(255),
																
																    source_change NUMERIC(8,2),
																
																    influence_type VARCHAR(50),
																
																    influence_strength VARCHAR(50),
																
																    target_dimension VARCHAR(100),
																
																    target_label VARCHAR(255),
																
																    target_change NUMERIC(8,2),
																
																    confidence_score NUMERIC(5,2),
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_life_connection_workspace
																ON business_life_connections(workspace_id);
-- >>>STMT<<<
CREATE TABLE business_life_insights (
																    life_insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    insight_type VARCHAR(100) NOT NULL,
																
																    insight_title VARCHAR(255) NOT NULL,
																
																    insight_body TEXT NOT NULL,
																
																    insight_score NUMERIC(5,2),
																
																    priority VARCHAR(30),
																
																    source_dimension VARCHAR(100),
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    insight_status VARCHAR(50) DEFAULT 'active'
																);
-- >>>STMT<<<
CREATE INDEX idx_life_insights_workspace
																ON business_life_insights(workspace_id);
-- >>>STMT<<<
CREATE INDEX idx_life_insights_type
																ON business_life_insights(insight_type);
-- >>>STMT<<<
CREATE TABLE business_life_snapshots (
																    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    life_score NUMERIC(5,2) NOT NULL,
																
																    life_status VARCHAR(50) NOT NULL,
																
																    people_score NUMERIC(5,2),
																
																    finance_score NUMERIC(5,2),
																
																    operations_score NUMERIC(5,2),
																
																    vendor_score NUMERIC(5,2),
																
																    growth_score NUMERIC(5,2),
																
																    active_moment_count INTEGER DEFAULT 0,
																
																    strongest_dimension VARCHAR(100),
																
																    weakest_dimension VARCHAR(100),
																
																    leverage_dimension VARCHAR(100),
																
																    drift_detected BOOLEAN DEFAULT FALSE,
																
																    life_score_delta NUMERIC(5,2),
																
																    included_moment_types JSONB,
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_life_snapshot_workspace
																ON business_life_snapshots(workspace_id);
-- >>>STMT<<<
CREATE TABLE business_memory_learnings (
																    learning_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    moment_id UUID
																        REFERENCES business_moments(moment_id),
																
																    learning_type VARCHAR(100),
																
																    learning_title VARCHAR(255),
																
																    learning_summary TEXT,
																
																    confidence_score NUMERIC(5,2),
																
																    derived_from_count INTEGER,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    learning_status VARCHAR(50) DEFAULT 'active'
																);
-- >>>STMT<<<
CREATE TABLE business_playbooks (
																    playbook_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    moment_id UUID
																        REFERENCES business_moments(moment_id),
																
																    playbook_title VARCHAR(255),
																
																    playbook_summary TEXT,
																
																    success_rate NUMERIC(5,2),
																
																    confidence_score NUMERIC(5,2),
																
																    playbook_status VARCHAR(50) DEFAULT 'active',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE TABLE business_success_memory (
																    success_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    moment_id UUID
																        REFERENCES business_moments(moment_id),
																
																    success_title VARCHAR(255),
																
																    success_summary TEXT,
																
																    action_taken TEXT,
																
																    impact_score NUMERIC(5,2),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE TABLE business_risk_memory (
																    risk_memory_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    moment_id UUID
																        REFERENCES business_moments(moment_id),
																
																    risk_title VARCHAR(255),
																
																    risk_summary TEXT,
																
																    observed_count INTEGER DEFAULT 1,
																
																    severity VARCHAR(30),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE TABLE business_wisdom (
																    wisdom_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    moment_id UUID
																        REFERENCES business_moments(moment_id),
																
																    wisdom_text TEXT NOT NULL,
																
																    confidence_score NUMERIC(5,2),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE TABLE business_memory_snapshots (
																    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    workspace_id UUID NOT NULL,
																
																    memory_score NUMERIC(5,2) NOT NULL,
																
																    memory_status VARCHAR(50) NOT NULL,
																
																    learning_count INTEGER DEFAULT 0,
																
																    playbook_count INTEGER DEFAULT 0,
																
																    risk_count INTEGER DEFAULT 0,
																
																    strongest_learning_id UUID,
																
																    strongest_wisdom_id UUID,
																
																    memory_score_delta NUMERIC(5,2),
																
																    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_memory_snapshot_workspace
																ON business_memory_snapshots(workspace_id);
-- >>>STMT<<<
CREATE TABLE business_activity_permissions (
																    permission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES business_moments(moment_id),
																
																    source_table VARCHAR(100) NOT NULL,
																
																    source_record_id UUID NOT NULL,
																
																    role_name VARCHAR(100) NOT NULL,
																
																    can_view BOOLEAN DEFAULT TRUE,
																
																    can_edit BOOLEAN DEFAULT FALSE,
																
																    can_delete BOOLEAN DEFAULT FALSE,
																
																    can_approve BOOLEAN DEFAULT FALSE,
																
																    permission_reason TEXT,
																
																    granted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE TABLE business_activity_center_items (
																    activity_center_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES business_moments(moment_id),
																
																    source_table VARCHAR(100),
																
																    source_record_id UUID,
																
																    activity_type VARCHAR(100),
																
																    activity_title VARCHAR(255),
																
																    activity_summary TEXT,
																
																    amount NUMERIC(18,2),
																
																    currency VARCHAR(10),
																
																    actor_user_id UUID,
																
																    actor_name VARCHAR(255),
																
																    activity_status VARCHAR(50),
																
																    permission_badge VARCHAR(50),
																
																    occurred_at TIMESTAMP NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_activity_center_moment
																ON business_activity_center_items(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_activity_center_occurred
																ON business_activity_center_items(occurred_at DESC);
-- >>>STMT<<<
ALTER TABLE business_pulse_snapshots
																ADD COLUMN IF NOT EXISTS pulse_category VARCHAR(50),
																
																ADD COLUMN IF NOT EXISTS pulse_description TEXT,
																
																ADD COLUMN IF NOT EXISTS health_driver_count INTEGER NOT NULL DEFAULT 0,
																
																ADD COLUMN IF NOT EXISTS attention_count INTEGER NOT NULL DEFAULT 0,
																
																ADD COLUMN IF NOT EXISTS signal_count INTEGER NOT NULL DEFAULT 0,
																
																ADD COLUMN IF NOT EXISTS next_best_action_id UUID;
-- >>>STMT<<<
ALTER TABLE business_moment_metrics
																ADD COLUMN IF NOT EXISTS progress_score NUMERIC(5,2),
																
																ADD COLUMN IF NOT EXISTS progress_status VARCHAR(50),
																
																ADD COLUMN IF NOT EXISTS recent_wins_count INTEGER NOT NULL DEFAULT 0,
																
																ADD COLUMN IF NOT EXISTS timeline_count INTEGER NOT NULL DEFAULT 0,
																
																ADD COLUMN IF NOT EXISTS continue_cta_label VARCHAR(100);
-- >>>STMT<<<
ALTER TABLE business_live_feed
																ADD COLUMN IF NOT EXISTS edit_mode VARCHAR(50),
																
																ADD COLUMN IF NOT EXISTS permission_badge VARCHAR(50),
																
																ADD COLUMN IF NOT EXISTS activity_center_visible BOOLEAN NOT NULL DEFAULT TRUE;
-- >>>STMT<<<
ALTER TABLE business_memory_patterns
																ADD COLUMN IF NOT EXISTS workspace_id UUID,
																
																ADD COLUMN IF NOT EXISTS pattern_strength NUMERIC(5,2),
																
																ADD COLUMN IF NOT EXISTS display_priority INTEGER NOT NULL DEFAULT 100;
-- >>>STMT<<<
ALTER TABLE business_orchestration_jobs
																ADD COLUMN IF NOT EXISTS workspace_id UUID,
																
																ADD COLUMN IF NOT EXISTS orchestration_scope VARCHAR(50),
																
																ADD COLUMN IF NOT EXISTS priority VARCHAR(30) DEFAULT 'medium';
-- >>>STMT<<<
ALTER TABLE business_moment_members
																
																ADD COLUMN IF NOT EXISTS can_add_runway_transactions BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_edit_financial_entries BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_manage_runway_settings BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_approve_runway_changes BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_add_operations_records BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_edit_operations_records BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_edit_own_operations_records BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_approve_operations_requests BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_delete_operations_records BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS can_manage_operations_settings BOOLEAN DEFAULT FALSE;
-- >>>STMT<<<
ALTER TABLE business_moment_governance
																
																ADD COLUMN IF NOT EXISTS runway_visibility_roles JSONB,
																
																ADD COLUMN IF NOT EXISTS runway_alert_roles JSONB,
																
																ADD COLUMN IF NOT EXISTS runway_alert_conditions JSONB,
																
																ADD COLUMN IF NOT EXISTS runway_approval_required BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS runway_approval_rules JSONB,
																
																ADD COLUMN IF NOT EXISTS operations_visibility_roles JSONB,
																
																ADD COLUMN IF NOT EXISTS operations_alert_roles JSONB,
																
																ADD COLUMN IF NOT EXISTS operations_alert_conditions JSONB,
																
																ADD COLUMN IF NOT EXISTS operations_approval_required BOOLEAN DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS operations_approval_rules JSONB,
																
																ADD COLUMN IF NOT EXISTS operations_monitoring_level VARCHAR(50);
-- >>>STMT<<<
ALTER TABLE business_transaction_permissions
																ADD COLUMN IF NOT EXISTS can_approve BOOLEAN DEFAULT FALSE;
-- >>>STMT<<<
ALTER TABLE team_approval_requests
																
																ADD COLUMN IF NOT EXISTS converted_activity_id UUID,
																
																ADD COLUMN IF NOT EXISTS converted_to_spend BOOLEAN NOT NULL DEFAULT FALSE,
																
																ADD COLUMN IF NOT EXISTS converted_at TIMESTAMP;
-- >>>STMT<<<
ALTER TABLE business_pulse_snapshots
																ADD CONSTRAINT fk_business_pulse_next_action
																FOREIGN KEY (next_best_action_id)
																REFERENCES business_recommended_actions(action_id);
-- >>>STMT<<<
ALTER TABLE business_memory_snapshots
																ADD CONSTRAINT fk_memory_snapshot_learning
																FOREIGN KEY (strongest_learning_id)
																REFERENCES business_memory_learnings(learning_id);
-- >>>STMT<<<
ALTER TABLE business_memory_snapshots
																ADD CONSTRAINT fk_memory_snapshot_wisdom
																FOREIGN KEY (strongest_wisdom_id)
																REFERENCES business_wisdom(wisdom_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_pulse_next_action
																ON business_pulse_snapshots(next_best_action_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_pattern_workspace
																ON business_memory_patterns(workspace_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_pattern_strength
																ON business_memory_patterns(pattern_strength DESC);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_orchestration_workspace
																ON business_orchestration_jobs(workspace_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_orchestration_scope
																ON business_orchestration_jobs(orchestration_scope);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_member_runway_permissions
																ON business_moment_members(
																    can_add_runway_transactions,
																    can_edit_financial_entries
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_member_operations_permissions
																ON business_moment_members(
																    can_add_operations_records,
																    can_edit_operations_records
																);
-- >>>STMT<<<
ALTER TABLE business_orchestration_jobs
ADD CONSTRAINT chk_business_orchestration_job_type
CHECK (
    job_type IN (
        'pulse_refresh',
        'moments_refresh',
        'life_refresh',
        'memory_refresh',
        'activity_refresh',
        'workspace_refresh',
        'business_360_refresh'
    )
);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_refresh
ON business_runway_transactions;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_operations_refresh
ON team_operation_activities;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_operations_refresh
ON business_operation_records;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_approval_refresh
ON team_approval_requests;
-- >>>STMT<<<
ALTER TABLE business_orchestration_jobs
ADD COLUMN IF NOT EXISTS attempts INTEGER DEFAULT 0;
-- >>>STMT<<<
ALTER TABLE operations_budget_categories
ADD COLUMN IF NOT EXISTS alert_threshold_percent NUMERIC(5,2)
DEFAULT 80;
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS business_activity_source_mapping (
    mapping_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    source_table VARCHAR(100) NOT NULL,

    title_field VARCHAR(100) NOT NULL,

    description_field VARCHAR(100),

    status_field VARCHAR(100),

    date_field VARCHAR(100),

    amount_field VARCHAR(100),

    active_flag BOOLEAN DEFAULT TRUE
);
-- >>>STMT<<<
COMMENT ON TABLE business_signal_insights IS
'Pulse UI signal cache generated from ai_signals and business analytics.';
-- >>>STMT<<<
COMMENT ON TABLE business_activity_permissions IS
'Derived permission cache for Activity Center rendering.';
-- >>>STMT<<<
CREATE TABLE business_driver_formula_registry (

    driver_formula_id UUID PRIMARY KEY
    DEFAULT gen_random_uuid(),

    moment_type VARCHAR(100) NOT NULL,

    driver_code VARCHAR(100) NOT NULL,

    driver_name VARCHAR(255) NOT NULL,

    driver_weight NUMERIC(5,2) NOT NULL,

    source_table VARCHAR(255) NOT NULL,

    source_column VARCHAR(255),

    formula_description TEXT NOT NULL,

    active_flag BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS business_driver_formula_registry (
    driver_formula_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    moment_type VARCHAR(100) NOT NULL,
    driver_code VARCHAR(100) NOT NULL,
    driver_name VARCHAR(255) NOT NULL,

    driver_weight NUMERIC(5,2) NOT NULL,

    source_table VARCHAR(255) NOT NULL,
    source_column VARCHAR(255),

    formula_description TEXT NOT NULL,

    active_flag BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_driver_formula_weight
        CHECK (driver_weight > 0 AND driver_weight <= 100)
);
-- >>>STMT<<<
CREATE UNIQUE INDEX IF NOT EXISTS uq_driver_formula_registry
ON business_driver_formula_registry(moment_type, driver_code)
WHERE active_flag = TRUE;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_driver_formula_moment_type
ON business_driver_formula_registry(moment_type);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_activities_archive
ON team_activities;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_approvals_archive
ON team_approval_requests;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_updates_archive
ON team_updates;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_issue_risks_archive
ON team_issue_risks;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_cash_inflows_archive
ON runway_cash_inflows;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_expense_burns_archive
ON runway_expense_burns;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_risks_archive
ON runway_risks;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_financial_updates_archive
ON runway_financial_updates;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_strategic_decisions_archive
ON runway_strategic_decisions;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_spend_entries_archive
ON operations_spend_entries;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_vendor_updates_archive
ON operations_vendor_updates;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_approval_requests_archive
ON operations_approval_requests;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_issues_archive
ON operations_issues;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_improvements_archive
ON operations_improvements;

CREATE TABLE group_moments (
																    moment_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_type              VARCHAR(50) NOT NULL,
																    moment_profile           VARCHAR(100) NOT NULL,
																    moment_name              VARCHAR(200) NOT NULL,
																
																    status                   VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
																    stage                    VARCHAR(50) NOT NULL DEFAULT 'CREATED',
																
																    currency_code            VARCHAR(10) NOT NULL DEFAULT 'INR',
																
																    created_by               UUID NOT NULL,
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    activated_at             TIMESTAMP NULL,
																    updated_at               TIMESTAMP NULL,
																
																    CONSTRAINT chk_group_moment_status
																        CHECK (status IN ('DRAFT','ACTIVE','COMPLETED','ARCHIVED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_group_moments_type
																ON group_moments(moment_type);
-- >>>STMT<<<
CREATE INDEX idx_group_moments_status
																ON group_moments(status);
-- >>>STMT<<<
CREATE INDEX idx_group_moments_stage
																ON group_moments(stage);
-- >>>STMT<<<
CREATE TABLE group_moment_profiles (
																    profile_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_type              VARCHAR(50) NOT NULL,
																
																    profile_code             VARCHAR(100) NOT NULL,
																    profile_name             VARCHAR(200) NOT NULL,
																
																    profile_description      TEXT,
																
																    display_order            INTEGER NOT NULL,
																
																    is_active                BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT uq_group_profile
																    UNIQUE(moment_type, profile_code)
																);
-- >>>STMT<<<
CREATE INDEX idx_group_profiles_type
																ON group_moment_profiles(moment_type);
-- >>>STMT<<<
CREATE TABLE group_moment_roles (
																    role_code                VARCHAR(100) PRIMARY KEY,
																
																    moment_type              VARCHAR(50) NOT NULL,
																
																    role_name                VARCHAR(200) NOT NULL,
																    role_description         TEXT,
																
																    permission_json          JSONB NOT NULL,
																
																    display_order            INTEGER NOT NULL,
																
																    is_default               BOOLEAN NOT NULL DEFAULT FALSE,
																    is_active                BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_group_roles_type
																ON group_moment_roles(moment_type);
-- >>>STMT<<<
CREATE TABLE group_moment_members (
																    member_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    display_name             VARCHAR(200) NOT NULL,
																
																    role_code                VARCHAR(100) NOT NULL,
																
																    status                   VARCHAR(30) NOT NULL DEFAULT 'INVITED',
																
																    joined_at                TIMESTAMP NULL,
																    left_at                  TIMESTAMP NULL,
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gmm_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gmm_role
																        FOREIGN KEY(role_code)
																        REFERENCES group_moment_roles(role_code)
																);
-- >>>STMT<<<
CREATE INDEX idx_group_members_moment
																ON group_moment_members(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_group_members_status
																ON group_moment_members(status);
-- >>>STMT<<<
CREATE TABLE group_quick_add_config (
																    config_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_type              VARCHAR(50) NOT NULL,
																    moment_profile           VARCHAR(100) NOT NULL,
																
																    module_code              VARCHAR(100) NOT NULL,
																    module_label             VARCHAR(200) NOT NULL,
																
																    display_order            INTEGER NOT NULL,
																
																    is_enabled               BOOLEAN NOT NULL DEFAULT TRUE,
																    is_visible               BOOLEAN NOT NULL DEFAULT TRUE,
																    is_required              BOOLEAN NOT NULL DEFAULT FALSE,
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_quick_add_profile
																ON group_quick_add_config(moment_type,moment_profile);
-- >>>STMT<<<
CREATE TABLE group_field_value_config (
																    config_value_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_type             VARCHAR(50) NOT NULL,
																    moment_profile          VARCHAR(100) NOT NULL,
																
																    module_code             VARCHAR(100) NOT NULL,
																
																    field_name              VARCHAR(100) NOT NULL,
																
																    value_code              VARCHAR(100) NOT NULL,
																    value_label             VARCHAR(200) NOT NULL,
																
																    display_order           INTEGER NOT NULL,
																
																    is_top_category         BOOLEAN NOT NULL DEFAULT FALSE,
																    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE INDEX idx_field_config_lookup
																ON group_field_value_config
																(moment_type,moment_profile,module_code,field_name);
-- >>>STMT<<<
CREATE TABLE group_moment_stage_history (
																    stage_history_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id               UUID NOT NULL,
																
																    old_stage               VARCHAR(50),
																    new_stage               VARCHAR(50) NOT NULL,
																
																    change_reason           TEXT,
																
																    source_event_id         UUID,
																
																    changed_by             UUID NOT NULL,
																
																    changed_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    is_current             BOOLEAN NOT NULL DEFAULT TRUE,
																
																    CONSTRAINT fk_stage_history_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_stage_history_moment
																ON group_moment_stage_history(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_stage_history_current
																ON group_moment_stage_history(is_current);
-- >>>STMT<<<
CREATE TABLE group_quick_add_events (
																    event_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id             UUID NOT NULL,
																
																    module_code           VARCHAR(100) NOT NULL,
																    event_ref_table       VARCHAR(150) NOT NULL,
																    event_ref_id          UUID NOT NULL,
																
																    event_action          VARCHAR(30) NOT NULL DEFAULT 'CREATED',
																    created_by            UUID NOT NULL,
																    event_time            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    event_payload_json    JSONB,
																
																    CONSTRAINT fk_qae_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_qae_action
																        CHECK (event_action IN ('CREATED','EDITED','DELETED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_qae_moment
																ON group_quick_add_events(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_qae_module
																ON group_quick_add_events(module_code);
-- >>>STMT<<<
CREATE INDEX idx_qae_time
																ON group_quick_add_events(event_time);
-- >>>STMT<<<
CREATE TABLE group_live_feed (
																    feed_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id             UUID NOT NULL,
																    event_id              UUID NOT NULL,
																
																    feed_category         VARCHAR(100) NOT NULL,
																    title                 VARCHAR(250) NOT NULL,
																    summary               TEXT,
																
																    can_view              BOOLEAN NOT NULL DEFAULT TRUE,
																    can_edit              BOOLEAN NOT NULL DEFAULT TRUE,
																
																    visibility            VARCHAR(50) NOT NULL DEFAULT 'EVERYONE',
																    is_hidden             BOOLEAN NOT NULL DEFAULT FALSE,
																
																    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_glf_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_glf_event
																        FOREIGN KEY(event_id)
																        REFERENCES group_quick_add_events(event_id),
																
																    CONSTRAINT chk_glf_visibility
																        CHECK (visibility IN ('EVERYONE','ORGANIZERS','SELECTED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_live_feed_moment
																ON group_live_feed(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_live_feed_event
																ON group_live_feed(event_id);
-- >>>STMT<<<
CREATE INDEX idx_live_feed_category
																ON group_live_feed(feed_category);
-- >>>STMT<<<
CREATE INDEX idx_live_feed_created
																ON group_live_feed(created_at);
-- >>>STMT<<<
CREATE TABLE group_change_history (
																    change_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id             UUID NOT NULL,
																
																    entity_name           VARCHAR(150) NOT NULL,
																    entity_id             UUID NOT NULL,
																
																    field_name            VARCHAR(150),
																    old_value             TEXT,
																    new_value             TEXT,
																
																    change_type           VARCHAR(30) NOT NULL,
																    changed_by            UUID NOT NULL,
																    changed_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gch_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_gch_type
																        CHECK (change_type IN ('CREATED','UPDATED','DELETED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_change_history_moment
																ON group_change_history(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_change_history_entity
																ON group_change_history(entity_name, entity_id);
-- >>>STMT<<<
CREATE INDEX idx_change_history_time
																ON group_change_history(changed_at);
-- >>>STMT<<<
CREATE TABLE group_attachments (
																    attachment_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id             UUID NOT NULL,
																    event_id              UUID,
																
																    entity_name           VARCHAR(150) NOT NULL,
																    entity_id             UUID NOT NULL,
																
																    file_url              TEXT NOT NULL,
																    file_type             VARCHAR(50) NOT NULL,
																
																    uploaded_by           UUID NOT NULL,
																    uploaded_at           TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    is_deleted            BOOLEAN NOT NULL DEFAULT FALSE,
																
																    CONSTRAINT fk_ga_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_ga_event
																        FOREIGN KEY(event_id)
																        REFERENCES group_quick_add_events(event_id),
																
																    CONSTRAINT chk_ga_file_type
																        CHECK (file_type IN ('IMAGE','PDF','AUDIO','VIDEO','OTHER'))
																);
-- >>>STMT<<<
CREATE INDEX idx_attachments_moment
																ON group_attachments(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_attachments_entity
																ON group_attachments(entity_name, entity_id);
-- >>>STMT<<<
CREATE INDEX idx_attachments_event
																ON group_attachments(event_id);
-- >>>STMT<<<
CREATE TABLE group_expenses (
																    expense_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id             UUID NOT NULL,
																
																    module_context        VARCHAR(50) NOT NULL,
																    category              VARCHAR(100) NOT NULL,
																
																    expense_name          VARCHAR(200) NOT NULL,
																    amount                DECIMAL(12,2) NOT NULL,
																    expense_date          DATE NOT NULL,
																
																    paid_by_member_id     UUID NOT NULL,
																
																    status                VARCHAR(30) NOT NULL DEFAULT 'RECORDED',
																    notes                 TEXT,
																
																    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at            TIMESTAMP,
																
																    CONSTRAINT fk_ge_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_ge_paid_by
																        FOREIGN KEY(paid_by_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_ge_amount
																        CHECK (amount > 0),
																
																    CONSTRAINT chk_ge_status
																        CHECK (status IN ('RECORDED','EDITED','DELETED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_group_expenses_moment
																ON group_expenses(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_group_expenses_context
																ON group_expenses(module_context);
-- >>>STMT<<<
CREATE INDEX idx_group_expenses_date
																ON group_expenses(expense_date);
-- >>>STMT<<<
CREATE TABLE group_expense_splits (
																    split_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    expense_id            UUID NOT NULL,
																    member_id             UUID NOT NULL,
																
																    split_method          VARCHAR(50) NOT NULL,
																    split_amount          DECIMAL(12,2) NOT NULL,
																    split_percentage      DECIMAL(5,2),
																
																    settlement_status     VARCHAR(30) NOT NULL DEFAULT 'OPEN',
																
																    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_ges_expense
																        FOREIGN KEY(expense_id)
																        REFERENCES group_expenses(expense_id),
																
																    CONSTRAINT fk_ges_member
																        FOREIGN KEY(member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_ges_amount
																        CHECK (split_amount >= 0),
																
																    CONSTRAINT chk_ges_method
																        CHECK (split_method IN ('EQUAL','CUSTOM_AMOUNT','CUSTOM_PERCENTAGE','ORGANIZER_PAID')),
																
																    CONSTRAINT chk_ges_settlement
																        CHECK (settlement_status IN ('OPEN','SETTLED','WAIVED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_expense_splits_expense
																ON group_expense_splits(expense_id);
-- >>>STMT<<<
CREATE INDEX idx_expense_splits_member
																ON group_expense_splits(member_id);
-- >>>STMT<<<
CREATE TABLE group_contributions (
																    contribution_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id              UUID NOT NULL,
																
																    contributor_member_id  UUID NOT NULL,
																    category               VARCHAR(100) NOT NULL,
																
																    amount                 DECIMAL(12,2) NOT NULL,
																    contribution_date      DATE NOT NULL,
																
																    payment_method         VARCHAR(50),
																    status                 VARCHAR(30) NOT NULL DEFAULT 'PENDING',
																
																    reference_number       VARCHAR(150),
																    notes                  TEXT,
																
																    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at             TIMESTAMP,
																
																    CONSTRAINT fk_gc_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gc_member
																        FOREIGN KEY(contributor_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_gc_amount
																        CHECK (amount > 0),
																
																    CONSTRAINT chk_gc_status
																        CHECK (status IN ('PENDING','RECEIVED')),
																
																    CONSTRAINT chk_gc_payment_method
																        CHECK (
																            payment_method IS NULL OR
																            payment_method IN ('UPI','BANK_TRANSFER','CARD','CASH','OTHER')
																        )
																);
-- >>>STMT<<<
CREATE INDEX idx_contributions_moment
																ON group_contributions(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_contributions_member
																ON group_contributions(contributor_member_id);
-- >>>STMT<<<
CREATE INDEX idx_contributions_status
																ON group_contributions(status);
-- >>>STMT<<<
CREATE TABLE group_attendance (
																    attendance_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id              UUID NOT NULL,
																    member_id              UUID NOT NULL,
																
																    attendance_type        VARCHAR(100) NOT NULL,
																    status                 VARCHAR(50) NOT NULL,
																    attendance_date        DATE,
																    notes                  TEXT,
																
																    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at             TIMESTAMP,
																
																    CONSTRAINT fk_ga_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_ga_member
																        FOREIGN KEY(member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_ga_status
																        CHECK (status IN ('CONFIRMED','TENTATIVE','DECLINED','ATTENDED','ABSENT'))
																);
-- >>>STMT<<<
CREATE INDEX idx_attendance_moment
																ON group_attendance(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_attendance_member
																ON group_attendance(member_id);
-- >>>STMT<<<
CREATE INDEX idx_attendance_status
																ON group_attendance(status);
-- >>>STMT<<<
CREATE TABLE group_polls (
																    poll_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id              UUID NOT NULL,
																
																    category               VARCHAR(100) NOT NULL,
																    question               VARCHAR(300) NOT NULL,
																    poll_type              VARCHAR(50) NOT NULL,
																
																    end_date               DATE,
																
																    is_anonymous           BOOLEAN NOT NULL DEFAULT FALSE,
																    allow_multiple_votes   BOOLEAN NOT NULL DEFAULT FALSE,
																
																    status                 VARCHAR(30) NOT NULL DEFAULT 'OPEN',
																
																    created_by             UUID NOT NULL,
																    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at             TIMESTAMP,
																
																    CONSTRAINT fk_gp_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gp_created_by
																        FOREIGN KEY(created_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_gp_type
																        CHECK (poll_type IN ('SINGLE_CHOICE','MULTIPLE_CHOICE','YES_NO','RANKING')),
																
																    CONSTRAINT chk_gp_status
																        CHECK (status IN ('OPEN','CLOSED','CANCELLED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_polls_moment
																ON group_polls(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_polls_status
																ON group_polls(status);
-- >>>STMT<<<
CREATE INDEX idx_polls_end_date
																ON group_polls(end_date);
-- >>>STMT<<<
CREATE TABLE group_poll_options (
																    option_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    poll_id                UUID NOT NULL,
																
																    option_text            VARCHAR(250) NOT NULL,
																    sort_order             INTEGER NOT NULL,
																    is_active              BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gpo_poll
																        FOREIGN KEY(poll_id)
																        REFERENCES group_polls(poll_id),
																
																    CONSTRAINT chk_gpo_sort
																        CHECK (sort_order > 0)
																);
-- >>>STMT<<<
CREATE INDEX idx_poll_options_poll
																ON group_poll_options(poll_id);
-- >>>STMT<<<
CREATE TABLE group_poll_votes (
																    vote_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    poll_id                UUID NOT NULL,
																    option_id              UUID NOT NULL,
																    voter_member_id        UUID NOT NULL,
																
																    rank_order             INTEGER,
																    voted_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gpv_poll
																        FOREIGN KEY(poll_id)
																        REFERENCES group_polls(poll_id),
																
																    CONSTRAINT fk_gpv_option
																        FOREIGN KEY(option_id)
																        REFERENCES group_poll_options(option_id),
																
																    CONSTRAINT fk_gpv_voter
																        FOREIGN KEY(voter_member_id)
																        REFERENCES group_moment_members(member_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_poll_votes_poll
																ON group_poll_votes(poll_id);
-- >>>STMT<<<
CREATE INDEX idx_poll_votes_voter
																ON group_poll_votes(voter_member_id);
-- >>>STMT<<<
CREATE TABLE group_updates (
																    update_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id              UUID NOT NULL,
																
																    category               VARCHAR(100) NOT NULL,
																    title                  VARCHAR(200) NOT NULL,
																    description            TEXT NOT NULL,
																
																    visibility             VARCHAR(50) NOT NULL DEFAULT 'EVERYONE',
																    status                 VARCHAR(30) NOT NULL DEFAULT 'POSTED',
																
																    created_by             UUID NOT NULL,
																    created_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at             TIMESTAMP,
																
																    CONSTRAINT fk_gu_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gu_created_by
																        FOREIGN KEY(created_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_gu_visibility
																        CHECK (visibility IN ('EVERYONE','ORGANIZERS','SELECTED')),
																
																    CONSTRAINT chk_gu_status
																        CHECK (status IN ('POSTED','EDITED','ARCHIVED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_updates_moment
																ON group_updates(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_updates_category
																ON group_updates(category);
-- >>>STMT<<<
CREATE INDEX idx_updates_created
																ON group_updates(created_at);
-- >>>STMT<<<
CREATE TABLE shared_experience_details (
																    experience_detail_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    experience_profile        VARCHAR(100) NOT NULL,
																    location                  VARCHAR(250),
																
																    start_date                DATE,
																    end_date                  DATE,
																
																    expected_participants     INTEGER,
																
																    planning_style            VARCHAR(50) NOT NULL,
																    money_tracking_mode       VARCHAR(50) NOT NULL,
																
																    description               TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_sed_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_sed_dates
																        CHECK (
																            start_date IS NULL
																            OR end_date IS NULL
																            OR start_date <= end_date
																        ),
																
																    CONSTRAINT chk_sed_expected_participants
																        CHECK (
																            expected_participants IS NULL
																            OR expected_participants >= 1
																        ),
																
																    CONSTRAINT chk_sed_planning_style
																        CHECK (planning_style IN ('SIMPLE','STRUCTURED','FULLY_MANAGED')),
																
																    CONSTRAINT chk_sed_money_mode
																        CHECK (money_tracking_mode IN ('NO_MONEY','SHARED_EXPENSES','CONTRIBUTIONS_AND_EXPENSES'))
																);
-- >>>STMT<<<
CREATE INDEX idx_shared_experience_details_moment
																ON shared_experience_details(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_shared_experience_details_profile
																ON shared_experience_details(experience_profile);
-- >>>STMT<<<
CREATE TABLE shared_experience_planning_items (
																    item_id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    item_type                 VARCHAR(50) NOT NULL,
																    category                  VARCHAR(100) NOT NULL,
																
																    title                     VARCHAR(200) NOT NULL,
																    owner_member_id           UUID,
																
																    due_date                  DATE,
																
																    status                    VARCHAR(50) NOT NULL DEFAULT 'PENDING',
																
																    estimated_cost            DECIMAL(12,2),
																    actual_cost               DECIMAL(12,2),
																
																    provider_name             VARCHAR(200),
																    booking_reference         VARCHAR(200),
																
																    notes                     TEXT,
																
																    created_by                UUID NOT NULL,
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_sepi_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_sepi_owner
																        FOREIGN KEY(owner_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT fk_sepi_created_by
																        FOREIGN KEY(created_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_sepi_item_type
																        CHECK (item_type IN ('PLANNING_ITEM','BOOKING','VENDOR','TASK','ACTIVITY')),
																
																    CONSTRAINT chk_sepi_status
																        CHECK (status IN ('PENDING','IN_PROGRESS','CONFIRMED','COMPLETED','CANCELLED')),
																
																    CONSTRAINT chk_sepi_estimated_cost
																        CHECK (estimated_cost IS NULL OR estimated_cost >= 0),
																
																    CONSTRAINT chk_sepi_actual_cost
																        CHECK (actual_cost IS NULL OR actual_cost >= 0)
																);
-- >>>STMT<<<
CREATE INDEX idx_se_planning_items_moment
																ON shared_experience_planning_items(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_se_planning_items_type
																ON shared_experience_planning_items(item_type);
-- >>>STMT<<<
CREATE INDEX idx_se_planning_items_status
																ON shared_experience_planning_items(status);
-- >>>STMT<<<
CREATE INDEX idx_se_planning_items_due_date
																ON shared_experience_planning_items(due_date);
-- >>>STMT<<<
CREATE TABLE shared_experience_settlements (
																    settlement_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    payer_member_id           UUID NOT NULL,
																    receiver_member_id        UUID NOT NULL,
																
																    settlement_amount         DECIMAL(12,2) NOT NULL,
																    settlement_status         VARCHAR(30) NOT NULL DEFAULT 'OPEN',
																
																    settled_at                TIMESTAMP,
																
																    source_expense_ids_json   JSONB,
																
																    notes                     TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_ses_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_ses_payer
																        FOREIGN KEY(payer_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT fk_ses_receiver
																        FOREIGN KEY(receiver_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_ses_amount
																        CHECK (settlement_amount > 0),
																
																    CONSTRAINT chk_ses_status
																        CHECK (settlement_status IN ('OPEN','SETTLED','WAIVED')),
																
																    CONSTRAINT chk_ses_not_same_person
																        CHECK (payer_member_id <> receiver_member_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_se_settlements_moment
																ON shared_experience_settlements(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_se_settlements_payer
																ON shared_experience_settlements(payer_member_id);
-- >>>STMT<<<
CREATE INDEX idx_se_settlements_receiver
																ON shared_experience_settlements(receiver_member_id);
-- >>>STMT<<<
CREATE INDEX idx_se_settlements_status
																ON shared_experience_settlements(settlement_status);
-- >>>STMT<<<
CREATE TABLE shared_experience_memory_highlights (
																    highlight_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    highlight_type            VARCHAR(100) NOT NULL,
																
																    title                     VARCHAR(200) NOT NULL,
																    description               TEXT,
																
																    source_event_id           UUID,
																
																    importance_score          DECIMAL(5,2) NOT NULL DEFAULT 50,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_semh_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_semh_source_event
																        FOREIGN KEY(source_event_id)
																        REFERENCES group_quick_add_events(event_id),
																
																    CONSTRAINT chk_semh_importance
																        CHECK (importance_score >= 0 AND importance_score <= 100)
																);
-- >>>STMT<<<
CREATE INDEX idx_se_memory_highlights_moment
																ON shared_experience_memory_highlights(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_se_memory_highlights_type
																ON shared_experience_memory_highlights(highlight_type);
-- >>>STMT<<<
CREATE INDEX idx_se_memory_highlights_score
																ON shared_experience_memory_highlights(importance_score);
-- >>>STMT<<<
CREATE TABLE shared_purchase_details (
																    purchase_detail_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    purchase_type             VARCHAR(100) NOT NULL,
																    purchase_name             VARCHAR(200) NOT NULL,
																
																    target_amount             DECIMAL(12,2) NOT NULL,
																    target_date               DATE,
																
																    purchase_link             TEXT,
																    description               TEXT,
																
																    funding_style             VARCHAR(50) NOT NULL,
																    expected_contributors     INTEGER,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_spd_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_spd_target_amount
																        CHECK (target_amount > 0),
																
																    CONSTRAINT chk_spd_expected_contributors
																        CHECK (expected_contributors IS NULL OR expected_contributors >= 1),
																
																    CONSTRAINT chk_spd_funding_style
																        CHECK (funding_style IN ('OPEN','SUGGESTED','FIXED','ORGANIZER_MANAGED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_shared_purchase_details_moment
																ON shared_purchase_details(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_shared_purchase_details_type
																ON shared_purchase_details(purchase_type);
-- >>>STMT<<<
CREATE TABLE shared_purchase_contributors (
																    contributor_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																    member_id                 UUID NOT NULL,
																
																    contributor_type          VARCHAR(100) NOT NULL,
																    expected_amount           DECIMAL(12,2),
																
																    status                    VARCHAR(30) NOT NULL DEFAULT 'INVITED',
																
																    invited_at                TIMESTAMP,
																    notes                     TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_spc_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_spc_member
																        FOREIGN KEY(member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_spc_expected_amount
																        CHECK (expected_amount IS NULL OR expected_amount >= 0),
																
																    CONSTRAINT chk_spc_status
																        CHECK (status IN ('INVITED','ACTIVE','PAID','DROPPED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_purchase_contributors_moment
																ON shared_purchase_contributors(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_purchase_contributors_member
																ON shared_purchase_contributors(member_id);
-- >>>STMT<<<
CREATE INDEX idx_purchase_contributors_status
																ON shared_purchase_contributors(status);
-- >>>STMT<<<
CREATE TABLE shared_purchase_items (
																    item_id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    category                  VARCHAR(100) NOT NULL,
																    item_name                 VARCHAR(200) NOT NULL,
																
																    target_price              DECIMAL(12,2),
																    quantity                  INTEGER DEFAULT 1,
																
																    purchase_link             TEXT,
																    priority                  VARCHAR(30),
																    status                    VARCHAR(30) NOT NULL DEFAULT 'PROPOSED',
																
																    notes                     TEXT,
																
																    created_by                UUID NOT NULL,
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_spi_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_spi_created_by
																        FOREIGN KEY(created_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_spi_target_price
																        CHECK (target_price IS NULL OR target_price >= 0),
																
																    CONSTRAINT chk_spi_quantity
																        CHECK (quantity IS NULL OR quantity >= 1),
																
																    CONSTRAINT chk_spi_priority
																        CHECK (priority IS NULL OR priority IN ('HIGH','MEDIUM','LOW')),
																
																    CONSTRAINT chk_spi_status
																        CHECK (status IN ('PROPOSED','SHORTLISTED','SELECTED','PURCHASED','DROPPED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_purchase_items_moment
																ON shared_purchase_items(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_purchase_items_category
																ON shared_purchase_items(category);
-- >>>STMT<<<
CREATE INDEX idx_purchase_items_status
																ON shared_purchase_items(status);
-- >>>STMT<<<
CREATE TABLE shared_purchase_vendors (
																    vendor_id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    vendor_category           VARCHAR(100) NOT NULL,
																    vendor_name               VARCHAR(200) NOT NULL,
																
																    contact_person            VARCHAR(200),
																    phone                     VARCHAR(50),
																    email                     VARCHAR(200),
																
																    quoted_price              DECIMAL(12,2),
																    vendor_link               TEXT,
																
																    status                    VARCHAR(30) NOT NULL DEFAULT 'EVALUATING',
																    notes                     TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_spv_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_spv_quoted_price
																        CHECK (quoted_price IS NULL OR quoted_price >= 0),
																
																    CONSTRAINT chk_spv_status
																        CHECK (status IN ('EVALUATING','SHORTLISTED','CONFIRMED','REJECTED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_purchase_vendors_moment
																ON shared_purchase_vendors(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_purchase_vendors_category
																ON shared_purchase_vendors(vendor_category);
-- >>>STMT<<<
CREATE INDEX idx_purchase_vendors_status
																ON shared_purchase_vendors(status);
-- >>>STMT<<<
CREATE TABLE shared_purchase_ownership (
																    ownership_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    owner_member_id           UUID NOT NULL,
																    ownership_type            VARCHAR(100) NOT NULL,
																
																    ownership_percentage      DECIMAL(5,2),
																    usage_rights              TEXT,
																
																    status                    VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
																    notes                     TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_spo_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_spo_owner
																        FOREIGN KEY(owner_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_spo_percentage
																        CHECK (
																            ownership_percentage IS NULL
																            OR (ownership_percentage >= 0 AND ownership_percentage <= 100)
																        ),
																
																    CONSTRAINT chk_spo_status
																        CHECK (status IN ('DRAFT','FINALIZED','REVISED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_purchase_ownership_moment
																ON shared_purchase_ownership(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_purchase_ownership_owner
																ON shared_purchase_ownership(owner_member_id);
-- >>>STMT<<<
CREATE INDEX idx_purchase_ownership_status
																ON shared_purchase_ownership(status);
-- >>>STMT<<<
CREATE TABLE shared_purchase_delivery (
																    delivery_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    delivery_category         VARCHAR(100) NOT NULL,
																    delivery_date             DATE,
																
																    received_by_member_id     UUID,
																
																    status                    VARCHAR(30) NOT NULL DEFAULT 'PENDING',
																
																    proof_attachment_id       UUID,
																
																    notes                     TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_spdeli_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_spdeli_receiver
																        FOREIGN KEY(received_by_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT fk_spdeli_attachment
																        FOREIGN KEY(proof_attachment_id)
																        REFERENCES group_attachments(attachment_id),
																
																    CONSTRAINT chk_spdeli_status
																        CHECK (status IN ('PENDING','COMPLETED','DELAYED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_purchase_delivery_moment
																ON shared_purchase_delivery(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_purchase_delivery_status
																ON shared_purchase_delivery(status);
-- >>>STMT<<<
CREATE INDEX idx_purchase_delivery_date
																ON shared_purchase_delivery(delivery_date);
-- >>>STMT<<<
CREATE TABLE shared_living_details (
																    living_detail_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    living_type               VARCHAR(100) NOT NULL,
																    living_name               VARCHAR(200) NOT NULL,
																
																    location                  VARCHAR(250),
																    move_in_date              DATE,
																
																    monthly_budget            DECIMAL(12,2),
																    management_style          VARCHAR(50) NOT NULL,
																
																    expected_residents        INTEGER,
																    description               TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_sld_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_sld_budget
																        CHECK (monthly_budget IS NULL OR monthly_budget >= 0),
																
																    CONSTRAINT chk_sld_expected_residents
																        CHECK (expected_residents IS NULL OR expected_residents >= 1),
																
																    CONSTRAINT chk_sld_management_style
																        CHECK (management_style IN ('COLLABORATIVE','SHARED_RESPONSIBILITY','HOUSEHOLD_LEAD','FAMILY_MANAGED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_shared_living_details_moment
																ON shared_living_details(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_shared_living_details_type
																ON shared_living_details(living_type);
-- >>>STMT<<<
CREATE TABLE shared_living_residents (
																    resident_id                         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                           UUID NOT NULL,
																    member_id                           UUID NOT NULL,
																
																    resident_type                       VARCHAR(100) NOT NULL,
																
																    move_in_date                        DATE,
																    move_out_date                       DATE,
																
																    expected_monthly_contribution       DECIMAL(12,2),
																
																    status                              VARCHAR(30) NOT NULL DEFAULT 'INVITED',
																    notes                               TEXT,
																
																    created_at                          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                          TIMESTAMP,
																
																    CONSTRAINT fk_slr_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_slr_member
																        FOREIGN KEY(member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_slr_expected_contribution
																        CHECK (
																            expected_monthly_contribution IS NULL
																            OR expected_monthly_contribution >= 0
																        ),
																
																    CONSTRAINT chk_slr_move_dates
																        CHECK (
																            move_in_date IS NULL
																            OR move_out_date IS NULL
																            OR move_out_date >= move_in_date
																        ),
																
																    CONSTRAINT chk_slr_status
																        CHECK (status IN ('INVITED','ACTIVE','PENDING','MOVED_OUT'))
																);
-- >>>STMT<<<
CREATE INDEX idx_living_residents_moment
																ON shared_living_residents(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_living_residents_member
																ON shared_living_residents(member_id);
-- >>>STMT<<<
CREATE INDEX idx_living_residents_status
																ON shared_living_residents(status);
-- >>>STMT<<<
CREATE TABLE shared_living_tasks (
																    task_id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    category                  VARCHAR(100) NOT NULL,
																    task_name                 VARCHAR(200) NOT NULL,
																
																    assigned_to_member_id     UUID,
																
																    due_date                  DATE,
																
																    frequency                 VARCHAR(50) NOT NULL DEFAULT 'ONE_TIME',
																    priority                  VARCHAR(30),
																
																    status                    VARCHAR(30) NOT NULL DEFAULT 'TO_DO',
																
																    completed_at              TIMESTAMP,
																    notes                     TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_slt_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_slt_assignee
																        FOREIGN KEY(assigned_to_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_slt_frequency
																        CHECK (frequency IN ('ONE_TIME','DAILY','WEEKLY','MONTHLY','CUSTOM')),
																
																    CONSTRAINT chk_slt_priority
																        CHECK (priority IS NULL OR priority IN ('LOW','MEDIUM','HIGH')),
																
																    CONSTRAINT chk_slt_status
																        CHECK (status IN ('TO_DO','IN_PROGRESS','COMPLETED','OVERDUE'))
																);
-- >>>STMT<<<
CREATE INDEX idx_living_tasks_moment
																ON shared_living_tasks(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_living_tasks_assignee
																ON shared_living_tasks(assigned_to_member_id);
-- >>>STMT<<<
CREATE INDEX idx_living_tasks_status
																ON shared_living_tasks(status);
-- >>>STMT<<<
CREATE INDEX idx_living_tasks_due_date
																ON shared_living_tasks(due_date);
-- >>>STMT<<<
CREATE TABLE shared_living_assets (
																    asset_id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    category                  VARCHAR(100) NOT NULL,
																    asset_name                VARCHAR(200) NOT NULL,
																
																    owner_member_id           UUID,
																
																    is_shared_asset           BOOLEAN NOT NULL DEFAULT TRUE,
																
																    purchase_date             DATE,
																    estimated_value           DECIMAL(12,2),
																
																    location_in_home          VARCHAR(200),
																
																    status                    VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
																    notes                     TEXT,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_sla_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_sla_owner
																        FOREIGN KEY(owner_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_sla_value
																        CHECK (estimated_value IS NULL OR estimated_value >= 0),
																
																    CONSTRAINT chk_sla_status
																        CHECK (status IN ('ACTIVE','RETIRED','REMOVED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_living_assets_moment
																ON shared_living_assets(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_living_assets_owner
																ON shared_living_assets(owner_member_id);
-- >>>STMT<<<
CREATE INDEX idx_living_assets_status
																ON shared_living_assets(status);
-- >>>STMT<<<
CREATE TABLE shared_living_rules (
																    rule_id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                 UUID NOT NULL,
																
																    category                  VARCHAR(100) NOT NULL,
																
																    rule_title                VARCHAR(200) NOT NULL,
																    rule_description          TEXT NOT NULL,
																
																    applies_to                VARCHAR(50) NOT NULL DEFAULT 'EVERYONE',
																
																    effective_date            DATE NOT NULL,
																    review_date               DATE,
																
																    status                    VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
																
																    created_by                UUID NOT NULL,
																
																    created_at                TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                TIMESTAMP,
																
																    CONSTRAINT fk_slrules_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_slrules_created_by
																        FOREIGN KEY(created_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_slrules_applies_to
																        CHECK (applies_to IN ('EVERYONE','SELECTED_RESIDENTS')),
																
																    CONSTRAINT chk_slrules_review_date
																        CHECK (
																            review_date IS NULL
																            OR review_date >= effective_date
																        ),
																
																    CONSTRAINT chk_slrules_status
																        CHECK (status IN ('ACTIVE','ARCHIVED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_living_rules_moment
																ON shared_living_rules(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_living_rules_status
																ON shared_living_rules(status);
-- >>>STMT<<<
CREATE INDEX idx_living_rules_effective
																ON shared_living_rules(effective_date);
-- >>>STMT<<<
CREATE TABLE shared_living_maintenance (
																    maintenance_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                  UUID NOT NULL,
																
																    category                   VARCHAR(100) NOT NULL,
																
																    issue_title                VARCHAR(200) NOT NULL,
																    description                TEXT,
																
																    reported_by_member_id      UUID NOT NULL,
																    assigned_to_member_id      UUID,
																
																    priority                   VARCHAR(30) NOT NULL DEFAULT 'MEDIUM',
																    status                     VARCHAR(30) NOT NULL DEFAULT 'REPORTED',
																
																    target_resolution_date     DATE,
																    fixed_at                   TIMESTAMP,
																
																    estimated_cost             DECIMAL(12,2),
																
																    notes                      TEXT,
																
																    created_at                 TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                 TIMESTAMP,
																
																    CONSTRAINT fk_slm_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_slm_reported_by
																        FOREIGN KEY(reported_by_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT fk_slm_assigned_to
																        FOREIGN KEY(assigned_to_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_slm_priority
																        CHECK (priority IN ('LOW','MEDIUM','HIGH','URGENT')),
																
																    CONSTRAINT chk_slm_status
																        CHECK (status IN ('REPORTED','IN_PROGRESS','FIXED')),
																
																    CONSTRAINT chk_slm_estimated_cost
																        CHECK (estimated_cost IS NULL OR estimated_cost >= 0)
																);
-- >>>STMT<<<
CREATE INDEX idx_living_maintenance_moment
																ON shared_living_maintenance(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_living_maintenance_status
																ON shared_living_maintenance(status);
-- >>>STMT<<<
CREATE INDEX idx_living_maintenance_priority
																ON shared_living_maintenance(priority);
-- >>>STMT<<<
CREATE INDEX idx_living_maintenance_target
																ON shared_living_maintenance(target_resolution_date);
-- >>>STMT<<<
CREATE TABLE shared_living_resident_dynamics (
																    dynamics_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                  UUID NOT NULL,
																    resident_member_id         UUID NOT NULL,
																
																    activity_score             DECIMAL(5,2) NOT NULL DEFAULT 0,
																    helpfulness_score          DECIMAL(5,2),
																    contribution_score         DECIMAL(5,2),
																
																    summary_label              VARCHAR(150),
																
																    period_start               DATE NOT NULL,
																    period_end                 DATE NOT NULL,
																
																    created_at                 TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                 TIMESTAMP,
																
																    CONSTRAINT fk_slrd_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_slrd_resident
																        FOREIGN KEY(resident_member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_slrd_activity_score
																        CHECK (activity_score >= 0 AND activity_score <= 100),
																
																    CONSTRAINT chk_slrd_helpfulness_score
																        CHECK (
																            helpfulness_score IS NULL
																            OR (helpfulness_score >= 0 AND helpfulness_score <= 100)
																        ),
																
																    CONSTRAINT chk_slrd_contribution_score
																        CHECK (
																            contribution_score IS NULL
																            OR (contribution_score >= 0 AND contribution_score <= 100)
																        ),
																
																    CONSTRAINT chk_slrd_period
																        CHECK (period_end >= period_start)
																);
-- >>>STMT<<<
CREATE INDEX idx_living_resident_dynamics_moment
																ON shared_living_resident_dynamics(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_living_resident_dynamics_resident
																ON shared_living_resident_dynamics(resident_member_id);
-- >>>STMT<<<
CREATE INDEX idx_living_resident_dynamics_period
																ON shared_living_resident_dynamics(period_start, period_end);
-- >>>STMT<<<
CREATE TABLE shared_living_home_personality (
																    personality_id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id                  UUID NOT NULL,
																
																    traits_json                JSONB NOT NULL,
																
																    primary_trait              VARCHAR(100) NOT NULL,
																    description                TEXT,
																
																    confidence_score           DECIMAL(5,2) NOT NULL DEFAULT 0,
																
																    snapshot_date              DATE NOT NULL,
																
																    created_at                 TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at                 TIMESTAMP,
																
																    CONSTRAINT fk_slhp_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_slhp_confidence
																        CHECK (confidence_score >= 0 AND confidence_score <= 100)
																);
-- >>>STMT<<<
CREATE INDEX idx_living_home_personality_moment
																ON shared_living_home_personality(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_living_home_personality_snapshot
																ON shared_living_home_personality(snapshot_date);
-- >>>STMT<<<
CREATE TABLE group_pulse_snapshots (
																    snapshot_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    snapshot_date            DATE NOT NULL,
																
																    completion_percentage    DECIMAL(5,2) NOT NULL DEFAULT 0,
																    participation_percentage DECIMAL(5,2) NOT NULL DEFAULT 0,
																    funding_percentage       DECIMAL(5,2) NOT NULL DEFAULT 0,
																
																    active_members           INTEGER NOT NULL DEFAULT 0,
																    active_tasks             INTEGER NOT NULL DEFAULT 0,
																    open_items               INTEGER NOT NULL DEFAULT 0,
																
																    pulse_score              DECIMAL(5,2) NOT NULL DEFAULT 0,
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gps_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_gps_pulse_score
																        CHECK (pulse_score >= 0 AND pulse_score <= 100)
																);
-- >>>STMT<<<
CREATE INDEX idx_gps_moment
																ON group_pulse_snapshots(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_gps_date
																ON group_pulse_snapshots(snapshot_date);
-- >>>STMT<<<
CREATE TABLE group_health_snapshots (
																    health_snapshot_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    snapshot_date            DATE NOT NULL,
																
																    health_score             DECIMAL(5,2) NOT NULL,
																
																    health_status            VARCHAR(30) NOT NULL,
																
																    people_score             DECIMAL(5,2),
																    money_score              DECIMAL(5,2),
																    activity_score           DECIMAL(5,2),
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_ghs_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_ghs_status
																        CHECK (health_status IN ('EXCELLENT','GOOD','STABLE','WARNING','CRITICAL'))
																);
-- >>>STMT<<<
CREATE INDEX idx_ghs_moment
																ON group_health_snapshots(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_ghs_date
																ON group_health_snapshots(snapshot_date);
-- >>>STMT<<<
CREATE TABLE group_signals (
																    signal_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    signal_type              VARCHAR(100) NOT NULL,
																    signal_category          VARCHAR(100) NOT NULL,
																
																    signal_title             VARCHAR(250) NOT NULL,
																    signal_description       TEXT,
																
																    priority                 VARCHAR(30) NOT NULL,
																
																    signal_score             DECIMAL(5,2),
																
																    is_active                BOOLEAN NOT NULL DEFAULT TRUE,
																
																    generated_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    expires_at               TIMESTAMP,
																
																    CONSTRAINT fk_gs_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_gs_priority
																        CHECK (priority IN ('LOW','MEDIUM','HIGH','CRITICAL'))
																);
-- >>>STMT<<<
CREATE INDEX idx_gs_moment
																ON group_signals(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_gs_active
																ON group_signals(is_active);
-- >>>STMT<<<
CREATE INDEX idx_gs_category
																ON group_signals(signal_category);
-- >>>STMT<<<
CREATE TABLE group_recommendations (
																    recommendation_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    recommendation_type      VARCHAR(100) NOT NULL,
																    recommendation_category  VARCHAR(100) NOT NULL,
																
																    title                    VARCHAR(250) NOT NULL,
																    description              TEXT,
																
																    priority                 VARCHAR(30) NOT NULL,
																
																    recommendation_score     DECIMAL(5,2),
																
																    status                   VARCHAR(30) NOT NULL DEFAULT 'OPEN',
																
																    generated_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    actioned_at              TIMESTAMP,
																
																    CONSTRAINT fk_gr_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_gr_priority
																        CHECK (priority IN ('LOW','MEDIUM','HIGH','CRITICAL')),
																
																    CONSTRAINT chk_gr_status
																        CHECK (status IN ('OPEN','ACCEPTED','DISMISSED','COMPLETED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_gr_moment
																ON group_recommendations(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_gr_status
																ON group_recommendations(status);
-- >>>STMT<<<
CREATE INDEX idx_gr_priority
																ON group_recommendations(priority);
-- >>>STMT<<<
CREATE TABLE group_memory_entries (
																    memory_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    memory_type              VARCHAR(100) NOT NULL,
																    category                 VARCHAR(100) NOT NULL,
																
																    title                    VARCHAR(250) NOT NULL,
																    description              TEXT,
																
																    source_event_id          UUID,
																
																    created_by               UUID,
																
																    memory_date              DATE NOT NULL,
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gme_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gme_event
																        FOREIGN KEY(source_event_id)
																        REFERENCES group_quick_add_events(event_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_gme_moment
																ON group_memory_entries(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_gme_memory_date
																ON group_memory_entries(memory_date);
-- >>>STMT<<<
CREATE INDEX idx_gme_category
																ON group_memory_entries(category);
-- >>>STMT<<<
CREATE TABLE group_memory_patterns (
																    pattern_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    moment_type              VARCHAR(50) NOT NULL,
																
																    pattern_type             VARCHAR(100) NOT NULL,
																    pattern_category         VARCHAR(100) NOT NULL,
																
																    insight_title            VARCHAR(250) NOT NULL,
																    insight_text             TEXT,
																
																    confidence_score         DECIMAL(5,2) NOT NULL,
																
																    supporting_event_ids_json JSONB,
																
																    status                   VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at               TIMESTAMP,
																
																    CONSTRAINT fk_gmp_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_gmp_status
																        CHECK (status IN ('ACTIVE','SUPERSEDED','DISMISSED'))
																);
-- >>>STMT<<<
CREATE INDEX idx_gmp_moment
																ON group_memory_patterns(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_gmp_type
																ON group_memory_patterns(pattern_type);
-- >>>STMT<<<
CREATE INDEX idx_gmp_status
																ON group_memory_patterns(status);
-- >>>STMT<<<
CREATE TABLE group_ai_insights (
																    insight_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    insight_type             VARCHAR(100) NOT NULL,
																
																    insight_title            VARCHAR(250) NOT NULL,
																    insight_text             TEXT NOT NULL,
																
																    confidence_score         DECIMAL(5,2),
																
																    source_snapshot_date     DATE,
																
																    generated_at             TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gai_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_gai_moment
																ON group_ai_insights(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_gai_type
																ON group_ai_insights(insight_type);
-- >>>STMT<<<
CREATE TABLE group_journey_metrics (
																    metric_id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id                UUID NOT NULL,
																
																    metric_date              DATE NOT NULL,
																
																    stage_name               VARCHAR(100) NOT NULL,
																
																    days_in_stage            INTEGER,
																
																    completion_percentage    DECIMAL(5,2),
																
																    milestone_count          INTEGER DEFAULT 0,
																
																    created_at               TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gjm_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id)
																);
-- >>>STMT<<<
CREATE INDEX idx_gjm_moment
																ON group_journey_metrics(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_gjm_date
																ON group_journey_metrics(metric_date);
-- >>>STMT<<<
CREATE TABLE shared_purchase_ownership_insights
																(
																    insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																
																    insight_type VARCHAR(100),
																
																    title VARCHAR(250),
																
																    description TEXT,
																
																    confidence_score DECIMAL(5,2),
																
																    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
ALTER TABLE group_moments
																ADD COLUMN IF NOT EXISTS experience_subtype VARCHAR(100),
																ADD COLUMN IF NOT EXISTS planning_mode VARCHAR(30) DEFAULT 'PLAN_NOW',
																ADD COLUMN IF NOT EXISTS activation_status VARCHAR(30) DEFAULT 'ACTIVE',
																ADD COLUMN IF NOT EXISTS planned_activation_date DATE,
																ADD COLUMN IF NOT EXISTS group_life_space_id UUID,
																ADD COLUMN IF NOT EXISTS is_life_included BOOLEAN NOT NULL DEFAULT TRUE;
-- >>>STMT<<<
ALTER TABLE group_moments
																DROP CONSTRAINT IF EXISTS chk_group_moments_planning_mode;
-- >>>STMT<<<
ALTER TABLE group_moments
																ADD CONSTRAINT chk_group_moments_planning_mode
																CHECK (
																    planning_mode IS NULL
																    OR planning_mode IN ('PLAN_NOW','FUTURE_PLAN')
																);
-- >>>STMT<<<
ALTER TABLE group_moments
																DROP CONSTRAINT IF EXISTS chk_group_moments_activation_status;
-- >>>STMT<<<
ALTER TABLE group_moments
																ADD CONSTRAINT chk_group_moments_activation_status
																CHECK (
																    activation_status IS NULL
																    OR activation_status IN ('PLANNING','ACTIVE','COMPLETED','CANCELLED')
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_group_moments_experience_subtype
																ON group_moments(experience_subtype);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_group_moments_planning_mode
																ON group_moments(planning_mode);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_group_moments_activation_status
																ON group_moments(activation_status);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_group_moments_life_space
																ON group_moments(group_life_space_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_group_moments_life_included
																ON group_moments(is_life_included);
-- >>>STMT<<<
ALTER TABLE shared_experience_details
																ADD COLUMN IF NOT EXISTS budget_enabled BOOLEAN NOT NULL DEFAULT TRUE,
																ADD COLUMN IF NOT EXISTS default_budget_plan_id UUID;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_sed_budget_enabled
																ON shared_experience_details(budget_enabled);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_sed_default_budget_plan
																ON shared_experience_details(default_budget_plan_id);
-- >>>STMT<<<
ALTER TABLE shared_experience_planning_items
																ADD COLUMN IF NOT EXISTS budget_plan_id UUID,
																ADD COLUMN IF NOT EXISTS budget_category_id UUID;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_sepi_budget_plan
																ON shared_experience_planning_items(budget_plan_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_sepi_budget_category
																ON shared_experience_planning_items(budget_category_id);
-- >>>STMT<<<
ALTER TABLE group_quick_add_config
																ADD COLUMN IF NOT EXISTS quick_add_category VARCHAR(100),
																ADD COLUMN IF NOT EXISTS moment_type_support VARCHAR(50);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gqac_quick_add_category
																ON group_quick_add_config(quick_add_category);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gqac_moment_type_support
																ON group_quick_add_config(moment_type_support);
-- >>>STMT<<<
ALTER TABLE group_field_value_config
																ADD COLUMN IF NOT EXISTS value_group VARCHAR(100),
																ADD COLUMN IF NOT EXISTS value_subgroup VARCHAR(100);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gfvc_value_group
																ON group_field_value_config(value_group);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gfvc_value_subgroup
																ON group_field_value_config(value_subgroup);
-- >>>STMT<<<
ALTER TABLE group_pulse_snapshots
																ADD COLUMN IF NOT EXISTS hero_snapshot_json JSONB,
																ADD COLUMN IF NOT EXISTS health_driver_json JSONB,
																ADD COLUMN IF NOT EXISTS progress_context_json JSONB,
																ADD COLUMN IF NOT EXISTS budget_snapshot_json JSONB,
																ADD COLUMN IF NOT EXISTS participation_json JSONB,
																ADD COLUMN IF NOT EXISTS timeline_preview_json JSONB,
																ADD COLUMN IF NOT EXISTS insights_json JSONB;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gps_hero_snapshot_json
																ON group_pulse_snapshots USING GIN(hero_snapshot_json);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gps_health_driver_json
																ON group_pulse_snapshots USING GIN(health_driver_json);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gps_budget_snapshot_json
																ON group_pulse_snapshots USING GIN(budget_snapshot_json);
-- >>>STMT<<<
ALTER TABLE group_health_snapshots
																ADD COLUMN IF NOT EXISTS health_delta NUMERIC(6,2),
																ADD COLUMN IF NOT EXISTS health_delta_period VARCHAR(30),
																ADD COLUMN IF NOT EXISTS health_driver_breakdown_json JSONB,
																ADD COLUMN IF NOT EXISTS budget_health_score NUMERIC(5,2),
																ADD COLUMN IF NOT EXISTS dimension_breakdown_json JSONB;
-- >>>STMT<<<
ALTER TABLE group_health_snapshots
																DROP CONSTRAINT IF EXISTS chk_ghs_budget_health_score;
-- >>>STMT<<<
ALTER TABLE group_health_snapshots
																ADD CONSTRAINT chk_ghs_budget_health_score
																CHECK (
																    budget_health_score IS NULL
																    OR (budget_health_score >= 0 AND budget_health_score <= 100)
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_ghs_health_driver_json
																ON group_health_snapshots USING GIN(health_driver_breakdown_json);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_ghs_dimension_breakdown_json
																ON group_health_snapshots USING GIN(dimension_breakdown_json);
-- >>>STMT<<<
ALTER TABLE group_signals
																ADD COLUMN IF NOT EXISTS severity VARCHAR(30),
																ADD COLUMN IF NOT EXISTS signal_status VARCHAR(30) DEFAULT 'OPEN',
																ADD COLUMN IF NOT EXISTS display_order INTEGER,
																ADD COLUMN IF NOT EXISTS action_ref UUID,
																ADD COLUMN IF NOT EXISTS source_widget VARCHAR(100),
																ADD COLUMN IF NOT EXISTS related_budget_plan_id UUID;
-- >>>STMT<<<
ALTER TABLE group_signals
																DROP CONSTRAINT IF EXISTS chk_group_signals_severity;
-- >>>STMT<<<
ALTER TABLE group_signals
																ADD CONSTRAINT chk_group_signals_severity
																CHECK (
																    severity IS NULL
																    OR severity IN ('INFO','WARN','CRITICAL')
																);
-- >>>STMT<<<
ALTER TABLE group_signals
																DROP CONSTRAINT IF EXISTS chk_group_signals_status;
-- >>>STMT<<<
ALTER TABLE group_signals
																ADD CONSTRAINT chk_group_signals_status
																CHECK (
																    signal_status IS NULL
																    OR signal_status IN ('OPEN','CLOSED','DISMISSED')
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gs_severity
																ON group_signals(severity);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gs_signal_status
																ON group_signals(signal_status);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gs_related_budget_plan
																ON group_signals(related_budget_plan_id);
-- >>>STMT<<<
ALTER TABLE group_recommendations
																ADD COLUMN IF NOT EXISTS expected_impact_json JSONB,
																ADD COLUMN IF NOT EXISTS impact_score NUMERIC(5,2),
																ADD COLUMN IF NOT EXISTS confidence_level VARCHAR(30),
																ADD COLUMN IF NOT EXISTS action_deeplink TEXT,
																ADD COLUMN IF NOT EXISTS related_life_space_id UUID;
-- >>>STMT<<<
ALTER TABLE group_recommendations
																DROP CONSTRAINT IF EXISTS chk_gr_impact_score;
-- >>>STMT<<<
ALTER TABLE group_recommendations
																ADD CONSTRAINT chk_gr_impact_score
																CHECK (
																    impact_score IS NULL
																    OR (impact_score >= 0 AND impact_score <= 100)
																);
-- >>>STMT<<<
ALTER TABLE group_recommendations
																DROP CONSTRAINT IF EXISTS chk_gr_confidence_level;
-- >>>STMT<<<
ALTER TABLE group_recommendations
																ADD CONSTRAINT chk_gr_confidence_level
																CHECK (
																    confidence_level IS NULL
																    OR confidence_level IN ('LOW','MEDIUM','HIGH')
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gr_expected_impact_json
																ON group_recommendations USING GIN(expected_impact_json);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gr_impact_score
																ON group_recommendations(impact_score);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gr_life_space
																ON group_recommendations(related_life_space_id);
-- >>>STMT<<<
ALTER TABLE group_live_feed
																ADD COLUMN IF NOT EXISTS category_chip VARCHAR(100),
																ADD COLUMN IF NOT EXISTS can_delete BOOLEAN NOT NULL DEFAULT TRUE,
																ADD COLUMN IF NOT EXISTS timeline_display_json JSONB,
																ADD COLUMN IF NOT EXISTS source_widget VARCHAR(100);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_glf_category_chip
																ON group_live_feed(category_chip);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_glf_timeline_display_json
																ON group_live_feed USING GIN(timeline_display_json);
-- >>>STMT<<<
ALTER TABLE group_memory_entries
																ADD COLUMN IF NOT EXISTS memory_category VARCHAR(100),
																ADD COLUMN IF NOT EXISTS media_count INTEGER DEFAULT 0,
																ADD COLUMN IF NOT EXISTS visibility VARCHAR(50) DEFAULT 'EVERYONE',
																ADD COLUMN IF NOT EXISTS highlight_score NUMERIC(5,2),
																ADD COLUMN IF NOT EXISTS is_gallery_item BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS budget_plan_id UUID;
-- >>>STMT<<<
ALTER TABLE group_memory_entries
																DROP CONSTRAINT IF EXISTS chk_gme_visibility;
-- >>>STMT<<<
ALTER TABLE group_memory_entries
																ADD CONSTRAINT chk_gme_visibility
																CHECK (
																    visibility IS NULL
																    OR visibility IN ('EVERYONE','ORGANIZERS','SELECTED')
																);
-- >>>STMT<<<
ALTER TABLE group_memory_entries
																DROP CONSTRAINT IF EXISTS chk_gme_highlight_score;
-- >>>STMT<<<
ALTER TABLE group_memory_entries
																ADD CONSTRAINT chk_gme_highlight_score
																CHECK (
																    highlight_score IS NULL
																    OR (highlight_score >= 0 AND highlight_score <= 100)
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gme_memory_category
																ON group_memory_entries(memory_category);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gme_highlight_score
																ON group_memory_entries(highlight_score);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gme_gallery_item
																ON group_memory_entries(is_gallery_item);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gme_budget_plan
																ON group_memory_entries(budget_plan_id);
-- >>>STMT<<<
ALTER TABLE group_memory_patterns
																ADD COLUMN IF NOT EXISTS lesson_text TEXT,
																ADD COLUMN IF NOT EXISTS identity_label VARCHAR(150),
																ADD COLUMN IF NOT EXISTS pattern_strength NUMERIC(5,2),
																ADD COLUMN IF NOT EXISTS trend_direction VARCHAR(30),
																ADD COLUMN IF NOT EXISTS supporting_metrics_json JSONB;
-- >>>STMT<<<
ALTER TABLE group_memory_patterns
																DROP CONSTRAINT IF EXISTS chk_gmp_pattern_strength;
-- >>>STMT<<<
ALTER TABLE group_memory_patterns
																ADD CONSTRAINT chk_gmp_pattern_strength
																CHECK (
																    pattern_strength IS NULL
																    OR (pattern_strength >= 0 AND pattern_strength <= 100)
																);
-- >>>STMT<<<
ALTER TABLE group_memory_patterns
																DROP CONSTRAINT IF EXISTS chk_gmp_trend_direction;
-- >>>STMT<<<
ALTER TABLE group_memory_patterns
																ADD CONSTRAINT chk_gmp_trend_direction
																CHECK (
																    trend_direction IS NULL
																    OR trend_direction IN ('UP','DOWN','STABLE','MIXED')
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gmp_identity_label
																ON group_memory_patterns(identity_label);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gmp_supporting_metrics_json
																ON group_memory_patterns USING GIN(supporting_metrics_json);
-- >>>STMT<<<
ALTER TABLE group_attachments
																ADD COLUMN IF NOT EXISTS attachment_context VARCHAR(100),
																ADD COLUMN IF NOT EXISTS thumbnail_url TEXT,
																ADD COLUMN IF NOT EXISTS is_gallery_item BOOLEAN NOT NULL DEFAULT FALSE,
																ADD COLUMN IF NOT EXISTS gallery_group VARCHAR(100);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_ga_attachment_context
																ON group_attachments(attachment_context);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_ga_gallery_item
																ON group_attachments(is_gallery_item);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_ga_gallery_group
																ON group_attachments(gallery_group);
-- >>>STMT<<<
ALTER TABLE group_change_history
																ADD COLUMN IF NOT EXISTS change_category VARCHAR(100),
																ADD COLUMN IF NOT EXISTS source_widget VARCHAR(100),
																ADD COLUMN IF NOT EXISTS rollback_supported BOOLEAN NOT NULL DEFAULT FALSE;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gch_change_category
																ON group_change_history(change_category);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gch_source_widget
																ON group_change_history(source_widget);
-- >>>STMT<<<
ALTER TABLE group_expenses
																ADD COLUMN IF NOT EXISTS budget_plan_id UUID,
																ADD COLUMN IF NOT EXISTS budget_category_id UUID,
																ADD COLUMN IF NOT EXISTS budget_variance_amount NUMERIC(14,2);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_ge_budget_plan
																ON group_expenses(budget_plan_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_ge_budget_category
																ON group_expenses(budget_category_id);
-- >>>STMT<<<
ALTER TABLE group_contributions
																ADD COLUMN IF NOT EXISTS budget_plan_id UUID,
																ADD COLUMN IF NOT EXISTS budget_split_id UUID,
																ADD COLUMN IF NOT EXISTS target_contribution_amount NUMERIC(14,2);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gc_budget_plan
																ON group_contributions(budget_plan_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gc_budget_split
																ON group_contributions(budget_split_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS budget_master_categories (
																    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    category_code VARCHAR(100) NOT NULL UNIQUE,
																    category_name VARCHAR(200) NOT NULL,
																    icon_name VARCHAR(100),
																    display_order INTEGER NOT NULL,
																    is_active BOOLEAN NOT NULL DEFAULT TRUE,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS experience_budget_templates (
																    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    experience_subtype VARCHAR(100) NOT NULL,
																    category_id UUID NOT NULL,
																    suggested_percentage NUMERIC(5,2) NOT NULL,
																    display_order INTEGER NOT NULL,
																    is_default BOOLEAN NOT NULL DEFAULT TRUE,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_ebt_category
																        FOREIGN KEY(category_id)
																        REFERENCES budget_master_categories(category_id),
																
																    CONSTRAINT chk_ebt_pct
																        CHECK (suggested_percentage >= 0 AND suggested_percentage <= 100)
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS shared_experience_budget_plans (
																    budget_plan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL,
																
																    planned_total_budget NUMERIC(14,2) NOT NULL,
																    final_total_budget NUMERIC(14,2) NOT NULL DEFAULT 0,
																
																    participant_count INTEGER NOT NULL DEFAULT 1,
																    split_method VARCHAR(50) NOT NULL DEFAULT 'EQUAL_SPLIT',
																
																    funding_readiness_pct NUMERIC(5,2) DEFAULT 0,
																
																    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
																
																    created_by UUID NOT NULL,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_sebp_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_sebp_budget
																        CHECK (planned_total_budget > 0 AND final_total_budget >= 0),
																
																    CONSTRAINT chk_sebp_participants
																        CHECK (participant_count >= 1),
																
																    CONSTRAINT chk_sebp_split_method
																        CHECK (split_method IN (
																            'EQUAL_SPLIT',
																            'CUSTOM_SPLIT',
																            'ORGANIZER_PAYS',
																            'SPONSOR_SUPPORTED',
																            'CONTRIBUTION_BASED'
																        )),
																
																    CONSTRAINT chk_sebp_readiness
																        CHECK (funding_readiness_pct >= 0 AND funding_readiness_pct <= 100),
																
																    CONSTRAINT chk_sebp_status
																        CHECK (status IN ('DRAFT','ACTIVE','LOCKED','COMPLETED','CANCELLED'))
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS shared_experience_budget_allocations (
																    allocation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    budget_plan_id UUID NOT NULL,
																    category_id UUID NOT NULL,
																
																    recommended_percentage NUMERIC(5,2),
																    recommended_amount NUMERIC(14,2),
																
																    final_percentage NUMERIC(5,2),
																    final_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
																
																    actual_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
																    variance_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
																
																    notes TEXT,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_seba_plan
																        FOREIGN KEY(budget_plan_id)
																        REFERENCES shared_experience_budget_plans(budget_plan_id),
																
																    CONSTRAINT fk_seba_category
																        FOREIGN KEY(category_id)
																        REFERENCES budget_master_categories(category_id),
																
																    CONSTRAINT chk_seba_pct
																        CHECK (
																            (recommended_percentage IS NULL OR recommended_percentage BETWEEN 0 AND 100)
																            AND
																            (final_percentage IS NULL OR final_percentage BETWEEN 0 AND 100)
																        ),
																
																    CONSTRAINT chk_seba_amounts
																        CHECK (
																            COALESCE(recommended_amount,0) >= 0
																            AND final_amount >= 0
																            AND actual_amount >= 0
																        )
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS shared_experience_budget_splits (
																    split_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    budget_plan_id UUID NOT NULL,
																    member_id UUID NOT NULL,
																
																    planned_share_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
																    committed_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
																    paid_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
																    pending_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
																
																    split_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_sebs_plan
																        FOREIGN KEY(budget_plan_id)
																        REFERENCES shared_experience_budget_plans(budget_plan_id),
																
																    CONSTRAINT fk_sebs_member
																        FOREIGN KEY(member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_sebs_amounts
																        CHECK (
																            planned_share_amount >= 0
																            AND committed_amount >= 0
																            AND paid_amount >= 0
																            AND pending_amount >= 0
																        ),
																
																    CONSTRAINT chk_sebs_status
																        CHECK (split_status IN ('PENDING','COMMITTED','PAID','OVERDUE','WAIVED'))
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS shared_goal_details (
																    goal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL,
																
																    goal_type VARCHAR(100) NOT NULL,
																    target_amount NUMERIC(14,2),
																    target_date DATE,
																    goal_owner_id UUID,
																
																    goal_status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
																    progress_pct NUMERIC(5,2) NOT NULL DEFAULT 0,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_sgd_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_sgd_owner
																        FOREIGN KEY(goal_owner_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_sgd_amount
																        CHECK (target_amount IS NULL OR target_amount >= 0),
																
																    CONSTRAINT chk_sgd_progress
																        CHECK (progress_pct >= 0 AND progress_pct <= 100),
																
																    CONSTRAINT chk_sgd_status
																        CHECK (goal_status IN ('DRAFT','ACTIVE','ACHIEVED','PAUSED','CANCELLED'))
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS community_coordination_details (
																    community_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL,
																
																    community_type VARCHAR(100) NOT NULL,
																    member_base_count INTEGER,
																    coordination_mode VARCHAR(50),
																    primary_owner_id UUID,
																
																    community_status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_ccd_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_ccd_owner
																        FOREIGN KEY(primary_owner_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_ccd_member_count
																        CHECK (member_base_count IS NULL OR member_base_count >= 0),
																
																    CONSTRAINT chk_ccd_mode
																        CHECK (
																            coordination_mode IS NULL
																            OR coordination_mode IN ('VOTING','ADMIN_APPROVAL','CONSENSUS','MIXED')
																        ),
																
																    CONSTRAINT chk_ccd_status
																        CHECK (community_status IN ('DRAFT','ACTIVE','COORDINATING','CLOSED'))
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_moment_work_items (
																    work_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL,
																
																    work_item_type VARCHAR(100) NOT NULL,
																    category VARCHAR(100),
																
																    title VARCHAR(250) NOT NULL,
																    description TEXT,
																
																    owner_id UUID,
																    status VARCHAR(40) NOT NULL DEFAULT 'OPEN',
																    priority VARCHAR(30),
																
																    due_date DATE,
																    event_date TIMESTAMP,
																    progress_pct NUMERIC(5,2),
																
																    source_quick_add VARCHAR(100) NOT NULL,
																    is_milestone BOOLEAN NOT NULL DEFAULT FALSE,
																
																    created_by UUID NOT NULL,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_gmwi_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gmwi_owner
																        FOREIGN KEY(owner_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT fk_gmwi_created_by
																        FOREIGN KEY(created_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_gmwi_type
																        CHECK (work_item_type IN (
																            'TASK','MILESTONE','EVENT','ISSUE','ANNOUNCEMENT',
																            'PROGRESS_UPDATE','ACHIEVEMENT','BOOKING','DELIVERY','MAINTENANCE'
																        )),
																
																    CONSTRAINT chk_gmwi_status
																        CHECK (status IN ('OPEN','IN_PROGRESS','COMPLETED','CANCELLED','BLOCKED','RESOLVED')),
																
																    CONSTRAINT chk_gmwi_priority
																        CHECK (priority IS NULL OR priority IN ('LOW','MEDIUM','HIGH','CRITICAL')),
																
																    CONSTRAINT chk_gmwi_progress
																        CHECK (progress_pct IS NULL OR progress_pct BETWEEN 0 AND 100)
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_moment_resources (
																    resource_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL,
																
																    resource_type VARCHAR(100) NOT NULL,
																    resource_name VARCHAR(250) NOT NULL,
																    description TEXT,
																
																    owner_id UUID,
																    attachment_id UUID,
																    resource_url TEXT,
																
																    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
																    is_memory_asset BOOLEAN NOT NULL DEFAULT FALSE,
																
																    created_by UUID NOT NULL,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_gmr_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gmr_owner
																        FOREIGN KEY(owner_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT fk_gmr_attachment
																        FOREIGN KEY(attachment_id)
																        REFERENCES group_attachments(attachment_id),
																
																    CONSTRAINT fk_gmr_created_by
																        FOREIGN KEY(created_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_gmr_type
																        CHECK (resource_type IN (
																            'DOCUMENT','TOOL','VENUE','EQUIPMENT','RECEIPT','TICKET',
																            'BOOKING','PHOTO','FILE','LINK','REFERENCE','ASSET'
																        )),
																
																    CONSTRAINT chk_gmr_status
																        CHECK (status IN ('ACTIVE','ARCHIVED','REMOVED','EXPIRED'))
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_decisions (
																    decision_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL,
																
																    decision_type VARCHAR(100) NOT NULL,
																    title VARCHAR(250) NOT NULL,
																
																    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
																    owner_id UUID,
																    result TEXT,
																
																    decision_date TIMESTAMP,
																
																    source_ref_table VARCHAR(150),
																    source_ref_id UUID,
																
																    created_by UUID NOT NULL,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_gd_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gd_owner
																        FOREIGN KEY(owner_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT fk_gd_created_by
																        FOREIGN KEY(created_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_gd_type
																        CHECK (decision_type IN (
																            'POLL','VOTE','APPROVAL','RESOLUTION','OWNERSHIP',
																            'RULE','PRIORITY','VENDOR'
																        )),
																
																    CONSTRAINT chk_gd_status
																        CHECK (status IN ('DRAFT','OPEN','APPROVED','REJECTED','RESOLVED','CLOSED'))
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_memory_snapshots (
																    snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL,
																    snapshot_date DATE NOT NULL,
																
																    memory_count INTEGER NOT NULL DEFAULT 0,
																    milestone_count INTEGER NOT NULL DEFAULT 0,
																
																    what_changed_json JSONB,
																    budget_reflection_json JSONB,
																    identity_label VARCHAR(150),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gms_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_gms_counts
																        CHECK (memory_count >= 0 AND milestone_count >= 0)
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_people_impact_scores (
																    impact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL,
																    member_id UUID NOT NULL,
																
																    impact_type VARCHAR(100) NOT NULL,
																    impact_score NUMERIC(6,2) NOT NULL,
																    rank_no INTEGER NOT NULL,
																
																    badge_label VARCHAR(150),
																    supporting_metrics_json JSONB,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gpis_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gpis_member
																        FOREIGN KEY(member_id)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_gpis_type
																        CHECK (impact_type IN (
																            'MOST_ACTIVE','MOST_HELPFUL','TOP_CONTRIBUTOR',
																            'MOST_CONSISTENT','COMMUNITY_BUILDER','MILESTONE_DRIVER'
																        )),
																
																    CONSTRAINT chk_gpis_score
																        CHECK (impact_score BETWEEN 0 AND 100),
																
																    CONSTRAINT chk_gpis_rank
																        CHECK (rank_no >= 1)
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_life_spaces (
																    life_space_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    user_id UUID NOT NULL,
																
																    space_name VARCHAR(200) NOT NULL DEFAULT 'Group Life',
																    space_status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT chk_gls_status
																        CHECK (space_status IN ('ACTIVE','ARCHIVED'))
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_life_moment_links (
																    life_link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    life_space_id UUID NOT NULL,
																    moment_id UUID NOT NULL,
																
																    moment_type VARCHAR(50) NOT NULL,
																    is_active BOOLEAN NOT NULL DEFAULT TRUE,
																    included_weight NUMERIC(6,3) NOT NULL DEFAULT 1.000,
																
																    linked_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_glml_space
																        FOREIGN KEY(life_space_id)
																        REFERENCES group_life_spaces(life_space_id),
																
																    CONSTRAINT fk_glml_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT chk_glml_weight
																        CHECK (included_weight >= 0),
																
																    CONSTRAINT uq_glml_space_moment
																        UNIQUE(life_space_id, moment_id)
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_life_snapshots (
																    life_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    life_space_id UUID NOT NULL,
																    snapshot_date DATE NOT NULL,
																
																    group_life_score NUMERIC(5,2) NOT NULL DEFAULT 0,
																    health_status VARCHAR(30) NOT NULL DEFAULT 'STABLE',
																
																    dominant_driver TEXT,
																    dominant_risk TEXT,
																    highest_leverage TEXT,
																    trend_delta NUMERIC(6,2),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_glsnap_space
																        FOREIGN KEY(life_space_id)
																        REFERENCES group_life_spaces(life_space_id),
																
																    CONSTRAINT chk_glsnap_score
																        CHECK (group_life_score BETWEEN 0 AND 100),
																
																    CONSTRAINT chk_glsnap_status
																        CHECK (health_status IN ('HEALTHY','STABLE','WATCH','NEEDS_ATTENTION','CRITICAL'))
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_life_dimension_scores (
																    dimension_score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    life_snapshot_id UUID NOT NULL,
																
																    dimension_code VARCHAR(100) NOT NULL,
																    dimension_name VARCHAR(150) NOT NULL,
																
																    score NUMERIC(5,2) NOT NULL DEFAULT 0,
																    status VARCHAR(30),
																    trend_delta NUMERIC(6,2),
																    explanation TEXT,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_glds_snapshot
																        FOREIGN KEY(life_snapshot_id)
																        REFERENCES group_life_snapshots(life_snapshot_id),
																
																    CONSTRAINT chk_glds_score
																        CHECK (score BETWEEN 0 AND 100)
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_life_driver_effects (
																    driver_effect_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    life_snapshot_id UUID NOT NULL,
																
																    source_moment_type VARCHAR(50) NOT NULL,
																    target_moment_type VARCHAR(50) NOT NULL,
																
																    effect_label VARCHAR(250) NOT NULL,
																    impact_pct NUMERIC(6,2) NOT NULL,
																
																    explanation TEXT NOT NULL,
																    recommended_action TEXT,
																
																    confidence_level VARCHAR(30) NOT NULL DEFAULT 'MEDIUM',
																    rank_no INTEGER NOT NULL,
																
																    supporting_metrics_json JSONB,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_glde_snapshot
																        FOREIGN KEY(life_snapshot_id)
																        REFERENCES group_life_snapshots(life_snapshot_id),
																
																    CONSTRAINT chk_glde_confidence
																        CHECK (confidence_level IN ('LOW','MEDIUM','HIGH')),
																
																    CONSTRAINT chk_glde_rank
																        CHECK (rank_no >= 1)
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_life_master_snapshots (
																    master_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    user_id UUID NOT NULL,
																    life_space_id UUID NOT NULL,
																    snapshot_date DATE NOT NULL,
																
																    group_life_score NUMERIC(5,2) NOT NULL DEFAULT 0,
																
																    participation_score NUMERIC(5,2),
																    contribution_score NUMERIC(5,2),
																    coordination_score NUMERIC(5,2),
																    progress_score NUMERIC(5,2),
																    community_score NUMERIC(5,2),
																
																    active_group_moments_count INTEGER DEFAULT 0,
																    active_members_count INTEGER DEFAULT 0,
																    open_group_actions_count INTEGER DEFAULT 0,
																    group_risk_count INTEGER DEFAULT 0,
																
																    dominant_group_driver TEXT,
																    dominant_group_risk TEXT,
																    highest_group_leverage TEXT,
																
																    source_snapshot_ids_json JSONB,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_glms_space
																        FOREIGN KEY(life_space_id)
																        REFERENCES group_life_spaces(life_space_id),
																
																    CONSTRAINT chk_glms_score
																        CHECK (group_life_score BETWEEN 0 AND 100)
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_ai_insights (
																    insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID,
																    related_life_space_id UUID,
																
																    insight_layer VARCHAR(50) NOT NULL,
																    insight_type VARCHAR(100) NOT NULL,
																
																    insight_title VARCHAR(250) NOT NULL,
																    insight_body TEXT NOT NULL,
																
																    confidence_level VARCHAR(30),
																    supporting_metrics_json JSONB,
																
																    display_order INTEGER,
																    is_active BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP,
																
																    CONSTRAINT fk_gai_moment_v2
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gai_life_space_v2
																        FOREIGN KEY(related_life_space_id)
																        REFERENCES group_life_spaces(life_space_id),
																
																    CONSTRAINT chk_gai_layer_v2
																        CHECK (insight_layer IN ('PULSE','MOMENTS','MEMORY','LIFE')),
																
																    CONSTRAINT chk_gai_confidence_v2
																        CHECK (confidence_level IS NULL OR confidence_level IN ('LOW','MEDIUM','HIGH'))
																);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_expenses_everything ON group_expenses;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_contributions_everything ON group_contributions;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_work_items_everything ON group_moment_work_items;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_resources_everything ON group_moment_resources;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_decisions_everything ON group_decisions;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_memory_entries_everything ON group_memory_entries;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_budget_plan_everything ON shared_experience_budget_plans;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_budget_allocations_everything ON shared_experience_budget_allocations;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_budget_splits_everything ON shared_experience_budget_splits;
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_life_links_everything ON group_life_moment_links;
-- >>>STMT<<<
ALTER TABLE group_moment_members
																ADD COLUMN IF NOT EXISTS user_id UUID,
																ADD COLUMN IF NOT EXISTS contact_email VARCHAR(255),
																ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(30),
																ADD COLUMN IF NOT EXISTS invite_token UUID,
																ADD COLUMN IF NOT EXISTS invite_sent_at TIMESTAMP,
																ADD COLUMN IF NOT EXISTS avatar_url TEXT;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gmm_user_id
																ON group_moment_members(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gmm_contact_email
																ON group_moment_members(contact_email);
-- >>>STMT<<<
CREATE UNIQUE INDEX IF NOT EXISTS uq_gmm_invite_token
																ON group_moment_members(invite_token)
																WHERE invite_token IS NOT NULL;
-- >>>STMT<<<
ALTER TABLE group_people_impact_scores
																ADD COLUMN IF NOT EXISTS activity_score NUMERIC(5,2),
																ADD COLUMN IF NOT EXISTS helpfulness_score NUMERIC(5,2),
																ADD COLUMN IF NOT EXISTS contribution_score NUMERIC(5,2);
-- >>>STMT<<<
ALTER TABLE group_people_impact_scores
																DROP CONSTRAINT IF EXISTS chk_gpis_activity_score;
-- >>>STMT<<<
ALTER TABLE group_people_impact_scores
																ADD CONSTRAINT chk_gpis_activity_score
																CHECK (
																    activity_score IS NULL
																    OR activity_score BETWEEN 0 AND 100
																);
-- >>>STMT<<<
ALTER TABLE group_people_impact_scores
																DROP CONSTRAINT IF EXISTS chk_gpis_helpfulness_score;
-- >>>STMT<<<
ALTER TABLE group_people_impact_scores
																ADD CONSTRAINT chk_gpis_helpfulness_score
																CHECK (
																    helpfulness_score IS NULL
																    OR helpfulness_score BETWEEN 0 AND 100
																);
-- >>>STMT<<<
ALTER TABLE group_people_impact_scores
																DROP CONSTRAINT IF EXISTS chk_gpis_contribution_score;
-- >>>STMT<<<
ALTER TABLE group_people_impact_scores
																ADD CONSTRAINT chk_gpis_contribution_score
																CHECK (
																    contribution_score IS NULL
																    OR contribution_score BETWEEN 0 AND 100
																);
-- >>>STMT<<<
ALTER TABLE group_pulse_snapshots
																ADD COLUMN IF NOT EXISTS extended_metrics_json JSONB,
																ADD COLUMN IF NOT EXISTS attention_items_json JSONB,
																ADD COLUMN IF NOT EXISTS next_best_action_json JSONB;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gps_extended_metrics_json
																ON group_pulse_snapshots USING GIN(extended_metrics_json);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gps_attention_items_json
																ON group_pulse_snapshots USING GIN(attention_items_json);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gps_next_best_action_json
																ON group_pulse_snapshots USING GIN(next_best_action_json);
-- >>>STMT<<<
ALTER TABLE group_recommendations
																ADD COLUMN IF NOT EXISTS action_label VARCHAR(100),
																ADD COLUMN IF NOT EXISTS action_deep_link VARCHAR(250);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gr_action_deep_link
																ON group_recommendations(action_deep_link);
-- >>>STMT<<<
ALTER TABLE group_live_feed
																ADD COLUMN IF NOT EXISTS created_by UUID;
-- >>>STMT<<<
ALTER TABLE group_live_feed
																DROP CONSTRAINT IF EXISTS fk_glf_created_by;
-- >>>STMT<<<
ALTER TABLE group_live_feed
																ADD CONSTRAINT fk_glf_created_by
																FOREIGN KEY(created_by)
																REFERENCES group_moment_members(member_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_glf_created_by
																ON group_live_feed(created_by);
-- >>>STMT<<<
ALTER TABLE group_attachments
																ADD COLUMN IF NOT EXISTS asset_category VARCHAR(100);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_ga_asset_category
																ON group_attachments(asset_category);
-- >>>STMT<<<
ALTER TABLE group_ai_insights
																ADD COLUMN IF NOT EXISTS display_context VARCHAR(50) NOT NULL DEFAULT 'BOTH';
-- >>>STMT<<<
ALTER TABLE group_ai_insights
																DROP CONSTRAINT IF EXISTS chk_gai_display_context;
-- >>>STMT<<<
ALTER TABLE group_ai_insights
																ADD CONSTRAINT chk_gai_display_context
																CHECK (display_context IN ('PULSE','MEMORY','LIFE','BOTH'));
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gai_display_context
																ON group_ai_insights(display_context);
-- >>>STMT<<<
ALTER TABLE shared_living_tasks
																ADD COLUMN IF NOT EXISTS next_due_date DATE;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_slt_next_due_date
																ON shared_living_tasks(next_due_date);
-- >>>STMT<<<
ALTER TABLE shared_living_maintenance
																ADD COLUMN IF NOT EXISTS linked_expense_id UUID;
-- >>>STMT<<<
ALTER TABLE shared_living_maintenance
																DROP CONSTRAINT IF EXISTS fk_slm_linked_expense;
-- >>>STMT<<<
ALTER TABLE shared_living_maintenance
																ADD CONSTRAINT fk_slm_linked_expense
																FOREIGN KEY(linked_expense_id)
																REFERENCES group_expenses(expense_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_slm_linked_expense
																ON shared_living_maintenance(linked_expense_id);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_prevent_duplicate_single_poll_vote
																ON group_poll_votes;
-- >>>STMT<<<
ALTER TABLE group_live_feed
																ADD COLUMN IF NOT EXISTS entity_name VARCHAR(150),
																ADD COLUMN IF NOT EXISTS entity_id UUID,
																ADD COLUMN IF NOT EXISTS is_editable BOOLEAN NOT NULL DEFAULT TRUE,
																ADD COLUMN IF NOT EXISTS edit_route VARCHAR(250);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_glf_entity
																ON group_live_feed(entity_name, entity_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_glf_is_editable
																ON group_live_feed(is_editable);
-- >>>STMT<<<
ALTER TABLE group_change_history
																ADD COLUMN IF NOT EXISTS edit_batch_id UUID,
																ADD COLUMN IF NOT EXISTS edit_reason TEXT,
																ADD COLUMN IF NOT EXISTS source_activity_id UUID;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gch_edit_batch
																ON group_change_history(edit_batch_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gch_source_activity
																ON group_change_history(source_activity_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS group_activity_edits (
																    edit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL,
																    activity_id UUID,
																
																    entity_name VARCHAR(150) NOT NULL,
																    entity_id UUID NOT NULL,
																
																    edit_status VARCHAR(30) NOT NULL DEFAULT 'SAVED',
																
																    edit_payload_json JSONB,
																    edit_reason TEXT,
																
																    edited_by UUID NOT NULL,
																    edited_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT fk_gae_moment
																        FOREIGN KEY(moment_id)
																        REFERENCES group_moments(moment_id),
																
																    CONSTRAINT fk_gae_activity
																        FOREIGN KEY(activity_id)
																        REFERENCES group_live_feed(feed_id),
																
																    CONSTRAINT fk_gae_edited_by
																        FOREIGN KEY(edited_by)
																        REFERENCES group_moment_members(member_id),
																
																    CONSTRAINT chk_gae_status
																        CHECK (edit_status IN ('DRAFT','SAVED','REVERTED','CANCELLED'))
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gae_moment
																ON group_activity_edits(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gae_entity
																ON group_activity_edits(entity_name, entity_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_gae_edited_by
																ON group_activity_edits(edited_by);

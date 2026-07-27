CREATE TABLE IF NOT EXISTS life360_snapshots (
    life360_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,

    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    snapshot_month DATE NOT NULL DEFAULT DATE_TRUNC('month', CURRENT_DATE)::DATE,

    source_personal_snapshot_id UUID,
    source_group_snapshot_id UUID,
    source_business_snapshot_id UUID,

    personal_score NUMERIC(5,2),
    group_score NUMERIC(5,2),
    business_score NUMERIC(5,2),

    life_alignment_score NUMERIC(5,2) NOT NULL DEFAULT 0,
    life_phase VARCHAR(50),

    money_score NUMERIC(5,2),
    relationship_score NUMERIC(5,2),
    execution_score NUMERIC(5,2),
    growth_score NUMERIC(5,2),

    personal_energy_pct NUMERIC(5,2),
    group_energy_pct NUMERIC(5,2),
    business_energy_pct NUMERIC(5,2),

    momentum_score NUMERIC(6,2),
    momentum_status VARCHAR(30),

    strongest_driver VARCHAR(100),
    biggest_tension VARCHAR(100),

    money_status VARCHAR(40),
    relationship_status VARCHAR(40),
    execution_status VARCHAR(40),
    growth_status VARCHAR(40),

    reflection_summary TEXT,

    active_dimensions_count INTEGER DEFAULT 0,
    signal_confidence_score NUMERIC(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_life360_user_date UNIQUE (user_id, snapshot_date)
);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS circle_participants (
    circle_participant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,

    participant_user_id UUID,
    participant_name VARCHAR(200) NOT NULL,
    participant_phone VARCHAR(30),
    participant_email VARCHAR(200),

    first_seen_date DATE,
    last_seen_date DATE,

    is_active BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_circle_participant UNIQUE (
        user_id,
        participant_name,
        COALESCE(participant_phone, ''),
        COALESCE(participant_email, '')
    )
);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS circle_participant_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_participant_id UUID NOT NULL REFERENCES circle_participants(circle_participant_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,

    source_type VARCHAR(30) NOT NULL, -- GROUP / BUSINESS
    source_moment_id UUID NOT NULL,
    source_moment_name VARCHAR(250),
    source_moment_type VARCHAR(100),

    participation_date DATE,
    is_active_source BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_circle_source UNIQUE (
        circle_participant_id,
        source_type,
        source_moment_id
    )
);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS circle_participant_stats (
    stats_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_participant_id UUID NOT NULL REFERENCES circle_participants(circle_participant_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,

    shared_moment_count INTEGER DEFAULT 0,
    active_moment_count INTEGER DEFAULT 0,
    recent_activity_count INTEGER DEFAULT 0,

    participation_score NUMERIC(5,2) DEFAULT 0,
    rank_order INTEGER,

    last_activity_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_circle_stats UNIQUE (circle_participant_id)
);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS circle_suggestions (
    suggestion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,

    suggestion_type VARCHAR(50) NOT NULL,
    participant_ids_json JSONB NOT NULL,

    suggestion_title VARCHAR(300) NOT NULL,
    suggestion_description TEXT NOT NULL,

    confidence_score NUMERIC(5,2) DEFAULT 0,
    cta_label VARCHAR(100),
    target_create_flow VARCHAR(100),

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

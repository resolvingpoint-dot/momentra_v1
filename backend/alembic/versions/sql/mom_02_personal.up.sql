CREATE TABLE IF NOT EXISTS personal_moment_types (
																    moment_type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_type_code VARCHAR(50) NOT NULL UNIQUE,
																    moment_type_name VARCHAR(100) NOT NULL UNIQUE,
																    description TEXT NOT NULL,
																    display_order INT NOT NULL CHECK (display_order BETWEEN 1 AND 4),
																    is_active BOOLEAN NOT NULL DEFAULT TRUE,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_personal_moment_type_code
																    CHECK (
																        moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    )
																);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_moments (
																    moment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    user_id UUID NOT NULL,
																    moment_type_id UUID NOT NULL REFERENCES personal_moment_types(moment_type_id),
																    moment_name VARCHAR(150) NOT NULL,
																    status VARCHAR(30) NOT NULL DEFAULT 'DRAFT',
																    activated_at TIMESTAMP NULL,
																    archived_at TIMESTAMP NULL,
																    current_identity_label VARCHAR(100),
																    current_state_label VARCHAR(100),
																    last_activity_at TIMESTAMP NULL,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_personal_moment_status
																    CHECK (status IN ('DRAFT', 'ACTIVE', 'PAUSED', 'ARCHIVED')),
																
																    CONSTRAINT chk_personal_moment_activation
																    CHECK (
																        status <> 'ACTIVE'
																        OR activated_at IS NOT NULL
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_moments_user
																ON personal_moments(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_moments_type_status
																ON personal_moments(moment_type_id, status);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_moment_profiles (
																    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
																    user_id UUID NOT NULL,
																    identity_label VARCHAR(100) NOT NULL,
																    identity_description TEXT NOT NULL,
																    energy_label VARCHAR(100),
																    primary_focus_label VARCHAR(100) NOT NULL,
																    primary_gap_label VARCHAR(100),
																    primary_opportunity_label VARCHAR(150),
																    horizon_current_label VARCHAR(100),
																    horizon_target_label VARCHAR(100),
																    horizon_gap_label VARCHAR(100),
																    horizon_potential_label VARCHAR(50),
																    setup_payload JSONB NOT NULL,
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_horizon_potential_label
																    CHECK (
																        horizon_potential_label IS NULL
																        OR horizon_potential_label IN ('LOW', 'MODERATE', 'HIGH')
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_moment_profiles_moment
																ON personal_moment_profiles(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_moment_profiles_user
																ON personal_moment_profiles(user_id);
-- >>>STMT<<<
CREATE UNIQUE INDEX IF NOT EXISTS uq_personal_moment_profiles_current
																ON personal_moment_profiles(moment_id)
																WHERE is_current = TRUE;
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_operations_profile (
																    life_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
																    user_id UUID NOT NULL,
																
																    current_life_state VARCHAR(50) NOT NULL,
																    desired_directions TEXT[] NOT NULL,
																    pressure_sources TEXT[] NOT NULL,
																    recovery_supports TEXT[] NOT NULL,
																
																    runtime_identity VARCHAR(100) NOT NULL,
																    initial_runtime_focus VARCHAR(100) NOT NULL,
																    recovery_integrity_score DECIMAL(5,2),
																    pressure_load_level VARCHAR(50),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_life_desired_directions_not_empty
																    CHECK (array_length(desired_directions, 1) >= 1),
																
																    CONSTRAINT chk_life_pressure_sources_not_empty
																    CHECK (array_length(pressure_sources, 1) >= 1),
																
																    CONSTRAINT chk_life_recovery_supports_not_empty
																    CHECK (array_length(recovery_supports, 1) >= 1),
																
																    CONSTRAINT chk_life_recovery_integrity_score
																    CHECK (
																        recovery_integrity_score IS NULL
																        OR recovery_integrity_score BETWEEN 0 AND 100
																    ),
																
																    CONSTRAINT chk_life_pressure_load_level
																    CHECK (
																        pressure_load_level IS NULL
																        OR pressure_load_level IN ('LOW', 'MODERATE', 'HIGH')
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_ops_profile_moment
																ON personal_life_operations_profile(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_ops_profile_user
																ON personal_life_operations_profile(user_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_future_building_profile (
																    future_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
																    user_id UUID NOT NULL,
																
																    future_theme VARCHAR(80) NOT NULL,
																    current_momentum_state VARCHAR(80) NOT NULL,
																    future_values TEXT[] NOT NULL,
																    friction_sources TEXT[] NOT NULL,
																    momentum_drivers TEXT[] NOT NULL,
																    future_confidence VARCHAR(50) NOT NULL,
																
																    future_identity VARCHAR(100) NOT NULL,
																    largest_friction_label VARCHAR(100),
																    primary_opportunity_label VARCHAR(150),
																    breakthrough_potential VARCHAR(50),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_future_values_not_empty
																    CHECK (array_length(future_values, 1) >= 1),
																
																    CONSTRAINT chk_future_friction_sources_not_empty
																    CHECK (array_length(friction_sources, 1) >= 1),
																
																    CONSTRAINT chk_future_momentum_drivers_not_empty
																    CHECK (array_length(momentum_drivers, 1) >= 1),
																
																    CONSTRAINT chk_future_confidence
																    CHECK (
																        future_confidence IN (
																            'Exciting',
																            'Hopeful',
																            'Confident',
																            'Unclear',
																            'Stuck',
																            'Overwhelming'
																        )
																    ),
																
																    CONSTRAINT chk_future_breakthrough_potential
																    CHECK (
																        breakthrough_potential IS NULL
																        OR breakthrough_potential IN ('LOW', 'MODERATE', 'HIGH')
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_profile_moment
																ON personal_future_building_profile(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_profile_user
																ON personal_future_building_profile(user_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_lifestyle_profile (
																    lifestyle_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
																    user_id UUID NOT NULL,
																
																    lifestyle_style VARCHAR(80) NOT NULL,
																    current_lifestyle_state VARCHAR(50) NOT NULL,
																    desired_lifestyle_vectors TEXT[] NOT NULL,
																    neglected_lifestyle_areas TEXT[] NOT NULL,
																    best_day_drivers TEXT[] NOT NULL,
																    lifestyle_enrichment_factors TEXT[] NOT NULL,
																
																    lifestyle_identity VARCHAR(100) NOT NULL,
																    lifestyle_energy VARCHAR(100) NOT NULL,
																    primary_lifestyle_gap VARCHAR(100),
																    primary_lifestyle_opportunity VARCHAR(150),
																    lifestyle_potential VARCHAR(50),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_lifestyle_desired_vectors_not_empty
																    CHECK (array_length(desired_lifestyle_vectors, 1) >= 1),
																
																    CONSTRAINT chk_lifestyle_neglected_areas_not_empty
																    CHECK (array_length(neglected_lifestyle_areas, 1) >= 1),
																
																    CONSTRAINT chk_lifestyle_best_day_drivers_not_empty
																    CHECK (array_length(best_day_drivers, 1) >= 1),
																
																    CONSTRAINT chk_lifestyle_enrichment_factors_not_empty
																    CHECK (array_length(lifestyle_enrichment_factors, 1) >= 1),
																
																    CONSTRAINT chk_lifestyle_potential
																    CHECK (
																        lifestyle_potential IS NULL
																        OR lifestyle_potential IN ('LOW', 'MODERATE', 'HIGH')
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_profile_moment
																ON personal_lifestyle_profile(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_profile_user
																ON personal_lifestyle_profile(user_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_relationships_profile (
																    relationship_profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
																    user_id UUID NOT NULL,
																
																    relationship_focus VARCHAR(80) NOT NULL,
																    current_relationship_state VARCHAR(50) NOT NULL,
																    desired_connection_types TEXT[] NOT NULL,
																    neglected_relationship_areas TEXT[] NOT NULL,
																    relationship_strength_factors TEXT[] NOT NULL,
																    relationship_investment_areas TEXT[] NOT NULL,
																
																    relationship_identity VARCHAR(100) NOT NULL,
																    relationship_energy VARCHAR(100) NOT NULL,
																    primary_relationship_gap VARCHAR(100),
																    primary_relationship_opportunity VARCHAR(150),
																    relationship_potential VARCHAR(50),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_relationship_desired_connection_not_empty
																    CHECK (array_length(desired_connection_types, 1) >= 1),
																
																    CONSTRAINT chk_relationship_neglected_areas_not_empty
																    CHECK (array_length(neglected_relationship_areas, 1) >= 1),
																
																    CONSTRAINT chk_relationship_strength_factors_not_empty
																    CHECK (array_length(relationship_strength_factors, 1) >= 1),
																
																    CONSTRAINT chk_relationship_investment_areas_not_empty
																    CHECK (array_length(relationship_investment_areas, 1) >= 1),
																
																    CONSTRAINT chk_relationship_potential
																    CHECK (
																        relationship_potential IS NULL
																        OR relationship_potential IN ('LOW', 'MODERATE', 'HIGH')
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationships_profile_moment
																ON personal_relationships_profile(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationships_profile_user
																ON personal_relationships_profile(user_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_quick_add_events (
																    quick_add_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id)
																        ON DELETE CASCADE,
																
																    user_id UUID NOT NULL,
																
																    moment_type_code VARCHAR(50) NOT NULL,
																
																    quick_add_tab_code VARCHAR(50) NOT NULL,
																
																    event_type VARCHAR(80) NOT NULL,
																
																    event_occurred_at TIMESTAMP NOT NULL,
																
																    raw_payload JSONB NOT NULL,
																
																    is_voided BOOLEAN NOT NULL DEFAULT FALSE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_personal_quick_add_moment_type
																    CHECK (
																        moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    )
																);
-- >>>STMT<<<
CREATE INDEX idx_personal_quick_add_events_moment
																ON personal_quick_add_events(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_personal_quick_add_events_user
																ON personal_quick_add_events(user_id);
-- >>>STMT<<<
CREATE INDEX idx_personal_quick_add_events_type
																ON personal_quick_add_events(moment_type_code);
-- >>>STMT<<<
CREATE INDEX idx_personal_quick_add_events_date
																ON personal_quick_add_events(event_occurred_at);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_attention_events (
																
																    attention_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    quick_add_event_id UUID NOT NULL UNIQUE
																        REFERENCES personal_quick_add_events(quick_add_event_id)
																        ON DELETE CASCADE,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id),
																
																    user_id UUID NOT NULL,
																
																    attention_category VARCHAR(100) NOT NULL,
																
																    intensity_level VARCHAR(30) NOT NULL,
																
																    status VARCHAR(30) NOT NULL,
																
																    note TEXT,
																
																    pressure_weight DECIMAL(5,2),
																
																    focus_load_score DECIMAL(5,2),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_attention_intensity
																    CHECK (
																        intensity_level IN (
																            'LIGHT',
																            'MODERATE',
																            'HEAVY'
																        )
																    ),
																
																    CONSTRAINT chk_attention_status
																    CHECK (
																        status IN (
																            'COMPLETED',
																            'IN_PROGRESS',
																            'DELAYED'
																        )
																    ),
																
																    CONSTRAINT chk_attention_focus_load
																    CHECK (
																        focus_load_score IS NULL
																        OR focus_load_score BETWEEN 0 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX idx_life_attention_moment
																ON personal_life_attention_events(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_life_attention_user
																ON personal_life_attention_events(user_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_recovery_events (
																
																    recovery_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    quick_add_event_id UUID NOT NULL UNIQUE
																        REFERENCES personal_quick_add_events(quick_add_event_id)
																        ON DELETE CASCADE,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id),
																
																    user_id UUID NOT NULL,
																
																    recovery_type VARCHAR(100) NOT NULL,
																
																    energy_impact VARCHAR(30) NOT NULL,
																
																    duration_bucket VARCHAR(50),
																
																    note TEXT,
																
																    recovery_score DECIMAL(5,2),
																
																    anchor_candidate_flag BOOLEAN DEFAULT FALSE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_recovery_energy
																    CHECK (
																        energy_impact IN (
																            'LOW',
																            'MODERATE',
																            'HIGH'
																        )
																    ),
																
																    CONSTRAINT chk_recovery_score
																    CHECK (
																        recovery_score IS NULL
																        OR recovery_score BETWEEN 0 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX idx_life_recovery_moment
																ON personal_life_recovery_events(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_life_recovery_user
																ON personal_life_recovery_events(user_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_mood_events (
																
																    mood_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    quick_add_event_id UUID NOT NULL UNIQUE
																        REFERENCES personal_quick_add_events(quick_add_event_id)
																        ON DELETE CASCADE,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id),
																
																    user_id UUID NOT NULL,
																
																    mood_state VARCHAR(50) NOT NULL,
																
																    reflection_text TEXT,
																
																    mood_tags TEXT[],
																
																    mood_score DECIMAL(5,2),
																
																    pressure_context_flag BOOLEAN DEFAULT FALSE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_mood_score
																    CHECK (
																        mood_score IS NULL
																        OR mood_score BETWEEN 0 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX idx_life_mood_moment
																ON personal_life_mood_events(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_life_mood_user
																ON personal_life_mood_events(user_id);
-- >>>STMT<<<
CREATE INDEX idx_life_mood_tags
																ON personal_life_mood_events
																USING GIN(mood_tags);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_adjust_events (
																
																    adjust_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    quick_add_event_id UUID NOT NULL UNIQUE
																        REFERENCES personal_quick_add_events(quick_add_event_id)
																        ON DELETE CASCADE,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id),
																
																    user_id UUID NOT NULL,
																
																    adjustment_areas TEXT[] NOT NULL,
																
																    pressure_signal VARCHAR(20),
																    recovery_signal VARCHAR(20),
																    focus_signal VARCHAR(20),
																    momentum_signal VARCHAR(20),
																
																    note TEXT,
																
																    runtime_shift_score DECIMAL(5,2),
																
																    recommended_runtime_priority VARCHAR(150),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CONSTRAINT chk_adjustment_area_not_empty
																    CHECK (
																        array_length(adjustment_areas,1) >= 1
																    ),
																
																    CONSTRAINT chk_pressure_signal
																    CHECK (
																        pressure_signal IS NULL
																        OR pressure_signal IN ('UP','DOWN','STABLE')
																    ),
																
																    CONSTRAINT chk_recovery_signal
																    CHECK (
																        recovery_signal IS NULL
																        OR recovery_signal IN ('UP','DOWN','STABLE')
																    ),
																
																    CONSTRAINT chk_focus_signal
																    CHECK (
																        focus_signal IS NULL
																        OR focus_signal IN ('UP','DOWN','STABLE')
																    ),
																
																    CONSTRAINT chk_momentum_signal
																    CHECK (
																        momentum_signal IS NULL
																        OR momentum_signal IN ('UP','DOWN','STABLE')
																    ),
																
																    CONSTRAINT chk_runtime_shift_score
																    CHECK (
																        runtime_shift_score IS NULL
																        OR runtime_shift_score BETWEEN 0 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX idx_life_adjust_moment
																ON personal_life_adjust_events(moment_id);
-- >>>STMT<<<
CREATE INDEX idx_life_adjust_user
																ON personal_life_adjust_events(user_id);
-- >>>STMT<<<
CREATE INDEX idx_life_adjust_area
																ON personal_life_adjust_events
																USING GIN(adjustment_areas);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_future_progress_events (
    progress_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    progress_type VARCHAR(80) NOT NULL,
    progress_level VARCHAR(50) NOT NULL,

    money_invested_amount DECIMAL(14,2),
    time_invested_bucket VARCHAR(30),
    effort_level VARCHAR(30),

    note TEXT,

    momentum_score_delta DECIMAL(5,2),
    investment_weight_score DECIMAL(5,2),
    velocity_signal_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_future_progress_level
    CHECK (
        progress_level IN (
            'Small Step',
            'Moderate Progress',
            'Major Progress',
            'Breakthrough'
        )
    ),

    CONSTRAINT chk_future_progress_money
    CHECK (
        money_invested_amount IS NULL
        OR money_invested_amount >= 0
    ),

    CONSTRAINT chk_future_progress_effort
    CHECK (
        effort_level IS NULL
        OR effort_level IN ('Low', 'Medium', 'High', 'Exceptional')
    ),

    CONSTRAINT chk_future_progress_momentum_score
    CHECK (
        momentum_score_delta IS NULL
        OR momentum_score_delta BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_progress_moment
ON personal_future_progress_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_progress_user
ON personal_future_progress_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_progress_date
ON personal_future_progress_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_future_milestone_events (
    milestone_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    milestone_nature VARCHAR(80) NOT NULL,
    impact_level VARCHAR(50) NOT NULL,
    outcome_value VARCHAR(80),
    celebration_level VARCHAR(50),

    note TEXT,

    achievement_score_delta DECIMAL(5,2),
    breakthrough_signal_flag BOOLEAN NOT NULL DEFAULT FALSE,
    future_return_signal VARCHAR(80),

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_future_milestone_nature
    CHECK (
        milestone_nature IN (
            'Achievement',
            'Recognition',
            'Completion',
            'Launch',
            'Certification',
            'Promotion',
            'Revenue Event',
            'Breakthrough'
        )
    ),

    CONSTRAINT chk_future_milestone_impact
    CHECK (
        impact_level IN (
            'Minor',
            'Meaningful',
            'Major',
            'Transformational'
        )
    ),

    CONSTRAINT chk_future_milestone_outcome
    CHECK (
        outcome_value IS NULL
        OR outcome_value IN (
            'Income Increase',
            'Savings Increase',
            'Revenue Increase',
            'Cost Reduction',
            'No Financial Impact'
        )
    ),

    CONSTRAINT chk_future_milestone_celebration
    CHECK (
        celebration_level IS NULL
        OR celebration_level IN (
            'Personal Win',
            'Shared Win',
            'Life Moment'
        )
    ),

    CONSTRAINT chk_future_milestone_score
    CHECK (
        achievement_score_delta IS NULL
        OR achievement_score_delta BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_milestone_moment
ON personal_future_milestone_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_milestone_user
ON personal_future_milestone_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_milestone_date
ON personal_future_milestone_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_future_opportunity_events (
    opportunity_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    opportunity_source VARCHAR(80) NOT NULL,
    potential_level VARCHAR(50) NOT NULL,
    opportunity_status VARCHAR(50) NOT NULL,

    note TEXT,

    opportunity_score_delta DECIMAL(5,2),
    acceleration_signal_flag BOOLEAN NOT NULL DEFAULT FALSE,
    best_opportunity_candidate_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_future_opportunity_source
    CHECK (
        opportunity_source IN (
            'New Connection',
            'New Skill',
            'New Resource',
            'New Funding',
            'New Role',
            'New Client',
            'New Market',
            'New Idea',
            'New Partnership',
            'New Exposure',
            'Unexpected Event',
            'Other'
        )
    ),

    CONSTRAINT chk_future_opportunity_potential
    CHECK (
        potential_level IN (
            'Low',
            'Moderate',
            'High',
            'Game-Changing'
        )
    ),

    CONSTRAINT chk_future_opportunity_status
    CHECK (
        opportunity_status IN (
            'Exploring',
            'Considering',
            'Acting',
            'Captured'
        )
    ),

    CONSTRAINT chk_future_opportunity_score
    CHECK (
        opportunity_score_delta IS NULL
        OR opportunity_score_delta BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_opportunity_moment
ON personal_future_opportunity_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_opportunity_user
ON personal_future_opportunity_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_opportunity_date
ON personal_future_opportunity_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_future_learning_events (
    learning_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    learning_type VARCHAR(50) NOT NULL,
    relevance_level VARCHAR(50) NOT NULL,
    application_status VARCHAR(50),

    note TEXT,

    capability_score_delta DECIMAL(5,2),
    confidence_boost_score DECIMAL(5,2),
    readiness_signal_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_future_learning_type
    CHECK (
        learning_type IN (
            'Skill',
            'Knowledge',
            'Insight',
            'Experience',
            'Mentorship',
            'Mistake'
        )
    ),

    CONSTRAINT chk_future_learning_relevance
    CHECK (
        relevance_level IN (
            'Useful',
            'Important',
            'High Leverage',
            'Transformational'
        )
    ),

    CONSTRAINT chk_future_learning_application
    CHECK (
        application_status IS NULL
        OR application_status IN (
            'Will Use Soon',
            'Already Applying',
            'Future Use'
        )
    ),

    CONSTRAINT chk_future_learning_capability_score
    CHECK (
        capability_score_delta IS NULL
        OR capability_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_future_learning_confidence_score
    CHECK (
        confidence_boost_score IS NULL
        OR confidence_boost_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_learning_moment
ON personal_future_learning_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_learning_user
ON personal_future_learning_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_learning_date
ON personal_future_learning_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_future_pivot_events (
    pivot_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    adjustment_type VARCHAR(80) NOT NULL,
    pivot_reason VARCHAR(80) NOT NULL,
    confidence_level VARCHAR(30) NOT NULL,

    note TEXT,

    direction_shift_score DECIMAL(5,2),
    adaptability_score_delta DECIMAL(5,2),
    future_horizon_update_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_future_pivot_adjustment
    CHECK (
        adjustment_type IN (
            'New Priority',
            'New Goal',
            'Reduce Scope',
            'Increase Focus',
            'Change Timeline',
            'Change Direction'
        )
    ),

    CONSTRAINT chk_future_pivot_reason
    CHECK (
        pivot_reason IN (
            'New Information',
            'Opportunity',
            'Constraint',
            'Personal Decision',
            'Market Change'
        )
    ),

    CONSTRAINT chk_future_pivot_confidence
    CHECK (
        confidence_level IN (
            'Low',
            'Medium',
            'High'
        )
    ),

    CONSTRAINT chk_future_pivot_direction_score
    CHECK (
        direction_shift_score IS NULL
        OR direction_shift_score BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_future_pivot_adaptability_score
    CHECK (
        adaptability_score_delta IS NULL
        OR adaptability_score_delta BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_pivot_moment
ON personal_future_pivot_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_pivot_user
ON personal_future_pivot_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_future_pivot_date
ON personal_future_pivot_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_lifestyle_experience_events (
    experience_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    experience_type VARCHAR(80) NOT NULL,
    experience_quality VARCHAR(50) NOT NULL,
    energy_impact VARCHAR(50) NOT NULL,
    people_context VARCHAR(50),
    location_context VARCHAR(50),

    cost_amount DECIMAL(14,2),
    spend_category VARCHAR(80),
    value_received VARCHAR(80),

    note TEXT,

    fulfillment_score_delta DECIMAL(5,2),
    lifestyle_roi_score DECIMAL(5,2),
    best_day_candidate_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_lifestyle_experience_type
    CHECK (
        experience_type IN (
            'Travel',
            'Food',
            'Nature',
            'Adventure',
            'Entertainment',
            'Social',
            'Family',
            'Personal',
            'Wellbeing',
            'Hobby',
            'Other'
        )
    ),

    CONSTRAINT chk_lifestyle_experience_quality
    CHECK (
        experience_quality IN (
            'Ordinary',
            'Enjoyable',
            'Memorable',
            'Exceptional'
        )
    ),

    CONSTRAINT chk_lifestyle_energy_impact
    CHECK (
        energy_impact IN (
            'Drained',
            'Neutral',
            'Refreshed',
            'Energized'
        )
    ),

    CONSTRAINT chk_lifestyle_people_context
    CHECK (
        people_context IS NULL
        OR people_context IN (
            'Alone',
            'Partner',
            'Friends',
            'Family',
            'Group'
        )
    ),

    CONSTRAINT chk_lifestyle_location_context
    CHECK (
        location_context IS NULL
        OR location_context IN (
            'Home',
            'Local',
            'Outing',
            'Travel'
        )
    ),

    CONSTRAINT chk_lifestyle_cost_amount
    CHECK (
        cost_amount IS NULL
        OR cost_amount >= 0
    ),

    CONSTRAINT chk_lifestyle_spend_category
    CHECK (
        spend_category IS NULL
        OR spend_category IN (
            'Travel',
            'Food & Dining',
            'Entertainment',
            'Wellbeing',
            'Fitness',
            'Learning',
            'Shopping',
            'Hobbies',
            'Experiences',
            'Other'
        )
    ),

    CONSTRAINT chk_lifestyle_value_received
    CHECK (
        value_received IS NULL
        OR value_received IN (
            'Not Worth It',
            'Okay',
            'Worth It',
            'Excellent Value',
            'Life Enriching'
        )
    ),

    CONSTRAINT chk_lifestyle_fulfillment_score
    CHECK (
        fulfillment_score_delta IS NULL
        OR fulfillment_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_lifestyle_roi_score
    CHECK (
        lifestyle_roi_score IS NULL
        OR lifestyle_roi_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_experience_moment
ON personal_lifestyle_experience_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_experience_user
ON personal_lifestyle_experience_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_experience_date
ON personal_lifestyle_experience_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_lifestyle_wellbeing_events (
    wellbeing_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    wellbeing_areas TEXT[] NOT NULL,
    wellbeing_state VARCHAR(50) NOT NULL,
    contributors TEXT[],

    note TEXT,

    wellbeing_score_delta DECIMAL(5,2),
    energy_signal_score DECIMAL(5,2),
    balance_driver_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_lifestyle_wellbeing_areas_not_empty
    CHECK (array_length(wellbeing_areas, 1) >= 1),

    CONSTRAINT chk_lifestyle_wellbeing_state
    CHECK (
        wellbeing_state IN (
            'Low',
            'Moderate',
            'Good',
            'Excellent'
        )
    ),

    CONSTRAINT chk_lifestyle_wellbeing_score
    CHECK (
        wellbeing_score_delta IS NULL
        OR wellbeing_score_delta BETWEEN -100 AND 100
    ),

    CONSTRAINT chk_lifestyle_energy_signal_score
    CHECK (
        energy_signal_score IS NULL
        OR energy_signal_score BETWEEN -100 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_wellbeing_moment
ON personal_lifestyle_wellbeing_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_wellbeing_user
ON personal_lifestyle_wellbeing_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_wellbeing_date
ON personal_lifestyle_wellbeing_events(event_date);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_wellbeing_areas
ON personal_lifestyle_wellbeing_events
USING GIN(wellbeing_areas);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_wellbeing_contributors
ON personal_lifestyle_wellbeing_events
USING GIN(contributors);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_lifestyle_discovery_events (
    discovery_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    discovery_type VARCHAR(80) NOT NULL,
    impact_level VARCHAR(50) NOT NULL,
    curiosity_level VARCHAR(30) NOT NULL,

    money_invested_amount DECIMAL(14,2),

    note TEXT,

    exploration_score_delta DECIMAL(5,2),
    curiosity_driver_flag BOOLEAN NOT NULL DEFAULT FALSE,
    expansion_signal_score DECIMAL(5,2),

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_lifestyle_discovery_type
    CHECK (
        discovery_type IN (
            'Place',
            'Idea',
            'Activity',
            'Person',
            'Skill',
            'Experience',
            'Opportunity',
            'Other'
        )
    ),

    CONSTRAINT chk_lifestyle_discovery_impact
    CHECK (
        impact_level IN (
            'Interesting',
            'Useful',
            'Inspiring',
            'Life-Changing'
        )
    ),

    CONSTRAINT chk_lifestyle_curiosity_level
    CHECK (
        curiosity_level IN (
            'Low',
            'Moderate',
            'High'
        )
    ),

    CONSTRAINT chk_lifestyle_discovery_money
    CHECK (
        money_invested_amount IS NULL
        OR money_invested_amount >= 0
    ),

    CONSTRAINT chk_lifestyle_exploration_score
    CHECK (
        exploration_score_delta IS NULL
        OR exploration_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_lifestyle_expansion_score
    CHECK (
        expansion_signal_score IS NULL
        OR expansion_signal_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_discovery_moment
ON personal_lifestyle_discovery_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_discovery_user
ON personal_lifestyle_discovery_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_discovery_date
ON personal_lifestyle_discovery_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_lifestyle_expression_events (
    expression_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    creation_type VARCHAR(80) NOT NULL,
    satisfaction_level VARCHAR(50) NOT NULL,
    time_invested_bucket VARCHAR(30),

    money_invested_amount DECIMAL(14,2),

    note TEXT,

    creativity_score_delta DECIMAL(5,2),
    expression_energy_score DECIMAL(5,2),
    inspiration_source_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_lifestyle_creation_type
    CHECK (
        creation_type IN (
            'Writing',
            'Art',
            'Music',
            'Design',
            'Content',
            'Photography',
            'Problem Solving',
            'Planning',
            'Other'
        )
    ),

    CONSTRAINT chk_lifestyle_satisfaction_level
    CHECK (
        satisfaction_level IN (
            'Low',
            'Moderate',
            'High',
            'Exceptional'
        )
    ),

    CONSTRAINT chk_lifestyle_expression_time
    CHECK (
        time_invested_bucket IS NULL
        OR time_invested_bucket IN (
            '<30',
            '30_60',
            '1_2_HOURS',
            '2_PLUS_HOURS'
        )
    ),

    CONSTRAINT chk_lifestyle_expression_money
    CHECK (
        money_invested_amount IS NULL
        OR money_invested_amount >= 0
    ),

    CONSTRAINT chk_lifestyle_creativity_score
    CHECK (
        creativity_score_delta IS NULL
        OR creativity_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_lifestyle_expression_energy_score
    CHECK (
        expression_energy_score IS NULL
        OR expression_energy_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_expression_moment
ON personal_lifestyle_expression_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_expression_user
ON personal_lifestyle_expression_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_expression_date
ON personal_lifestyle_expression_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_lifestyle_adjust_events (
    lifestyle_adjust_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    adjustment_area VARCHAR(100) NOT NULL,
    priority_level VARCHAR(30) NOT NULL,
    confidence_level VARCHAR(30) NOT NULL,

    note TEXT,

    lifestyle_gap_score DECIMAL(5,2),
    change_readiness_score DECIMAL(5,2),
    recommended_action_label VARCHAR(150),

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_lifestyle_adjustment_area
    CHECK (
        adjustment_area IN (
            'More Rest',
            'More Travel',
            'More Creativity',
            'More Social Time',
            'More Exercise',
            'More Personal Time',
            'More Exploration',
            'More Balance',
            'More Presence'
        )
    ),

    CONSTRAINT chk_lifestyle_adjust_priority
    CHECK (
        priority_level IN (
            'Low',
            'Medium',
            'High'
        )
    ),

    CONSTRAINT chk_lifestyle_adjust_confidence
    CHECK (
        confidence_level IN (
            'Not Sure',
            'Somewhat Sure',
            'Very Sure'
        )
    ),

    CONSTRAINT chk_lifestyle_gap_score
    CHECK (
        lifestyle_gap_score IS NULL
        OR lifestyle_gap_score BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_lifestyle_change_readiness_score
    CHECK (
        change_readiness_score IS NULL
        OR change_readiness_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_adjust_moment
ON personal_lifestyle_adjust_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_adjust_user
ON personal_lifestyle_adjust_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_lifestyle_adjust_date
ON personal_lifestyle_adjust_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_relationship_connection_events (
    connection_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    connection_type VARCHAR(80) NOT NULL,
    relationship_type VARCHAR(80) NOT NULL,
    connection_quality VARCHAR(50) NOT NULL,
    emotional_tone VARCHAR(50),
    time_invested_bucket VARCHAR(30),

    note TEXT,

    connection_score_delta DECIMAL(5,2),
    trust_score_delta DECIMAL(5,2),
    presence_signal_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_relationship_connection_type
    CHECK (
        connection_type IN (
            'Conversation',
            'Call',
            'Message',
            'Visit',
            'Shared Time',
            'Meal Together',
            'Celebration',
            'Check-In',
            'Other'
        )
    ),

    CONSTRAINT chk_relationship_connection_relationship_type
    CHECK (
        relationship_type IN (
            'Partner',
            'Family',
            'Friend',
            'Parent',
            'Child',
            'Mentor',
            'Professional',
            'Community'
        )
    ),

    CONSTRAINT chk_relationship_connection_quality
    CHECK (
        connection_quality IN (
            'Routine',
            'Meaningful',
            'Deep',
            'Memorable'
        )
    ),

    CONSTRAINT chk_relationship_emotional_tone
    CHECK (
        emotional_tone IS NULL
        OR emotional_tone IN (
            'Positive',
            'Neutral',
            'Difficult',
            'Supportive',
            'Celebratory'
        )
    ),

    CONSTRAINT chk_relationship_connection_time
    CHECK (
        time_invested_bucket IS NULL
        OR time_invested_bucket IN (
            '<15',
            '15_30',
            '30_60',
            '1_2_HOURS',
            '2_PLUS_HOURS'
        )
    ),

    CONSTRAINT chk_relationship_connection_score
    CHECK (
        connection_score_delta IS NULL
        OR connection_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_relationship_trust_score
    CHECK (
        trust_score_delta IS NULL
        OR trust_score_delta BETWEEN -100 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_connection_moment
ON personal_relationship_connection_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_connection_user
ON personal_relationship_connection_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_connection_date
ON personal_relationship_connection_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_relationship_support_events (
    support_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    support_type VARCHAR(80) NOT NULL,
    relationship_type VARCHAR(80) NOT NULL,
    support_direction VARCHAR(30) NOT NULL,
    impact_level VARCHAR(50) NOT NULL,

    note TEXT,

    support_score_delta DECIMAL(5,2),
    resilience_score_delta DECIMAL(5,2),
    support_balance_side VARCHAR(30),

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_relationship_support_type
    CHECK (
        support_type IN (
            'Emotional',
            'Practical',
            'Financial',
            'Advice',
            'Encouragement',
            'Care',
            'Celebration',
            'Other'
        )
    ),

    CONSTRAINT chk_relationship_support_relationship_type
    CHECK (
        relationship_type IN (
            'Partner',
            'Family',
            'Friend',
            'Parent',
            'Child',
            'Mentor',
            'Professional',
            'Community'
        )
    ),

    CONSTRAINT chk_relationship_support_direction
    CHECK (
        support_direction IN (
            'Given',
            'Received',
            'Mutual'
        )
    ),

    CONSTRAINT chk_relationship_support_impact
    CHECK (
        impact_level IN (
            'Small',
            'Meaningful',
            'Important',
            'Transformational'
        )
    ),

    CONSTRAINT chk_relationship_support_score
    CHECK (
        support_score_delta IS NULL
        OR support_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_relationship_resilience_score
    CHECK (
        resilience_score_delta IS NULL
        OR resilience_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_relationship_support_balance_side
    CHECK (
        support_balance_side IS NULL
        OR support_balance_side IN (
            'GIVEN',
            'RECEIVED',
            'MUTUAL'
        )
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_support_moment
ON personal_relationship_support_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_support_user
ON personal_relationship_support_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_support_date
ON personal_relationship_support_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_relationship_experience_events (
    relationship_experience_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    experience_type VARCHAR(80) NOT NULL,
    relationship_type VARCHAR(80) NOT NULL,

    cost_amount DECIMAL(14,2),
    spend_category VARCHAR(80),
    value_received VARCHAR(80) NOT NULL,

    note TEXT,

    connection_score_delta DECIMAL(5,2),
    relationship_roi_score DECIMAL(5,2),
    meaningful_moment_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_relationship_experience_type
    CHECK (
        experience_type IN (
            'Dining',
            'Travel',
            'Celebration',
            'Entertainment',
            'Activity',
            'Learning',
            'Family Event',
            'Milestone',
            'Other'
        )
    ),

    CONSTRAINT chk_relationship_experience_relationship_type
    CHECK (
        relationship_type IN (
            'Partner',
            'Family',
            'Friend',
            'Child',
            'Parent',
            'Group'
        )
    ),

    CONSTRAINT chk_relationship_experience_cost
    CHECK (
        cost_amount IS NULL
        OR cost_amount >= 0
    ),

    CONSTRAINT chk_relationship_experience_spend_category
    CHECK (
        spend_category IS NULL
        OR spend_category IN (
            'Dining',
            'Travel',
            'Gift',
            'Event',
            'Support',
            'Experience',
            'Other'
        )
    ),

    CONSTRAINT chk_relationship_experience_value
    CHECK (
        value_received IN (
            'Okay',
            'Worth It',
            'Excellent Value',
            'Relationship Building',
            'Life Enriching'
        )
    ),

    CONSTRAINT chk_relationship_experience_connection_score
    CHECK (
        connection_score_delta IS NULL
        OR connection_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_relationship_experience_roi_score
    CHECK (
        relationship_roi_score IS NULL
        OR relationship_roi_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_experience_moment
ON personal_relationship_experience_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_experience_user
ON personal_relationship_experience_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_experience_date
ON personal_relationship_experience_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_relationship_investment_events (
    investment_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    investment_type VARCHAR(80) NOT NULL,
    relationship_type VARCHAR(80) NOT NULL,

    amount DECIMAL(14,2) NOT NULL,
    investment_purpose VARCHAR(80) NOT NULL,
    perceived_value VARCHAR(50) NOT NULL,

    note TEXT,

    investment_score_delta DECIMAL(5,2),
    connection_roi_score DECIMAL(5,2),
    financial_support_flag BOOLEAN NOT NULL DEFAULT FALSE,

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_relationship_investment_type
    CHECK (
        investment_type IN (
            'Gift',
            'Support',
            'Education',
            'Travel',
            'Celebration',
            'Shared Goal',
            'Family Expense',
            'Contribution',
            'Other'
        )
    ),

    CONSTRAINT chk_relationship_investment_relationship_type
    CHECK (
        relationship_type IN (
            'Partner',
            'Family',
            'Friend',
            'Child',
            'Parent',
            'Group'
        )
    ),

    CONSTRAINT chk_relationship_investment_amount
    CHECK (amount >= 0),

    CONSTRAINT chk_relationship_investment_purpose
    CHECK (
        investment_purpose IN (
            'Care',
            'Growth',
            'Support',
            'Celebration',
            'Responsibility',
            'Shared Future'
        )
    ),

    CONSTRAINT chk_relationship_investment_perceived_value
    CHECK (
        perceived_value IN (
            'Low',
            'Moderate',
            'High',
            'Exceptional'
        )
    ),

    CONSTRAINT chk_relationship_investment_score
    CHECK (
        investment_score_delta IS NULL
        OR investment_score_delta BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_relationship_connection_roi_score
    CHECK (
        connection_roi_score IS NULL
        OR connection_roi_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_investment_moment
ON personal_relationship_investment_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_investment_user
ON personal_relationship_investment_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_investment_date
ON personal_relationship_investment_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_relationship_adjust_events (
    relationship_adjust_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL UNIQUE
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    relationship_focus VARCHAR(80) NOT NULL,
    adjustment_area VARCHAR(100) NOT NULL,
    priority_level VARCHAR(30) NOT NULL,
    confidence_level VARCHAR(30) NOT NULL,
    desired_outcome VARCHAR(100),

    note TEXT,

    connection_gap_score DECIMAL(5,2),
    relationship_readiness_score DECIMAL(5,2),
    recommended_connection_action VARCHAR(150),

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_relationship_adjust_focus
    CHECK (
        relationship_focus IN (
            'Partner',
            'Family',
            'Friend',
            'Parent',
            'Child'
        )
    ),

    CONSTRAINT chk_relationship_adjust_area
    CHECK (
        adjustment_area IN (
            'More Time Together',
            'Better Communication',
            'More Presence',
            'More Support',
            'More Fun',
            'More Shared Experiences',
            'More Appreciation',
            'More Consistency'
        )
    ),

    CONSTRAINT chk_relationship_adjust_priority
    CHECK (
        priority_level IN (
            'Low',
            'Medium',
            'High'
        )
    ),

    CONSTRAINT chk_relationship_adjust_confidence
    CHECK (
        confidence_level IN (
            'Not Sure',
            'Somewhat Sure',
            'Very Sure'
        )
    ),

    CONSTRAINT chk_relationship_desired_outcome
    CHECK (
        desired_outcome IS NULL
        OR desired_outcome IN (
            'Closer',
            'More Trust',
            'More Support',
            'More Fun',
            'More Consistency',
            'Better Communication'
        )
    ),

    CONSTRAINT chk_relationship_gap_score
    CHECK (
        connection_gap_score IS NULL
        OR connection_gap_score BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_relationship_readiness_score
    CHECK (
        relationship_readiness_score IS NULL
        OR relationship_readiness_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_adjust_moment
ON personal_relationship_adjust_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_adjust_user
ON personal_relationship_adjust_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_relationship_adjust_date
ON personal_relationship_adjust_events(event_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    account_name VARCHAR(120) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    currency_code VARCHAR(10) NOT NULL DEFAULT 'INR',

    opening_balance DECIMAL(14,2) DEFAULT 0,
    current_balance DECIMAL(14,2) NOT NULL DEFAULT 0,

    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_personal_account_type
    CHECK (
        account_type IN (
            'Cash',
            'Bank',
            'Wallet',
            'Credit Card',
            'Investment',
            'Custom'
        )
    ),

    CONSTRAINT chk_personal_account_opening_balance
    CHECK (opening_balance IS NULL OR opening_balance >= 0)
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_accounts_user
ON personal_accounts(user_id);
-- >>>STMT<<<
CREATE UNIQUE INDEX IF NOT EXISTS uq_personal_default_account
ON personal_accounts(user_id)
WHERE is_default = TRUE;
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_categories (
    category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NULL,

    moment_type_code VARCHAR(50) NOT NULL,
    category_group VARCHAR(80) NOT NULL,
    category_code VARCHAR(80) NOT NULL,
    category_name VARCHAR(120) NOT NULL,

    display_order INT DEFAULT 0,
    is_money_category BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_personal_category_moment_type
    CHECK (
        moment_type_code IN (
            'ALL',
            'LIFE_OPERATIONS',
            'FUTURE_BUILDING',
            'LIFESTYLE',
            'RELATIONSHIPS'
        )
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_categories_scope
ON personal_categories(moment_type_code, category_group);
-- >>>STMT<<<
CREATE UNIQUE INDEX IF NOT EXISTS uq_personal_categories_code_scope
ON personal_categories(
    COALESCE(user_id, '00000000-0000-0000-0000-000000000000'::uuid),
    moment_type_code,
    category_group,
    category_code
);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_money_events (
    money_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id),

    user_id UUID NOT NULL,

    moment_type_code VARCHAR(50) NOT NULL,
    source_event_type VARCHAR(80) NOT NULL,
    linked_event_id UUID NOT NULL,

    money_event_type VARCHAR(50) NOT NULL,

    amount DECIMAL(14,2) NOT NULL,
    currency_code VARCHAR(10) NOT NULL DEFAULT 'INR',
    category_code VARCHAR(80) NOT NULL,

    account_id UUID NULL
        REFERENCES personal_accounts(account_id),

    direction VARCHAR(20) NOT NULL,

    impact_label VARCHAR(80),
    value_received_label VARCHAR(80),

    financial_pressure_score DECIMAL(5,2),
    investment_score DECIMAL(5,2),
    roi_signal_score DECIMAL(5,2),

    event_date DATE NOT NULL DEFAULT CURRENT_DATE,

    is_voided BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_personal_money_moment_type
    CHECK (
        moment_type_code IN (
            'LIFE_OPERATIONS',
            'FUTURE_BUILDING',
            'LIFESTYLE',
            'RELATIONSHIPS'
        )
    ),

    CONSTRAINT chk_personal_money_event_type
    CHECK (
        money_event_type IN (
            'EXPENSE',
            'INCOME',
            'TRANSFER',
            'CONTRIBUTION',
            'SAVINGS',
            'INVESTMENT',
            'SUPPORT',
            'GIFT',
            'SHARED_EXPERIENCE_COST'
        )
    ),

    CONSTRAINT chk_personal_money_amount
    CHECK (amount >= 0),

    CONSTRAINT chk_personal_money_direction
    CHECK (
        direction IN (
            'CREDIT',
            'DEBIT',
            'NEUTRAL'
        )
    ),

    CONSTRAINT chk_personal_money_financial_pressure_score
    CHECK (
        financial_pressure_score IS NULL
        OR financial_pressure_score BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_personal_money_investment_score
    CHECK (
        investment_score IS NULL
        OR investment_score BETWEEN 0 AND 100
    ),

    CONSTRAINT chk_personal_money_roi_score
    CHECK (
        roi_signal_score IS NULL
        OR roi_signal_score BETWEEN 0 AND 100
    )
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_money_events_user
ON personal_money_events(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_money_events_moment
ON personal_money_events(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_money_events_quick_add
ON personal_money_events(quick_add_event_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_money_events_type
ON personal_money_events(moment_type_code, money_event_type);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_money_events_date
ON personal_money_events(event_date);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_money_events_account
ON personal_money_events(account_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_runtime_snapshots (
    runtime_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    moment_type_code VARCHAR(50) NOT NULL,
    runtime_state_label VARCHAR(120) NOT NULL,
    runtime_summary TEXT,
    primary_score DECIMAL(5,2) NOT NULL,
    secondary_score DECIMAL(5,2),
    risk_or_gap_label VARCHAR(150),
    trend_direction VARCHAR(30) NOT NULL DEFAULT 'STABLE',
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IN ('LIFE_OPERATIONS','FUTURE_BUILDING','LIFESTYLE','RELATIONSHIPS')),
    CHECK (primary_score BETWEEN 0 AND 100),
    CHECK (secondary_score IS NULL OR secondary_score BETWEEN 0 AND 100),
    CHECK (trend_direction IN ('UP','DOWN','STABLE'))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_runtime_snapshots_moment_date
ON personal_runtime_snapshots(moment_id, snapshot_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_pulse_snapshots (
    pulse_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    moment_id UUID REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
    moment_type_code VARCHAR(50),
    pulse_title VARCHAR(150) NOT NULL,
    pulse_summary TEXT,
    primary_metric_label VARCHAR(100) NOT NULL,
    primary_metric_value DECIMAL(5,2) NOT NULL,
    secondary_metrics JSONB,
    emerging_signal_label VARCHAR(150),
    opportunity_label VARCHAR(150),
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IS NULL OR moment_type_code IN ('LIFE_OPERATIONS','FUTURE_BUILDING','LIFESTYLE','RELATIONSHIPS')),
    CHECK (primary_metric_value BETWEEN 0 AND 100)
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_pulse_snapshots_user_date
ON personal_pulse_snapshots(user_id, snapshot_date);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_pulse_snapshots_moment
ON personal_pulse_snapshots(moment_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_live_priorities (
    live_priority_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    moment_type_code VARCHAR(50) NOT NULL,
    priority_title VARCHAR(150) NOT NULL,
    priority_reason TEXT,
    recommended_action_label VARCHAR(150) NOT NULL,
    expected_impact_json JSONB,
    recent_activity_json JSONB,
    quick_actions_json JSONB,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IN ('LIFE_OPERATIONS','FUTURE_BUILDING','LIFESTYLE','RELATIONSHIPS'))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_live_priorities_moment_current
ON personal_live_priorities(moment_id, is_current);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_memory_patterns (
    memory_pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    moment_type_code VARCHAR(50) NOT NULL,
    pattern_type VARCHAR(80) NOT NULL,
    pattern_title VARCHAR(150) NOT NULL,
    pattern_description TEXT NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL,
    supporting_event_count INT NOT NULL DEFAULT 0,
    contribution_breakdown_json JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IN ('LIFE_OPERATIONS','FUTURE_BUILDING','LIFESTYLE','RELATIONSHIPS')),
    CHECK (confidence_score BETWEEN 0 AND 100),
    CHECK (supporting_event_count >= 0)
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_patterns_moment_active
ON personal_memory_patterns(moment_id, is_active);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_insights (
    insight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    moment_id UUID REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
    moment_type_code VARCHAR(50),
    insight_scope VARCHAR(50) NOT NULL,
    insight_type VARCHAR(80) NOT NULL,
    insight_title VARCHAR(150) NOT NULL,
    insight_text TEXT NOT NULL,
    severity_level VARCHAR(30),
    recommended_action VARCHAR(150),
    source_metric_json JSONB,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IS NULL OR moment_type_code IN ('LIFE_OPERATIONS','FUTURE_BUILDING','LIFESTYLE','RELATIONSHIPS')),
    CHECK (insight_scope IN ('PULSE','LIVE','MEMORY','DETAIL','GLOBAL')),
    CHECK (severity_level IS NULL OR severity_level IN ('LOW','MEDIUM','HIGH','POSITIVE'))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_insights_moment_scope
ON personal_insights(moment_id, insight_scope, is_active);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_metric_snapshots (
    metric_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    moment_id UUID NOT NULL REFERENCES personal_moments(moment_id) ON DELETE CASCADE,
    moment_type_code VARCHAR(50) NOT NULL,
    metric_code VARCHAR(80) NOT NULL,
    metric_label VARCHAR(120) NOT NULL,
    metric_value DECIMAL(5,2) NOT NULL,
    metric_delta DECIMAL(5,2),
    trend_direction VARCHAR(30),
    measurement_period VARCHAR(30) NOT NULL DEFAULT 'DAILY',
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IN ('LIFE_OPERATIONS','FUTURE_BUILDING','LIFESTYLE','RELATIONSHIPS')),
    CHECK (metric_value BETWEEN 0 AND 100),
    CHECK (trend_direction IS NULL OR trend_direction IN ('UP','DOWN','STABLE')),
    CHECK (measurement_period IN ('DAILY','WEEKLY','MONTHLY'))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_metric_snapshots_moment_metric_date
ON personal_metric_snapshots(moment_id, metric_code, snapshot_date);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_activity_timeline (
    timeline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id)
        ON DELETE CASCADE,

    user_id UUID NOT NULL,
    moment_type_code VARCHAR(50) NOT NULL,
    event_type VARCHAR(80) NOT NULL,

    display_title VARCHAR(150) NOT NULL,
    display_subtitle VARCHAR(250),
    display_amount DECIMAL(14,2),
    impact_labels_json JSONB,

    event_occurred_at TIMESTAMP NOT NULL,

    is_editable BOOLEAN NOT NULL DEFAULT TRUE,
    is_voided BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IN (
        'LIFE_OPERATIONS',
        'FUTURE_BUILDING',
        'LIFESTYLE',
        'RELATIONSHIPS'
    ))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_timeline_moment_date
ON personal_activity_timeline(moment_id, event_occurred_at DESC);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_timeline_user
ON personal_activity_timeline(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_timeline_event_type
ON personal_activity_timeline(moment_type_code, event_type);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_event_edits (
    edit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id)
        ON DELETE CASCADE,

    user_id UUID NOT NULL,

    edited_table_name VARCHAR(120) NOT NULL,
    edited_record_id UUID NOT NULL,

    before_payload JSONB NOT NULL,
    after_payload JSONB NOT NULL,
    changed_fields TEXT[],

    edit_reason VARCHAR(250),
    requires_recalculation BOOLEAN NOT NULL DEFAULT TRUE,
    recalculated_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_event_edits_event
ON personal_event_edits(quick_add_event_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_event_edits_moment
ON personal_event_edits(moment_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_event_voids (
    void_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    quick_add_event_id UUID NOT NULL
        REFERENCES personal_quick_add_events(quick_add_event_id)
        ON DELETE CASCADE,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id)
        ON DELETE CASCADE,

    user_id UUID NOT NULL,

    voided_table_name VARCHAR(120) NOT NULL,
    voided_record_id UUID NOT NULL,

    void_reason VARCHAR(250),
    void_payload JSONB NOT NULL,

    reversal_allowed BOOLEAN NOT NULL DEFAULT TRUE,
    undo_expires_at TIMESTAMP,
    restored_at TIMESTAMP,

    requires_recalculation BOOLEAN NOT NULL DEFAULT TRUE,
    recalculated_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_event_voids_event
ON personal_event_voids(quick_add_event_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_event_voids_moment
ON personal_event_voids(moment_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_notification_queue (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    moment_id UUID
        REFERENCES personal_moments(moment_id)
        ON DELETE CASCADE,

    moment_type_code VARCHAR(50),

    notification_type VARCHAR(80) NOT NULL,

    title VARCHAR(150) NOT NULL,
    body TEXT NOT NULL,
    deep_link_target VARCHAR(150),

    priority_level VARCHAR(30) NOT NULL DEFAULT 'MEDIUM',

    scheduled_for TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,

    status VARCHAR(30) NOT NULL DEFAULT 'QUEUED',
    metadata_json JSONB,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        moment_type_code IS NULL
        OR moment_type_code IN (
            'LIFE_OPERATIONS',
            'FUTURE_BUILDING',
            'LIFESTYLE',
            'RELATIONSHIPS'
        )
    ),

    CHECK (priority_level IN ('LOW', 'MEDIUM', 'HIGH')),

    CHECK (status IN ('QUEUED', 'SENT', 'FAILED', 'CANCELLED'))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_notification_user_status
ON personal_notification_queue(user_id, status);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_notification_scheduled
ON personal_notification_queue(scheduled_for, status);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_user_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL UNIQUE,

    default_currency_code VARCHAR(10) NOT NULL DEFAULT 'INR',
    timezone_name VARCHAR(100) NOT NULL DEFAULT 'Asia/Kolkata',
    week_start_day VARCHAR(20) DEFAULT 'MONDAY',

    default_account_id UUID
        REFERENCES personal_accounts(account_id),

    notification_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    quick_add_reminder_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    daily_summary_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    preferred_summary_time TIME,

    privacy_mode_enabled BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (week_start_day IN ('MONDAY', 'SUNDAY'))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_user_preferences_user
ON personal_user_preferences(user_id);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_signals (
    signal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id)
        ON DELETE CASCADE,

    moment_type_code VARCHAR(50) NOT NULL,

    signal_type VARCHAR(100) NOT NULL,
    signal_title VARCHAR(150) NOT NULL,
    signal_description TEXT NOT NULL,

    signal_score DECIMAL(5,2) NOT NULL,
    severity_level VARCHAR(30) NOT NULL,
    trend_direction VARCHAR(30),

    source_metric_code VARCHAR(100),
    source_metric_delta DECIMAL(8,2),
    source_event_count INT NOT NULL DEFAULT 0,
    signal_window VARCHAR(50) NOT NULL DEFAULT '30D',

    source_payload JSONB,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    expires_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IN (
        'LIFE_OPERATIONS',
        'FUTURE_BUILDING',
        'LIFESTYLE',
        'RELATIONSHIPS'
    )),

    CHECK (signal_score BETWEEN 0 AND 100),

    CHECK (severity_level IN (
        'LOW',
        'MEDIUM',
        'HIGH',
        'POSITIVE',
        'WARNING'
    )),

    CHECK (
        trend_direction IS NULL
        OR trend_direction IN ('UP', 'DOWN', 'STABLE')
    ),

    CHECK (source_event_count >= 0),

    CHECK (signal_window IN ('7D', '14D', '30D', '90D'))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_signals_moment_active
ON personal_signals(moment_id, is_active);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_signals_user_active
ON personal_signals(user_id, is_active);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_signals_type
ON personal_signals(moment_type_code, signal_type);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    moment_id UUID NOT NULL
        REFERENCES personal_moments(moment_id)
        ON DELETE CASCADE,

    moment_type_code VARCHAR(50) NOT NULL,

    recommendation_type VARCHAR(100) NOT NULL,
    recommendation_title VARCHAR(150) NOT NULL,
    recommendation_description TEXT NOT NULL,
    recommended_action VARCHAR(200) NOT NULL,

    expected_impact_json JSONB,

    confidence_score DECIMAL(5,2) NOT NULL,
    priority_score DECIMAL(5,2) NOT NULL,

    source_signal_id UUID
        REFERENCES personal_signals(signal_id),

    source_pattern_id UUID
        REFERENCES personal_memory_patterns(memory_pattern_id),

    status VARCHAR(30) NOT NULL DEFAULT 'ACTIVE',

    acted_at TIMESTAMP,
    dismissed_at TIMESTAMP,
    expires_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (moment_type_code IN (
        'LIFE_OPERATIONS',
        'FUTURE_BUILDING',
        'LIFESTYLE',
        'RELATIONSHIPS'
    )),

    CHECK (confidence_score BETWEEN 0 AND 100),
    CHECK (priority_score BETWEEN 0 AND 100),

    CHECK (status IN (
        'ACTIVE',
        'DONE',
        'DISMISSED',
        'EXPIRED'
    ))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_recommendations_moment_status
ON personal_recommendations(moment_id, status);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_recommendations_user_status
ON personal_recommendations(user_id, status);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_recommendations_priority
ON personal_recommendations(priority_score DESC);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_ai_interpretation_runs (
    run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    moment_id UUID
        REFERENCES personal_moments(moment_id)
        ON DELETE CASCADE,

    moment_type_code VARCHAR(50),

    run_type VARCHAR(80) NOT NULL,

    input_payload JSONB NOT NULL,
    output_payload JSONB,
    records_created_json JSONB,

    status VARCHAR(30) NOT NULL DEFAULT 'QUEUED',

    error_message TEXT,

    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (
        moment_type_code IS NULL
        OR moment_type_code IN (
            'LIFE_OPERATIONS',
            'FUTURE_BUILDING',
            'LIFESTYLE',
            'RELATIONSHIPS'
        )
    ),

    CHECK (run_type IN (
        'SIGNAL_REFRESH',
        'RECOMMENDATION_REFRESH',
        'MEMORY_REFRESH',
        'FULL_REFRESH'
    )),

    CHECK (status IN (
        'QUEUED',
        'RUNNING',
        'COMPLETED',
        'FAILED',
        'SKIPPED'
    ))
);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_ai_runs_user
ON personal_ai_interpretation_runs(user_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_ai_runs_moment
ON personal_ai_interpretation_runs(moment_id);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_ai_runs_status
ON personal_ai_interpretation_runs(status);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_ai_runs_type
ON personal_ai_interpretation_runs(run_type);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_memory_identity_snapshots (
																
																    identity_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id)
																        ON DELETE CASCADE,
																
																    moment_type_code VARCHAR(50) NOT NULL,
																
																    identity_title VARCHAR(100) NOT NULL,
																
																    confidence_pct DECIMAL(5,2) NOT NULL,
																
																    confidence_trend_pct DECIMAL(5,2),
																
																    identity_summary TEXT,
																
																    identity_visual_type VARCHAR(50),
																
																    snapshot_month DATE NOT NULL,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (confidence_pct BETWEEN 0 AND 100),
																
																    CHECK (
																        confidence_trend_pct IS NULL
																        OR confidence_trend_pct BETWEEN -100 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_identity_user_type_current
																ON personal_memory_identity_snapshots(
																    user_id,
																    moment_type_code,
																    is_current
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_identity_moment
																ON personal_memory_identity_snapshots(moment_id);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_memory_identity_updated_at
																ON personal_memory_identity_snapshots;
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_memory_driver_rankings (
																
																    driver_ranking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id)
																        ON DELETE CASCADE,
																
																    moment_type_code VARCHAR(50) NOT NULL,
																
																    driver_category VARCHAR(50) NOT NULL,
																
																    driver_rank INT NOT NULL,
																
																    driver_name VARCHAR(100) NOT NULL,
																
																    impact_pct DECIMAL(5,2),
																
																    impact_description TEXT,
																
																    return_multiplier DECIMAL(8,2),
																
																    snapshot_month DATE NOT NULL,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (
																        driver_category IN (
																            'POSITIVE',
																            'NEGATIVE',
																            'HIGHEST_RETURN',
																            'FULFILLMENT_DRIVER',
																            'GROWTH_DRIVER',
																            'CONNECTION_DRIVER',
																            'CAPACITY_DRIVER'
																        )
																    ),
																
																    CHECK (driver_rank > 0),
																
																    CHECK (
																        impact_pct IS NULL
																        OR impact_pct BETWEEN 0 AND 100
																    ),
																
																    CHECK (
																        return_multiplier IS NULL
																        OR return_multiplier >= 0
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_driver_user_type_current
																ON personal_memory_driver_rankings(
																    user_id,
																    moment_type_code,
																    driver_category,
																    is_current
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_driver_moment
																ON personal_memory_driver_rankings(moment_id);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_memory_driver_rankings_updated_at
																ON personal_memory_driver_rankings;
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_memory_emotional_dna (
																
																    emotional_dna_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    moment_id UUID
																        REFERENCES personal_moments(moment_id)
																        ON DELETE CASCADE,
																
																    moment_type_code VARCHAR(50),
																
																    emotion_name VARCHAR(50) NOT NULL,
																
																    emotion_pct DECIMAL(5,2) NOT NULL,
																
																    emotion_rank INT NOT NULL,
																
																    dna_summary TEXT,
																
																    snapshot_month DATE NOT NULL,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        moment_type_code IS NULL
																        OR moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (emotion_pct BETWEEN 0 AND 100),
																
																    CHECK (emotion_rank > 0)
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_emotional_user_current
																ON personal_memory_emotional_dna(
																    user_id,
																    moment_type_code,
																    is_current
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_emotional_moment
																ON personal_memory_emotional_dna(moment_id);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_memory_emotional_dna_updated_at
																ON personal_memory_emotional_dna;
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_memory_evolution_snapshots (
																
																    evolution_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id)
																        ON DELETE CASCADE,
																
																    moment_type_code VARCHAR(50) NOT NULL,
																
																    previous_stage VARCHAR(100) NOT NULL,
																
																    current_stage VARCHAR(100) NOT NULL,
																
																    emerging_stage VARCHAR(100),
																
																    evolution_confidence_pct DECIMAL(5,2),
																
																    transition_date DATE NOT NULL,
																
																    snapshot_month DATE NOT NULL,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (
																        evolution_confidence_pct IS NULL
																        OR evolution_confidence_pct BETWEEN 0 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_evolution_user_type_current
																ON personal_memory_evolution_snapshots(
																    user_id,
																    moment_type_code,
																    is_current
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_evolution_moment
																ON personal_memory_evolution_snapshots(moment_id);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_memory_evolution_updated_at
																ON personal_memory_evolution_snapshots;
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_moment_highlights (
																
																    moment_highlight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id)
																        ON DELETE CASCADE,
																
																    moment_type_code VARCHAR(50) NOT NULL,
																
																    source_event_id UUID,
																
																    source_event_type VARCHAR(100),
																
																    highlight_title VARCHAR(150) NOT NULL,
																
																    highlight_type VARCHAR(80) NOT NULL,
																
																    impact_label VARCHAR(150),
																
																    impact_score DECIMAL(5,2),
																
																    amount DECIMAL(14,2),
																
																    occurred_at TIMESTAMP NOT NULL,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (
																        impact_score IS NULL
																        OR impact_score BETWEEN 0 AND 100
																    ),
																
																    CHECK (
																        amount IS NULL
																        OR amount >= 0
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_moment_highlights_moment_current
																ON personal_moment_highlights(moment_id, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_moment_highlights_user_type
																ON personal_moment_highlights(user_id, moment_type_code);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_moment_highlights_occurred_at
																ON personal_moment_highlights(occurred_at DESC);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_moment_turning_points (
																
																    turning_point_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    moment_id UUID NOT NULL
																        REFERENCES personal_moments(moment_id)
																        ON DELETE CASCADE,
																
																    moment_type_code VARCHAR(50) NOT NULL,
																
																    source_event_id UUID,
																
																    source_event_type VARCHAR(100),
																
																    turning_point_title VARCHAR(150) NOT NULL,
																
																    turning_point_type VARCHAR(80) NOT NULL,
																
																    turning_point_description TEXT,
																
																    impact_score DECIMAL(5,2),
																
																    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    occurred_at TIMESTAMP,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (
																        impact_score IS NULL
																        OR impact_score BETWEEN 0 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_moment_turning_points_moment_current
																ON personal_moment_turning_points(moment_id, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_moment_turning_points_user_type
																ON personal_moment_turning_points(user_id, moment_type_code);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_moment_turning_points_occurred_at
																ON personal_moment_turning_points(occurred_at DESC);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_health_snapshots (
																
																    life_health_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    life_health_score DECIMAL(5,2) NOT NULL,
																
																    health_status_label VARCHAR(100) NOT NULL,
																
																    monthly_delta_score DECIMAL(5,2),
																
																    summary_text TEXT,
																
																    snapshot_month DATE NOT NULL,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (life_health_score BETWEEN 0 AND 100),
																
																    CHECK (
																        monthly_delta_score IS NULL
																        OR monthly_delta_score BETWEEN -100 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_health_user_current
																ON personal_life_health_snapshots(user_id, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_health_user_month
																ON personal_life_health_snapshots(user_id, snapshot_month);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_dimension_scores (
																
																    life_dimension_score_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    dimension_code VARCHAR(50) NOT NULL,
																
																    dimension_label VARCHAR(100) NOT NULL,
																
																    dimension_score DECIMAL(5,2) NOT NULL,
																
																    status_label VARCHAR(100) NOT NULL,
																
																    driver_summary TEXT,
																
																    trend_direction VARCHAR(20),
																
																    snapshot_month DATE NOT NULL,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        dimension_code IN (
																            'STRESS',
																            'CAPACITY',
																            'GROWTH',
																            'FULFILLMENT'
																        )
																    ),
																
																    CHECK (dimension_score BETWEEN 0 AND 100),
																
																    CHECK (
																        trend_direction IS NULL
																        OR trend_direction IN ('UP','DOWN','STABLE')
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_dimension_user_current
																ON personal_life_dimension_scores(user_id, dimension_code, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_dimension_user_month
																ON personal_life_dimension_scores(user_id, snapshot_month);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_connections (
																
																    life_connection_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    source_moment_type_code VARCHAR(50) NOT NULL,
																
																    target_moment_type_code VARCHAR(50) NOT NULL,
																
																    connection_title VARCHAR(150) NOT NULL,
																
																    connection_summary TEXT NOT NULL,
																
																    signal_label VARCHAR(80) NOT NULL,
																
																    connection_strength_pct DECIMAL(5,2),
																
																    snapshot_month DATE NOT NULL,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        source_moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (
																        target_moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (
																        connection_strength_pct IS NULL
																        OR connection_strength_pct BETWEEN 0 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_connections_user_current
																ON personal_life_connections(user_id, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_connections_user_month
																ON personal_life_connections(user_id, snapshot_month);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_drift_alerts (
																
																    life_drift_alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    drift_title VARCHAR(150) NOT NULL,
																
																    rising_dimension_code VARCHAR(50),
																
																    falling_dimension_code VARCHAR(50),
																
																    drift_message TEXT NOT NULL,
																
																    severity_level VARCHAR(30) NOT NULL,
																
																    recommended_action VARCHAR(200),
																
																    is_active BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        rising_dimension_code IS NULL
																        OR rising_dimension_code IN (
																            'STRESS',
																            'CAPACITY',
																            'GROWTH',
																            'FULFILLMENT'
																        )
																    ),
																
																    CHECK (
																        falling_dimension_code IS NULL
																        OR falling_dimension_code IN (
																            'STRESS',
																            'CAPACITY',
																            'GROWTH',
																            'FULFILLMENT'
																        )
																    ),
																
																    CHECK (severity_level IN ('LOW','MEDIUM','HIGH'))
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_drift_user_active
																ON personal_life_drift_alerts(user_id, is_active);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_monthly_changes (
																
																    life_monthly_change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    change_label VARCHAR(150) NOT NULL,
																
																    change_value_pct DECIMAL(5,2) NOT NULL,
																
																    direction VARCHAR(20) NOT NULL,
																
																    moment_type_code VARCHAR(50),
																
																    dimension_code VARCHAR(50),
																
																    snapshot_month DATE NOT NULL,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (change_value_pct BETWEEN -100 AND 100),
																
																    CHECK (direction IN ('UP','DOWN','STABLE')),
																
																    CHECK (
																        moment_type_code IS NULL
																        OR moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (
																        dimension_code IS NULL
																        OR dimension_code IN (
																            'STRESS',
																            'CAPACITY',
																            'GROWTH',
																            'FULFILLMENT'
																        )
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_monthly_changes_user_month
																ON personal_life_monthly_changes(user_id, snapshot_month);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_journey_events (
																
																    life_journey_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    journey_month DATE NOT NULL,
																
																    journey_title VARCHAR(150) NOT NULL,
																
																    journey_description TEXT,
																
																    source_moment_type_code VARCHAR(50),
																
																    source_dimension_code VARCHAR(50),
																
																    importance_score DECIMAL(5,2),
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (
																        source_moment_type_code IS NULL
																        OR source_moment_type_code IN (
																            'LIFE_OPERATIONS',
																            'FUTURE_BUILDING',
																            'LIFESTYLE',
																            'RELATIONSHIPS'
																        )
																    ),
																
																    CHECK (
																        source_dimension_code IS NULL
																        OR source_dimension_code IN (
																            'STRESS',
																            'CAPACITY',
																            'GROWTH',
																            'FULFILLMENT'
																        )
																    ),
																
																    CHECK (
																        importance_score IS NULL
																        OR importance_score BETWEEN 0 AND 100
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_journey_user_month
																ON personal_life_journey_events(user_id, journey_month);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS personal_life_aggregate_snapshots (
																
																    life_aggregate_snapshot_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
																
																    user_id UUID NOT NULL,
																
																    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
																
																    snapshot_month DATE NOT NULL,
																
																    life_health_score DECIMAL(5,2) NOT NULL,
																
																    stability_score DECIMAL(5,2) NOT NULL,
																
																    growth_score DECIMAL(5,2) NOT NULL,
																
																    fulfillment_score DECIMAL(5,2) NOT NULL,
																
																    relationship_health_score DECIMAL(5,2) NOT NULL,
																
																    stress_score DECIMAL(5,2) NOT NULL,
																
																    capacity_score DECIMAL(5,2) NOT NULL,
																
																    growth_dimension_score DECIMAL(5,2) NOT NULL,
																
																    fulfillment_dimension_score DECIMAL(5,2) NOT NULL,
																
																    dominant_emotion VARCHAR(50),
																
																    dominant_emotion_pct DECIMAL(5,2),
																
																    emotional_momentum_score DECIMAL(5,2),
																
																    drift_score DECIMAL(5,2),
																
																    drift_status VARCHAR(50),
																
																    leverage_score DECIMAL(5,2),
																
																    leverage_area VARCHAR(100),
																
																    happiness_driver VARCHAR(100),
																
																    happiness_driver_score DECIMAL(8,2),
																
																    life_stage VARCHAR(100),
																
																    life_intelligence_summary TEXT,
																
																    is_current BOOLEAN NOT NULL DEFAULT TRUE,
																
																    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
																
																    CHECK (life_health_score BETWEEN 0 AND 100),
																
																    CHECK (stability_score BETWEEN 0 AND 100),
																
																    CHECK (growth_score BETWEEN 0 AND 100),
																
																    CHECK (fulfillment_score BETWEEN 0 AND 100),
																
																    CHECK (relationship_health_score BETWEEN 0 AND 100),
																
																    CHECK (stress_score BETWEEN 0 AND 100),
																
																    CHECK (capacity_score BETWEEN 0 AND 100),
																
																    CHECK (growth_dimension_score BETWEEN 0 AND 100),
																
																    CHECK (fulfillment_dimension_score BETWEEN 0 AND 100),
																
																    CHECK (
																        dominant_emotion_pct IS NULL
																        OR dominant_emotion_pct BETWEEN 0 AND 100
																    ),
																
																    CHECK (
																        emotional_momentum_score IS NULL
																        OR emotional_momentum_score BETWEEN -100 AND 100
																    ),
																
																    CHECK (
																        drift_score IS NULL
																        OR drift_score >= 0
																    ),
																
																    CHECK (
																        drift_status IS NULL
																        OR drift_status IN ('LOW','MEDIUM','HIGH')
																    ),
																
																    CHECK (
																        leverage_score IS NULL
																        OR leverage_score >= 0
																    ),
																
																    CHECK (
																        happiness_driver_score IS NULL
																        OR happiness_driver_score >= 0
																    )
																);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_aggregate_user_current
																ON personal_life_aggregate_snapshots(user_id, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_aggregate_user_month
																ON personal_life_aggregate_snapshots(user_id, snapshot_month);
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_life_aggregate_updated_at
																ON personal_life_aggregate_snapshots;
-- >>>STMT<<<
ALTER TABLE personal_recommendations
																    ALTER COLUMN moment_id DROP NOT NULL;
-- >>>STMT<<<
ALTER TABLE personal_recommendations
																    ALTER COLUMN moment_type_code DROP NOT NULL;
-- >>>STMT<<<
ALTER TABLE personal_recommendations
																    ADD COLUMN IF NOT EXISTS recommendation_scope VARCHAR(50) NOT NULL DEFAULT 'MOMENT';
-- >>>STMT<<<
ALTER TABLE personal_recommendations
																    ADD COLUMN IF NOT EXISTS growth_edge_multiplier DECIMAL(8,2);
-- >>>STMT<<<
ALTER TABLE personal_recommendations
																    ADD COLUMN IF NOT EXISTS growth_edge_confidence_pct DECIMAL(5,2);
-- >>>STMT<<<
ALTER TABLE personal_recommendations
																    ADD COLUMN IF NOT EXISTS life_impact_json JSONB;
-- >>>STMT<<<
DO $$
																BEGIN
																    IF NOT EXISTS (
																        SELECT 1
																        FROM pg_constraint
																        WHERE conname = 'chk_personal_recommendation_scope'
																    ) THEN
																        ALTER TABLE personal_recommendations
																        ADD CONSTRAINT chk_personal_recommendation_scope
																        CHECK (
																            recommendation_scope IN (
																                'MOMENT',
																                'PULSE',
																                'MEMORY',
																                'LIFE'
																            )
																        );
																    END IF;
																
																    IF NOT EXISTS (
																        SELECT 1
																        FROM pg_constraint
																        WHERE conname = 'chk_personal_growth_edge_multiplier'
																    ) THEN
																        ALTER TABLE personal_recommendations
																        ADD CONSTRAINT chk_personal_growth_edge_multiplier
																        CHECK (
																            growth_edge_multiplier IS NULL
																            OR growth_edge_multiplier >= 0
																        );
																    END IF;
																
																    IF NOT EXISTS (
																        SELECT 1
																        FROM pg_constraint
																        WHERE conname = 'chk_personal_growth_edge_confidence'
																    ) THEN
																        ALTER TABLE personal_recommendations
																        ADD CONSTRAINT chk_personal_growth_edge_confidence
																        CHECK (
																            growth_edge_confidence_pct IS NULL
																            OR growth_edge_confidence_pct BETWEEN 0 AND 100
																        );
																    END IF;
																END $$;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_recommendations_scope
																ON personal_recommendations(user_id, recommendation_scope, status);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_personal_recommendations_life_scope
																ON personal_recommendations(user_id, recommendation_scope)
																WHERE recommendation_scope = 'LIFE';
-- >>>STMT<<<
ALTER TABLE personal_memory_patterns
																    ADD COLUMN IF NOT EXISTS pattern_confidence_pct DECIMAL(5,2);
-- >>>STMT<<<
ALTER TABLE personal_memory_patterns
																    ADD COLUMN IF NOT EXISTS pattern_explanation TEXT;
-- >>>STMT<<<
DO $$
																BEGIN
																    IF NOT EXISTS (
																        SELECT 1
																        FROM pg_constraint
																        WHERE conname = 'chk_personal_memory_pattern_confidence_pct'
																    ) THEN
																        ALTER TABLE personal_memory_patterns
																        ADD CONSTRAINT chk_personal_memory_pattern_confidence_pct
																        CHECK (
																            pattern_confidence_pct IS NULL
																            OR pattern_confidence_pct BETWEEN 0 AND 100
																        );
																    END IF;
																END $$;
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_health_current_month
																ON personal_life_health_snapshots(user_id, snapshot_month, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_life_dimension_current_month
																ON personal_life_dimension_scores(user_id, snapshot_month, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_identity_current_month
																ON personal_memory_identity_snapshots(user_id, snapshot_month, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_driver_current_month
																ON personal_memory_driver_rankings(user_id, snapshot_month, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_emotional_current_month
																ON personal_memory_emotional_dna(user_id, snapshot_month, is_current);
-- >>>STMT<<<
CREATE INDEX IF NOT EXISTS idx_memory_evolution_current_month
																ON personal_memory_evolution_snapshots(user_id, snapshot_month, is_current);
-- >>>STMT<<<
DROP INDEX IF EXISTS idx_live_priorities_moment_current;
-- >>>STMT<<<
CREATE UNIQUE INDEX IF NOT EXISTS uq_personal_live_priorities_current
ON personal_live_priorities(moment_id)
WHERE is_current = TRUE;

CREATE UNLOGGED TABLE IF NOT EXISTS mom_migration_skips (id serial PRIMARY KEY, migration text NOT NULL, seq int NOT NULL, error text, sql text, recorded_at timestamptz DEFAULT now())
-- >>>STMT<<<
CREATE EXTENSION IF NOT EXISTS pgcrypto
-- >>>STMT<<<
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- >>>STMT<<<
ALTER TABLE users ADD COLUMN IF NOT EXISTS user_id UUID GENERATED ALWAYS AS (id) STORED
-- >>>STMT<<<
CREATE UNIQUE INDEX IF NOT EXISTS uq_users_user_id ON users(user_id)

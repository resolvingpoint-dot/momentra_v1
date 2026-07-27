DROP INDEX IF EXISTS uq_users_user_id
-- >>>STMT<<<
ALTER TABLE users DROP COLUMN IF EXISTS user_id
-- >>>STMT<<<
DROP TABLE IF EXISTS mom_migration_skips

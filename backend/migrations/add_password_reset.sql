-- ============================================================
-- Migración: Reset de contraseña
-- Tabla afectada: users
-- ============================================================

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS password_reset_token   VARCHAR(128) UNIQUE,
    ADD COLUMN IF NOT EXISTS password_reset_expires  TIMESTAMP WITH TIME ZONE;

CREATE INDEX IF NOT EXISTS ix_users_password_reset_token ON users (password_reset_token);

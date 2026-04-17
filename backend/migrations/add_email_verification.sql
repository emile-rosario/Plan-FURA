-- ============================================================
-- Migración: Verificación de email
-- Tabla afectada: users
-- Ejecutar en psql o cualquier cliente PostgreSQL
-- ============================================================

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS email_verified    BOOLEAN     NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS verification_token VARCHAR(128) UNIQUE;

-- Marcar usuarios existentes como verificados para no bloquearlos
UPDATE users SET email_verified = TRUE WHERE email_verified = FALSE;

-- Índice opcional para búsqueda rápida por token
CREATE INDEX IF NOT EXISTS ix_users_verification_token ON users (verification_token);

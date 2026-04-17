-- ============================================================
-- Migración: campos adjunto en contacto y cédula en suscripciones
-- ============================================================

ALTER TABLE mensajes_contacto
    ADD COLUMN IF NOT EXISTS archivo_adjunto VARCHAR(500);

ALTER TABLE suscripciones
    ADD COLUMN IF NOT EXISTS cedula        VARCHAR(20),
    ADD COLUMN IF NOT EXISTS documento_url VARCHAR(500);

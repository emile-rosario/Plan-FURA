"""
Configuración centralizada — Funeraria Rancier
Lee variables desde .env usando pydantic-settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Seguridad ──────────────────────────────────────────────
    SECRET_KEY: str = "CAMBIA_ESTA_CLAVE_EN_PRODUCCION_usa_openssl_rand_hex_32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── Base de datos PostgreSQL ───────────────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "funeraria_rancier"
    DB_USER: str = "funeraria_user"
    DB_PASSWORD: str = "funeraria_pass"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # ── CORS ───────────────────────────────────────────────────
    CORS_ORIGINS: str = (
        "http://127.0.0.1:5500,http://localhost:5500,"
        "http://127.0.0.1:5501,http://localhost:5501,"
        "http://localhost:3000"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    # ── Uploads ────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]

    # ── Email (Resend) ─────────────────────────────────────────
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Funerarias Rancier <onboarding@resend.dev>"
    FRONTEND_URL: str = "http://127.0.0.1:5500"
    BACKEND_URL: str = "http://localhost:8000"
    ADMIN_EMAIL: str = "admin@funerariarancier.com"
    FUNERARIA_PHONE: str = "(809) 564-2200"

    # ── App ────────────────────────────────────────────────────
    APP_ENV: str = "development"  # development | production

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "arbitrary_types_allowed": True,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

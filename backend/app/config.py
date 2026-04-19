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

    # ── Contraseña admin inicial ───────────────────────────────
    ADMIN_PASSWORD: str = "Admin@2025"

    # ── Hosts permitidos ───────────────────────────────────────
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [h.strip() for h in self.ALLOWED_HOSTS.split(",")]

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

    # ── Email / SMTP ───────────────────────────────────────────
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@funerariarancier.com"

    # ── Frontend URL (para enlaces en emails) ──────────────────
    FRONTEND_URL: str = "http://localhost:5500"

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

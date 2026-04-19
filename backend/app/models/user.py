"""
Modelo de usuario con soporte para roles y auditoría.
"""
import enum
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class RolUsuario(str, enum.Enum):
    cliente = "cliente"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    telefono = Column(String(30))
    password = Column(String(255), nullable=False)
    rol = Column(String(20), default=RolUsuario.cliente.value, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    suscripciones = relationship("Suscripcion", back_populates="user")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_activo", "activo"),
    )


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(64), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(48)

    @staticmethod
    def expiry() -> datetime:
        return datetime.now(timezone.utc) + timedelta(hours=1)

    def is_valid(self) -> bool:
        return not self.used and datetime.now(timezone.utc) < self.expires_at

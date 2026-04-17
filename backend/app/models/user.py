"""
Modelo de usuario con soporte para roles y auditoría.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(254), unique=True, nullable=False)
    telefono = Column(String(30))
    password = Column(String(255), nullable=False)
    rol = Column(String(20), default="cliente", nullable=False)  # cliente | admin
    activo = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String(128), unique=True, nullable=True)
    password_reset_token = Column(String(128), unique=True, nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    suscripciones = relationship("Suscripcion", back_populates="user")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_activo", "activo"),
    )

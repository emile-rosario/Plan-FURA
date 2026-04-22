"""
Modelos de base de datos — PostgreSQL optimizado con índices y relaciones.
"""
from sqlalchemy import (
    Column, Integer, String, Numeric, Text, ForeignKey,
    DateTime, Boolean, Index, CheckConstraint, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class EstadoSuscripcion(str, enum.Enum):
    activo = "activo"
    cancelado = "cancelado"
    vencido = "vencido"


class Plan(Base):
    __tablename__ = "planes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=False)
    precio_mensual = Column(Numeric(12, 2), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    destacado = Column(Boolean, default=False, nullable=False)
    beneficios = Column(JSON, default=list)  # Lista nativa — sin json.dumps/loads
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    suscripciones = relationship("Suscripcion", back_populates="plan")

    __table_args__ = (
        CheckConstraint("precio_mensual > 0", name="ck_plan_precio_positivo"),
        Index("ix_planes_activo", "activo"),
    )


class Coffin(Base):
    __tablename__ = "ataudes"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    material = Column(String(100), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(12, 2), nullable=False)
    imagen_url = Column(String(500))
    imagen_url_2 = Column(String(500))
    disponible = Column(Boolean, default=True, nullable=False)
    destacado = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("precio > 0", name="ck_coffin_precio_positivo"),
        Index("ix_ataudes_disponible", "disponible"),
    )


class Suscripcion(Base):
    __tablename__ = "suscripciones"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_id = Column(Integer, ForeignKey("planes.id", ondelete="RESTRICT"), nullable=False)
    estado = Column(
        SAEnum(EstadoSuscripcion, name="estado_suscripcion"),
        default=EstadoSuscripcion.activo,
        nullable=False,
    )
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_cancelacion = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="suscripciones")
    plan = relationship("Plan", back_populates="suscripciones")

    __table_args__ = (
        Index("ix_suscripciones_user_id", "user_id"),
        Index("ix_suscripciones_estado", "estado"),
    )


class MensajeContacto(Base):
    __tablename__ = "mensajes_contacto"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(254), nullable=False)
    telefono = Column(String(30))
    asunto = Column(String(200))
    mensaje = Column(Text, nullable=False)
    leido = Column(Boolean, default=False, nullable=False)
    fecha = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_mensajes_leido", "leido"),
        Index("ix_mensajes_fecha", "fecha"),
    )

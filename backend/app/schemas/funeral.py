"""
Schemas Pydantic — Funeraria Rancier
Validación de datos de entrada y salida.
"""
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import re


# ── Ataúdes ───────────────────────────────────────────────────

class CoffinBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    material: str = Field(min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=1000)
    precio: Decimal = Field(gt=0, decimal_places=2)
    imagen_url: Optional[str] = Field(None, max_length=500)
    disponible: bool = True
    destacado: bool = False


class CoffinCreate(CoffinBase):
    pass


class CoffinUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=150)
    material: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=1000)
    precio: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    imagen_url: Optional[str] = Field(None, max_length=500)
    disponible: Optional[bool] = None
    destacado: Optional[bool] = None


class CoffinResponse(CoffinBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ── Planes Funerarios ─────────────────────────────────────────

class PlanBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str = Field(min_length=2, max_length=2000)
    precio_mensual: Decimal = Field(gt=0, decimal_places=2)
    activo: bool = True
    destacado: bool = False
    beneficios: Optional[str] = None  # JSON string


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, min_length=2, max_length=2000)
    precio_mensual: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    activo: Optional[bool] = None
    destacado: Optional[bool] = None
    beneficios: Optional[str] = None


class PlanResponse(PlanBase):
    id: int
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ── Suscripciones ─────────────────────────────────────────────

class SuscripcionCreate(BaseModel):
    plan_id: int = Field(gt=0)
    cedula: str = Field(min_length=6, max_length=20)
    documento_url: Optional[str] = Field(None, max_length=500)


class SuscripcionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    estado: str
    fecha_inicio: datetime
    plan: Optional[PlanResponse] = None
    model_config = {"from_attributes": True}


# ── Contacto ─────────────────────────────────────────────────

class ContactoCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=30)
    asunto: Optional[str] = Field(None, max_length=200)
    mensaje: str = Field(min_length=10, max_length=2000)
    archivo_adjunto: Optional[str] = Field(None, max_length=500)

    @field_validator("telefono")
    @classmethod
    def validate_telefono(cls, v):
        if v and not re.match(r"^[\d\s\+\-\(\)]{7,30}$", v):
            raise ValueError("Formato de teléfono inválido.")
        return v


class ContactoResponse(BaseModel):
    id: int
    nombre: str
    model_config = {"from_attributes": True}


class ContactoDetailResponse(BaseModel):
    """Respuesta completa de mensaje de contacto (para admin)."""
    id: int
    nombre: str
    email: str
    telefono: Optional[str] = None
    asunto: Optional[str] = None
    mensaje: str
    archivo_adjunto: Optional[str] = None
    leido: bool
    fecha: Optional[datetime] = None
    model_config = {"from_attributes": True}

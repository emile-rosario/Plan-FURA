"""
Schemas de usuario — Pydantic v2
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class UserCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr
    telefono: str = Field(min_length=7, max_length=30)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra.")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número.")
        return v

    @field_validator("telefono")
    @classmethod
    def validate_telefono(cls, v):
        if not re.match(r"^[\d\s\+\-\(\)]{7,30}$", v):
            raise ValueError("Formato de teléfono inválido.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    telefono: str
    rol: str
    activo: bool
    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    user_name: str
    user_rol: str
    user_email: str

"""
Router de autenticación — registro, login, perfil, verificación de email, reset de contraseña.
"""
import logging
import secrets
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
import re

from app.config import settings
from app.database import get_db
from app.email import send_verification_email, send_password_reset_email
from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest, UserResponse, LoginResponse
from app.security import hash_password, verify_password, create_access_token, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Autenticación"])

PASSWORD_RESET_EXPIRE_MINUTES = 30


# ── Schemas locales ────────────────────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)

    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra.")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número.")
        return v


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registrar un nuevo usuario cliente y enviar email de verificación."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta con ese correo electrónico.",
        )

    verification_token = secrets.token_urlsafe(32)
    new_user = User(
        nombre=user_data.nombre,
        email=user_data.email,
        telefono=user_data.telefono,
        password=hash_password(user_data.password),
        rol="cliente",
        email_verified=False,
        verification_token=verification_token,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_verification_email(new_user.email, new_user.nombre, verification_token)
    logger.info("Nuevo usuario registrado (pendiente verificación): %s", new_user.email)
    return new_user


@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verifica el email del usuario y redirige al frontend."""
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login.html?verified=error", status_code=302)

    if user.email_verified:
        return RedirectResponse(url=f"{settings.FRONTEND_URL}/login.html?verified=1", status_code=302)

    user.email_verified = True
    user.verification_token = None
    db.commit()

    logger.info("Email verificado: %s", user.email)
    return RedirectResponse(url=f"{settings.FRONTEND_URL}/login.html?verified=1", status_code=302)


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión y obtener token JWT."""
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.password):
        logger.warning("Login fallido: %s", login_data.email)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas.")

    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta desactivada. Contacta al administrador.")

    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="EMAIL_NOT_VERIFIED")

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(data={"sub": user.email, "rol": user.rol})
    logger.info("Login exitoso: %s (rol: %s)", user.email, user.rol)
    return LoginResponse(
        access_token=token, token_type="bearer",
        user_id=user.id, user_name=user.nombre, user_rol=user.rol, user_email=user.email,
    )


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Genera un token de reset y envía el email.
    Siempre responde 200 para no revelar si el email existe.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if user and user.activo:
        reset_token = secrets.token_urlsafe(32)
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)
        db.commit()
        send_password_reset_email(user.email, user.nombre, reset_token)
        logger.info("Reset de contraseña solicitado: %s", user.email)

    return {"message": "Si ese correo existe, recibirás las instrucciones en breve."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Valida el token y actualiza la contraseña."""
    user = db.query(User).filter(User.password_reset_token == data.token).first()

    if not user or not user.password_reset_expires:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido o expirado.")

    if datetime.now(timezone.utc) > user.password_reset_expires:
        user.password_reset_token = None
        user.password_reset_expires = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El enlace expiró. Solicita uno nuevo.")

    # Validar complejidad de contraseña
    pwd = data.password
    if not re.search(r"[A-Za-z]", pwd) or not re.search(r"\d", pwd):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La contraseña debe tener letras y números.")

    user.password = hash_password(data.password)
    user.password_reset_token = None
    user.password_reset_expires = None
    db.commit()

    logger.info("Contraseña actualizada: %s", user.email)
    return {"message": "Contraseña actualizada correctamente."}


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Obtener perfil del usuario autenticado."""
    return current_user

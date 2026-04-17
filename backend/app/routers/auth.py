"""
Router de autenticación — registro, login, perfil, verificación de email.
"""
import logging
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.email import send_verification_email
from app.models.user import User
from app.schemas.user import UserCreate, LoginRequest, UserResponse, LoginResponse
from app.security import hash_password, verify_password, create_access_token, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Autenticación"])


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
    logger.info("Nuevo usuario registrado (pendiente de verificación): %s", new_user.email)

    return new_user


@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verifica el email del usuario mediante el token recibido por correo.
    Redirige al frontend con el resultado.
    """
    user = db.query(User).filter(User.verification_token == token).first()

    if not user:
        logger.warning("Token de verificación inválido: %s", token[:12])
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login.html?verified=error",
            status_code=302,
        )

    if user.email_verified:
        # Ya estaba verificado — redirigir igual como éxito
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login.html?verified=1",
            status_code=302,
        )

    user.email_verified = True
    user.verification_token = None  # Invalida el token tras el uso
    db.commit()

    logger.info("Email verificado: %s", user.email)
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/login.html?verified=1",
        status_code=302,
    )


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Iniciar sesión y obtener token JWT."""
    user = db.query(User).filter(User.email == login_data.email).first()

    # Misma respuesta para usuario no encontrado y contraseña incorrecta (evita enumeración)
    if not user or not verify_password(login_data.password, user.password):
        logger.warning("Intento de login fallido para: %s", login_data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas.",
        )

    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada. Contacta al administrador.",
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="EMAIL_NOT_VERIFIED",
        )

    # Actualizar último login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(data={"sub": user.email, "rol": user.rol})
    logger.info("Login exitoso: %s (rol: %s)", user.email, user.rol)

    return LoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        user_name=user.nombre,
        user_rol=user.rol,
        user_email=user.email,
    )


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Obtener perfil del usuario autenticado."""
    return current_user

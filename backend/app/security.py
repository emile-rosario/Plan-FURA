"""
Seguridad — Funeraria Rancier
Hashing con bcrypt, JWT tokens y dependencias de autenticación.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)


# ── Contraseñas ────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash seguro bcrypt con sal aleatoria (costo 12)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica contraseña contra hash bcrypt."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── JWT Tokens ─────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Genera token JWT firmado con expiración."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    logger.info("Token generado para: %s", data.get("sub"))
    return token


def decode_token(token: str) -> dict:
    """Decodifica y valida un JWT. Lanza excepción si es inválido."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── Dependencias de FastAPI ────────────────────────────────────

def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    """Extrae el email del token JWT (requiere autenticación)."""
    payload = decode_token(token)
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin identidad válida.",
        )
    return email


def get_current_user(
    email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db),
):
    """Retorna el objeto User completo desde la base de datos."""
    from app.models.user import User
    user = db.query(User).filter(User.email == email, User.activo.is_(True)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o desactivado.",
        )
    return user


def get_current_admin(current_user=Depends(get_current_user)):
    """Verifica que el usuario sea administrador."""
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador.",
        )
    return current_user


def get_optional_user(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
):
    """Usuario opcional — retorna None si no hay token."""
    if not token:
        return None
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        if not email:
            return None
        from app.models.user import User
        return db.query(User).filter(User.email == email, User.activo.is_(True)).first()
    except Exception:
        return None

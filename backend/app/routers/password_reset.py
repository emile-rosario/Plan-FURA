import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.email_utils import send_password_reset_email
from app.models.user import User, PasswordResetToken
from app.security import hash_password

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Contraseña"])


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    # siempre respondemos lo mismo para no revelar si el email existe
    _GENERIC_MSG = "Si ese correo está registrado, recibirás un enlace para restablecer tu contraseña."

    user = db.query(User).filter(
        User.email == data.email,
        User.activo.is_(True),
    ).first()

    if not user:
        return {"message": _GENERIC_MSG}

    # anulamos tokens viejos antes de crear uno nuevo
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used.is_(False),
    ).update({"used": True})

    token_value = PasswordResetToken.generate_token()
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token_value,
        expires_at=PasswordResetToken.expiry(),
    )
    db.add(reset_token)
    db.commit()

    send_password_reset_email(user.email, token_value)
    logger.info("Token de reset generado para: %s", user.email)

    return {"message": _GENERIC_MSG}


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
    ).first()

    if not reset_token or not reset_token.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido o expirado. Solicita un nuevo enlace.",
        )

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    user.password = hash_password(data.new_password)
    reset_token.used = True
    db.commit()

    logger.info("Contraseña restablecida para: %s", user.email)
    return {"message": "Contraseña actualizada correctamente. Ya puedes iniciar sesión."}

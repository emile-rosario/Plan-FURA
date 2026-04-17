"""
Router de contacto — Recibir mensajes del formulario.
"""
import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.email import send_contact_notification
from app.models.funeral import MensajeContacto
from app.schemas.funeral import ContactoCreate, ContactoResponse, ContactoDetailResponse
from app.security import get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contacto", tags=["Contacto"])


@router.post("", response_model=ContactoResponse, status_code=status.HTTP_201_CREATED)
def enviar_mensaje(data: ContactoCreate, db: Session = Depends(get_db)):
    """Recibir mensaje del formulario de contacto (público)."""
    mensaje = MensajeContacto(**data.model_dump())
    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)
    logger.info("Mensaje de contacto recibido de: %s", data.email)

    # Notificar al admin por email
    send_contact_notification(
        nombre=data.nombre,
        email=data.email,
        telefono=data.telefono,
        asunto=data.asunto,
        mensaje=data.mensaje,
        archivo_url=data.archivo_adjunto,
    )

    return mensaje


@router.get("", response_model=list[ContactoDetailResponse])
def listar_mensajes(
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Listar mensajes de contacto (solo admin)."""
    return db.query(MensajeContacto).order_by(MensajeContacto.fecha.desc()).all()

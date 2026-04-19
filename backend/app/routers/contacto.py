"""
Router de contacto — Recibir mensajes del formulario.
"""
import logging

from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.limiter import limiter
from app.models.funeral import MensajeContacto
from app.schemas.funeral import ContactoCreate, ContactoResponse, ContactoDetailResponse, PaginatedContacto
from app.security import get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contacto", tags=["Contacto"])


@router.post("", response_model=ContactoResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/hour")
def enviar_mensaje(request: Request, data: ContactoCreate, db: Session = Depends(get_db)):
    """Recibir mensaje del formulario de contacto (público). Límite: 3/hora por IP."""
    mensaje = MensajeContacto(**data.model_dump())
    db.add(mensaje)
    db.commit()
    db.refresh(mensaje)
    logger.info("Mensaje de contacto recibido de: %s", data.email)
    return mensaje


@router.get("", response_model=PaginatedContacto)
def listar_mensajes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Listar mensajes de contacto con paginación (solo admin)."""
    q = db.query(MensajeContacto).order_by(MensajeContacto.fecha.desc())
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"total": total, "items": items, "skip": skip, "limit": limit}

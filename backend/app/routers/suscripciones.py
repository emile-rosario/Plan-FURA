"""
Router de suscripciones — Contratar y gestionar planes.
"""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.email import send_plan_notification
from app.models.funeral import Suscripcion, Plan, EstadoSuscripcion
from app.schemas.funeral import SuscripcionCreate, SuscripcionResponse
from app.security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/suscripciones", tags=["Suscripciones"])


@router.post("", response_model=SuscripcionResponse, status_code=status.HTTP_201_CREATED)
def contratar_plan(
    data: SuscripcionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Contratar un plan funerario (requiere autenticación y cédula)."""
    plan = db.query(Plan).filter(Plan.id == data.plan_id, Plan.activo.is_(True)).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado o no disponible.")

    suscripcion_activa = db.query(Suscripcion).filter(
        Suscripcion.user_id == current_user.id,
        Suscripcion.estado == EstadoSuscripcion.activo,
    ).first()
    if suscripcion_activa:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya tienes un plan activo. Cancela el actual para contratar uno nuevo.",
        )

    nueva = Suscripcion(
        user_id=current_user.id,
        plan_id=data.plan_id,
        cedula=data.cedula,
        documento_url=data.documento_url,
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)

    suscripcion = (
        db.query(Suscripcion)
        .options(joinedload(Suscripcion.plan))
        .filter(Suscripcion.id == nueva.id)
        .first()
    )

    # Notificar al admin
    send_plan_notification(
        nombre=current_user.nombre,
        email=current_user.email,
        telefono=getattr(current_user, "telefono", None),
        plan_nombre=plan.nombre,
        cedula=data.cedula,
        documento_url=data.documento_url,
    )

    logger.info("Plan contratado: user=%d, plan=%d, cedula=%s", current_user.id, data.plan_id, data.cedula)
    return suscripcion


@router.get("/mi-plan", response_model=SuscripcionResponse)
def get_mi_plan(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Obtener el plan activo del usuario autenticado."""
    suscripcion = (
        db.query(Suscripcion)
        .options(joinedload(Suscripcion.plan))
        .filter(
            Suscripcion.user_id == current_user.id,
            Suscripcion.estado == EstadoSuscripcion.activo,
        )
        .first()
    )
    if not suscripcion:
        raise HTTPException(status_code=404, detail="No tienes ningún plan activo.")
    return suscripcion


@router.delete("/mi-plan", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_plan(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Cancelar el plan activo del usuario."""
    suscripcion = db.query(Suscripcion).filter(
        Suscripcion.user_id == current_user.id,
        Suscripcion.estado == EstadoSuscripcion.activo,
    ).first()
    if not suscripcion:
        raise HTTPException(status_code=404, detail="No tienes ningún plan activo.")

    suscripcion.estado = EstadoSuscripcion.cancelado
    suscripcion.fecha_cancelacion = datetime.now(timezone.utc)
    db.commit()
    logger.info("Plan cancelado: user=%d, suscripcion=%d", current_user.id, suscripcion.id)

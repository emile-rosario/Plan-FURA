"""
Router de ataúdes — CRUD completo.
GET público; POST/PUT/DELETE solo admin.
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.funeral import Coffin
from app.schemas.funeral import CoffinCreate, CoffinUpdate, CoffinResponse
from app.security import get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ataudes", tags=["Ataúdes"])


@router.get("", response_model=list[CoffinResponse])
def list_coffins(
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    db: Session = Depends(get_db),
):
    """Listar ataúdes (público). Filtra por disponibilidad si se especifica."""
    q = db.query(Coffin)
    if disponible is not None:
        q = q.filter(Coffin.disponible == disponible)
    return q.order_by(Coffin.precio).all()


@router.get("/{coffin_id}", response_model=CoffinResponse)
def get_coffin(coffin_id: int, db: Session = Depends(get_db)):
    """Obtener un ataúd por ID (público)."""
    coffin = db.query(Coffin).filter(Coffin.id == coffin_id).first()
    if not coffin:
        raise HTTPException(status_code=404, detail="Ataúd no encontrado.")
    return coffin


@router.post("", response_model=CoffinResponse, status_code=status.HTTP_201_CREATED)
def create_coffin(
    data: CoffinCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Crear ataúd (solo admin)."""
    coffin = Coffin(**data.model_dump())
    db.add(coffin)
    db.commit()
    db.refresh(coffin)
    logger.info("Ataúd creado: %s", coffin.nombre)
    return coffin


@router.put("/{coffin_id}", response_model=CoffinResponse)
def update_coffin(
    coffin_id: int,
    data: CoffinUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Actualizar ataúd (solo admin)."""
    coffin = db.query(Coffin).filter(Coffin.id == coffin_id).first()
    if not coffin:
        raise HTTPException(status_code=404, detail="Ataúd no encontrado.")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(coffin, key, val)
    db.commit()
    db.refresh(coffin)
    logger.info("Ataúd actualizado: ID %d", coffin_id)
    return coffin


@router.delete("/{coffin_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coffin(
    coffin_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Eliminar ataúd (solo admin)."""
    coffin = db.query(Coffin).filter(Coffin.id == coffin_id).first()
    if not coffin:
        raise HTTPException(status_code=404, detail="Ataúd no encontrado.")
    db.delete(coffin)
    db.commit()
    logger.info("Ataúd eliminado: ID %d", coffin_id)

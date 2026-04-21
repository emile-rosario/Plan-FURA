import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.funeral import Coffin
from app.schemas.funeral import CoffinCreate, CoffinUpdate, CoffinResponse, PaginatedCoffins
from app.security import get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ataudes", tags=["Ataúdes"])


@router.get("", response_model=PaginatedCoffins)
def list_coffins(
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Coffin)
    if disponible is not None:
        q = q.filter(Coffin.disponible == disponible)
    q = q.order_by(Coffin.precio)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"total": total, "items": items, "skip": skip, "limit": limit}


@router.get("/{coffin_id}", response_model=CoffinResponse)
def get_coffin(coffin_id: int, db: Session = Depends(get_db)):
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
    # marcamos como no disponible en lugar de borrar
    coffin = db.query(Coffin).filter(Coffin.id == coffin_id).first()
    if not coffin:
        raise HTTPException(status_code=404, detail="Ataúd no encontrado.")
    coffin.disponible = False
    db.commit()
    logger.info("Ataúd desactivado: ID %d", coffin_id)

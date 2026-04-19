"""
Router de planes funerarios — CRUD completo.
GET público; POST/PUT/DELETE solo admin.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.funeral import Plan
from app.schemas.funeral import PlanCreate, PlanUpdate, PlanResponse, PaginatedPlanes
from app.security import get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/planes", tags=["Planes Funerarios"])


@router.get("", response_model=PaginatedPlanes)
def list_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Listar planes activos con paginación (público)."""
    q = db.query(Plan).filter(Plan.activo.is_(True)).order_by(Plan.precio_mensual)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {"total": total, "items": items, "skip": skip, "limit": limit}


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Obtener un plan por ID (público)."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    return plan


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    data: PlanCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Crear plan funerario (solo admin)."""
    plan = Plan(**data.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    logger.info("Plan creado: %s", plan.nombre)
    return plan


@router.put("/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: int,
    data: PlanUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Actualizar plan (solo admin)."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(plan, key, val)
    db.commit()
    db.refresh(plan)
    logger.info("Plan actualizado: ID %d", plan_id)
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin),
):
    """Soft delete de plan — desactiva en lugar de eliminar (solo admin)."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    plan.activo = False
    db.commit()
    logger.info("Plan desactivado (soft delete): ID %d", plan_id)

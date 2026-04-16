"""
Router de planes funerarios — CRUD completo.
GET público; POST/PUT/DELETE solo admin.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.funeral import Plan
from app.schemas.funeral import PlanCreate, PlanUpdate, PlanResponse
from app.security import get_current_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/planes", tags=["Planes Funerarios"])


@router.get("", response_model=list[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    """Listar planes activos (público)."""
    return db.query(Plan).filter(Plan.activo.is_(True)).order_by(Plan.precio_mensual).all()


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
    """Eliminar plan (solo admin)."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado.")
    db.delete(plan)
    db.commit()
    logger.info("Plan eliminado: ID %d", plan_id)

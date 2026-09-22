from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Alert
from app.schemas import AlertCreate

router = APIRouter(prefix="/api/alertas", tags=["Alertas"])
@router.post("", status_code=201)
def create_alert(payload: AlertCreate, current_user: Annotated[dict, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    alert = Alert(**payload.model_dump(), usuario_id=current_user["id"])
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.get("")
def list_alerts(_: Annotated[dict, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(Alert).order_by(Alert.creada_en.desc()).limit(100)).all()


@router.patch("/{alert_id}/close")
def close_alert(alert_id: str, current_user: Annotated[dict, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    alert = db.get(Alert, alert_id)
    if not alert:
        return {"detail": "Alerta no encontrada"}
    alert.estado = "cerrada"
    alert.atendida_por = current_user["id"]
    db.commit()
    db.refresh(alert)
    return alert

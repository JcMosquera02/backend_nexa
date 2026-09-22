from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import Access, User
from app.schemas import AccessCreate

router = APIRouter(prefix="/api/accesos", tags=["Control de acceso"])
@router.post("", status_code=201)
def create_access(payload: AccessCreate, current_user: Annotated[dict, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    user = db.get(User, payload.usuario_id)
    if not user or not user.activo:
        raise HTTPException(status_code=403, detail="No permitir acceso: usuario inexistente o inactivo")
    record = Access(**payload.model_dump(), registrado_por=UUID(current_user["id"]))
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("")
def list_accesses(_: Annotated[dict, Depends(get_current_user)], db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(Access).order_by(Access.ocurrio_en.desc()).limit(100)).all()

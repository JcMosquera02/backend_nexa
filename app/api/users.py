from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_roles
from app.core.database import get_db
from app.models import User
from app.schemas import UserResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/users", tags=["Usuarios"])


@router.get("", response_model=list[UserResponse])
def list_users(_: Annotated[dict, Depends(require_roles("admin", "operador"))], db: Annotated[Session, Depends(get_db)]):
    return [{**user.__dict__, "role": user.role.nombre} for user in db.scalars(select(User)).all()]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, _: Annotated[dict, Depends(require_roles("admin", "operador"))], db: Annotated[Session, Depends(get_db)]):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {**user.__dict__, "role": user.role.nombre}


@router.patch("/{user_id}/status")
def change_status(user_id: str, activo: bool, _: Annotated[dict, Depends(require_roles("admin"))], db: Annotated[Session, Depends(get_db)]):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.activo = activo
    db.commit()
    return {"id": user_id, "activo": activo}

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles
from app.models import Camera

router = APIRouter(prefix="/api/cameras", tags=["Videovigilancia"])
@router.get("")
def list_cameras(_: Annotated[dict, Depends(require_roles("admin", "operador", "autoridad"))], db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(Camera).where(Camera.activa.is_(True))).all()


@router.get("/{camera_id}/stream")
def camera_stream(camera_id: str, _: Annotated[dict, Depends(require_roles("admin", "operador"))], db: Annotated[Session, Depends(get_db)]):
    camera = db.get(Camera, camera_id)
    if not camera or not camera.activa:
        raise HTTPException(status_code=404, detail="Camara no disponible")
    return {"camera_id": camera_id, "stream_url": camera.url_streaming, "anonimizado": camera.anonimizado}

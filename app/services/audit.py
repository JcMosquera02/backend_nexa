from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session


def record_audit(db: Session, actor_id: UUID | None, accion: str, recurso: str, resultado: str = "exitoso") -> None:
    db.execute(
        text("INSERT INTO auditoria (actor_id, accion, recurso, resultado) VALUES (:actor_id, :accion, :recurso, :resultado)"),
        {"actor_id": actor_id, "accion": accion, "recurso": recurso, "resultado": resultado},
    )
    db.commit()

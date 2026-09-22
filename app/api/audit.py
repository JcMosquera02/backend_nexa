from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.security import require_roles

router = APIRouter(prefix="/api/auditoria", tags=["Cumplimiento"])


@router.get("")
def list_audit(_: Annotated[dict, Depends(require_roles("admin", "autoridad"))]):
    return {"items": [], "retention_days": 365}

from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends

from app.core.security import require_roles

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


@router.get("/access-summary")
def access_summary(_: Annotated[dict, Depends(require_roles("admin", "autoridad"))]):
    return {"report_id": str(uuid4()), "format": "json", "scope": "accesses", "status": "generated"}

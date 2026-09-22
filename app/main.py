from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import access, alerts, audit, auth, cameras, reports, users
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0", description="Gestion integral de seguridad residencial")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(access.router)
app.include_router(alerts.router)
app.include_router(cameras.router)
app.include_router(reports.router)
app.include_router(audit.router)


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok", "service": settings.app_name}

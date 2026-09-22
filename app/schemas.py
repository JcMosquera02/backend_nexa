from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleName(StrEnum):
    admin = "admin"
    operador = "operador"
    residente = "residente"
    autoridad = "autoridad"


class UserCreate(BaseModel):
    cedula: str = Field(min_length=5, max_length=20)
    nombre_completo: str = Field(min_length=2, max_length=150)
    correo: EmailStr
    password: str = Field(min_length=10)
    role: RoleName = RoleName.residente
    consentimiento_datos: bool


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    cedula: str
    nombre_completo: str
    correo: EmailStr
    activo: bool
    role: RoleName
    consentimiento_datos: bool


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccessCreate(BaseModel):
    usuario_id: UUID
    tipo_credencial: str = Field(pattern="^(biometria|rfid|placa|manual)$")
    punto_acceso: str
    placa_vehiculo: str | None = Field(default=None, pattern=r"^[A-Z]{3}[0-9]{3}$")
    resultado: str = Field(default="permitido", pattern="^(permitido|denegado)$")


class AlertCreate(BaseModel):
    tipo: str
    severidad: str = Field(pattern="^(baja|media|alta|critica)$")
    descripcion: str
    camera_id: UUID | None = None


class CameraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nombre: str
    ubicacion: str
    url_streaming: str
    anonimizado: bool
    activa: bool


class AuditResponse(BaseModel):
    timestamp: datetime
    actor_id: UUID | None
    accion: str
    recurso: str
    resultado: str

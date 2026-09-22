from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(40), unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text)
    usuarios: Mapped[list["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "usuarios"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    cedula: Mapped[str] = mapped_column(String(20), unique=True)
    nombre_completo: Mapped[str] = mapped_column(String(150))
    correo: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("roles.id"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    consentimiento_datos: Mapped[bool] = mapped_column(Boolean, default=False)
    fecha_consentimiento: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_retencion: Mapped[date | None] = mapped_column(Date)
    role: Mapped[Role] = relationship(back_populates="usuarios")


class Camera(Base):
    __tablename__ = "camaras"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    nombre: Mapped[str] = mapped_column(String(100))
    ubicacion: Mapped[str] = mapped_column(String(200))
    url_streaming: Mapped[str] = mapped_column(Text)
    url_grabacion: Mapped[str | None] = mapped_column(Text)
    anonimizado: Mapped[bool] = mapped_column(Boolean, default=True)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    retencion_dias: Mapped[int] = mapped_column(Integer, default=30)


class Access(Base):
    __tablename__ = "accesos"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    usuario_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("usuarios.id"))
    camara_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("camaras.id"))
    tipo_credencial: Mapped[str] = mapped_column(String(20))
    punto_acceso: Mapped[str] = mapped_column(String(100))
    placa_vehiculo: Mapped[str | None] = mapped_column(String(6))
    resultado: Mapped[str] = mapped_column(String(10))
    motivo: Mapped[str | None] = mapped_column(Text)
    ocurrio_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    registrado_por: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)


class Alert(Base):
    __tablename__ = "alertas"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    camera_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("camaras.id"))
    usuario_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("usuarios.id"))
    tipo: Mapped[str] = mapped_column(String(60))
    severidad: Mapped[str] = mapped_column(String(10))
    descripcion: Mapped[str] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(15), default="abierta")
    creada_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atendida_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    atendida_por: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("usuarios.id"))

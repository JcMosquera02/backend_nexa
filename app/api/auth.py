from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Role, User
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Autenticacion"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    if not payload.consentimiento_datos:
        raise HTTPException(status_code=422, detail="Se requiere consentimiento informado")
    existing = db.scalar(select(User).where(or_(User.correo == payload.correo, User.cedula == payload.cedula)))
    if existing:
        raise HTTPException(status_code=409, detail="Cedula o correo ya registrado")
    role = db.scalar(select(Role).where(Role.nombre == payload.role.value))
    if not role:
        role = Role(nombre=payload.role.value, descripcion=f"Rol {payload.role.value}")
        db.add(role)
        db.flush()
    user = User(cedula=payload.cedula, nombre_completo=payload.nombre_completo, correo=payload.correo,
                password_hash=hash_password(payload.password), role_id=role.id,
                consentimiento_datos=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {**user.__dict__, "role": role.nombre}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.scalar(select(User).where(User.correo == payload.correo))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales invalidas")
    if not user.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")
    return {"access_token": create_access_token(str(user.id), user.role.nombre), "token_type": "bearer"}


@router.post("/refresh", response_model=TokenResponse)
def refresh(current_user: Annotated[dict, Depends(__import__("app.core.security", fromlist=["get_current_user"]).get_current_user)]):
    return {"access_token": create_access_token(current_user["id"], current_user["role"]), "token_type": "bearer"}

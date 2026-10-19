from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.service import AuthService
from app.db.sessions import get_db
from app.users.models import User
from app.users.schemas import UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

def get_auth_service() -> AuthService:
    return AuthService()

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service)
):
    return service.register(db, data)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
    service: AuthService = Depends(get_auth_service),
):
    return service.login(db, data)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
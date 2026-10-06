from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.sessions import get_db
from app.users.repository import UserRepository
from app.users.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.users.service import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

def get_user_service() -> UserService:
    return UserService(
        repository=UserRepository(),
    )

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    return service.create_user(
        db,
        user_data
    )

@router.get(
    "/",
    response_model=list[UserResponse],
)
def get_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    return service.get_users(
        db,
        skip=skip,
        limit=limit
    )

@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    return service.get_user(
        db,
        user_id,
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    return service.update_user(
        db,
        user_id,
        user_data,
    )

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    service: UserService = Depends(get_user_service),
):
    service.delete_user(
        db,
        user_id,
    )

    return None
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.auth.schemas import LoginRequest, RegisterRequest
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password
)
from app.users.models import User
from app.users.repository import UserRepository

class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register(
        self,
        db: Session,
        data: RegisterRequest,
    ) -> User:
        email = str(data.email).lower()

        existing_user = self.user_repository.get_by_email(
            db,
            email
        )

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered."
            )

        user = User(
            name=data.name,
            email=email,
            password_hash=hash_password(data.password),
            role="customer",
        )

        try:
            return self.user_repository.create(db, user)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email is already registered",
            )

    
    def login(
        self,
        db: Session,
        data: LoginRequest,
    ) -> dict[str, str]:

        email = str(data.email).lower()

        user = self.user_repository.get_by_email(
            db,
            email
        )

        if user is None or not verify_password(
            data.password,
            user.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(user.id)

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
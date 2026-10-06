from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.users.models import User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate, UserUpdate

class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(
        self,
        db: Session,
        user_data: UserCreate,
    ) -> User:

        existing_user = self.repository.get_by_email(
            db,
            user_data.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=user_data.password,
            role=user_data.role,
        )

        try:
            return self.repository.create(db, user)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

    def get_user(
        self,
        db: Session,
        user_id: int,
    ) -> User:

        user = self.repository.get_by_id(
            db,
            user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        return user

    def get_users(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:

        return self.repository.get_all(
            db,
            skip=skip,
            limit=limit,
        )

    def update_user(
        self,
        db: Session,
        user_id: int,
        user_data: UserUpdate,
    ) -> User:

        user = self.get_user(db, user_id)

        if user_data.name is not None:
            user.name = user_data.name

        if user_data.email is not None:

            existing_user = self.repository.get_by_email(
                db,
                user_data.email,
            )

            if existing_user and existing_user.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A user with this email already exists.",
                )

            user.email = user_data.email

        try:
            return self.repository.update(db, user)

        except IntegrityError:
            db.rollback()

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists.",
            )

    def delete_user(
        self,
        db: Session,
        user_id: int,
    ) -> None:

        user = self.get_user(db, user_id)

        self.repository.delete(db, user)
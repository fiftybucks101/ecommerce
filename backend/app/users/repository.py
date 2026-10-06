from sqlalchemy import select
from sqlalchemy.orm import Session

from app.users.models import User

class UserRepository:

    def create(self, db: Session, user: User) -> User:
        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def get_by_id(self, db: Session, user_id: int) -> User | None:
        statement = select(User).where(User.id == user_id)

        return db.scalar(statement)

    def get_by_email(self, db: Session, email: str) -> User | None:
        statement = select(User).where(User.email == email)

        return db.scalar(statement)

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:

        statement = (
            select(User)
            .offset(skip)
            .limit(limit)
        )

        return list(db.scalars(statement).all())

    def update(self, db: Session, user: User) -> User:
        db.commit()
        db.refresh(user)

        return user

    def delete(self, db: Session, user: User) -> None:
        db.delete(user)
        db.commit()
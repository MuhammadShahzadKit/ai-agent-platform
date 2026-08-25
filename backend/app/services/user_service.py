from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserUpdate,
)


def get_user_by_username(
    db: Session,
    username: str,
):
    return (
        db.query(User)
        .filter(User.username == username)
        .first()
    )


def authenticate_user(
    db: Session,
    username: str,
    password: str,
):
    user = get_user_by_username(
        db,
        username,
    )

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user


def create_user(
    db: Session,
    user: UserCreate,
):
    existing_user = get_user_by_username(
        db,
        user.username,
    )

    if existing_user:
        raise ValueError("Username already exists")

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password),
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_users(db: Session):
    return db.query(User).all()


def get_user(
    db: Session,
    user_id: int,
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def update_user(
    db: Session,
    user_id: int,
    data: UserUpdate,
):
    user = get_user(
        db,
        user_id,
    )

    if not user:
        return None

    user.username = data.username
    user.email = data.email

    db.commit()
    db.refresh(user)

    return user


def delete_user(
    db: Session,
    user_id: int,
):
    user = get_user(
        db,
        user_id,
    )

    if not user:
        return None

    db.delete(user)
    db.commit()

    return user
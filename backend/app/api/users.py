from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
)
from app.db.session import get_db
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    Token,
)
from app.services.user_service import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user,
    authenticate_user,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ==========================
# Register
# ==========================
@router.post(
    "/register",
    response_model=UserResponse,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_user(db, user)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================
# Login
# ==========================
@router.post(
    "/login",
    response_model=Token,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    access_token = create_access_token(
        {
            "sub": user.username,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ==========================
# Current User
# ==========================
@router.get("/me")
def me(
    current_user=Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }


# ==========================
# Get All Users
# ==========================
@router.get(
    "/",
    response_model=list[UserResponse],
)
def read_all(
    db: Session = Depends(get_db),
):
    return get_users(db)


# ==========================
# Get Single User
# ==========================
@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def read_one(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = get_user(db, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ==========================
# Update User
# ==========================
@router.put(
    "/{user_id}",
    response_model=UserResponse,
)
def update(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = update_user(
        db,
        user_id,
        data,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


# ==========================
# Delete User
# ==========================
@router.delete("/{user_id}")
def remove(
    user_id: int,
    db: Session = Depends(get_db),
):
    user = delete_user(
        db,
        user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "message": "User deleted"
    }
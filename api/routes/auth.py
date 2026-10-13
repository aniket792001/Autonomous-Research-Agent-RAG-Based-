"""
Authentication routes for AegisAudit AI.
Handles user registration, login, JWT token issuance, and profile verification.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from models.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    UserRole
)
from core.security import PasswordHasher, TokenManager
from db.user_store import UserDatabase
from api.deps import get_current_user, require_roles
from typing import List

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
user_db = UserDatabase()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_user(req: UserRegisterRequest):
    """
    Registers a new user account and immediately returns an authentication token.
    """
    existing = user_db.get_user_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user = user_db.create_user(
        email=req.email,
        password=req.password,
        full_name=req.full_name,
        role=req.role
    )

    token = TokenManager.create_access_token(data={
        "sub": user.id,
        "email": user.email,
        "role": user.role.value
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user
    )

@router.post("/login", response_model=TokenResponse)
def login_user(req: UserLoginRequest):
    """
    Authenticates user credentials and issues a signed JWT access token.
    """
    user_record = user_db.get_user_by_email(req.email)
    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not PasswordHasher.verify_password(req.password, user_record["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if not user_record["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Contact an administrator."
        )

    user = UserResponse(
        id=user_record["id"],
        email=user_record["email"],
        full_name=user_record["full_name"],
        role=user_record["role"],
        is_active=user_record["is_active"],
        created_at=user_record["created_at"]
    )

    token = TokenManager.create_access_token(data={
        "sub": user.id,
        "email": user.email,
        "role": user.role.value
    })

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: UserResponse = Depends(get_current_user)):
    """
    Returns profile information of the currently authenticated user.
    """
    return current_user

@router.get("/users", response_model=List[UserResponse])
def list_registered_users(admin_user: UserResponse = Depends(require_roles([UserRole.ADMIN]))):
    """
    Lists all users. Restricted to Admin role only.
    """
    return user_db.list_users()

"""Authentication routes — /api/v1/auth/*"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import ActiveUser, get_db
from app.api.v1.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Create a new user account and return an access token.

    The token is not scoped to any organisation yet — the client must
    create or join an org and then call ``/auth/switch-org``.
    """
    svc = AuthService(db)
    user, token = svc.register(
        email=body.email,
        password=body.password,
        full_name=body.full_name,
    )
    db.commit()
    db.refresh(user)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login and receive an access token",
)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email + password and receive a JWT."""
    svc = AuthService(db)
    user, token = svc.login(email=body.email, password=body.password)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Return the currently authenticated user",
)
def me(current_user: ActiveUser) -> UserResponse:
    """Return profile information for the authenticated user."""
    return UserResponse.model_validate(current_user)

"""Authentication service.

Handles registration, login, and token management.
All methods operate within the caller-supplied SQLAlchemy session;
the service never commits — the caller (API route or test) commits.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.models.membership import Membership
from app.models.user import User
from app.repositories.membership import MembershipRepository
from app.repositories.user import UserRepository


class AuthService:
    """Stateless auth service — instantiate per-request with a DB session."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._users = UserRepository(session)
        self._memberships = MembershipRepository(session)

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None = None,
    ) -> tuple[User, str]:
        """Create a new user account.

        Returns:
            (user, access_token) — the new user and a token scoped to no org
            (the user has not joined any org yet).

        Raises:
            HTTPException 409: if the email is already registered.
        """
        if self._users.get_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )

        user = self._users.create_user(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        token = create_access_token(subject=user.id)
        return user, token

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def login(self, *, email: str, password: str) -> tuple[User, str]:
        """Authenticate a user and issue a JWT.

        The token is scoped to the user's first organisation (if any).

        Returns:
            (user, access_token)

        Raises:
            HTTPException 401: if credentials are wrong or account is inactive.
        """
        user = self._users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated.",
            )

        # Scope the token to the first org membership (if any)
        memberships = self._memberships.list_user_orgs(user.id)
        first = memberships[0] if memberships else None

        token = create_access_token(
            subject=user.id,
            org_id=first.organization_id if first else "",
            role=first.role if first else "",
        )
        return user, token

    # ------------------------------------------------------------------
    # Token scoping
    # ------------------------------------------------------------------

    def switch_org(
        self, *, user: User, org_id: uuid.UUID
    ) -> str:
        """Re-issue a token scoped to a different organisation.

        Raises:
            HTTPException 403: if the user is not a member of *org_id*.
        """
        membership = self._memberships.get_membership(org_id, user.id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of the requested organisation.",
            )
        return create_access_token(
            subject=user.id,
            org_id=org_id,
            role=membership.role,
        )

    # ------------------------------------------------------------------
    # Token → User resolution (used by FastAPI deps)
    # ------------------------------------------------------------------

    def get_user_from_token(self, token: str) -> User:
        """Decode *token* and return the corresponding User.

        Raises:
            HTTPException 401: if the token is invalid or the user is not found.
        """
        try:
            payload = decode_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from None

        user = self._users.get_by_id_global(uuid.UUID(payload.sub))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    # ------------------------------------------------------------------
    # Membership helper
    # ------------------------------------------------------------------

    def get_membership(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Membership | None:
        """Return the membership record for a (org, user) pair."""
        return self._memberships.get_membership(org_id, user_id)

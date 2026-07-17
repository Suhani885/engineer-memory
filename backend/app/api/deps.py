"""FastAPI dependency helpers.

Every route that needs authentication or org-scoping pulls its dependencies
from this module.  The dependency tree looks like:

    get_db
      └── get_current_user   (validates JWT, loads User)
            └── get_current_active_user  (checks is_active)
                  └── get_org_context   (validates org membership)
                        └── require_role("owner", "admin")
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.organization_service import OrganizationService

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------


def get_db() -> Generator[Session, None, None]:
    yield from get_db_session()


DBDep = Annotated[Session, Depends(get_db)]

# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

_bearer = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    db: DBDep,
) -> User:
    """Decode the Bearer token and return the authenticated User."""
    return AuthService(db).get_user_from_token(credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_user(current_user: CurrentUser) -> User:
    """Raise 403 if the account is deactivated."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated.",
        )
    return current_user


ActiveUser = Annotated[User, Depends(get_current_active_user)]

# ---------------------------------------------------------------------------
# Organisation context
# ---------------------------------------------------------------------------


def get_org_context(
    org_slug: Annotated[str, Header(alias="X-Org-Slug")],
    current_user: ActiveUser,
    db: DBDep,
) -> tuple[Organization, Membership]:
    """Validate that the authenticated user is a member of the org in the header.

    Callers declare the dependency as::

        OrgCtx = Annotated[tuple[Organization, Membership], Depends(get_org_context)]

    The ``X-Org-Slug`` request header selects which organisation is active for
    this request.  The JWT's ``org_id`` is advisory; the header is authoritative.
    """
    svc = OrganizationService(db)
    org = svc.get_org_by_slug(org_slug)
    membership = svc.assert_membership(org.id, current_user.id)
    return org, membership


OrgContext = Annotated[tuple[Organization, Membership], Depends(get_org_context)]


# ---------------------------------------------------------------------------
# Role guard (factory dependency)
# ---------------------------------------------------------------------------


def require_role(*allowed_roles: str):
    """Return a FastAPI dependency that enforces membership role.

    Usage::

        @router.delete("/{slug}/members/{user_id}")
        def remove_member(
            ctx: OrgContext,
            _: Annotated[None, Depends(require_role("owner", "admin"))],
        ):
            ...
    """

    def _check(ctx: OrgContext) -> None:
        _, membership = ctx
        if membership.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of: {list(allowed_roles)}.",
            )

    return Depends(_check)

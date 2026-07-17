from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for the User model.

    Users exist at the platform level (not scoped to an org), so
    the standard BaseRepository org-scoped helpers are intentionally
    not exposed.  Cross-org user lookups (login, OAuth) use the global
    helpers below.
    """

    model = User

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ------------------------------------------------------------------
    # Global reads (used during auth — no org scope required)
    # ------------------------------------------------------------------

    def get_by_email(self, email: str) -> User | None:
        """Look up a user by email address (global — used at login time)."""
        stmt = select(User).where(User.email == email)
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_id_global(self, user_id) -> User | None:
        """Return a user by PK (no org scope — for auth middleware)."""
        stmt = select(User).where(User.id == user_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_oauth(self, provider: str, subject: str) -> User | None:
        """Look up a user by OAuth provider + subject ID.

        Used when processing the OAuth callback to find an existing
        account linked to the provider identity.
        """
        stmt = select(User).where(
            User.oauth_provider == provider,
            User.oauth_subject == subject,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def create_user(
        self,
        *,
        email: str,
        hashed_password: str,
        full_name: str | None = None,
    ) -> User:
        """Create and persist a new platform user."""
        return self.create(
            {
                "email": email,
                "hashed_password": hashed_password,
                "full_name": full_name,
            }
        )

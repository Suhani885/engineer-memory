from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.membership import Membership


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A platform user.

    Authentication is currently password-based (placeholder bcrypt hash).
    The `oauth_provider` / `oauth_subject` columns are intentionally left
    nullable so the model is ready for GitHub / Google OAuth without a
    schema migration.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # OAuth-ready columns — null for password-only accounts
    oauth_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # "github" | "google"
    oauth_subject: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # provider's sub / user-id

    # Relationships
    memberships: Mapped[list[Membership]] = relationship(
        "Membership", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!s} email={self.email!r}>"

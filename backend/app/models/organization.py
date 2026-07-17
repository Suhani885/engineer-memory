from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.github_installation import GitHubInstallation
    from app.models.github_repository import GitHubRepository
    from app.models.membership import Membership


class Organization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A tenant organisation.

    Every resource in the system is scoped to exactly one organisation.
    The `slug` is the URL-safe, globally unique handle (e.g. "acme-corp").
    """

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    memberships: Mapped[list[Membership]] = relationship(
        "Membership", back_populates="organization", cascade="all, delete-orphan"
    )
    github_installations: Mapped[list[GitHubInstallation]] = relationship(
        "GitHubInstallation", back_populates="organization", cascade="all, delete-orphan"
    )
    github_repositories: Mapped[list[GitHubRepository]] = relationship(
        "GitHubRepository", back_populates="organization", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id!s} slug={self.slug!r}>"

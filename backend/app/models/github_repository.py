from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.github_installation import GitHubInstallation
    from app.models.organization import Organization


class GitHubRepository(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A GitHub repository tracked under a GitHub App installation.

    Repositories are discovered when processing ``installation_repositories``
    or ``push``/``pull_request`` webhook events.  Each repository belongs to
    exactly one installation and therefore one organisation.

    Fields
    ------
    github_repo_id
        The numeric ID GitHub assigns to each repository.  Globally unique.
    full_name
        The canonical ``owner/repo`` slug (e.g. ``"acme-corp/backend"``).
    permissions
        Repository-level permissions granted to the installation
        (e.g. ``{"contents": "read", "pull_requests": "read"}``).
    """

    __tablename__ = "github_repositories"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    installation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("github_installations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    github_repo_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False, default="main")
    permissions: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="github_repositories"
    )
    installation: Mapped[GitHubInstallation] = relationship(
        "GitHubInstallation", back_populates="repositories"
    )

    def __repr__(self) -> str:
        return f"<GitHubRepository id={self.id!s} full_name={self.full_name!r}>"

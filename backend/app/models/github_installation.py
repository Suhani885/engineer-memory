from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, BigInteger, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.github_repository import GitHubRepository
    from app.models.organization import Organization

class GitHubInstallation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Records a GitHub App installation linked to an Engineering Memory organisation.

    When a user installs the GitHub App on their GitHub organisation or user
    account, GitHub sends an ``installation`` webhook event.  That event is
    used to create (or update) a row here, binding the GitHub installation to
    one of our ``Organization`` tenants.

    Fields
    ------
    github_installation_id
        The numeric ID GitHub assigns to each installation.  Globally unique
        across all GitHub App installations.
    github_app_id
        The ID of our GitHub App (matches ``GITHUB_APP_ID`` in settings).
    github_account_login
        The GitHub login of the account/org that installed the app
        (e.g. ``"acme-corp"``).
    github_account_type
        ``"Organization"`` or ``"User"``.
    permissions
        The permission set granted to the app at installation time
        (e.g. ``{"contents": "read", "pull_requests": "read"}``).
    events
        The webhook events the installation is subscribed to
        (e.g. ``["pull_request"]``).
    """

    __tablename__ = "github_installations"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    github_installation_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    github_app_id: Mapped[str] = mapped_column(String(100), nullable=False)
    github_account_login: Mapped[str] = mapped_column(String(255), nullable=False)
    github_account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    permissions: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    events: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="github_installations"
    )
    repositories: Mapped[list[GitHubRepository]] = relationship(
        "GitHubRepository", back_populates="installation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<GitHubInstallation id={self.id!s} "
            f"github_id={self.github_installation_id} "
            f"account={self.github_account_login!r}>"
        )

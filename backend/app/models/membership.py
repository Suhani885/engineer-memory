from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User

ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_MEMBER = "member"

VALID_ROLES = {ROLE_OWNER, ROLE_ADMIN, ROLE_MEMBER}


class Membership(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Junction table linking a User to an Organization with a role.

    A user can belong to many organisations; each membership carries
    exactly one role — 'owner', 'admin', or 'member'.
    The UNIQUE constraint on (organization_id, user_id) prevents
    duplicate memberships.
    """

    __tablename__ = "memberships"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_membership_org_user"),
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=ROLE_MEMBER)

    # Relationships
    organization: Mapped[Organization] = relationship("Organization", back_populates="memberships")
    user: Mapped[User] = relationship("User", back_populates="memberships")

    def __repr__(self) -> str:
        return (
            f"<Membership org={self.organization_id!s} "
            f"user={self.user_id!s} role={self.role!r}>"
        )

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.repositories.base import BaseRepository


class MembershipRepository(BaseRepository[Membership]):
    """Repository for the Membership join table."""

    model = Membership

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ------------------------------------------------------------------
    # Specialised queries
    # ------------------------------------------------------------------

    def get_membership(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Membership | None:
        """Return the membership record for a specific (org, user) pair."""
        stmt = select(Membership).where(
            Membership.organization_id == org_id,
            Membership.user_id == user_id,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list_org_members(
        self, org_id: uuid.UUID, *, limit: int = 100, offset: int = 0
    ) -> list[Membership]:
        """Return all memberships for an organisation (with users eager-loaded)."""
        stmt = (
            select(Membership)
            .where(Membership.organization_id == org_id)
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.execute(stmt).scalars().all())

    def list_user_orgs(self, user_id: uuid.UUID) -> list[Membership]:
        """Return all memberships for a user (all orgs they belong to)."""
        stmt = select(Membership).where(Membership.user_id == user_id)
        return list(self._session.execute(stmt).scalars().all())

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def add_member(
        self, *, org_id: uuid.UUID, user_id: uuid.UUID, role: str
    ) -> Membership:
        """Add a user to an organisation with the given role."""
        return self.create(
            {
                "organization_id": org_id,
                "user_id": user_id,
                "role": role,
            }
        )

    def set_role(self, membership: Membership, role: str) -> Membership:
        """Update the role of an existing membership."""
        return self.update(membership, {"role": role})

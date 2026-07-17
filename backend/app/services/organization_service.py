"""Organisation management service.

Handles org creation, membership management, and role changes.
The service never commits — commit responsibility lives in the API layer.
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.membership import ROLE_MEMBER, ROLE_OWNER, VALID_ROLES, Membership
from app.models.organization import Organization
from app.models.user import User
from app.repositories.membership import MembershipRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository


class OrganizationService:
    """Stateless org service — instantiate per-request."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._orgs = OrganizationRepository(session)
        self._users = UserRepository(session)
        self._memberships = MembershipRepository(session)

    # ------------------------------------------------------------------
    # Organisation CRUD
    # ------------------------------------------------------------------

    def create_org(
        self,
        *,
        owner: User,
        name: str,
        slug: str,
        plan: str = "free",
    ) -> tuple[Organization, Membership]:
        """Create a new organisation and make *owner* its owner.

        Returns:
            (organisation, owner_membership)

        Raises:
            HTTPException 409: if the slug is already taken.
        """
        if self._orgs.get_by_slug(slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"The organisation handle '{slug}' is already taken.",
            )

        org = self._orgs.create_organization(name=name, slug=slug, plan=plan)
        membership = self._memberships.add_member(
            org_id=org.id,
            user_id=owner.id,
            role=ROLE_OWNER,
        )
        return org, membership

    def get_org_by_slug(self, slug: str) -> Organization:
        """Return an organisation by slug or raise 404."""
        org = self._orgs.get_by_slug(slug)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organisation '{slug}' not found.",
            )
        return org

    def get_org_by_id(self, org_id: uuid.UUID) -> Organization:
        """Return an organisation by ID or raise 404."""
        org = self._orgs.get_by_id_global(org_id)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organisation not found.",
            )
        return org

    # ------------------------------------------------------------------
    # Membership management
    # ------------------------------------------------------------------

    def add_member(
        self,
        *,
        org_id: uuid.UUID,
        email: str,
        role: str = ROLE_MEMBER,
    ) -> Membership:
        """Add a user (looked up by email) to an organisation.

        Raises:
            HTTPException 404: if no user with *email* exists.
            HTTPException 409: if the user is already a member.
            HTTPException 422: if *role* is invalid.
        """
        if role not in VALID_ROLES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid role '{role}'. Valid roles: {sorted(VALID_ROLES)}.",
            )

        user = self._users.get_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No user with email '{email}' found.",
            )

        existing = self._memberships.get_membership(org_id, user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a member of this organisation.",
            )

        return self._memberships.add_member(org_id=org_id, user_id=user.id, role=role)

    def remove_member(self, *, org_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Remove a member from an organisation.

        Raises:
            HTTPException 404: if the membership does not exist.
            HTTPException 403: if attempting to remove the last owner.
        """
        membership = self._memberships.get_membership(org_id, user_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found.",
            )

        # Prevent orphaning the org by removing the last owner
        if membership.role == ROLE_OWNER:
            owners = [
                m
                for m in self._memberships.list_org_members(org_id)
                if m.role == ROLE_OWNER
            ]
            if len(owners) <= 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot remove the last owner of an organisation.",
                )

        self._memberships.delete(membership)

    def list_members(self, org_id: uuid.UUID) -> list[Membership]:
        """Return all memberships for an organisation."""
        return self._memberships.list_org_members(org_id)

    def assert_membership(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Membership:
        """Return the membership or raise 403."""
        membership = self._memberships.get_membership(org_id, user_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this organisation.",
            )
        return membership

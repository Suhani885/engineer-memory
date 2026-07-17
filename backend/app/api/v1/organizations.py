"""Organisation routes — /api/v1/organizations/*"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import ActiveUser, OrgContext, get_db, require_role
from app.api.v1.schemas.organization import (
    AddMemberRequest,
    MemberResponse,
    OrgCreateRequest,
    OrgResponse,
    OrgWithMembershipResponse,
)
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


# ---------------------------------------------------------------------------
# Organisation CRUD
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=OrgWithMembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organisation",
)
def create_organization(
    body: OrgCreateRequest,
    current_user: ActiveUser,
    db: Session = Depends(get_db),
) -> OrgWithMembershipResponse:
    """Create a new organisation.  The authenticated user becomes the owner."""
    svc = OrganizationService(db)
    org, membership = svc.create_org(
        owner=current_user,
        name=body.name,
        slug=body.slug,
        plan=body.plan,
    )
    db.commit()
    db.refresh(org)
    db.refresh(membership)

    return OrgWithMembershipResponse(
        organization=OrgResponse.model_validate(org),
        membership=_membership_response(membership),
    )


@router.get(
    "/{slug}",
    response_model=OrgResponse,
    status_code=status.HTTP_200_OK,
    summary="Get an organisation by slug",
)
def get_organization(
    slug: str,
    ctx: OrgContext,
) -> OrgResponse:
    """Return organisation details.  Requires membership."""
    org, _ = ctx
    return OrgResponse.model_validate(org)


# ---------------------------------------------------------------------------
# Member management
# ---------------------------------------------------------------------------


@router.get(
    "/{slug}/members",
    response_model=list[MemberResponse],
    status_code=status.HTTP_200_OK,
    summary="List organisation members",
)
def list_members(
    slug: str,
    ctx: OrgContext,
    db: Session = Depends(get_db),
) -> list[MemberResponse]:
    """List all members of an organisation."""
    org, _ = ctx
    svc = OrganizationService(db)
    memberships = svc.list_members(org.id)
    return [_membership_response(m) for m in memberships]


@router.post(
    "/{slug}/members",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a member to an organisation",
    dependencies=[require_role("owner", "admin")],
)
def add_member(
    slug: str,
    body: AddMemberRequest,
    ctx: OrgContext,
    db: Session = Depends(get_db),
) -> MemberResponse:
    """Add an existing platform user to the organisation.  Requires owner or admin role."""
    org, _ = ctx
    svc = OrganizationService(db)
    membership = svc.add_member(org_id=org.id, email=body.email, role=body.role)
    db.commit()
    db.refresh(membership)
    return _membership_response(membership)


@router.delete(
    "/{slug}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Remove a member from an organisation",
    dependencies=[require_role("owner", "admin")],
)
def remove_member(
    slug: str,
    user_id: uuid.UUID,
    ctx: OrgContext,
    db: Session = Depends(get_db),
) -> Response:
    """Remove a user from the organisation.  Requires owner or admin role.
    Cannot remove the last owner."""
    org, _ = ctx
    svc = OrganizationService(db)
    svc.remove_member(org_id=org.id, user_id=user_id)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _membership_response(m) -> MemberResponse:
    """Build a MemberResponse, eagerly including flattened user fields."""
    return MemberResponse(
        id=m.id,
        user_id=m.user_id,
        organization_id=m.organization_id,
        role=m.role,
        created_at=m.created_at,
        user_email=m.user.email if m.user else None,
        user_full_name=m.user.full_name if m.user else None,
    )

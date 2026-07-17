"""Pydantic schemas for organisation and membership endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Organisation
# ---------------------------------------------------------------------------


class OrgCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9][a-z0-9\-]*[a-z0-9]$",
        description="URL-safe, globally unique handle (lowercase alphanumeric + hyphens).",
    )
    plan: str = Field(default="free")


class OrgResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    plan: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Membership
# ---------------------------------------------------------------------------


class MemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    role: str
    created_at: datetime
    # Flattened user fields
    user_email: str | None = None
    user_full_name: str | None = None

    model_config = {"from_attributes": True}


class AddMemberRequest(BaseModel):
    email: str = Field(description="Email address of an existing platform user.")
    role: str = Field(default="member", description="'owner', 'admin', or 'member'.")


class OrgWithMembershipResponse(BaseModel):
    """Returned when creating an org — includes the owner membership."""

    organization: OrgResponse
    membership: MemberResponse

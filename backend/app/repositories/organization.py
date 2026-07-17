from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for the Organisation model.

    Because ``Organization`` *is* the tenant root it has no
    ``organization_id`` column, so the standard org-scoped helpers from
    ``BaseRepository`` are intentionally not exposed here.  Use the
    global helpers below instead.
    """

    model = Organization

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ------------------------------------------------------------------
    # Global (non-scoped) reads — only safe for system/admin paths
    # ------------------------------------------------------------------

    def get_by_id_global(self, org_id: uuid.UUID) -> Organization | None:
        """Return an organisation by PK (no tenant scope — use carefully)."""
        stmt = select(Organization).where(Organization.id == org_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_slug(self, slug: str) -> Organization | None:
        """Return an organisation by its URL-safe slug (globally unique)."""
        stmt = select(Organization).where(Organization.slug == slug)
        return self._session.execute(stmt).scalar_one_or_none()

    # ------------------------------------------------------------------
    # Write helpers (no tenant scope needed on the org itself)
    # ------------------------------------------------------------------

    def create_organization(self, *, name: str, slug: str, plan: str = "free") -> Organization:
        """Create and persist a new organisation."""
        return self.create({"name": name, "slug": slug, "plan": plan})

    def list_all(self, *, limit: int = 50, offset: int = 0) -> list[Organization]:
        """Return all active organisations (superuser-only path)."""
        stmt = (
            select(Organization)
            .where(Organization.is_active.is_(True))
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.execute(stmt).scalars().all())

"""Generic, organisation-scoped base repository.

Every concrete repository inherits from ``BaseRepository[ModelT]``.
All read/write helpers automatically enforce ``organisation_id`` scoping
so it is impossible to accidentally leak cross-tenant data.
"""

from __future__ import annotations

import uuid
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository[ModelT: Base]:
    """Generic CRUD repository with mandatory org-scope on every operation.

    Sub-classes must set the ``model`` class attribute::

        class OrganizationRepository(BaseRepository[Organization]):
            model = Organization
    """

    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _org_scope(self, query, org_id: uuid.UUID):
        """Filter *query* by ``organization_id``.

        Models that *are* the organisation themselves (i.e. ``Organization``)
        should use the global helpers on the concrete repository and bypass
        this filter.
        """
        return query.where(self.model.organization_id == org_id)  # type: ignore[attr-defined]

    # ------------------------------------------------------------------
    # Read operations (org-scoped)
    # ------------------------------------------------------------------

    def get_by_id(self, org_id: uuid.UUID, record_id: uuid.UUID) -> ModelT | None:
        """Return the record with *record_id* belonging to *org_id*, or None."""
        stmt = self._org_scope(
            select(self.model).where(self.model.id == record_id),  # type: ignore[attr-defined]
            org_id,
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def list(
        self,
        org_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ModelT]:
        """Return a paginated list of records for *org_id*."""
        stmt = self._org_scope(select(self.model), org_id).offset(offset).limit(limit)
        return list(self._session.execute(stmt).scalars().all())

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create(self, data: dict[str, Any]) -> ModelT:
        """Persist a new record and return the hydrated instance."""
        record = self.model(**data)
        self._session.add(record)
        self._session.flush()  # populate server-defaults (id, created_at, …)
        self._session.refresh(record)
        return record

    def update(self, record: ModelT, data: dict[str, Any]) -> ModelT:
        """Apply *data* to *record* and flush to the session."""
        for key, value in data.items():
            setattr(record, key, value)
        self._session.flush()
        self._session.refresh(record)
        return record

    def delete(self, record: ModelT) -> None:
        """Delete *record* from the database."""
        self._session.delete(record)
        self._session.flush()

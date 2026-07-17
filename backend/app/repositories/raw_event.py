from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.raw_event import RawEvent
from app.repositories.base import BaseRepository


class RawEventRepository(BaseRepository[RawEvent]):
    """Repository for raw GitHub webhook payloads."""

    model = RawEvent

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def get_by_delivery_id(self, delivery_id: str) -> RawEvent | None:
        """Return a raw event by its GitHub delivery ID (global — no org scope)."""
        stmt = select(RawEvent).where(RawEvent.delivery_id == delivery_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def list_pending(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[RawEvent]:
        """Return pending events ordered by receipt time (oldest first).

        Used by background workers to fetch the next batch to process.
        """
        stmt = (
            select(RawEvent)
            .where(RawEvent.status == "pending")
            .order_by(RawEvent.received_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.execute(stmt).scalars().all())

    def list_for_org(
        self,
        org_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[RawEvent]:
        """Return events for a specific organisation (most recent first)."""
        stmt = (
            select(RawEvent)
            .where(RawEvent.organization_id == org_id)
            .order_by(RawEvent.received_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self._session.execute(stmt).scalars().all())

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def create_event(
        self,
        *,
        event_type: str,
        delivery_id: str,
        payload_json: dict[str, Any],
        organization_id: uuid.UUID | None = None,
    ) -> RawEvent:
        """Persist a new raw event and return it."""
        return self.create(
            {
                "event_type": event_type,
                "delivery_id": delivery_id,
                "payload_json": payload_json,
                "organization_id": organization_id,
                "processed": False,
                "processing_attempts": 0,
                "status": "pending",
            }
        )

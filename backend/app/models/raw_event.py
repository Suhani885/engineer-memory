from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class RawEvent(UUIDPrimaryKeyMixin, Base):
    """Immutable store of raw GitHub webhook payloads.

    Fields
    ------
    organization_id
        Nullable FK to organizations.
    event_type
        The GitHub event type (e.g. "pull_request").
    delivery_id
        The GitHub delivery ID to prevent duplicates.
    payload_json
        The exact JSON payload as received.
    received_at
        Timestamp of receipt.
    processed
        Whether this event has been processed.
    processing_attempts
        Number of times processing was attempted.
    status
        Status string: 'pending', 'processing', 'completed', 'failed'.
    """

    __tablename__ = "raw_events"

    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    delivery_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    processed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    processing_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)

    # Relationships
    organization: Mapped[Organization | None] = relationship("Organization")

    def __repr__(self) -> str:
        return (
            f"<RawEvent id={self.id!s} "
            f"type={self.event_type!r} "
            f"status={self.status!r}>"
        )

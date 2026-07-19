# ruff: noqa: E501
from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class EngineeringDigest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """AI-generated engineering digests (Daily/Weekly)."""

    __tablename__ = "engineering_digests"

    digest_type: Mapped[str] = mapped_column(VARCHAR(50), nullable=False, index=True) # "daily" or "weekly"
    period_start: Mapped[datetime.datetime] = mapped_column(nullable=False)
    period_end: Mapped[datetime.datetime] = mapped_column(nullable=False)
    
    markdown_content: Mapped[str] = mapped_column(TEXT, nullable=False)
    structured_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")

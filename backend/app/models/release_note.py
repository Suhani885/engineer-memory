# ruff: noqa: E501
from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy.dialects.postgresql import JSONB, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ReleaseNote(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """AI-generated release notes."""

    __tablename__ = "release_notes"

    start_tag_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    end_tag_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    start_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    end_date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    
    markdown_content: Mapped[str] = mapped_column(TEXT, nullable=False)
    structured_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, server_default="{}")

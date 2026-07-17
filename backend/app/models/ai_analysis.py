# ruff: noqa: E501
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest


class AIAnalysis(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """OpenAI generated structural analysis for a Pull Request."""

    __tablename__ = "ai_analyses"

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    summary: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    engineering_impact: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    business_impact: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    affected_modules: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    security_impact: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    database_changes: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    api_changes: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    configuration_changes: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    risk_level: Mapped[str] = mapped_column(VARCHAR, nullable=False, default="Low")
    deployment_notes: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    testing_required: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    breaking_changes: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    release_notes: Mapped[str] = mapped_column(TEXT, nullable=False, default="")

    # Relationships
    pull_request: Mapped[PullRequest] = relationship("PullRequest", back_populates="ai_analysis")

    def __repr__(self) -> str:
        return f"<AIAnalysis id={self.id!s} pr_id={self.pull_request_id!s}>"

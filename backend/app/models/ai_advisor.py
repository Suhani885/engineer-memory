# ruff: noqa: E501
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest


class AIAdvisor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """OpenAI generated engineering advisory insights for a Pull Request."""

    __tablename__ = "ai_advisors"

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    missing_test_cases: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    potential_edge_cases: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    suggested_documentation_updates: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    possible_performance_issues: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    security_recommendations: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    related_files_that_may_need_changes: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    rollback_strategy: Mapped[str] = mapped_column(TEXT, nullable=False, default="")
    deployment_checklist: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    future_refactoring_suggestions: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    suggested_reviewers: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)

    # Relationships
    pull_request: Mapped[PullRequest] = relationship("PullRequest", back_populates="ai_advisor")

    def __repr__(self) -> str:
        return f"<AIAdvisor id={self.id!s} pr_id={self.pull_request_id!s}>"

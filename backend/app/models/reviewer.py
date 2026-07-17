from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest


class Reviewer(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A review submitted on a synchronized GitHub Pull Request."""

    __tablename__ = "reviewers"

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    github_review_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    github_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    github_login: Mapped[str] = mapped_column(String(255), nullable=False)
    
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    pull_request: Mapped[PullRequest] = relationship("PullRequest", back_populates="reviewers")

    def __repr__(self) -> str:
        return f"<Reviewer id={self.id!s} login={self.github_login!r}>"

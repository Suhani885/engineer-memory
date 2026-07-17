from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest


class Commit(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A commit belonging to a synchronized GitHub Pull Request."""

    __tablename__ = "commits"

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    github_commit_sha: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_github_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    author_login: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_merge_commit: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    pull_request: Mapped[PullRequest] = relationship("PullRequest", back_populates="commits")

    def __repr__(self) -> str:
        return f"<Commit id={self.id!s} sha={self.github_commit_sha!r}>"

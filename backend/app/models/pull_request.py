from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.ai_advisor import AIAdvisor
    from app.models.ai_analysis import AIAnalysis
    from app.models.commit import Commit
    from app.models.github_repository import GitHubRepository
    from app.models.parsed_change import ParsedChange
    from app.models.pull_request_file import PullRequestFile
    from app.models.reviewer import Reviewer


class PullRequest(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A synchronized Pull Request from GitHub."""

    __tablename__ = "pull_requests"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("github_repositories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    github_pr_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    
    author_github_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    author_login: Mapped[str] = mapped_column(String(255), nullable=False)
    
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    merge_commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)
    
    additions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deletions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    changed_files: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    repository: Mapped[GitHubRepository] = relationship("GitHubRepository")
    files: Mapped[list[PullRequestFile]] = relationship(
        "PullRequestFile", back_populates="pull_request", cascade="all, delete-orphan"
    )
    commits: Mapped[list[Commit]] = relationship(
        "Commit", back_populates="pull_request", cascade="all, delete-orphan"
    )
    reviewers: Mapped[list[Reviewer]] = relationship(
        "Reviewer", back_populates="pull_request", cascade="all, delete-orphan"
    )
    parsed_change: Mapped[ParsedChange | None] = relationship(
        "ParsedChange", back_populates="pull_request", cascade="all, delete-orphan", uselist=False
    )
    ai_analysis: Mapped[AIAnalysis | None] = relationship(
        "AIAnalysis", back_populates="pull_request", cascade="all, delete-orphan", uselist=False
    )
    ai_advisor: Mapped[AIAdvisor | None] = relationship(
        "AIAdvisor", back_populates="pull_request", cascade="all, delete-orphan", uselist=False
    )

    def __repr__(self) -> str:
        return f"<PullRequest id={self.id!s} number={self.number}>"

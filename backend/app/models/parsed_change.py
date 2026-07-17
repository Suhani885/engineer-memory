# ruff: noqa: E501
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.pull_request import PullRequest


class ParsedChange(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Structured engineering changes parsed from a Pull Request."""

    __tablename__ = "parsed_changes"

    pull_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pull_requests.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Parsed structural outputs
    functions_modified: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    classes_modified: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    routes: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    api_endpoints: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    sql_migrations: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dependencies: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    configuration: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    environment_variables: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    frontend_components: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    backend_services: Mapped[list[str]] = mapped_column(ARRAY(VARCHAR), nullable=False, default=list)
    tests: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Relationships
    pull_request: Mapped[PullRequest] = relationship("PullRequest", back_populates="parsed_change")

    def __repr__(self) -> str:
        return f"<ParsedChange id={self.id!s} pr_id={self.pull_request_id!s}>"

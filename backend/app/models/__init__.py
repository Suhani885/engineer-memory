"""SQLAlchemy persistence models.

Import all models here so that:
  1. Alembic autogenerate can discover every table.
  2. SQLAlchemy relationship resolution works across modules.
"""

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.ai_advisor import AIAdvisor
from app.models.ai_analysis import AIAnalysis
from app.models.commit import Commit
from app.models.github_installation import GitHubInstallation
from app.models.github_repository import GitHubRepository
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.parsed_change import ParsedChange
from app.models.pull_request import PullRequest
from app.models.pull_request_file import PullRequestFile
from app.models.raw_event import RawEvent
from app.models.reviewer import Reviewer
from app.models.user import User
from app.models.engineering_digest import EngineeringDigest
from app.models.release_note import ReleaseNote

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "Organization",
    "User",
    "Membership",
    "GitHubInstallation",
    "GitHubRepository",
    "RawEvent",
    "PullRequest",
    "PullRequestFile",
    "Commit",
    "Reviewer",
    "ParsedChange",
    "AIAnalysis",
    "AIAdvisor",
    "EngineeringDigest",
    "ReleaseNote",
]

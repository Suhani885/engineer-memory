"""Pydantic schemas for GitHub webhook payloads.

Only the fields we actively read are declared here.  All schemas use
``model_config = ConfigDict(extra="allow")`` so that unknown fields
from GitHub's payload are silently ignored rather than raising
validation errors — this keeps the ingest path resilient to GitHub
adding new fields in the future.

Reference: https://docs.github.com/en/webhooks/webhook-events-and-payloads
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class _FlexModel(BaseModel):
    """Base model that silently ignores extra fields."""

    model_config = ConfigDict(extra="allow")


# ---------------------------------------------------------------------------
# GitHub object fragments
# ---------------------------------------------------------------------------


class GitHubUser(_FlexModel):
    """Minimal GitHub user / actor object."""

    id: int
    login: str
    type: str = "User"


class GitHubInstallationRef(_FlexModel):
    """The ``installation`` object embedded in webhook payloads."""

    id: int
    node_id: str = ""


class GitHubRepo(_FlexModel):
    """The ``repository`` object embedded in webhook payloads."""

    id: int
    name: str
    full_name: str
    private: bool
    default_branch: str = "main"
    owner: GitHubUser


class PullRequestHead(_FlexModel):
    ref: str
    sha: str


class PullRequestBase(_FlexModel):
    ref: str
    sha: str


class PullRequest(_FlexModel):
    """The ``pull_request`` object inside a pull_request webhook event."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: str  # "open" | "closed"
    merged: bool
    merged_at: str | None = None
    merge_commit_sha: str | None = None
    head: PullRequestHead
    base: PullRequestBase
    user: GitHubUser
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    html_url: str = ""


# ---------------------------------------------------------------------------
# Top-level event payloads
# ---------------------------------------------------------------------------


class PullRequestEvent(_FlexModel):
    """Schema for the ``pull_request`` webhook event.

    GitHub sends this for every action on a pull request (opened, closed,
    synchronize, …).  We only persist events where
    ``action == "closed"`` AND ``pull_request.merged == True``.
    """

    action: str
    number: int
    pull_request: PullRequest
    repository: GitHubRepo
    sender: GitHubUser
    installation: GitHubInstallationRef | None = None
    organization: dict[str, Any] | None = None


class WebhookResponse(BaseModel):
    """Standard response body for the webhook endpoint."""

    status: str
    message: str = ""
    event_id: str | None = None

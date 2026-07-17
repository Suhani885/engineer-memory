"""github_sync_tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-17

Creates tables for GitHub Sync:
  - pull_requests
  - pull_request_files
  - commits
  - reviewers
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # pull_requests
    # ------------------------------------------------------------------
    op.create_table(
        "pull_requests",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("repository_id", sa.UUID(), nullable=False),
        sa.Column("github_pr_id", sa.BigInteger(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("state", sa.String(length=50), nullable=False),
        sa.Column("author_github_id", sa.BigInteger(), nullable=False),
        sa.Column("author_login", sa.String(length=255), nullable=False),
        sa.Column("merged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("merge_commit_sha", sa.String(length=40), nullable=True),
        sa.Column("additions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("changed_files", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["repository_id"], ["github_repositories.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_pr_id", name="uq_pull_requests_github_pr_id"),
    )
    op.create_index("ix_pull_requests_repository_id", "pull_requests", ["repository_id"])
    op.create_index(
        "ix_pull_requests_github_pr_id", "pull_requests", ["github_pr_id"], unique=True
    )

    # ------------------------------------------------------------------
    # pull_request_files
    # ------------------------------------------------------------------
    op.create_table(
        "pull_request_files",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("pull_request_id", sa.UUID(), nullable=False),
        sa.Column("github_sha", sa.String(length=40), nullable=False),
        sa.Column("filename", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("additions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("changes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("patch", sa.Text(), nullable=True),
        sa.Column("raw_url", sa.String(length=2000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["pull_request_id"], ["pull_requests.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_pull_request_files_pull_request_id", "pull_request_files", ["pull_request_id"]
    )

    # ------------------------------------------------------------------
    # commits
    # ------------------------------------------------------------------
    op.create_table(
        "commits",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("pull_request_id", sa.UUID(), nullable=False),
        sa.Column("github_commit_sha", sa.String(length=40), nullable=False),
        sa.Column("author_name", sa.String(length=255), nullable=True),
        sa.Column("author_email", sa.String(length=255), nullable=True),
        sa.Column("author_github_id", sa.BigInteger(), nullable=True),
        sa.Column("author_login", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("is_merge_commit", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["pull_request_id"], ["pull_requests.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pull_request_id", "github_commit_sha", name="uq_commits_pr_sha"),
    )
    op.create_index("ix_commits_pull_request_id", "commits", ["pull_request_id"])
    op.create_index("ix_commits_github_commit_sha", "commits", ["github_commit_sha"])

    # ------------------------------------------------------------------
    # reviewers
    # ------------------------------------------------------------------
    op.create_table(
        "reviewers",
        sa.Column(
            "id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False
        ),
        sa.Column("pull_request_id", sa.UUID(), nullable=False),
        sa.Column("github_review_id", sa.BigInteger(), nullable=False),
        sa.Column("github_user_id", sa.BigInteger(), nullable=False),
        sa.Column("github_login", sa.String(length=255), nullable=False),
        sa.Column("state", sa.String(length=50), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["pull_request_id"], ["pull_requests.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_review_id", name="uq_reviewers_github_review_id"),
    )
    op.create_index("ix_reviewers_pull_request_id", "reviewers", ["pull_request_id"])
    op.create_index(
        "ix_reviewers_github_review_id", "reviewers", ["github_review_id"], unique=True
    )


def downgrade() -> None:
    op.drop_table("reviewers")
    op.drop_table("commits")
    op.drop_table("pull_request_files")
    op.drop_table("pull_requests")

"""github_integration

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-17

Creates three tables for GitHub App integration:
  - github_installations
  - github_repositories
  - raw_events
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # github_installations
    # ------------------------------------------------------------------
    op.create_table(
        "github_installations",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("github_installation_id", sa.BigInteger(), nullable=False),
        sa.Column("github_app_id", sa.String(length=100), nullable=False),
        sa.Column("github_account_login", sa.String(length=255), nullable=False),
        sa.Column("github_account_type", sa.String(length=50), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("events", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_installation_id", name="uq_github_installation_id"),
    )
    op.create_index(
        "ix_github_installations_organization_id",
        "github_installations",
        ["organization_id"],
    )
    op.create_index(
        "ix_github_installations_github_installation_id",
        "github_installations",
        ["github_installation_id"],
        unique=True,
    )

    # ------------------------------------------------------------------
    # github_repositories
    # ------------------------------------------------------------------
    op.create_table(
        "github_repositories",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("installation_id", sa.UUID(), nullable=False),
        sa.Column("github_repo_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("default_branch", sa.String(length=255), nullable=False, server_default="main"),
        sa.Column("permissions", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["installation_id"],
            ["github_installations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_repo_id", name="uq_github_repo_id"),
    )
    op.create_index(
        "ix_github_repositories_organization_id",
        "github_repositories",
        ["organization_id"],
    )
    op.create_index(
        "ix_github_repositories_installation_id",
        "github_repositories",
        ["installation_id"],
    )
    op.create_index(
        "ix_github_repositories_github_repo_id",
        "github_repositories",
        ["github_repo_id"],
        unique=True,
    )
    op.create_index(
        "ix_github_repositories_full_name",
        "github_repositories",
        ["full_name"],
    )

    # ------------------------------------------------------------------
    # raw_events
    # ------------------------------------------------------------------
    op.create_table(
        "raw_events",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("organization_id", sa.UUID(), nullable=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("delivery_id", sa.String(length=100), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("processing_attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="'pending'"),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_id", name="uq_raw_event_delivery_id"),
    )
    op.create_index("ix_raw_events_organization_id", "raw_events", ["organization_id"])
    op.create_index("ix_raw_events_event_type", "raw_events", ["event_type"])
    op.create_index("ix_raw_events_delivery_id", "raw_events", ["delivery_id"], unique=True)
    op.create_index("ix_raw_events_received_at", "raw_events", ["received_at"])
    op.create_index("ix_raw_events_status", "raw_events", ["status"])


def downgrade() -> None:
    op.drop_table("raw_events")
    op.drop_table("github_repositories")
    op.drop_table("github_installations")

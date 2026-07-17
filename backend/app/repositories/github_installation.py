from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.github_installation import GitHubInstallation
from app.repositories.base import BaseRepository


class GitHubInstallationRepository(BaseRepository[GitHubInstallation]):
    """Repository for GitHubInstallation.

    Installations are org-level resources, but they have no ``organization_id``
    on the base query path because lookups by ``github_installation_id`` are
    global (called at webhook receipt time before the org is identified).
    """

    model = GitHubInstallation

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ------------------------------------------------------------------
    # Global reads (called before tenant context is established)
    # ------------------------------------------------------------------

    def get_by_github_id(self, github_installation_id: int) -> GitHubInstallation | None:
        """Return an installation by GitHub's numeric installation ID."""
        stmt = select(GitHubInstallation).where(
            GitHubInstallation.github_installation_id == github_installation_id
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def get_by_account_login(
        self, account_login: str
    ) -> GitHubInstallation | None:
        """Return the most-recently-created active installation for a GitHub account."""
        stmt = (
            select(GitHubInstallation)
            .where(
                GitHubInstallation.github_account_login == account_login,
                GitHubInstallation.is_active.is_(True),
            )
            .order_by(GitHubInstallation.created_at.desc())
            .limit(1)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    # ------------------------------------------------------------------
    # Write helpers
    # ------------------------------------------------------------------

    def upsert_installation(
        self,
        *,
        organization_id,
        github_installation_id: int,
        github_app_id: str,
        github_account_login: str,
        github_account_type: str,
        permissions: dict,
        events: list,
    ) -> GitHubInstallation:
        """Create or reactivate an installation record.

        If an installation with ``github_installation_id`` already exists
        (e.g. a reinstall), it is reactivated and its metadata updated in
        place rather than creating a duplicate row.
        """
        existing = self.get_by_github_id(github_installation_id)
        if existing:
            return self.update(
                existing,
                {
                    "organization_id": organization_id,
                    "github_app_id": github_app_id,
                    "github_account_login": github_account_login,
                    "github_account_type": github_account_type,
                    "permissions": permissions,
                    "events": events,
                    "is_active": True,
                },
            )
        return self.create(
            {
                "organization_id": organization_id,
                "github_installation_id": github_installation_id,
                "github_app_id": github_app_id,
                "github_account_login": github_account_login,
                "github_account_type": github_account_type,
                "permissions": permissions,
                "events": events,
            }
        )

    def deactivate(self, installation: GitHubInstallation) -> GitHubInstallation:
        """Mark an installation as inactive (app was uninstalled)."""
        return self.update(installation, {"is_active": False})

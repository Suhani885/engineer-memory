from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.commit import Commit
from app.models.github_repository import GitHubRepository
from app.models.pull_request import PullRequest
from app.models.pull_request_file import PullRequestFile
from app.models.reviewer import Reviewer


class GitHubSyncRepository:
    """Repository for upserting synchronized GitHub data."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_repository_by_github_id(self, github_repo_id: int) -> GitHubRepository | None:
        """Find a repository by its GitHub ID."""
        stmt = select(GitHubRepository).where(GitHubRepository.github_repo_id == github_repo_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def upsert_pull_request(self, repo_id: uuid.UUID, pr_data: dict[str, Any]) -> PullRequest:
        """Upsert a pull request based on GitHub PR ID."""
        github_pr_id = pr_data["id"]
        
        # Parse merged_at if available
        merged_at = None
        if pr_data.get("merged_at"):
            # e.g., '2026-07-17T05:00:00Z'
            try:
                merged_at_str = pr_data["merged_at"].replace("Z", "+00:00")
                merged_at = datetime.fromisoformat(merged_at_str)
            except Exception:
                pass

        user = pr_data.get("user", {})

        stmt = insert(PullRequest).values(
            repository_id=repo_id,
            github_pr_id=github_pr_id,
            number=pr_data["number"],
            title=pr_data.get("title", ""),
            body=pr_data.get("body", ""),
            state=pr_data.get("state", "open"),
            author_github_id=user.get("id", 0),
            author_login=user.get("login", ""),
            merged_at=merged_at,
            merge_commit_sha=pr_data.get("merge_commit_sha"),
            additions=pr_data.get("additions", 0),
            deletions=pr_data.get("deletions", 0),
            changed_files=pr_data.get("changed_files", 0),
        )

        stmt = stmt.on_conflict_do_update(
            index_elements=["github_pr_id"],
            set_={
                "title": stmt.excluded.title,
                "body": stmt.excluded.body,
                "state": stmt.excluded.state,
                "merged_at": stmt.excluded.merged_at,
                "merge_commit_sha": stmt.excluded.merge_commit_sha,
                "additions": stmt.excluded.additions,
                "deletions": stmt.excluded.deletions,
                "changed_files": stmt.excluded.changed_files,
                "updated_at": datetime.now(),
            }
        ).returning(PullRequest)

        return self._session.execute(stmt).scalar_one()

    def sync_pull_request_files(self, pr_id: uuid.UUID, files_data: list[dict[str, Any]]) -> None:
        """Sync files for a pull request (replaces existing)."""
        # Clear existing files for simplicity
        # (since PR files can be renamed/deleted, a full replace is safest)
        self._session.query(PullRequestFile).filter_by(pull_request_id=pr_id).delete()
        
        files_to_insert = []
        for file in files_data:
            files_to_insert.append(
                PullRequestFile(
                    pull_request_id=pr_id,
                    github_sha=file.get("sha", ""),
                    filename=file.get("filename", ""),
                    status=file.get("status", ""),
                    additions=file.get("additions", 0),
                    deletions=file.get("deletions", 0),
                    changes=file.get("changes", 0),
                    patch=file.get("patch"),
                    raw_url=file.get("raw_url"),
                )
            )
        if files_to_insert:
            self._session.bulk_save_objects(files_to_insert)

    def sync_commits(
        self,
        pr_id: uuid.UUID,
        commits_data: list[dict[str, Any]],
        merge_commit_data: dict[str, Any] | None = None,
    ) -> None:
        """Upsert commits for a pull request."""
        # Include merge commit in the list if available
        all_commits = list(commits_data)
        if merge_commit_data:
            merge_commit_data["_is_merge_commit"] = True
            all_commits.append(merge_commit_data)

        for commit_obj in all_commits:
            sha = commit_obj.get("sha")
            if not sha:
                continue

            commit_info = commit_obj.get("commit", {})
            author_info = commit_info.get("author", {})
            
            # Github user vs git author
            github_author = commit_obj.get("author") or {}
            
            is_merge = commit_obj.get("_is_merge_commit", False)

            stmt = insert(Commit).values(
                pull_request_id=pr_id,
                github_commit_sha=sha,
                author_name=author_info.get("name"),
                author_email=author_info.get("email"),
                author_github_id=github_author.get("id"),
                author_login=github_author.get("login"),
                message=commit_info.get("message"),
                is_merge_commit=is_merge,
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=["pull_request_id", "github_commit_sha"],
                set_={
                    "author_name": stmt.excluded.author_name,
                    "author_email": stmt.excluded.author_email,
                    "author_github_id": stmt.excluded.author_github_id,
                    "author_login": stmt.excluded.author_login,
                    "message": stmt.excluded.message,
                    "is_merge_commit": stmt.excluded.is_merge_commit,
                    "updated_at": datetime.now(),
                }
            )
            self._session.execute(stmt)

    def sync_reviews(self, pr_id: uuid.UUID, reviews_data: list[dict[str, Any]]) -> None:
        """Upsert reviews for a pull request."""
        for review in reviews_data:
            github_review_id = review.get("id")
            if not github_review_id:
                continue

            user = review.get("user") or {}
            
            submitted_at = None
            if review.get("submitted_at"):
                try:
                    dt_str = review["submitted_at"].replace("Z", "+00:00")
                    submitted_at = datetime.fromisoformat(dt_str)
                except Exception:
                    pass

            stmt = insert(Reviewer).values(
                pull_request_id=pr_id,
                github_review_id=github_review_id,
                github_user_id=user.get("id", 0),
                github_login=user.get("login", ""),
                state=review.get("state", ""),
                submitted_at=submitted_at,
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=["github_review_id"],
                set_={
                    "state": stmt.excluded.state,
                    "submitted_at": stmt.excluded.submitted_at,
                    "updated_at": datetime.now(),
                }
            )
            self._session.execute(stmt)

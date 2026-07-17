"""Celery tasks for processing background jobs."""

from __future__ import annotations

import logging
from typing import Any

from app.ai.analyzer import analyze_pull_request, generate_advisor_insights
from app.core.db import SessionLocal
from app.parser.diff_parser import EngineeringParser
from app.repositories.github_sync import GitHubSyncRepository
from app.services.github_client import GitHubClient, GitHubClientError
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_raw_event(self: Any, raw_event_id: str) -> None:
    """Process a raw GitHub webhook event.

    Steps:
    1. Load RawEvent from DB.
    2. Extract repository, PR number, installation ID.
    3. Call GitHub REST API to fetch full PR details.
    4. Mark event as processed.
    """
    db = SessionLocal()
    try:
        from app.models.raw_event import RawEvent
        raw_event = db.get(RawEvent, raw_event_id)

        if not raw_event:
            logger.error("RawEvent %s not found.", raw_event_id)
            return

        if raw_event.status == "completed":
            logger.info("RawEvent %s is already completed.", raw_event_id)
            return

        # Mark as processing
        raw_event.status = "processing"
        raw_event.processing_attempts += 1
        db.commit()
        db.refresh(raw_event)

        payload = raw_event.payload_json
        
        # Validate payload format
        action = payload.get("action")
        pull_request = payload.get("pull_request", {})
        merged = pull_request.get("merged")

        if action != "closed" or not merged:
            logger.info("RawEvent %s is not a merged PR, marking completed.", raw_event_id)
            raw_event.status = "completed"
            raw_event.processed = True
            db.commit()
            return

        # Extract repo, PR number, and installation ID
        repo_data = payload.get("repository", {})
        owner = repo_data.get("owner", {}).get("login")
        repo_name = repo_data.get("name")
        pr_number = pull_request.get("number")
        
        installation_data = payload.get("installation", {})
        installation_id = installation_data.get("id")

        if not all([owner, repo_name, pr_number, installation_id]):
            logger.error("RawEvent %s missing required fields for GitHub API.", raw_event_id)
            raw_event.status = "failed"
            db.commit()
            return

        # Initialize GitHub Client and Repositories
        gh_client = GitHubClient()
        sync_repo = GitHubSyncRepository(db)

        # 1. Resolve Repository
        github_repo_id = repo_data.get("id")
        repository = sync_repo.get_repository_by_github_id(github_repo_id)
        if not repository:
            logger.error("Repository with github_id=%s not found in DB.", github_repo_id)
            raw_event.status = "failed"
            db.commit()
            return

        logger.info(
            "Fetching PR %s/%s#%s for event %s",
            owner,
            repo_name,
            pr_number,
            raw_event_id,
        )

        try:
            # Call GitHub REST API sequentially
            pr_details = gh_client.fetch_pull_request(
                owner=owner, repo=repo_name, pr_number=pr_number, installation_id=installation_id
            )
            files_data = gh_client.fetch_pull_request_files(
                owner=owner, repo=repo_name, pr_number=pr_number, installation_id=installation_id
            )
            commits_data = gh_client.fetch_pull_request_commits(
                owner=owner, repo=repo_name, pr_number=pr_number, installation_id=installation_id
            )
            reviews_data = gh_client.fetch_pull_request_reviews(
                owner=owner, repo=repo_name, pr_number=pr_number, installation_id=installation_id
            )

            # Fetch merge commit if available
            merge_commit_sha = pr_details.get("merge_commit_sha")
            merge_commit_data = None
            if merge_commit_sha:
                try:
                    merge_commit_data = gh_client.fetch_commit(
                        owner=owner,
                        repo=repo_name,
                        commit_sha=merge_commit_sha,
                        installation_id=installation_id,
                    )
                except GitHubClientError as e:
                    logger.warning("Could not fetch merge commit %s: %s", merge_commit_sha, e)

            # 2. Persist data via GitHubSyncRepository
            pr_record = sync_repo.upsert_pull_request(repository.id, pr_details)
            sync_repo.sync_pull_request_files(pr_record.id, files_data)
            sync_repo.sync_commits(pr_record.id, commits_data, merge_commit_data)
            sync_repo.sync_reviews(pr_record.id, reviews_data)

            # 3. Parse Structural Changes (No AI)
            db_files = pr_record.files
            parser = EngineeringParser()
            parsed_data = parser.parse(db_files)
            sync_repo.upsert_parsed_change(pr_record.id, parsed_data)

            # 4. Deep AI Analysis (Summary)
            ai_data = analyze_pull_request(pr_details, files_data, parsed_data)
            if ai_data:
                sync_repo.upsert_ai_analysis(pr_record.id, ai_data)

            # 5. Deep AI Advisor Insights
            advisor_data = generate_advisor_insights(pr_details, files_data, parsed_data)
            if advisor_data:
                sync_repo.upsert_ai_advisor(pr_record.id, advisor_data)

            # Commit all changes to DB
            db.commit()

        except GitHubClientError as exc:
            logger.error("GitHub API error processing %s: %s", raw_event_id, exc)
            db.rollback()
            raise self.retry(exc=exc) from exc
        except Exception as exc:
            # If the DB insert fails (e.g. constraints) we should also rollback and retry
            logger.error("Database sync error for event %s: %s", raw_event_id, exc)
            db.rollback()
            raise self.retry(exc=exc) from exc

        # Mark completed
        raw_event.status = "completed"
        raw_event.processed = True
        db.commit()
        logger.info("RawEvent %s processing completed successfully.", raw_event_id)

    except Exception as exc:
        db.rollback()
        # Fallback error handling if it's not a GitHubClientError
        if not isinstance(exc, GitHubClientError):
            logger.exception("Unexpected error processing RawEvent %s: %s", raw_event_id, exc)
            
        # Re-fetch the event to update its status reliably if db.rollback() was called
        try:
            from app.models.raw_event import RawEvent
            raw_event = db.get(RawEvent, raw_event_id)
            if raw_event:
                raw_event.status = "failed"
                db.commit()
        except Exception:
            db.rollback()

        # Reraise so Celery knows it failed and can retry if applicable
        raise self.retry(exc=exc) from exc
    finally:
        db.close()

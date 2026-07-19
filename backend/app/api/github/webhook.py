"""GitHub App webhook endpoint — POST /github/webhook

Design
------
This endpoint is called by GitHub, not by API clients.  It has no JWT auth.

Ingest pipeline (synchronous, completes before returning HTTP 200):

    1. Read raw body bytes (needed for HMAC verification).
    2. Verify HMAC-SHA256 signature  →  401 if invalid.
    3. Check X-GitHub-Event header.
       * Anything other than "pull_request"  →  200 {"status": "ignored"}.
    4. Parse JSON payload loosely.
    5. Filter: action == "closed" AND pull_request.merged == True.
       * Other actions (opened, synchronize, …)  →  200 {"status": "ignored"}.
    6. Idempotency check: if this delivery ID was already stored  →  200 {"status": "duplicate"}.
    7. Resolve the GitHub installation to an internal org (best-effort).
    8. Write to raw_events table exactly as received.
    9. Return HTTP 200 {"status": "accepted", "event_id": "<uuid>"}.

Workers consume pending raw_events asynchronously.
"""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.github.schemas import WebhookResponse
from app.github.security import verify_webhook_signature
from app.repositories.github_installation import GitHubInstallationRepository
from app.repositories.raw_event import RawEventRepository
from app.workers.tasks import process_raw_event

logger = logging.getLogger(__name__)

router = APIRouter(tags=["github"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_EVENT_PULL_REQUEST = "pull_request"
_ACTION_CLOSED = "closed"


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/webhook",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Receive GitHub App webhook events",
    description=(
        "Receives and stores merged pull-request events from the GitHub App. "
        "The endpoint verifies the HMAC-SHA256 signature, filters for merged PRs, "
        "and stores the raw payload for background processing. "
        "All other event types are acknowledged and discarded immediately."
    ),
)
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
) -> WebhookResponse:
    # ------------------------------------------------------------------
    # 1. Read raw body — must happen before any parsing so HMAC is correct
    # ------------------------------------------------------------------
    body: bytes = await request.body()

    # ------------------------------------------------------------------
    # 2. Verify HMAC-SHA256 signature
    # ------------------------------------------------------------------
    settings = get_settings()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_webhook_signature(body, signature, settings.github_webhook_secret):
        logger.warning(
            "GitHub webhook signature verification failed "
            "(delivery=%s, event=%s)",
            request.headers.get("X-GitHub-Delivery", "unknown"),
            request.headers.get("X-GitHub-Event", "unknown"),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature.",
        )

    # ------------------------------------------------------------------
    # 3. Check event type — immediately acknowledge anything we don't handle
    # ------------------------------------------------------------------
    event_type = request.headers.get("X-GitHub-Event", "")
    delivery_id = request.headers.get("X-GitHub-Delivery", "")

    if event_type != _EVENT_PULL_REQUEST:
        logger.debug("Ignored GitHub event type %r (delivery=%s)", event_type, delivery_id)
        return WebhookResponse(
            status="ignored",
            message=f"Event type '{event_type}' is not handled.",
        )

    # ------------------------------------------------------------------
    # 4. Parse JSON payload (loose parsing, no strict schema validation)
    # ------------------------------------------------------------------
    try:
        raw_payload: dict = json.loads(body)
    except (json.JSONDecodeError, ValueError) as exc:
        logger.error("Failed to parse webhook JSON body: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed JSON payload.",
        ) from exc

    # ------------------------------------------------------------------
    # 5. Filter: only closed + merged pull requests
    # ------------------------------------------------------------------
    action = raw_payload.get("action")
    pull_request = raw_payload.get("pull_request", {})
    merged = pull_request.get("merged")

    if action != _ACTION_CLOSED or not merged:
        logger.debug(
            "Ignored pull_request event (action=%r, merged=%r, delivery=%s)",
            action,
            merged,
            delivery_id,
        )
        return WebhookResponse(
            status="ignored",
            message=f"pull_request action '{action}' / merged={merged} is not handled.",
        )

    # ------------------------------------------------------------------
    # 6. Idempotency — deduplicate on X-GitHub-Delivery
    # ------------------------------------------------------------------
    raw_repo = RawEventRepository(db)

    if delivery_id and raw_repo.get_by_delivery_id(delivery_id):
        logger.info("Duplicate webhook delivery %s — already stored.", delivery_id)
        return WebhookResponse(
            status="duplicate",
            message=f"Delivery '{delivery_id}' was already recorded.",
        )

    # ------------------------------------------------------------------
    # 7. Resolve / auto-create org → installation → repository chain
    # ------------------------------------------------------------------
    from sqlalchemy import select

    from app.models.github_installation import GitHubInstallation
    from app.models.github_repository import GitHubRepository
    from app.models.organization import Organization

    org_id = None
    installation_db_id = None
    installation_data = raw_payload.get("installation", {})
    installation_github_id = installation_data.get("id")
    repo_data = raw_payload.get("repository", {})
    sender = raw_payload.get("sender", {})
    account = installation_data.get("account", {})

    # Step 7a: resolve/create Organization
    inst_repo_obj = GitHubInstallationRepository(db)
    installation_record = None
    if installation_github_id:
        installation_record = inst_repo_obj.get_by_github_id(installation_github_id)
        if installation_record:
            org_id = installation_record.organization_id
            installation_db_id = installation_record.id

    if org_id is None:
        # Auto-create org named after the GitHub account that installed the app
        account_login = account.get("login") or sender.get("login") or "github"
        existing_org = db.execute(
            select(Organization).where(Organization.slug == account_login)
        ).scalar_one_or_none()
        if existing_org:
            org_id = existing_org.id
        else:
            new_org = Organization(
                name=account_login,
                slug=account_login,
                plan="free",
                is_active=True,
            )
            db.add(new_org)
            db.flush()
            org_id = new_org.id
            logger.info("Auto-created organization slug=%s for GitHub account", account_login)

    # Step 7b: resolve/create GitHubInstallation
    if installation_github_id and installation_db_id is None:
        new_installation = GitHubInstallation(
            organization_id=org_id,
            github_installation_id=installation_github_id,
            github_app_id=str(settings.github_app_id or "0"),
            github_account_login=account.get("login", "unknown"),
            github_account_type=account.get("type", "User"),
            permissions=installation_data.get("permissions", {}),
            events=installation_data.get("events", []),
            is_active=True,
        )
        db.add(new_installation)
        db.flush()
        installation_db_id = new_installation.id
        logger.info("Auto-created GitHubInstallation github_id=%s", installation_github_id)

    # Step 7c: resolve/create GitHubRepository
    if repo_data.get("id"):
        existing_repo = db.execute(
            select(GitHubRepository).where(
                GitHubRepository.github_repo_id == repo_data["id"]
            )
        ).scalar_one_or_none()

        if not existing_repo and installation_db_id is not None and org_id is not None:
            new_repo = GitHubRepository(
                github_repo_id=repo_data["id"],
                name=repo_data.get("name", "unknown"),
                full_name=repo_data.get("full_name", "unknown"),
                is_private=repo_data.get("private", False),
                default_branch=repo_data.get("default_branch", "main"),
                organization_id=org_id,
                installation_id=installation_db_id,
                permissions={},
            )
            db.add(new_repo)
            db.flush()
            logger.info(
                "Auto-registered repository %s (github_id=%s)",
                repo_data.get("full_name"),
                repo_data["id"],
            )

    # ------------------------------------------------------------------
    # 8. Persist raw event exactly as received
    # ------------------------------------------------------------------
    try:
        raw_event = raw_repo.create_event(
            event_type=event_type,
            delivery_id=delivery_id,
            payload_json=raw_payload,
            organization_id=org_id,
        )
        db.commit()
    except IntegrityError:
        # Race condition: another request stored the same delivery_id
        db.rollback()
        logger.info("Concurrent duplicate webhook delivery %s.", delivery_id)
        return WebhookResponse(
            status="duplicate",
            message=f"Delivery '{delivery_id}' was already recorded (concurrent).",
        )
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to store raw event (delivery=%s): %s", delivery_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store event — please retry.",
        ) from exc

    pr_number = pull_request.get("number", 0)
    repo_data = raw_payload.get("repository", {})
    repo_name = repo_data.get("full_name", "unknown")

    logger.info(
        "Stored merged PR event (delivery=%s, pr=#%s, repo=%s, event_id=%s)",
        delivery_id,
        pr_number,
        repo_name,
        raw_event.id,
    )

    # ------------------------------------------------------------------
    # 8.5 Queue processing job
    # ------------------------------------------------------------------
    process_raw_event.delay(str(raw_event.id))  # type: ignore[attr-defined]
    logger.info("Queued process_raw_event task for event_id=%s", raw_event.id)

    # ------------------------------------------------------------------
    # 9. Return HTTP 200 immediately — workers process asynchronously
    # ------------------------------------------------------------------
    return WebhookResponse(
        status="accepted",
        event_id=str(raw_event.id),
    )

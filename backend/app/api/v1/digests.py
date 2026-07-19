import datetime
from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.ai.digest_generator import generate_engineering_digest
from app.models.engineering_digest import EngineeringDigest
from app.models.pull_request import PullRequest
from app.models.ai_analysis import AIAnalysis
from app.models.ai_advisor import AIAdvisor

router = APIRouter(prefix="/digests", tags=["digests"])


class GenerateDigestRequest(BaseModel):
    period_type: str  # "daily" or "weekly"


@router.post("/generate")
def generate_digest(
    request: GenerateDigestRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Generate a new daily or weekly digest."""
    now = datetime.datetime.now(datetime.UTC)
    if request.period_type == "daily":
        period_start = now - datetime.timedelta(days=1)
    elif request.period_type == "weekly":
        period_start = now - datetime.timedelta(days=7)
    else:
        raise HTTPException(status_code=400, detail="period_type must be daily or weekly")

    # Fetch PRs merged in the timeframe
    stmt = (
        select(PullRequest)
        .where(PullRequest.merged_at >= period_start)
        .where(PullRequest.merged_at <= now)
        .order_by(PullRequest.merged_at.desc())
    )
    prs = db.scalars(stmt).all()

    if not prs:
        raise HTTPException(status_code=400, detail="No PRs merged in this period.")

    prs_data = []
    for pr in prs:
        pr_info = {
            "title": pr.title,
            "author_login": pr.author_login,
            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
        }
        
        if pr.ai_analysis:
            pr_info["ai_analysis"] = pr.ai_analysis.structured_data
        if pr.ai_advisor:
            pr_info["ai_advisor"] = pr.ai_advisor.structured_data
            
        prs_data.append(pr_info)

    digest_output = generate_engineering_digest(request.period_type, prs_data)
    if not digest_output:
        raise HTTPException(status_code=500, detail="AI generation failed.")

    markdown_content = digest_output.pop("full_markdown_report")
    
    digest = EngineeringDigest(
        digest_type=request.period_type,
        period_start=period_start,
        period_end=now,
        markdown_content=markdown_content,
        structured_data=digest_output,
    )
    db.add(digest)
    db.commit()
    db.refresh(digest)

    return {
        "id": digest.id,
        "digest_type": digest.digest_type,
        "period_start": digest.period_start,
        "period_end": digest.period_end,
    }


@router.get("")
def list_digests(
    db: Session = Depends(get_db),
    limit: int = 10,
) -> list[dict[str, Any]]:
    """List recent digests."""
    stmt = select(EngineeringDigest).order_by(desc(EngineeringDigest.created_at)).limit(limit)
    digests = db.scalars(stmt).all()
    
    return [
        {
            "id": d.id,
            "digest_type": d.digest_type,
            "period_start": d.period_start,
            "period_end": d.period_end,
            "created_at": d.created_at,
        }
        for d in digests
    ]


@router.get("/{digest_id}")
def get_digest(
    digest_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get a specific digest."""
    digest = db.get(EngineeringDigest, digest_id)
    if not digest:
        raise HTTPException(status_code=404, detail="Digest not found")
        
    return {
        "id": digest.id,
        "digest_type": digest.digest_type,
        "period_start": digest.period_start,
        "period_end": digest.period_end,
        "markdown_content": digest.markdown_content,
        "structured_data": digest.structured_data,
        "created_at": digest.created_at,
    }

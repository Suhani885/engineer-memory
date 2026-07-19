import datetime
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.ai.release_generator import generate_release_notes
from app.models.release_note import ReleaseNote
from app.models.pull_request import PullRequest

router = APIRouter(prefix="/releases", tags=["releases"])


class GenerateReleaseRequest(BaseModel):
    start_tag_name: str
    end_tag_name: str
    start_date: datetime.datetime
    end_date: datetime.datetime


@router.post("/generate")
def generate_release(
    request: GenerateReleaseRequest,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Generate a new set of release notes based on a date range."""
    
    # Fetch PRs merged in the timeframe
    stmt = (
        select(PullRequest)
        .where(PullRequest.merged_at >= request.start_date)
        .where(PullRequest.merged_at <= request.end_date)
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

    release_output = generate_release_notes(request.start_tag_name, request.end_tag_name, prs_data)
    if not release_output:
        raise HTTPException(status_code=500, detail="AI generation failed.")

    markdown_content = release_output.pop("full_markdown_report")
    
    release_note = ReleaseNote(
        start_tag_name=request.start_tag_name,
        end_tag_name=request.end_tag_name,
        start_date=request.start_date,
        end_date=request.end_date,
        markdown_content=markdown_content,
        structured_data=release_output,
    )
    db.add(release_note)
    db.commit()
    db.refresh(release_note)

    return {
        "id": release_note.id,
        "start_tag_name": release_note.start_tag_name,
        "end_tag_name": release_note.end_tag_name,
        "start_date": release_note.start_date,
        "end_date": release_note.end_date,
    }


@router.get("")
def list_releases(
    db: Session = Depends(get_db),
    limit: int = 10,
) -> list[dict[str, Any]]:
    """List recent release notes."""
    stmt = select(ReleaseNote).order_by(desc(ReleaseNote.created_at)).limit(limit)
    releases = db.scalars(stmt).all()
    
    return [
        {
            "id": r.id,
            "start_tag_name": r.start_tag_name,
            "end_tag_name": r.end_tag_name,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "created_at": r.created_at,
        }
        for r in releases
    ]


@router.get("/{release_id}")
def get_release(
    release_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Get a specific release note."""
    release = db.get(ReleaseNote, release_id)
    if not release:
        raise HTTPException(status_code=404, detail="Release note not found")
        
    return {
        "id": release.id,
        "start_tag_name": release.start_tag_name,
        "end_tag_name": release.end_tag_name,
        "start_date": release.start_date,
        "end_date": release.end_date,
        "markdown_content": release.markdown_content,
        "structured_data": release.structured_data,
        "created_at": release.created_at,
    }

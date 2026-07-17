from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.search import execute_hybrid_search

router = APIRouter(prefix="/search", tags=["search"])


@router.get("")
def search(
    q: str = Query(..., description="Natural language search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Execute a hybrid search combining natural language filters and semantic vector search."""
    results = execute_hybrid_search(db, query_text=q, limit=limit)
    return {"results": results}

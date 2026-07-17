from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.assistant import AssistantQuery, ask_assistant

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/ask")
def ask(
    query: AssistantQuery,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Ask the Engineering Memory Assistant a question."""
    answer = ask_assistant(db, question=query.question)
    return {"answer": answer}

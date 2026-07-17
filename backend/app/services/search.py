# ruff: noqa: E501
"""Hybrid search service combining semantic search and SQL filters."""

from datetime import datetime
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from app.ai.embedder import generate_embeddings
from app.core.config import get_settings
from app.models.ai_analysis import AIAnalysis
from app.models.github_repository import GitHubRepository
from app.models.pull_request import PullRequest


class ParsedSearchQuery(BaseModel):
    """Structured filters extracted from a natural language query."""
    
    semantic_query: str | None = Field(
        default=None, 
        description="The core semantic intent to search for, excluding the filter keywords. Example: 'authentication changes' or 'Redis migrations'"
    )
    author: str | None = Field(default=None, description="The GitHub username of the author if specified")
    repository_name: str | None = Field(default=None, description="The name of the repository if specified")
    risk_level: str | None = Field(default=None, description="The deployment risk level if specified (e.g., 'Low', 'Medium', 'High')")
    module_name: str | None = Field(default=None, description="A specific module or directory name if specified")
    start_date: str | None = Field(default=None, description="ISO8601 start date if a time range is specified")
    end_date: str | None = Field(default=None, description="ISO8601 end date if a time range is specified")


def parse_natural_language_query(query_text: str) -> ParsedSearchQuery:
    """Use OpenAI to extract SQL filters and semantic intent from raw text."""
    settings = get_settings()
    if not settings.openai_api_key:
        return ParsedSearchQuery(semantic_query=query_text)

    client = OpenAI(api_key=settings.openai_api_key)

    prompt = f"""
Analyze the following natural language query and extract structured search filters.
Current date/time for relative date context: {datetime.now().isoformat()}

Query: "{query_text}"
"""

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a specialized query parser that maps natural language searches into strict SQL-like filters and isolates the core semantic query."},
                {"role": "user", "content": prompt}
            ],
            response_format=ParsedSearchQuery,
            temperature=0.0,
        )
        if response.choices and response.choices[0].message.parsed:
            return response.choices[0].message.parsed
    except Exception:
        pass

    # Fallback if parsing fails
    return ParsedSearchQuery(semantic_query=query_text)


def execute_hybrid_search(db: Session, query_text: str, limit: int = 10) -> list[dict[str, Any]]:
    """Execute a hybrid search combining pgvector semantic search and SQL filters."""
    # 1. Parse the query
    parsed = parse_natural_language_query(query_text)

    # 2. Base query: Join PR with AIAnalysis and Repo
    stmt = select(PullRequest).join(PullRequest.ai_analysis).join(PullRequest.repository)

    # Eagerly load the AI analysis so we can return its summary
    stmt = stmt.options(joinedload(PullRequest.ai_analysis))

    # 3. Apply exact SQL filters
    conditions = []
    
    if parsed.author:
        conditions.append(PullRequest.author_login.ilike(f"%{parsed.author}%"))
    
    if parsed.repository_name:
        conditions.append(GitHubRepository.name.ilike(f"%{parsed.repository_name}%"))
        
    if parsed.risk_level:
        conditions.append(AIAnalysis.risk_level.ilike(parsed.risk_level))
        
    if parsed.module_name:
        # `affected_modules` is an array of strings in AIAnalysis, using ANY for partial match
        # SQLAlchemy supports `.any()` on array types using `Array.any()` or we can cast
        # For simplicity, we can do an ILIKE cast on the array as text
        conditions.append(sa_cast_array_to_text(parsed.module_name))
        
    if parsed.start_date:
        try:
            start_dt = datetime.fromisoformat(parsed.start_date)
            conditions.append(PullRequest.merged_at >= start_dt)
        except Exception:
            pass

    if parsed.end_date:
        try:
            end_dt = datetime.fromisoformat(parsed.end_date)
            conditions.append(PullRequest.merged_at <= end_dt)
        except Exception:
            pass

    if conditions:
        stmt = stmt.where(and_(*conditions))

    # 4. Apply vector search if there is a semantic query
    if parsed.semantic_query:
        embeddings = generate_embeddings([parsed.semantic_query])
        if embeddings and len(embeddings) > 0:
            query_vector = embeddings[0]
            # Use cosine distance operator `<=>` (mapped to cosine_distance in pgvector-sqlalchemy)
            # Order by the closest distance
            stmt = stmt.order_by(AIAnalysis.summary_embedding.cosine_distance(query_vector))
            
    stmt = stmt.limit(limit)

    results = db.execute(stmt).scalars().unique().all()
    
    # 5. Format results
    output = []
    for pr in results:
        ai_data = pr.ai_analysis
        output.append({
            "id": str(pr.id),
            "repository": pr.repository.name,
            "pr_number": pr.number,
            "title": pr.title,
            "author": pr.author_login,
            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
            "risk_level": ai_data.risk_level if ai_data else "Unknown",
            "summary": ai_data.summary if ai_data else "",
            "engineering_impact": ai_data.engineering_impact if ai_data else "",
        })
        
    return output


def sa_cast_array_to_text(module_name: str) -> Any:
    """Helper to do ILIKE over a postgres array."""
    from sqlalchemy import String, cast
    return cast(AIAnalysis.affected_modules, String).ilike(f"%{module_name}%")

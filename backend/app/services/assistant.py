# ruff: noqa: E501
"""Engineering Memory Assistant powered by RAG and Hybrid Search."""

from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.models.pull_request import PullRequest
from app.services.search import execute_hybrid_search


class AssistantQuery(BaseModel):
    """Payload for asking the assistant a question."""
    question: str


def ask_assistant(db: Session, question: str) -> str:
    """Answers an engineering question using retrieved context from hybrid search."""
    settings = get_settings()
    if not settings.openai_api_key:
        return "Assistant unavailable: OpenAI API key is missing."

    client = OpenAI(api_key=settings.openai_api_key)

    # 1. Retrieve the top 5 most relevant PRs using our hybrid search
    search_results = execute_hybrid_search(db, query_text=question, limit=5)
    
    if not search_results:
        return "I could not find any relevant pull requests in the engineering memory to answer your question."

    # 2. Extract the PR IDs and fetch the full context
    pr_ids = [res["id"] for res in search_results]
    
    # Eagerly load all the rich AI context for these PRs
    prs = db.query(PullRequest).options(
        joinedload(PullRequest.repository),
        joinedload(PullRequest.ai_analysis),
        joinedload(PullRequest.ai_advisor),
        joinedload(PullRequest.parsed_change),
    ).filter(PullRequest.id.in_(pr_ids)).all()

    # 3. Construct the context block
    context_blocks = []
    for pr in prs:
        block = f"### PR #{pr.number} ({pr.repository.name})\n"
        block += f"Title: {pr.title}\n"
        block += f"Author: {pr.author_login}\n"
        if pr.merged_at:
            block += f"Merged At: {pr.merged_at.isoformat()}\n"
        
        if pr.ai_analysis:
            block += f"Summary: {pr.ai_analysis.summary}\n"
            block += f"Engineering Impact: {pr.ai_analysis.engineering_impact}\n"
            block += f"Risk Level: {pr.ai_analysis.risk_level}\n"
            
        if pr.ai_advisor:
            block += f"Missing Tests: {', '.join(pr.ai_advisor.missing_test_cases)}\n"
            block += f"Security Recommendations: {', '.join(pr.ai_advisor.security_recommendations)}\n"
            
        if pr.parsed_change:
            block += f"Modified Functions: {', '.join(pr.parsed_change.functions_modified)}\n"
            
        context_blocks.append(block)

    full_context = "\n\n".join(context_blocks)

    # 4. Ask the LLM
    system_prompt = (
        "You are an expert Engineering Memory Assistant. "
        "Your sole purpose is to answer engineering and architectural questions based ONLY on the provided context.\n"
        "RULES:\n"
        "1. Never hallucinate. If the context does not contain the answer, say you don't know.\n"
        "2. Always cite your sources by referencing the PRs.\n"
        "3. Always format PR citations as markdown links to GitHub: [PR #{number}](https://github.com/{repo_name}/pull/{number})."
    )

    prompt = f"""
Context:
{full_context}

Question:
{question}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content or "No response generated."
    except Exception as e:
        return f"Error communicating with AI: {e}"

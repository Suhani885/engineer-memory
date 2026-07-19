"""AI analyzer for Engineering Digests."""
# ruff: noqa: E501

import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import get_settings


class AIDigestOutput(BaseModel):
    """Pydantic model representing the expected JSON schema from OpenAI for digests."""

    merged_prs_summary: str
    high_risk_changes: list[str]
    breaking_changes: list[str]
    security_changes: list[str]
    deployment_notes: str
    major_features: list[str]
    top_contributors: list[str]
    executive_summary: str
    full_markdown_report: str


def generate_engineering_digest(
    period_type: str,
    prs_data: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Analyze a list of PRs and generate an engineering digest using OpenAI."""
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    client = OpenAI(api_key=settings.openai_api_key)

    prs_str = json.dumps(
        [
            {
                "title": pr.get("title"),
                "author": pr.get("author_login"),
                "merged_at": pr.get("merged_at"),
                "ai_analysis": pr.get("ai_analysis"),
                "ai_advisor": pr.get("ai_advisor"),
            }
            for pr in prs_data
        ],
        indent=2,
    )

    prompt = f"""
You are an expert VP of Engineering. Your task is to generate a {period_type} engineering digest summarizing the work that has been merged into the main branch.
You are given a list of Pull Requests, each containing its title, author, and previously generated AI analyses (which highlight risk, security, and impact).

Generate a highly structured JSON output.
CRITICAL: The `full_markdown_report` field MUST contain a beautifully formatted markdown report. Use headings, bullet points, and emojis. It must include sections for:
- Executive Summary
- Major Features Delivered
- High Risk & Breaking Changes
- Security Updates
- Deployment & Infrastructure Notes
- Top Contributors

--- MERGED PRs DATA ---
{prs_str}
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a VP of Engineering. Always return data matching the provided JSON schema perfectly. Produce exceptionally high-quality markdown."},
            {"role": "user", "content": prompt},
        ],
        response_format=AIDigestOutput,
        temperature=0.3,
    )

    if response.choices and response.choices[0].message.parsed:
        return response.choices[0].message.parsed.model_dump()
    
    return None

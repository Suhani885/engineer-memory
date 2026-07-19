"""AI analyzer for Release Notes."""
# ruff: noqa: E501

import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import get_settings


class ReleaseNoteOutput(BaseModel):
    """Pydantic model representing the expected JSON schema from OpenAI for release notes."""

    release_summary: str
    breaking_changes: list[str]
    migration_guide: str
    customer_facing_notes: list[str]
    internal_engineering_notes: list[str]
    known_risks: list[str]
    rollback_strategy: str
    testing_checklist: list[str]
    full_markdown_report: str


def generate_release_notes(
    start_tag: str,
    end_tag: str,
    prs_data: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Analyze a list of PRs and generate release notes using OpenAI."""
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
You are an expert Engineering Release Manager. Your task is to generate comprehensive Release Notes summarizing all work merged between tag {start_tag} and tag {end_tag}.
You are given a list of Pull Requests, each containing its title, author, and previously generated AI analyses.

Generate a highly structured JSON output.
CRITICAL: The `full_markdown_report` field MUST contain a beautifully formatted markdown report. Use headings, bullet points, and emojis. It must include all the following sections:
- 🚀 Release Summary
- 💥 Breaking Changes
- 📖 Migration Guide
- 📢 Customer Facing Notes
- 🛠️ Internal Engineering Notes
- ⚠️ Known Risks
- ⏪ Rollback Strategy
- ✅ Testing Checklist

--- MERGED PRs DATA ---
{prs_str}
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Release Manager. Always return data matching the provided JSON schema perfectly. Produce exceptionally high-quality markdown."},
            {"role": "user", "content": prompt},
        ],
        response_format=ReleaseNoteOutput,
        temperature=0.2,
    )

    if response.choices and response.choices[0].message.parsed:
        return response.choices[0].message.parsed.model_dump()
    
    return None

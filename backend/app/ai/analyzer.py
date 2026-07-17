"""AI analyzer for PRs using OpenAI Structured Outputs."""
# ruff: noqa: E501

import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import get_settings


class AIAnalysisOutput(BaseModel):
    """Pydantic model representing the expected JSON schema from OpenAI."""

    summary: str
    engineering_impact: str
    business_impact: str
    affected_modules: list[str]
    security_impact: str
    database_changes: str
    api_changes: str
    configuration_changes: str
    risk_level: str
    deployment_notes: str
    testing_required: str
    breaking_changes: bool
    release_notes: str


def analyze_pull_request(
    pr_details: dict[str, Any],
    files_data: list[dict[str, Any]],
    parsed_changes: dict[str, Any],
) -> dict[str, Any] | None:
    """Analyze a pull request using OpenAI and return structured JSON output.

    If OpenAI API key is not configured, returns None.
    """
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    client = OpenAI(api_key=settings.openai_api_key)

    # 1. Prepare context for the AI
    pr_title = pr_details.get("title", "No Title")
    pr_body = pr_details.get("body", "No Description")
    
    # We truncate the files data string if it's too large to prevent huge token usage.
    # In a production app, we would selectively include only the most relevant diffs.
    files_str = json.dumps(
        [
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "patch": f.get("patch", "")[:1000],  # Truncating diff to first 1000 chars per file
            }
            for f in files_data
        ],
        indent=2,
    )
    
    parsed_str = json.dumps(parsed_changes, indent=2)

    prompt = f"""
You are an expert Engineering AI Assistant. You must analyze the following Pull Request and generate a highly structured assessment.
You will extract technical details, infer the business impact, and assess the overall risk of the changes.

--- PR METADATA ---
Title: {pr_title}
Description: {pr_body}

--- STRUCTURAL CHANGES DETECTED (NO AI) ---
{parsed_str}

--- MODIFIED FILES (PARTIAL DIFF) ---
{files_str}
"""

    # 2. Call OpenAI Structured Outputs
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a senior engineering manager. Always return data matching the provided JSON schema perfectly."},
            {"role": "user", "content": prompt},
        ],
        response_format=AIAnalysisOutput,
        temperature=0.1,
    )

    # 3. Return the parsed object as a dictionary
    if response.choices and response.choices[0].message.parsed:
        return response.choices[0].message.parsed.model_dump()
    
    return None


class AIAdvisorOutput(BaseModel):
    """Pydantic model representing the expected JSON schema for Engineering Advisor."""

    missing_test_cases: list[str]
    potential_edge_cases: list[str]
    suggested_documentation_updates: list[str]
    possible_performance_issues: list[str]
    security_recommendations: list[str]
    related_files_that_may_need_changes: list[str]
    rollback_strategy: str
    deployment_checklist: list[str]
    future_refactoring_suggestions: list[str]
    suggested_reviewers: list[str]


def generate_advisor_insights(
    pr_details: dict[str, Any],
    files_data: list[dict[str, Any]],
    parsed_changes: dict[str, Any],
) -> dict[str, Any] | None:
    """Generate engineering advisor insights for a pull request using OpenAI."""
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    client = OpenAI(api_key=settings.openai_api_key)

    pr_title = pr_details.get("title", "No Title")
    pr_body = pr_details.get("body", "No Description")
    
    files_str = json.dumps(
        [
            {
                "filename": f.get("filename"),
                "status": f.get("status"),
                "patch": f.get("patch", "")[:1000],
            }
            for f in files_data
        ],
        indent=2,
    )
    parsed_str = json.dumps(parsed_changes, indent=2)

    prompt = f"""
You are an expert Principal Engineer advising the team. Review the following Pull Request and generate deep, actionable engineering insights.
Think critically about edge cases, security, performance, and deployment risks.

--- PR METADATA ---
Title: {pr_title}
Description: {pr_body}

--- STRUCTURAL CHANGES DETECTED ---
{parsed_str}

--- MODIFIED FILES (PARTIAL DIFF) ---
{files_str}
"""

    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a Principal Engineering Advisor. Always return data perfectly matching the requested JSON schema."},
            {"role": "user", "content": prompt},
        ],
        response_format=AIAdvisorOutput,
        temperature=0.2,
    )

    if response.choices and response.choices[0].message.parsed:
        return response.choices[0].message.parsed.model_dump()
    
    return None

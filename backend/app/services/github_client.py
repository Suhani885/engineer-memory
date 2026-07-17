"""GitHub REST API client."""

from __future__ import annotations

import base64
import time
from typing import Any

import httpx
from jose import jwt

from app.core.config import get_settings


class GitHubClientError(Exception):
    """Base exception for GitHub API errors."""


class GitHubClient:
    """Client for authenticating and interacting with the GitHub REST API."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def _generate_app_jwt(self) -> str:
        """Generate a short-lived JWT for authenticating as the GitHub App."""
        if not self.settings.github_app_id or not self.settings.github_app_private_key:
            raise GitHubClientError("GitHub App ID or private key not configured.")

        # The private key might be base64-encoded in the environment for easy injection
        raw_key = self.settings.github_app_private_key
        try:
            # Try to base64 decode if it lacks PEM headers, otherwise use as-is
            if "-----BEGIN" not in raw_key:
                raw_key = base64.b64decode(raw_key).decode("utf-8")
        except Exception:
            pass  # Fall back to using it as-is if decoding fails

        now = int(time.time())
        payload = {
            "iat": now - 60,  # Issued at (60s in the past to handle clock drift)
            "exp": now + (10 * 60),  # Expiration time (10 minutes maximum)
            "iss": self.settings.github_app_id,  # Issuer
        }
        return jwt.encode(payload, raw_key, algorithm="RS256")

    def get_installation_token(self, installation_id: int) -> str:
        """Exchange the App JWT for a repository-scoped installation access token."""
        app_jwt = self._generate_app_jwt()
        
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {app_jwt}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, headers=headers)
            
            if response.status_code != 201:
                raise GitHubClientError(
                    f"Failed to get installation token for {installation_id}: "
                    f"{response.status_code} {response.text}"
                )
                
            return response.json()["token"]

    def fetch_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        installation_id: int,
    ) -> dict[str, Any]:
        """Fetch full details of a pull request from the GitHub REST API."""
        token = self.get_installation_token(installation_id)
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers)
            
            if response.status_code != 200:
                raise GitHubClientError(
                    f"Failed to fetch PR {owner}/{repo}#{pr_number}: "
                    f"{response.status_code} {response.text}"
                )
                
            return response.json()

    def fetch_pull_request_files(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        installation_id: int,
    ) -> list[dict[str, Any]]:
        """Fetch files modified in a pull request."""
        token = self.get_installation_token(installation_id)
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        # Handle pagination for files (up to 3000 max across pages).
        # We'll fetch page 1 for now or paginate if needed.
        # To keep it simple, we'll fetch one page with per_page=100.
        params = {"per_page": 100}

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise GitHubClientError(
                    f"Failed to fetch PR files {owner}/{repo}#{pr_number}: "
                    f"{response.status_code} {response.text}"
                )
            return response.json()

    def fetch_pull_request_commits(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        installation_id: int,
    ) -> list[dict[str, Any]]:
        """Fetch commits in a pull request."""
        token = self.get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/commits"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        params = {"per_page": 100}

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise GitHubClientError(
                    f"Failed to fetch PR commits {owner}/{repo}#{pr_number}: "
                    f"{response.status_code} {response.text}"
                )
            return response.json()

    def fetch_pull_request_reviews(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        installation_id: int,
    ) -> list[dict[str, Any]]:
        """Fetch reviews for a pull request."""
        token = self.get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        params = {"per_page": 100}

        with httpx.Client(timeout=15.0) as client:
            response = client.get(url, headers=headers, params=params)
            if response.status_code != 200:
                raise GitHubClientError(
                    f"Failed to fetch PR reviews {owner}/{repo}#{pr_number}: "
                    f"{response.status_code} {response.text}"
                )
            return response.json()

    def fetch_commit(
        self,
        owner: str,
        repo: str,
        commit_sha: str,
        installation_id: int,
    ) -> dict[str, Any]:
        """Fetch a specific commit (e.g. merge commit)."""
        token = self.get_installation_token(installation_id)
        url = f"https://api.github.com/repos/{owner}/{repo}/commits/{commit_sha}"
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, headers=headers)
            if response.status_code != 200:
                raise GitHubClientError(
                    f"Failed to fetch commit {owner}/{repo}@{commit_sha}: "
                    f"{response.status_code} {response.text}"
                )
            return response.json()

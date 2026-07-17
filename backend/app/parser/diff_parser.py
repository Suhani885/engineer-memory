"""Engineering Parser for GitHub Patches."""
# ruff: noqa: E501

from __future__ import annotations

import re
from typing import Any

from app.models.pull_request_file import PullRequestFile


class EngineeringParser:
    """Parses structural engineering changes from PR file diffs (patches)."""

    def __init__(self) -> None:
        self.re_func = re.compile(r"^[+-]\s*(?:async\s+)?(?:def|function)\s+([a-zA-Z0-9_]+)\s*\(", re.MULTILINE)
        self.re_arrow_func = re.compile(r"^[+-]\s*(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_]+)\s*=\s*(?:async\s+)?\(.*?\)\s*=>", re.MULTILINE)
        self.re_class = re.compile(r"^[+-]\s*(?:export\s+)?class\s+([a-zA-Z0-9_]+)", re.MULTILINE)
        
        self.re_env = re.compile(r"(?:os\.environ(?:\.get)?\(['\"](.*?)['\"]|process\.env\.([a-zA-Z0-9_]+))")

    def parse(self, files: list[PullRequestFile]) -> dict[str, Any]:
        """Parse a list of PullRequestFiles to extract structural changes."""
        
        functions_modified = set()
        classes_modified = set()
        routes = set()
        api_endpoints = set()
        sql_migrations = False
        dependencies = set()
        configuration = set()
        environment_variables = set()
        frontend_components = set()
        backend_services = set()
        tests = False

        for file in files:
            filename = file.filename or ""
            patch = file.patch or ""

            # Check filename categories
            if filename.endswith(".sql") or filename.startswith("alembic/versions/") or filename.startswith("infra/postgres/"):
                sql_migrations = True

            if filename in ("package.json", "requirements.txt", "pyproject.toml", "package-lock.json", "poetry.lock"):
                dependencies.add(filename)

            if filename.endswith((".yaml", ".yml", ".toml")) or "config" in filename:
                configuration.add(filename)

            if ".env" in filename:
                configuration.add(filename)
                environment_variables.add(filename)

            if filename.startswith("frontend/") and filename.endswith((".tsx", ".jsx")):
                frontend_components.add(filename)

            if filename.startswith("backend/app/services/") and filename.endswith(".py"):
                backend_services.add(filename)

            if filename.startswith("frontend/app/") or "routes" in filename:
                routes.add(filename)

            if filename.startswith("backend/app/api/"):
                api_endpoints.add(filename)

            if "test_" in filename or "_test" in filename or ".test." in filename or ".spec." in filename or "tests/" in filename:
                tests = True

            # Parse patch for specifics
            if patch:
                # Functions
                for match in self.re_func.finditer(patch):
                    functions_modified.add(match.group(1))
                for match in self.re_arrow_func.finditer(patch):
                    functions_modified.add(match.group(1))

                # Classes
                for match in self.re_class.finditer(patch):
                    classes_modified.add(match.group(1))

                # Environment Variables (in code)
                for match in self.re_env.finditer(patch):
                    env_name = match.group(1) or match.group(2)
                    if env_name:
                        environment_variables.add(env_name)

        return {
            "functions_modified": sorted(list(functions_modified)),
            "classes_modified": sorted(list(classes_modified)),
            "routes": sorted(list(routes)),
            "api_endpoints": sorted(list(api_endpoints)),
            "sql_migrations": sql_migrations,
            "dependencies": sorted(list(dependencies)),
            "configuration": sorted(list(configuration)),
            "environment_variables": sorted(list(environment_variables)),
            "frontend_components": sorted(list(frontend_components)),
            "backend_services": sorted(list(backend_services)),
            "tests": tests,
        }

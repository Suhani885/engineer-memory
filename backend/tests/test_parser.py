from __future__ import annotations

import uuid

from app.models.pull_request_file import PullRequestFile
from app.parser.diff_parser import EngineeringParser


def test_engineering_parser_functions_and_classes() -> None:
    parser = EngineeringParser()
    
    # Mock files
    f1 = PullRequestFile(
        id=uuid.uuid4(),
        pull_request_id=uuid.uuid4(),
        github_sha="abc",
        filename="backend/app/services/example.py",
        status="modified",
        patch="""@@ -10,5 +10,6 @@
+def do_something_new():
+    pass
-class OldClass:
+class NewClass:
"""
    )
    
    f2 = PullRequestFile(
        id=uuid.uuid4(),
        pull_request_id=uuid.uuid4(),
        github_sha="def",
        filename="frontend/app/page.tsx",
        status="modified",
        patch="""@@ -1,5 +1,6 @@
+export const MyComponent = () => {
+    return <div>Hello</div>
+}
+const ignored = "value"
"""
    )

    f3 = PullRequestFile(
        id=uuid.uuid4(),
        pull_request_id=uuid.uuid4(),
        github_sha="ghi",
        filename="infra/postgres/init.sql",
        status="added",
        patch="""+CREATE TABLE test ();"""
    )

    f4 = PullRequestFile(
        id=uuid.uuid4(),
        pull_request_id=uuid.uuid4(),
        github_sha="jkl",
        filename="backend/app/api/endpoints.py",
        status="modified",
        patch="""+os.environ.get("MY_SECRET")"""
    )

    f5 = PullRequestFile(
        id=uuid.uuid4(),
        pull_request_id=uuid.uuid4(),
        github_sha="mno",
        filename="package.json",
        status="modified",
        patch="""+"react": "^18.0.0" """
    )

    parsed = parser.parse([f1, f2, f3, f4, f5])

    assert "do_something_new" in parsed["functions_modified"]
    assert "MyComponent" in parsed["functions_modified"]
    
    assert "OldClass" in parsed["classes_modified"]
    assert "NewClass" in parsed["classes_modified"]

    assert parsed["sql_migrations"] is True
    assert "backend/app/api/endpoints.py" in parsed["api_endpoints"]
    assert "frontend/app/page.tsx" in parsed["routes"]
    assert "frontend/app/page.tsx" in parsed["frontend_components"]
    assert "backend/app/services/example.py" in parsed["backend_services"]
    
    assert "MY_SECRET" in parsed["environment_variables"]
    assert "package.json" in parsed["dependencies"]

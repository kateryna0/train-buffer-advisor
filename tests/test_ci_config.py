"""Phase 21: verify CI configuration and Python pin are present and correct.

These guard the safety net itself — if someone deletes the workflow, drops the
pytest/import-smoke steps, or unpins Python, a test fails.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYTHON_VERSION_FILE = REPO_ROOT / ".python-version"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
README = REPO_ROOT / "README.md"


def test_python_version_is_pinned():
    assert PYTHON_VERSION_FILE.exists(), ".python-version must exist"
    version = PYTHON_VERSION_FILE.read_text().strip()
    assert re.fullmatch(r"3\.\d+(\.\d+)?", version), f"unexpected pin: {version!r}"


def test_ci_workflow_exists():
    assert CI_WORKFLOW.exists(), ".github/workflows/ci.yml must exist"


def test_ci_runs_pytest_and_import_smoke_check():
    text = CI_WORKFLOW.read_text()
    assert "pytest" in text, "CI must run pytest"
    assert "import app" in text, "CI must run the import smoke check"


def test_ci_uses_the_pinned_python_version():
    text = CI_WORKFLOW.read_text()
    assert "setup-python" in text
    assert "python-version-file: .python-version" in text


def test_ci_triggers_on_push_and_pull_request():
    text = CI_WORKFLOW.read_text()
    assert "push:" in text
    assert "pull_request:" in text


def test_readme_has_ci_badge():
    text = README.read_text()
    assert "actions/workflows/ci.yml/badge.svg" in text

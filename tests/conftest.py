"""Shared pytest fixtures."""

import shutil
import uuid
from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_config_yaml() -> str:
    return """\
course: "cab201"
assignment: "t6q1"
zip_name: out.zip
include:
  - "*.py"
notify_when_graded: false
headless: true
"""


@pytest.fixture
def config_file(tmp_path, sample_config_yaml):
    path = tmp_path / "gradescope.yml"
    path.write_text(sample_config_yaml, encoding="utf-8")
    return path


@pytest.fixture
def fake_git_repo(project_root):
    """Minimal repo under tests/.pytest_work/ (writable .git/hooks on macOS)."""
    work = project_root / "tests" / ".pytest_work" / uuid.uuid4().hex[:8]
    work.mkdir(parents=True, exist_ok=True)
    (work / ".git").mkdir()
    (work / "main.py").write_text("print('hi')\n", encoding="utf-8")
    (work / "notes.md").write_text("# notes\n", encoding="utf-8")
    yield work
    shutil.rmtree(work, ignore_errors=True)

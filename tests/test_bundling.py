"""Zip bundling behaviour."""

import zipfile
from pathlib import Path

import pytest

from gradescope_autosubmitter.core import GradescopeSubmitter


def test_create_zip_with_mocked_git_paths(fake_git_repo, monkeypatch):
    monkeypatch.chdir(fake_git_repo)
    monkeypatch.setattr(
        GradescopeSubmitter,
        "_candidate_paths",
        lambda self: ["main.py", "notes.md"],
    )
    GradescopeSubmitter().create_zip(["*.py"], "sub.zip")
    with zipfile.ZipFile(fake_git_repo / "sub.zip") as zf:
        names = zf.namelist()
    assert names == ["main.py"]


def test_skips_missing_paths_from_git_listing(fake_git_repo, monkeypatch):
    """Regression: index can list paths removed from disk."""
    monkeypatch.chdir(fake_git_repo)
    monkeypatch.setattr(
        GradescopeSubmitter,
        "_candidate_paths",
        lambda self: ["main.py", "removed.py"],
    )
    GradescopeSubmitter().create_zip(["*.py"], "sub.zip")
    with zipfile.ZipFile(fake_git_repo / "sub.zip") as zf:
        assert zf.namelist() == ["main.py"]


def test_create_zip_without_git(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.py").write_text("pass\n", encoding="utf-8")
    (tmp_path / ".hidden").write_text("no\n", encoding="utf-8")
    GradescopeSubmitter().create_zip(["*.py"], "out.zip")
    with zipfile.ZipFile(tmp_path / "out.zip") as zf:
        assert zf.namelist() == ["a.py"]


def test_no_matching_files_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "a.py").write_text("x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="No files matched"):
        GradescopeSubmitter().create_zip(["*.xyz"], "empty.zip")

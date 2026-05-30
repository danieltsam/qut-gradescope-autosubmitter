"""Session profile paths."""

from pathlib import Path

from gradescope_autosubmitter.core import SessionManager


def test_session_dir_is_under_home():
    sm = SessionManager()
    home = Path.home().resolve()
    assert home == sm.session_dir.resolve() or home in sm.session_dir.resolve().parents


def test_session_exists_false_when_missing(monkeypatch, tmp_path):
    sm = SessionManager()
    monkeypatch.setattr(sm, "session_dir", tmp_path / "no-session")
    assert sm.session_exists() is False


def test_session_exists_true_when_populated(monkeypatch, tmp_path):
    sm = SessionManager()
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "Default").mkdir()
    monkeypatch.setattr(sm, "session_dir", profile)
    assert sm.session_exists() is True


def test_clear_session_removes_dir(monkeypatch, tmp_path):
    sm = SessionManager()
    profile = tmp_path / "profile"
    profile.mkdir()
    (profile / "cookies").write_text("x", encoding="utf-8")
    monkeypatch.setattr(sm, "session_dir", profile)
    sm.clear_session()
    assert not profile.exists()

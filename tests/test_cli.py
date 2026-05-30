"""CLI commands (no live browser)."""

import os
import stat
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from gradescope_autosubmitter.cli import cli
from gradescope_autosubmitter.core import GradescopeSubmitter, SessionManager


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help_lists_commands(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for cmd in ("submit", "bundle", "login", "logout", "init", "validate", "doctor", "hooks"):
        assert cmd in result.output
    assert "init" in result.output and "login" in result.output


def test_cli_bare_invocation_shows_help(runner):
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "submit" in result.output


def test_cli_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "v" in result.output
    assert "gradescope" in result.output.lower() or "QUT" in result.output


def test_submit_help_shows_options(runner):
    result = runner.invoke(cli, ["submit", "--help"])
    assert result.exit_code == 0
    assert "--headless" in result.output


def test_init_writes_config(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    text = (tmp_path / "gradescope.yml").read_text(encoding="utf-8")
    assert "course:" in text
    assert "include:" in text


def test_validate_ok(runner, config_file, monkeypatch):
    monkeypatch.chdir(config_file.parent)
    result = runner.invoke(cli, ["validate", "--config", str(config_file)])
    assert result.exit_code == 0
    assert "Config OK" in result.output


def test_bundle_creates_zip(runner, config_file, monkeypatch):
    monkeypatch.chdir(config_file.parent)
    (config_file.parent / "work.py").write_text("x=1\n", encoding="utf-8")
    result = runner.invoke(cli, ["bundle", "--config", str(config_file)])
    assert result.exit_code == 0
    assert (config_file.parent / "out.zip").exists()


def test_submit_headless_without_session_fails(runner, config_file, monkeypatch):
    monkeypatch.chdir(config_file.parent)
    (config_file.parent / "work.py").write_text("x=1\n", encoding="utf-8")

    async def fake_submit(self, course, assignment, file, notify_when_graded=True):
        if self.headless:
            raise Exception(
                "No saved Gradescope session. Run `gradescope login` once "
                "(opens a browser for QUT SSO and 2FA), then run `gradescope submit` again."
            )

    with patch.object(GradescopeSubmitter, "submit_to_gradescope", fake_submit):
        result = runner.invoke(
            cli, ["submit", "--config", str(config_file), "--headless"]
        )
    assert result.exit_code == 1
    assert "gradescope login" in result.output


def test_submit_calls_browser_flow(runner, config_file, monkeypatch):
    monkeypatch.chdir(config_file.parent)
    (config_file.parent / "work.py").write_text("x=1\n", encoding="utf-8")
    with patch(
        "gradescope_autosubmitter.cli.GradescopeSubmitter.submit_to_gradescope",
        new_callable=AsyncMock,
    ) as mock_submit:
        with patch(
            "gradescope_autosubmitter.core.SessionManager.is_logged_in",
            new_callable=AsyncMock,
            return_value=(True, "https://www.gradescope.com.au/"),
        ):
            result = runner.invoke(
                cli,
                ["submit", "--config", str(config_file), "--headless", "--no-grade-wait"],
            )
    assert result.exit_code == 0
    mock_submit.assert_awaited_once()


def test_logout_clears_session(runner):
    with patch("gradescope_autosubmitter.cli.SessionManager.clear_session") as clear:
        result = runner.invoke(cli, ["logout"])
    assert result.exit_code == 0
    clear.assert_called_once()


def test_hooks_install_pre_commit(runner, fake_git_repo, monkeypatch):
    monkeypatch.chdir(fake_git_repo)
    result = runner.invoke(cli, ["hooks", "--install", "pre-commit", "--quick"])
    assert result.exit_code == 0
    hook = fake_git_repo / ".git" / "hooks" / "pre-commit"
    assert hook.exists()
    assert os.access(hook, os.X_OK)
    content = hook.read_text(encoding="utf-8")
    assert "gradescope submit" in content
    assert "--no-grade-wait" in content


def test_hooks_requires_git_repo(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(cli, ["hooks", "--install", "pre-commit"])
    assert result.exit_code == 1


def test_doctor_runs(runner, config_file, monkeypatch):
    monkeypatch.chdir(config_file.parent)
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 0
    assert "Python" in result.output


def test_login_invokes_interactive(runner):
    with patch(
        "gradescope_autosubmitter.cli.interactive_login",
        new_callable=AsyncMock,
    ) as mock_login:
        result = runner.invoke(cli, ["login"])
    assert result.exit_code == 0
    mock_login.assert_awaited_once_with(clear_first=False)


def test_submit_missing_course_exits(runner, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "gradescope.yml"
    path.write_text("assignment: only\n", encoding="utf-8")
    result = runner.invoke(cli, ["submit", "--config", str(path)])
    assert result.exit_code != 0

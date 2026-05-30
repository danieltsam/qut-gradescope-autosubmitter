"""Command-line interface."""

import asyncio
import stat
import sys
from pathlib import Path

import click
from dotenv import load_dotenv

from .config import Config
from .core import GradescopeSubmitter, SessionManager, interactive_login
from .rich_console import (
    clear_live,
    console,
    create_config_panel,
    create_doctor_table,
    create_hook_panel,
    log_error,
    log_success,
    log_warning,
    print_banner,
    print_command_help,
    print_hint,
    print_root_help,
    print_version,
)

load_dotenv()

try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("qut-gradescope-autosubmitter")
except Exception:
    __version__ = "dev"


class OrangeCommand(click.Command):
    """Rich help for subcommands."""

    def format_help(self, ctx, formatter):
        print_command_help(ctx)


class OrangeGroup(click.Group):
    """Rich help for the root command group."""

    command_class = OrangeCommand

    def format_help(self, ctx, formatter):
        print_root_help(ctx)


def _version_callback(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    print_version(__version__)
    ctx.exit()


@click.group(
    cls=OrangeGroup,
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.option(
    "--version",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_version_callback,
    help="Show version and exit.",
)
@click.pass_context
def cli(ctx):
    """Submit assignments to QUT Gradescope (browser login once)."""
    if ctx.invoked_subcommand is not None:
        return
    if any(flag in sys.argv for flag in ("--help", "-h", "--version")):
        return
    print_root_help(ctx)
    ctx.exit(0)


@cli.command(cls=OrangeCommand)
@click.option("-c", "--course", help="Course shortname (overrides config).")
@click.option("-a", "--assignment", help="Assignment name substring (overrides config).")
@click.option("-f", "--file", "zip_name", default=None, help="Zip filename.")
@click.option("-i", "--include", multiple=True, help="Include glob (overrides config).")
@click.option("--config", type=click.Path(), help="Path to gradescope.yml.")
@click.option("--headless", is_flag=True, help="No browser window (requires prior login).")
@click.option("--no-grade-wait", is_flag=True, help="Skip waiting for autograder score.")
def submit(course, assignment, zip_name, include, config, headless, no_grade_wait):
    """Zip tracked files and upload to Gradescope."""
    _run_submit(course, assignment, zip_name, include, config, headless, no_grade_wait)


@cli.command(cls=OrangeCommand)
@click.option("-c", "--course", help="Course shortname (overrides config).")
@click.option("-a", "--assignment", help="Assignment name substring (overrides config).")
@click.option("-f", "--file", "zip_name", default=None, help="Zip filename.")
@click.option("-i", "--include", multiple=True, help="Include glob (overrides config).")
@click.option("--config", type=click.Path(), help="Path to gradescope.yml.")
def bundle(course, assignment, zip_name, include, config):
    """Build submission.zip only (no browser)."""
    print_banner("bundle")
    _, course, assignment, zip_name, patterns, _, _ = _load_submit_opts(
        course, assignment, zip_name, include, config, headless=False, no_grade_wait=True
    )
    GradescopeSubmitter(headless=True).create_zip(patterns, zip_name)
    log_success(f"Bundle ready: {zip_name}")


@cli.command(cls=OrangeCommand)
@click.option("-p", "--path", default="gradescope.yml", show_default=True, help="Config path.")
def init(path):
    """Create an example gradescope.yml in this directory."""
    target = Path(path)
    if target.exists() and not click.confirm(f"{path} exists. Overwrite?", default=False):
        return
    Config().create_example_config(path)
    log_success(f"Wrote {path}")
    print_hint(["gradescope login", "gradescope submit"])


@cli.command(cls=OrangeCommand)
@click.option("--config", type=click.Path(), help="Path to gradescope.yml.")
def validate(config):
    """Validate gradescope.yml and show resolved settings."""
    cfg = Config(config)
    cfg.validate()
    log_success("Config OK")
    rows = [
        ("Course", cfg.get("course")),
        ("Assignment", cfg.get("assignment")),
        ("Zip", cfg.get("zip_name")),
        ("Include", ", ".join(cfg.include_patterns())),
    ]
    console.print(create_config_panel(rows))
    sm = SessionManager()
    if sm.session_exists():
        log_success(f"Session ready: {sm.session_dir}")
    else:
        log_warning("No session — run gradescope login")


@cli.command(cls=OrangeCommand)
@click.option("--fresh", is_flag=True, help="Delete saved session before opening browser.")
def login(fresh):
    """Open browser for QUT SSO + 2FA; save session for later submits."""
    try:
        asyncio.run(interactive_login(clear_first=fresh))
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except Exception as e:
        log_error(str(e))
        raise SystemExit(1) from e


@cli.command(cls=OrangeCommand)
def logout():
    """Remove saved browser session (~/.cache/qut_gradescope)."""
    SessionManager().clear_session()


@cli.command(cls=OrangeCommand)
@click.option(
    "--install",
    type=click.Choice(["pre-commit", "post-commit"], case_sensitive=False),
    required=True,
    help="Which git hook to install.",
)
@click.option("--quick", is_flag=True, help="Hook runs submit with --no-grade-wait.")
def hooks(install, quick):
    """Install a git hook that runs gradescope submit."""
    if not Path(".git").exists():
        log_error("Not a git repository.")
        raise SystemExit(1)

    flags = "--headless"
    if quick:
        flags += " --no-grade-wait"

    script = f"""#!/bin/sh
if [ -f gradescope.yml ]; then
  gradescope submit {flags} || echo "gradescope submit failed"
fi
"""
    hooks_dir = Path(".git/hooks")
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / install
    hook_path.write_text(script, encoding="utf-8")
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
    console.print(create_hook_panel(str(hook_path), f"gradescope submit {flags}"))
    log_success("Hook is executable — commit to trigger submit.")


@cli.command(cls=OrangeCommand)
def doctor():
    """Check Python, Playwright, Chromium, config, and login session."""
    import sys

    checks = []

    checks.append({
        "component": "Python",
        "status": "ok" if sys.version_info >= (3, 8) else "error",
        "details": sys.version.split()[0],
    })

    try:
        import playwright  # noqa: F401
        checks.append({"component": "Playwright", "status": "ok", "details": "installed"})
    except ImportError:
        checks.append({"component": "Playwright", "status": "error", "details": "pip install playwright"})

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            ok = Path(p.chromium.executable_path or "").exists()
        checks.append({
            "component": "Chromium",
            "status": "ok" if ok else "error",
            "details": "ready" if ok else "run: playwright install chromium",
        })
    except Exception:
        checks.append({"component": "Chromium", "status": "error", "details": "playwright install chromium"})

    try:
        Config().validate()
        checks.append({"component": "gradescope.yml", "status": "ok", "details": "valid"})
    except Exception as e:
        checks.append({"component": "gradescope.yml", "status": "warning", "details": str(e)})

    sm = SessionManager()
    checks.append({
        "component": "Session",
        "status": "ok" if sm.session_exists() else "warning",
        "details": str(sm.session_dir) if sm.session_exists() else "run gradescope login",
    })

    print_banner("doctor")
    console.print(create_doctor_table(checks))
    ok = sum(1 for c in checks if c["status"] == "ok")
    log_success(f"{ok}/{len(checks)} checks passed")


def _load_submit_opts(course, assignment, zip_name, include, config, headless, no_grade_wait):
    cfg = Config(config)
    cfg.validate()
    course = course or cfg.get("course")
    assignment = assignment or cfg.get("assignment")
    zip_name = zip_name or cfg.get("zip_name", "submission.zip")
    patterns = list(include) if include else cfg.include_patterns()
    headless = headless or cfg.get("headless", False)
    wait_grade = not no_grade_wait and cfg.get("notify_when_graded", True)
    if not course or not assignment:
        raise click.UsageError("Set course and assignment in gradescope.yml or pass -c / -a")
    return cfg, course, assignment, zip_name, patterns, headless, wait_grade


def _run_submit(course, assignment, zip_name, include, config, headless, no_grade_wait):
    print_banner("submit")
    try:
        _, course, assignment, zip_name, patterns, headless, wait_grade = _load_submit_opts(
            course, assignment, zip_name, include, config, headless, no_grade_wait
        )
        submitter = GradescopeSubmitter(headless=headless)
        submitter.create_zip(patterns, zip_name)
        clear_live()
        asyncio.run(submitter.submit_to_gradescope(course, assignment, zip_name, wait_grade))
    except click.UsageError:
        raise
    except (FileNotFoundError, ValueError) as e:
        log_error(str(e))
        print_hint(["gradescope init", "gradescope login", "gradescope submit"])
        raise SystemExit(1) from e
    except KeyboardInterrupt:
        raise SystemExit(130) from None
    except Exception as e:
        log_error(str(e))
        raise SystemExit(1) from e


def main():
    try:
        cli(standalone_mode=True)
    except SystemExit:
        raise
    except Exception as e:
        log_error(f"Fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

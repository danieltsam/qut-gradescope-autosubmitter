"""Rich helpers — orange-themed CLI output without a heavy TUI."""

from __future__ import annotations

from typing import List, Optional

import click
from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich.markup import escape

COLORS = {
    "primary": "dark_orange",
    "accent": "orange1",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "muted": "dim",
}

console = Console(
    theme=Theme(
        {
            "info": COLORS["primary"],
            "success": COLORS["success"],
            "warning": COLORS["warning"],
            "error": COLORS["error"],
        }
    )
)


def get_colors():
    return COLORS


def clear_live() -> None:
    """Clear any Rich live/progress row so plain log lines don't get overwritten."""
    while True:
        try:
            console.clear_live()
        except IndexError:
            break


def _style(text: str, color: str) -> str:
    return f"[{color}]{escape(text)}[/{color}]"


def print_cli_header() -> None:
    """Compact centered title for --help and --version."""
    p, a = COLORS["primary"], COLORS["accent"]
    line = Text()
    line.append("gradescope", style=f"bold {p}")
    line.append(" · ", style=COLORS["muted"])
    line.append("QUT Gradescope Auto Submitter", style=f"bold {a}")
    console.print()
    console.print(Align.center(line))


def print_version(version: str) -> None:
    """Styled --version output."""
    import sys

    print_cli_header()
    console.print(Align.center(Text(f"v{version.lstrip('v')}", style=f"bold {COLORS['accent']}")))
    console.print(
        Align.center(Text(f"Python {sys.version.split()[0]}", style=COLORS["muted"]))
    )
    console.print(
        Align.center(
            Text("https://pypi.org/project/qut-gradescope-autosubmitter/", style="dim underline")
        )
    )
    console.print()


def print_root_help(ctx: click.Context) -> None:
    """Main `gradescope --help` / bare `gradescope`."""
    p, a, m = COLORS["primary"], COLORS["accent"], COLORS["muted"]
    print_cli_header()
    console.print(
        Align.center(
            Text(
                "Bundle, upload, and poll Gradescope — log in once with the browser.",
                style=m,
            )
        )
    )
    console.print()
    console.print(Rule(style=p))

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style=f"bold {p}",
        border_style=p,
        padding=(0, 1),
    )
    table.add_column("Command", style=f"bold {a}", no_wrap=True)
    table.add_column("What it does")

    for name in sorted(ctx.command.commands):
        cmd = ctx.command.commands[name]
        table.add_row(name, escape(cmd.get_short_help_str() or ""))

    console.print(table)
    console.print()
    console.print(
        f"[{m}]Typical flow:[/]  "
        f"[{a}]init[/] → [{a}]login[/] → [{a}]submit[/]  "
        f"[{m}]·[/]  [{m}]Details:[/] [{p}]gradescope <cmd> --help[/]  "
        f"[{m}]·[/]  [{m}]Version:[/] [{p}]--version[/]"
    )
    console.print(Rule(style=p))
    console.print()


def _option_default_suffix(opt: click.Option) -> str:
    """Human-readable default for help — hide Click's internal Sentinel.UNSET."""
    if opt.is_flag:
        return ""
    default = opt.default
    if default is None or str(default) == "Sentinel.UNSET" or default == ():
        return ""
    return f" [dim](default: {default})[/]"


def print_command_help(ctx: click.Context) -> None:
    """Per-command `gradescope <cmd> --help`."""
    p, a, m = COLORS["primary"], COLORS["accent"], COLORS["muted"]
    cmd = ctx.command
    name = ctx.info_name or cmd.name

    console.print()
    console.print(f"[bold {p}]gradescope[/] [bold {a}]{escape(name)}[/]")
    if cmd.help:
        console.print(f"  [{m}]{escape(cmd.help)}[/]")
    console.print()

    opts = [
        param
        for param in cmd.get_params(ctx)
        if isinstance(param, click.Option) and param.name != "help"
    ]
    if opts:
        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style=f"bold {p}",
            border_style=p,
        )
        table.add_column("Option", style=a, no_wrap=True)
        table.add_column("Description")
        for opt in opts:
            opts_str = ", ".join(opt.opts)
            if opt.is_flag:
                opts_str = opts_str or f"--{opt.name}"
            table.add_row(opts_str, escape(opt.help or "") + _option_default_suffix(opt))
        console.print(table)
        console.print()

    console.print(f"[{m}]Run from your assignment repo (needs gradescope.yml).[/]")
    console.print()


def print_banner(subtitle: str = "submit") -> None:
    """One-line command header."""
    p, a = COLORS["primary"], COLORS["accent"]
    console.print(f"[bold {p}]gradescope[/] [dim]·[/] [bold {a}]{escape(subtitle)}[/]")


def log_info(message: str) -> None:
    console.print(f"{_style('·', COLORS['primary'])} {escape(message)}")


def log_success(message: str) -> None:
    console.print(f"{_style('✓', COLORS['success'])} {escape(message)}")


def log_warning(message: str) -> None:
    console.print(f"{_style('!', COLORS['warning'])} {escape(message)}")


def log_error(message: str) -> None:
    console.print(f"{_style('✗', COLORS['error'])} {escape(message)}")


def create_hook_panel(hook_path: str, command: str) -> Panel:
    return Panel(
        f"[bold]Hook[/bold]     {escape(hook_path)}\n"
        f"[bold]Command[/bold]  {escape(command)}",
        title="[bold]Git hook installed[/bold]",
        border_style=COLORS["primary"],
        box=box.ROUNDED,
        padding=(0, 1),
    )


def print_hint(steps: List[str]) -> None:
    """Numbered next-steps panel (init, errors)."""
    body = "\n".join(
        f"[{COLORS['primary']}]{i}.[/] [{COLORS['accent']}]{escape(s)}[/]"
        for i, s in enumerate(steps, 1)
    )
    console.print(
        Panel(
            body,
            title="[bold]Next steps[/bold]",
            border_style=COLORS["primary"],
            box=box.ROUNDED,
            padding=(0, 1),
        )
    )


def log_bundle(
    filename: str, file_count: int, size_str: str, sample_files: Optional[List[str]] = None
) -> None:
    """Compact bundle line (no panel, no second line that can collide with live UI)."""
    p = COLORS["primary"]
    detail = f"{file_count} files, {escape(size_str)}"
    if sample_files:
        preview = sample_files[:4]
        extra = len(sample_files) - len(preview)
        names = ", ".join(preview)
        if extra > 0:
            names += f" (+{extra} more)"
        detail += f" — {escape(names)}"
    console.print(
        f"{_style('✓', COLORS['success'])} "
        f"Created [{p}]{escape(filename)}[/] ({detail})"
    )


def create_config_panel(rows: List[tuple]) -> Panel:
    """Key/value panel for validate."""
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style=f"bold {COLORS['primary']}", width=12)
    table.add_column("Value")
    for key, value in rows:
        table.add_row(key, escape(str(value)))
    return Panel(
        table,
        title="[bold]Configuration[/bold]",
        border_style=COLORS["primary"],
        box=box.ROUNDED,
    )


def create_doctor_table(checks: list) -> Table:
    p = COLORS["primary"]
    table = Table(
        title="[bold]Health check[/bold]",
        title_style=p,
        box=box.ROUNDED,
        border_style=p,
        header_style=f"bold {p}",
    )
    table.add_column("Component", style=p)
    table.add_column("Status", justify="center")
    table.add_column("Details", style=COLORS["muted"])

    icons = {"ok": "✓", "error": "✗", "warning": "!"}
    for check in checks:
        icon = icons.get(check["status"], "?")
        color = COLORS.get(check["status"], "white")
        if check["status"] == "warning":
            color = COLORS["warning"]
        table.add_row(
            check["component"],
            f"[{color} bold]{icon}[/]",
            escape(str(check["details"])),
        )
    return table


def create_progress_bar(description: str = "Processing...") -> Progress:
    return Progress(
        SpinnerColumn(style=COLORS["primary"]),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=32, style=COLORS["muted"], complete_style=COLORS["accent"]),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    )


def create_spinner_progress() -> Progress:
    """Grade wait spinner — one elapsed timer (TimeElapsedColumn only)."""
    clear_live()
    return Progress(
        SpinnerColumn(style=COLORS["primary"]),
        TextColumn("[bold]{task.description}[/]"),
        BarColumn(
            bar_width=20,
            style=COLORS["muted"],
            pulse_style=COLORS["accent"],
        ),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )


class StepTracker:
    """Lightweight step labels — no live progress bar."""

    def __init__(self, total_steps: int):
        self.total_steps = total_steps
        self.current_step = 0

    def next_step(self, description: str) -> None:
        self.current_step += 1
        clear_live()
        p = COLORS["primary"]
        console.print(
            f"[{p}]›[/] [{self.current_step}/{self.total_steps}] {escape(description)}",
            soft_wrap=True,
        )

    def complete_step(self, message: str = None) -> None:
        if message:
            log_success(message)

    def complete(self, message: str = None) -> None:
        if message:
            log_success(message)

    def stop(self) -> None:
        pass

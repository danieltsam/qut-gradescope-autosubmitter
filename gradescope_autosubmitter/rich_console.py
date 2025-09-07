"""Rich console utilities for enhanced CLI output."""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.prompt import Prompt
from rich import box
from datetime import datetime
import time

# Global console instance
console = Console()

# UI Configuration support
_ui_config = None

def get_ui_config():
    """Get current UI configuration, loading it if needed."""
    global _ui_config
    if _ui_config is None:
        try:
            from .ui_config import load_ui_config
            _ui_config = load_ui_config()
        except ImportError:
            # Fallback to default config if ui_config module is not available
            _ui_config = {
                "log_timestamps": True,
                "colors": {
                    "primary": "cyan",
                    "success": "green",
                    "warning": "yellow", 
                    "error": "red"
                },
                "animations": True,
                "compact_mode": False,
                "show_step_timings": True,
                "grade_wait_display": "timer"
            }
    return _ui_config

def reload_ui_config():
    """Reload UI configuration from file."""
    global _ui_config
    _ui_config = None
    return get_ui_config()

def get_colors():
    """Get the current color configuration as a convenient dict."""
    config = get_ui_config()
    return config['colors']

def timestamp() -> str:
    """Generate a timestamp string."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-2]

def log_info(message: str, prefix: str = "INFO") -> None:
    """Log an info message with Rich formatting."""
    config = get_ui_config()
    color = config['colors']['primary']
    timestamp_str = f"[{color}]\\[{timestamp()}][/{color}] " if config['log_timestamps'] else ""
    console.print(f"{timestamp_str}[{color}]{prefix}[/{color}] {message}")

def log_success(message: str, prefix: str = "✓") -> None:
    """Log a success message with Rich formatting."""
    config = get_ui_config()
    primary_color = config['colors']['primary']
    timestamp_str = f"[{primary_color}]\\[{timestamp()}][/{primary_color}] " if config['log_timestamps'] else ""
    color = config['colors']['success']
    console.print(f"{timestamp_str}[{color}]{prefix}[/{color}] {message}")

def log_warning(message: str, prefix: str = "WARN") -> None:
    """Log a warning message with Rich formatting."""
    config = get_ui_config()
    primary_color = config['colors']['primary']
    timestamp_str = f"[{primary_color}]\\[{timestamp()}][/{primary_color}] " if config['log_timestamps'] else ""
    color = config['colors']['warning']
    console.print(f"{timestamp_str}[{color}]{prefix}[/{color}] {message}")

def log_error(message: str, prefix: str = "ERROR") -> None:
    """Log an error message with Rich formatting."""
    config = get_ui_config()
    primary_color = config['colors']['primary']
    timestamp_str = f"[{primary_color}]\\[{timestamp()}][/{primary_color}] " if config['log_timestamps'] else ""
    color = config['colors']['error']
    console.print(f"{timestamp_str}[{color}]{prefix}[/{color}] {message}")

def log_step(step: int, total: int, message: str, status: str = "in_progress") -> None:
    """Log a step in a multi-step process."""
    config = get_ui_config()
    primary_color = config['colors']['primary']
    if status == "complete":
        icon = "✓"
        color = config['colors']['success']
    elif status == "in_progress":
        icon = ">"
        color = config['colors']['primary']
    else:
        icon = "..."
        color = config['colors']['warning']
    
    console.print(f"[{primary_color}]\\[{timestamp()}][/{primary_color}] [{color}]{icon}[/{color}] [bold][{step}/{total}][/bold] {message}")

def create_submission_summary(course: str, assignment: str, file: str, grade: str = None) -> Panel:
    """Create a formatted submission summary panel."""
    config = get_ui_config()
    primary_color = config['colors']['primary']
    success_color = config['colors']['success']
    
    content = f"""Course: [{primary_color}]{course}[/{primary_color}]
Assignment: [{primary_color}]{assignment}[/{primary_color}]
File: [{primary_color}]{file}[/{primary_color}]"""
    
    if grade:
        content += f"\nGrade: [bold {success_color}]{grade}[/bold {success_color}]"
    
    return Panel(
        content,
        title="Submission Summary",
        border_style=primary_color,
        box=box.ROUNDED
    )

def create_credential_status_table(username: str = None, password: str = None, 
                                 env_path: str = None) -> Table:
    """Create a table showing credential status."""
    config = get_ui_config()
    primary_color = config['colors']['primary']
    success_color = config['colors']['success']
    
    table = Table(title="Credential Status", box=box.ROUNDED)
    table.add_column("Item", style=primary_color, no_wrap=True)
    table.add_column("Status", style="magenta")
    table.add_column("Details", style=success_color)
    
    # Username status
    if username:
        table.add_row("Username", "✅ Set", username)
    else:
        table.add_row("Username", "❌ Missing", "Not configured")
    
    # Password status
    if password:
        masked = "•" * min(len(password), 12)
        table.add_row("Password", "✅ Set", masked)
    else:
        table.add_row("Password", "❌ Missing", "Not configured")
    
    # Storage location
    if env_path:
        table.add_row("Storage", "📁 .env file", env_path)
    else:
        table.add_row("Storage", "🌍 Environment", "Session variables")
    
    return table

def create_doctor_table(checks: list) -> Table:
    """Create a system diagnostics table."""
    config = get_ui_config()
    primary_color = config['colors']['primary']
    
    table = Table(title="System Diagnostics", box=box.ROUNDED)
    table.add_column("Component", style=primary_color, no_wrap=True)
    table.add_column("Status", style="magenta", width=12)
    table.add_column("Details", style="dim")
    
    for check in checks:
        # Use consistent single-character status indicators
        success_color = config['colors']['success']
        error_color = config['colors']['error']
        warning_color = config['colors']['warning']
        
        if check["status"] == "ok":
            status_text = "✅ Ok"
            status_color = success_color
        elif check["status"] == "error":
            status_text = "❌ Error"
            status_color = error_color
        else:  # warning
            status_text = "⚠  Warning"  # Use single warning symbol + space for alignment
            status_color = warning_color
        
        table.add_row(
            check["component"],
            f"[{status_color}]{status_text}[/{status_color}]",
            check["details"]
        )
    
    return table

def create_progress_bar(description: str = "Processing...") -> Progress:
    """Create a progress bar for operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    )

def create_spinner_progress(description: str = "Working...") -> Progress:
    """Create a spinner for indeterminate operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    )

class StepTracker:
    """Track progress through multi-step operations."""
    
    def __init__(self, total_steps: int, manual_completion: bool = False):
        self.total_steps = total_steps
        self.current_step = 0
        self.start_time = time.time()
        self.step_times = []
        self.manual_completion = manual_completion
        self.step_completed = False
    
    def next_step(self, description: str, status: str = "in_progress"):
        """Move to the next step."""
        config = get_ui_config()
        
        # Only auto-complete previous step if not using manual completion
        if self.current_step > 0 and not self.manual_completion:
            # Mark previous step as complete
            step_time = time.time() - self.step_start_time
            self.step_times.append(step_time)
            color = config['colors']['success']
            primary_color = config['colors']['primary']
            console.print(f"[{color}]✓[/{color}] [{primary_color}][{self.current_step}/{self.total_steps}][/{primary_color}] {self.current_description}")
            if config['show_step_timings']:
                console.print(f"[dim]    → Completed in {step_time:.1f}s[/dim]")
        
        self.current_step += 1
        self.current_description = description
        self.step_start_time = time.time()
        self.step_completed = False
        
        if self.current_step <= self.total_steps:
            color = config['colors']['primary']
            primary_color = config['colors']['primary']
            console.print(f"[{color}]>[/{color}] [{primary_color}][{self.current_step}/{self.total_steps}][/{primary_color}] {description}")
    
    def complete_step(self, success_message: str = None):
        """Mark the current step as complete with optional success message."""
        if self.current_step > 0 and self.current_step <= self.total_steps and not self.step_completed:
            config = get_ui_config()
            step_time = time.time() - self.step_start_time
            self.step_times.append(step_time)
            success_color = config['colors']['success']
            primary_color = config['colors']['primary']
            
            # In manual completion mode, don't show the step completion line
            # The success message with timestamp is enough
            if not self.manual_completion:
                # Show step completion
                console.print(f"[{success_color}]✓[/{success_color}] [{primary_color}][{self.current_step}/{self.total_steps}][/{primary_color}] {self.current_description}")
            
            # Show success message with timestamp if provided
            if success_message:
                log_success(success_message)
            
            if config['show_step_timings']:
                console.print(f"[dim]    → Completed in {step_time:.1f}s[/dim]")
            
            self.step_completed = True

    def complete(self, final_message: str = None):
        """Mark the entire process as complete."""
        config = get_ui_config()
        
        if self.current_step > 0 and self.current_step <= self.total_steps:
            step_time = time.time() - self.step_start_time
            self.step_times.append(step_time)
            success_color = config['colors']['success']
            primary_color = config['colors']['primary']
            console.print(f"[{success_color}]✓[/{success_color}] [{primary_color}][{self.current_step}/{self.total_steps}][/{primary_color}] {self.current_description}")
            if config['show_step_timings']:
                console.print(f"[dim]    → Completed in {step_time:.1f}s[/dim]")
        
        total_time = time.time() - self.start_time
        if final_message:
            log_success(f"{final_message} [dim](Total: {total_time:.1f}s)[/dim]")
        else:
            log_success(f"All steps completed [dim](Total: {total_time:.1f}s)[/dim]")

def create_credentials_interface(username: str = None, password: str = None, env_path: str = None) -> Panel:
    """Create a compact credentials interface panel."""
    
    # Status indicators
    user_status = "✅" if username else "❌"
    pass_status = "✅" if password else "❌"
    storage_info = "📁 .env" if env_path else "🌍 env vars" if (username or password) else "❌ none"
    
    config = get_ui_config()
    primary_color = config['colors']['primary']
    content = f"""[bold {primary_color}]Credentials[/bold {primary_color}]  {user_status} User  {pass_status} Pass  {storage_info}

[bold]Options:[/bold]
[{primary_color}]1[/{primary_color}] Manage .env credentials    [{primary_color}]2[/{primary_color}] Environment variables    [{primary_color}]3[/{primary_color}] Exit"""

    return Panel(
        content,
        border_style=primary_color,
        box=box.ROUNDED,
        padding=(0, 1)
    )

def create_submenu_panel(title: str, options: list, back_option: str = "Back") -> Panel:
    """Create a compact submenu panel."""
    config = get_ui_config()
    primary_color = config['colors']['primary']
    warning_color = config['colors']['warning']
    
    content = f"[bold]{title}[/bold]\n\n"
    
    for i, option in enumerate(options, 1):
        content += f"[{primary_color}]{i}[/{primary_color}] {option}\n"
    
    if back_option:
        content += f"[{primary_color}]{len(options) + 1}[/{primary_color}] {back_option}"
    
    return Panel(
        content,
        border_style=primary_color, 
        box=box.ROUNDED,
        padding=(0, 1)
    )

def create_ui_config_panel(config: dict) -> Panel:
    """Create a panel showing current UI configuration."""
    
    primary_color = config['colors']['primary']
    success_color = config['colors']['success']
    warning_color = config['colors']['warning']
    error_color = config['colors']['error']
    
    content = f"""[bold]Settings:[/bold]
[{primary_color}]•[/{primary_color}] Timestamps: {'[' + success_color + ']On[/' + success_color + ']' if config['log_timestamps'] else '[' + error_color + ']Off[/' + error_color + ']'}
[{primary_color}]•[/{primary_color}] Animations: {'[' + success_color + ']On[/' + success_color + ']' if config['animations'] else '[' + error_color + ']Off[/' + error_color + ']'}  
[{primary_color}]•[/{primary_color}] Compact Mode: {'[' + success_color + ']On[/' + success_color + ']' if config['compact_mode'] else '[' + error_color + ']Off[/' + error_color + ']'}
[{primary_color}]•[/{primary_color}] Step Timings: {'[' + success_color + ']On[/' + success_color + ']' if config['show_step_timings'] else '[' + error_color + ']Off[/' + error_color + ']'}
[{primary_color}]•[/{primary_color}] Grade Display: [{warning_color}]{config['grade_wait_display']}[/{warning_color}]

[bold]Current Colors:[/bold]
[{primary_color}]•[/{primary_color}] Primary: [{primary_color}]■[/{primary_color}] {config['colors']['primary']}
[{primary_color}]•[/{primary_color}] Success: [{success_color}]■[/{success_color}] {config['colors']['success']}  
[{primary_color}]•[/{primary_color}] Warning: [{warning_color}]■[/{warning_color}] {config['colors']['warning']}
[{primary_color}]•[/{primary_color}] Error: [{error_color}]■[/{error_color}] {config['colors']['error']}"""
    
    return Panel(
        content,
        title="UI Configuration",
        border_style=primary_color,
        box=box.ROUNDED
    )

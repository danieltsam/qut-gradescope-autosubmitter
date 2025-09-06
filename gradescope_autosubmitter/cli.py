"""Command-line interface for Gradescope Auto Submitter."""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, List

import click
from dotenv import load_dotenv

from .config import Config
from .core import GradescopeSubmitter, log
from .credentials import get_credentials


# Load .env file if available
load_dotenv()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit.')
@click.pass_context
def cli(ctx, version):
    """QUT Gradescope Auto Submitter - Secure automation for QUT students."""
    if version:
        from . import __version__
        click.echo(f"qut-gradescope-autosubmitter {__version__}")
        return
    
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
# Single-character flags first

@click.option('-c', '--course', help='Course name (e.g., CAB201)')
@click.option('-a', '--assignment', help='Assignment name (e.g., Assignment 2)')
@click.option('-f', '--file', 'zip_name', help='Output zip file name (default: submission.zip)')
@click.option('-b', '--bundle', multiple=True, help='File patterns to bundle (can be used multiple times)')
@click.option('-u', '--username', help='QUT username (or set GRADESCOPE_USERNAME env var)')
@click.option('-p', '--password', help='QUT password (or set GRADESCOPE_PASSWORD env var)')
# Double-dash flags
@click.option('--config', help='Path to config file')
@click.option('--headless', is_flag=True, help='Run browser in headless mode')
@click.option('--no-grade-wait', is_flag=True, help="Don't wait for grade to appear")
@click.option('--fresh-login', is_flag=True, help='Force fresh login (ignore saved session)')
@click.option('--manual-login', is_flag=True, help='Open browser for manual login (maximum security)')
@click.option('--no-session-save', is_flag=True, help='Don\'t save credentials to session env vars')
def submit(config, course, assignment, zip_name, bundle, headless, no_grade_wait, fresh_login, manual_login, no_session_save, username, password):
    """Submit files to Gradescope."""
    try:
        # Load configuration
        cfg = Config(config)
        cfg.validate()
        
        # Get parameters from CLI args or config
        course = course or cfg.get('course')
        assignment = assignment or cfg.get('assignment')
        zip_name = zip_name or cfg.get('zip_name', 'submission.zip')
        bundle_patterns = list(bundle) if bundle else cfg.get('bundle', ['*'])
        headless = headless or cfg.get('headless', False)
        notify_when_graded = not no_grade_wait and cfg.get('notify_when_graded', True)
        
        # Check config for always_fresh_login preference
        # Read config values and combine with CLI flags
        config_fresh_login = cfg.get('always_fresh_login', False)
        config_manual_login = cfg.get('manual_login', False)
        config_no_session_save = cfg.get('no_session_save', False)
        
        # Combine CLI flags with config values
        fresh_login = fresh_login or config_fresh_login
        manual_login = manual_login or config_manual_login
        no_session_save = no_session_save or config_no_session_save
        
        # Manual login takes precedence over fresh login
        if manual_login:
            fresh_login = True
        
        if not course or not assignment:
            click.echo("❌ Course and assignment are required. Set them in config file or use --course and --assignment")
            return 1
        
        # Handle different credential modes
        if manual_login:
            # Manual login mode - no credentials needed from us
            creds = None
            log("🔓 Manual login mode - you'll login in the browser")
        elif username and password:
            # Explicit credentials provided
            creds = (username, password)
            log("🔒 Using provided credentials")
        else:
            # Check if credentials are available
            username = os.getenv('GRADESCOPE_USERNAME')
            password = os.getenv('GRADESCOPE_PASSWORD')
            
            if not username or not password:
                click.echo("❌ No credentials found!")
                click.echo("\n💡 Recommended: Set credentials with environment variables")
                click.echo("   Run 'gradescope credentials' to see setup commands")
                click.echo("\n🔄 Alternative: Enter credentials for this submission only")
                
                if click.confirm("\nEnter credentials now (will need to re-enter next time)?"):
                    # One-time credential input
                    from .credentials import get_credentials
                    try:
                        creds = get_credentials(set_session_vars=False)
                        log("🔒 Using one-time credentials")
                    except Exception as e:
                        click.echo(f"❌ Error: {e}")
                        return 1
                else:
                    click.echo("\n💡 To set persistent credentials:")
                    click.echo("   Run 'gradescope credentials' to see setup commands")
                    click.echo("   Or set environment variables manually")
                    return 1
            else:
                creds = (username, password)
                log("🔒 Credentials loaded from environment")
        
        # Create submitter and run submission
        if manual_login:
            # Force non-headless for manual login
            submitter = GradescopeSubmitter(None, None, False, True, manual_login=True)
        else:
            submitter = GradescopeSubmitter(creds[0], creds[1], headless, fresh_login)
        
        submitter.create_zip(bundle_patterns, zip_name)
        
        asyncio.run(submitter.submit_to_gradescope(
            course, assignment, zip_name, notify_when_graded
        ))
        
        click.echo("\n🎉 Submission completed successfully!\n")
        
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"\n❌ {e}")
        click.echo("\nSetup Help:")
        click.echo("1. Run 'gradescope init' to create a config file")
        click.echo("2. Run 'gradescope credentials' to see credential setup commands")
        click.echo("3. Set environment variables: GRADESCOPE_USERNAME and GRADESCOPE_PASSWORD")
        click.echo("4. Or use --username and --password flags (less secure)")
        return 1
    except KeyboardInterrupt:
        click.echo("\n\nOperation cancelled by user\n")
        return 1
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {e}\n")
        return 1


@cli.command()
@click.option('--path', '-p', default='gradescope.yml', help='Config file path (default: gradescope.yml)')
def init(path):
    """Create an example configuration file."""
    if Path(path).exists():
        if not click.confirm(f"Config file '{path}' already exists. Overwrite?"):
            return
    
    cfg = Config()
    cfg.create_example_config(path)
    
    click.echo(f"\n📝 Next steps:")
    click.echo(f"1. Edit {path} with your course and assignment details")
    click.echo("2. Set your credentials: run 'gradescope credentials' to see setup commands")
    click.echo("3. Run: gradescope submit\n")


@cli.command()
@click.option('--config', help='Path to config file')
def validate(config):
    """Validate configuration file."""
    try:
        cfg = Config(config)
        cfg.validate()
        click.echo("✅ Configuration is valid!")
        
        # Show current config
        click.echo("\n📋 Current configuration:")
        
        # Required settings
        click.echo("\nRequired Settings:")
        for key in ['course', 'assignment']:
            value = cfg.get(key)
            if value is not None:
                click.echo(f"  {key}: {value}")
            else:
                click.echo(f"  {key}: ❌ NOT SET")
        
        # Submission settings  
        click.echo("\n📦 Submission Settings:")
        submission_defaults = {
            'zip_name': 'submission.zip',
            'bundle': ['*']
        }
        for key in ['zip_name', 'bundle']:
            value = cfg.get(key, submission_defaults[key])
            click.echo(f"  {key}: {value}")
        
        # Behavior settings
        click.echo("\nBehavior Settings:")
        behavior_defaults = {
            'notify_when_graded': True,
            'headless': False
        }
        for key in ['notify_when_graded', 'headless']:
            value = cfg.get(key, behavior_defaults[key])
            click.echo(f"  {key}: {value}")
            
        # Security settings
        click.echo("\n🔒 Security Settings:")
        security_defaults = {
            'always_fresh_login': False,
            'manual_login': False,
            'no_session_save': False
        }
        for key in ['always_fresh_login', 'manual_login', 'no_session_save']:
            value = cfg.get(key, security_defaults[key])
            click.echo(f"  {key}: {value}")
        
        # Check credentials
        click.echo("\n🔐 Credential Status:")
        username = os.getenv('GRADESCOPE_USERNAME')
        password = os.getenv('GRADESCOPE_PASSWORD')
        
        if username:
            click.echo(f"  Username: {username}")
        else:
            click.echo("  Username: ❌ NOT SET")
        
        if password:
            click.echo(f"  Password: {'*' * len(password)}")
        else:
            click.echo("  Password: ❌ NOT SET")
        
        # Show credential help
        if not username or not password:
            click.echo("\n💡 To set credentials: 'gradescope credentials' or set environment variables\n")
                
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}\n")
        return 1


@cli.command()
def debug_session():
    """Debug session persistence status."""
    from .core import SessionManager
    import asyncio
    
    async def check_session():
        session_manager = SessionManager()
        context, playwright, browser = await session_manager.get_browser_context(False)  # Non-headless for debugging
        
        try:
            # Check what's in the session directory
            click.echo(f"Session directory: {session_manager.session_dir}")
            click.echo(f"Session exists: {session_manager.session_dir.exists()}")
            
            if session_manager.session_dir.exists():
                import os
                session_files = []
                for root, dirs, files in os.walk(session_manager.session_dir):
                    for file in files:
                        rel_path = os.path.relpath(os.path.join(root, file), session_manager.session_dir)
                        session_files.append(rel_path)
                click.echo(f"Session files: {session_files[:10]}...")  # Show first 10 files
            
            is_logged_in = await session_manager.is_logged_in(context)
            click.echo(f"Logged in: {is_logged_in}")
            
            # Check session status
            page = await context.new_page()
            cookies = await context.cookies()
            
            gradescope_cookies = [c for c in cookies if 'gradescope' in c.get('domain', '')]
            qut_cookies = [c for c in cookies if 'qut.edu.au' in c.get('domain', '') or 'esoe.qut.edu.au' in c.get('domain', '')]
            
            click.echo(f"📊 Session Status:")
            click.echo(f"   Gradescope cookies: {len(gradescope_cookies)}")
            click.echo(f"   QUT SSO cookies: {len(qut_cookies)}")
            
            if qut_cookies:
                click.echo("✅ QUT SSO session active")
            else:
                click.echo("❌ No QUT SSO session - explains why login required")
            
            # Test cookie persistence
            try:
                await context.add_cookies([{
                    'name': 'test_persistence',
                    'value': 'working',
                    'domain': '.gradescope.com.au',
                    'path': '/'
                }])
                
                test_cookies = await context.cookies('https://gradescope.com.au')
                test_cookie = next((c for c in test_cookies if c['name'] == 'test_persistence'), None)
                if test_cookie:
                    click.echo("✅ Cookie persistence working")
                else:
                    click.echo("❌ Cookie persistence failed")
            except Exception as e:
                click.echo(f"❌ Cookie test failed: {e}")
            
            await page.close()
        finally:
            if browser:
                await browser.close()
            else:
                await context.close()
            await playwright.stop()
    
    asyncio.run(check_session())

@cli.command()
def cleanup():
    """Clear saved session data."""
    from .core import SessionManager
    session_manager = SessionManager()
    session_manager.cleanup_session()
    click.echo("✅ Session data cleared\n")


@cli.command()
def credentials():
    """Manage credentials - view, set, or clear them."""
    import os
    
    click.echo("🔐 Credential Management\n")
    
    # Check current credential status
    username = os.getenv('GRADESCOPE_USERNAME')
    password = os.getenv('GRADESCOPE_PASSWORD')
    
    if username:
        click.echo(f"✅ Username: {username}")
    else:
        click.echo("❌ Username: Not set")
    
    if password:
        click.echo(f"✅ Password: {'*' * len(password)}")
    else:
        click.echo("❌ Password: Not set")
    
    click.echo("\nOptions:")
    click.echo("1. Show setup commands (recommended)")
    click.echo("2. Show clear commands")
    click.echo("3. View credential sources")
    click.echo("4. Exit")
    
    choice = click.prompt("\nChoose an option (1-4)", type=int)
    
    if choice == 1:
        # Show setup commands
        click.echo("\n🔧 Recommended Setup Commands:")
        click.echo("\nFor session-only credentials (current terminal):")
        click.echo("   Windows: $env:GRADESCOPE_USERNAME='n12345678'; $env:GRADESCOPE_PASSWORD='password'")
        click.echo("   Linux/Mac: export GRADESCOPE_USERNAME='n12345678'; export GRADESCOPE_PASSWORD='password'")
        click.echo("\nFor permanent credentials:")
        click.echo("   Windows: setx GRADESCOPE_USERNAME n12345678")
        click.echo("   Linux/Mac: echo 'export GRADESCOPE_USERNAME=n12345678' >> ~/.bashrc")
        click.echo("\nFor .env file (recommended for projects):")
        click.echo("   Create .env file in your project directory with:")
        click.echo("   GRADESCOPE_USERNAME=n12345678")
        click.echo("   GRADESCOPE_PASSWORD=your_password")
        
    elif choice == 2:
        # Show clear credentials commands
        click.echo("\n🗑️ Clear Credentials Commands:")
        click.echo("\nTo clear session environment variables:")
        click.echo("   Windows: Remove-Variable GRADESCOPE_USERNAME, GRADESCOPE_PASSWORD")
        click.echo("   Linux/Mac: unset GRADESCOPE_USERNAME GRADESCOPE_PASSWORD")
        click.echo("\nTo clear permanent environment variables:")
        click.echo("   Windows: setx GRADESCOPE_USERNAME \"\"")
        click.echo("            setx GRADESCOPE_PASSWORD \"\"")
        click.echo("   Linux/Mac: Remove from ~/.bashrc, ~/.zshrc, etc.")
        click.echo("\nTo clear .env file:")
        click.echo("   Delete or edit the .env file in your project directory")
        
    elif choice == 3:
        # Show credential sources
        click.echo("\n📋 Credential Sources (in order of priority):")
        click.echo("1. Session environment variables (current session only)")
        click.echo("2. System environment variables (persistent)")
        click.echo("3. .env file (project-specific)")
        click.echo("4. One-time input in gradescope submit")
        
    elif choice == 4:
        click.echo("👋 Goodbye!\n")
        
    else:
        click.echo("❌ Invalid choice\n")


@cli.command()
def doctor():
    """Check system requirements and configuration."""
    click.echo("QUT Gradescope Auto Submitter - System Check\n")
    
    # Check Python version
    import sys
    if sys.version_info >= (3, 8):
        click.echo(f"✅ Python {sys.version.split()[0]}")
    else:
        click.echo(f"❌ Python {sys.version.split()[0]} (requires 3.8+)")
    
    # Check dependencies
    try:
        import playwright
        # Try to get version from multiple sources
        playwright_version = None
        try:
            # Method 1: Try __version__ attribute
            from playwright import __version__ as playwright_version
        except ImportError:
            try:
                # Method 2: Try importlib.metadata (Python 3.8+)
                import importlib.metadata
                playwright_version = importlib.metadata.version('playwright')
            except (ImportError, Exception):
                try:
                    # Method 3: Try pkg_resources (fallback)
                    import pkg_resources
                    playwright_version = pkg_resources.get_distribution('playwright').version
                except Exception:
                    pass
        
        if playwright_version:
            click.echo(f"✅ Playwright {playwright_version}")
        else:
            click.echo("✅ Playwright installed (version detection failed)")
    except ImportError:
        click.echo("❌ Playwright not installed")
    
    try:
        import yaml
        click.echo("✅ PyYAML available")
    except ImportError:
        click.echo("❌ PyYAML not installed")
    
    # Check Playwright browser installation (fast file check)
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            # Check if Chromium executable exists without launching
            chromium_path = p.chromium.executable_path
            if chromium_path and Path(chromium_path).exists():
                click.echo("✅ Chromium browser available")
            else:
                click.echo("❌ Chromium browser not installed")
                click.echo("   Run: playwright install chromium")
    except ImportError:
        click.echo("❌ Playwright not available for browser check")
    except Exception as e:
        click.echo("❌ Chromium browser not installed")
        click.echo("   Run: playwright install chromium")
    
    # Check for config files
    cfg = Config()
    config_file = cfg._find_config_file()
    if config_file:
        click.echo(f"✅ Config file found: {config_file}")
        try:
            cfg.validate()
            click.echo("✅ Config file is valid")
        except Exception as e:
            click.echo(f"⚠️ Config validation warning: {e}")
    else:
        click.echo("⚠️ No config file found (run 'gradescope init')")
    
    # Check credentials
    username = os.getenv('GRADESCOPE_USERNAME')
    password = os.getenv('GRADESCOPE_PASSWORD')
    
    if username:
        click.echo("✅ Username environment variable set")
    else:
        click.echo("⚠️ GRADESCOPE_USERNAME not set")
    
    if password:
        click.echo("✅ Password environment variable set")
    else:
        click.echo("⚠️ GRADESCOPE_PASSWORD not set")
    
    click.echo("\nIf any items show ❌, install missing dependencies or run setup commands.")
    click.echo("\n💡 Next steps:")
    click.echo("   1. Set credentials: gradescope credentials")
    click.echo("   2. Create config: gradescope init")
    click.echo("   3. Submit: gradescope submit\n")


def main():
    """Entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        click.echo(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

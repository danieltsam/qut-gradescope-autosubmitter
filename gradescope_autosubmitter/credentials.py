"""Secure credential management."""

import os
from getpass import getpass
from typing import Tuple
from pathlib import Path


def _user_env_path() -> Path:
    """Return the user-level .env path for persistent credentials."""
    if os.name == 'nt':
        # Windows: %LOCALAPPDATA%/qut_gradescope_autosubmitter/.env
        base = Path.home() / "AppData" / "Local" / "qut_gradescope_autosubmitter"
    else:
        # macOS/Linux: ~/.qut-gradescope-autosubmitter/.env
        base = Path.home() / ".qut-gradescope-autosubmitter"
    base.mkdir(parents=True, exist_ok=True)
    return base / ".env"


def _write_env_file(username: str, password: str, env_path: str | Path | None = None) -> None:
    """Create or update a local .env file with credentials."""
    # Default to user-level .env if path not provided
    path = Path(env_path) if env_path else _user_env_path()
    # Preserve any other existing keys in .env
    existing = {}
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.rstrip("\n")
                    if not line or line.lstrip().startswith('#'):
                        continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        existing[k.strip()] = v
        except Exception:
            # If parse fails, we will overwrite just our keys and keep file text
            pass
    # Quote values to preserve special characters/spaces
    def _quote(value: str) -> str:
        # Escape existing backslashes and double quotes
        escaped = value.replace('\\', r'\\').replace('"', r'\"')
        return f'"{escaped}"'

    existing['GRADESCOPE_USERNAME'] = _quote(username)
    existing['GRADESCOPE_PASSWORD'] = _quote(password)
    # Write back
    with open(path, 'w', encoding='utf-8') as f:
        for k, v in existing.items():
            f.write(f"{k}={v}\n")


def get_credentials(set_session_vars: bool = True, persist_to_env: bool = False, force_prompt: bool = False) -> Tuple[str, str]:
    """Get credentials from environment variables or prompt user."""
    username = None if force_prompt else os.getenv('GRADESCOPE_USERNAME')
    password = None if force_prompt else os.getenv('GRADESCOPE_PASSWORD')
    
    prompted_for_credentials = False
    
    # Validate username format if provided via environment
    if username and (not username.startswith('n') or len(username) != 9):
        print("⚠️ Warning: Username should be in format 'n12345678' (QUT student number)")
    
    if not username:
        prompted_for_credentials = True
        while True:
            username = input("Enter your QUT username (e.g., n12345678): ").strip()
            if not username:
                print("❌ Username cannot be empty")
                continue
            if not username.startswith('n') or len(username) != 9:
                response = input("⚠️ Username format seems incorrect. Continue anyway? (y/n): ").strip().lower()
                if response == 'n':
                    continue
            break
    
    if not password:
        prompted_for_credentials = True
        
        def _sanitize_pasted(value: str) -> str:
            # Remove zero-width and bidi marks
            value = (
                value
                .replace('\u200b', '')   # zero-width space
                .replace('\u200c', '')   # zero-width non-joiner
                .replace('\u200d', '')   # zero-width joiner
                .replace('\u200e', '')   # left-to-right mark
                .replace('\u200f', '')   # right-to-left mark
            )
            # Common Ctrl+V literal in consoles shows as ^V (or ^v)
            value = value.replace('^V', '').replace('^v', '')
            # Strip common trailing newlines from paste
            value = value.rstrip("\r\n")
            # Drop ASCII control characters (0-31, 127)
            value = ''.join(ch for ch in value if (32 <= ord(ch) <= 126) or (ord(ch) >= 160))
            return value

        # Prompt in a loop until we get a non-empty sanitized password
        for _ in range(5):
            raw_password = getpass("Enter your QUT password: ")
            password = _sanitize_pasted(raw_password)
            if password:
                break
            print("⚠️ Paste didn’t come through. Use right-click or Shift+Insert to paste (Ctrl+V may not work). Try again.")
        else:
            raise ValueError("❌ Password cannot be empty after sanitization")
    
    # If we prompted for credentials, set session vars and optionally persist to .env
    if prompted_for_credentials:
        if set_session_vars:
            os.environ['GRADESCOPE_USERNAME'] = username
            os.environ['GRADESCOPE_PASSWORD'] = password
            print("✅ Credentials set for this session only")
        if persist_to_env:
            user_env = _user_env_path()
            _write_env_file(username, password, env_path=user_env)
            print(f"✅ Credentials saved to {user_env} (user-level file)")
            print("⚠️ Anyone with access to your user account can read this file.")
            print("   Consider environment variables for a more secure approach.")
    
    return username, password



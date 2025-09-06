"""Secure credential management."""

import os
from getpass import getpass
from typing import Tuple


def get_credentials(set_session_vars: bool = True) -> Tuple[str, str]:
    """Get credentials from environment variables or prompt user."""
    username = os.getenv('GRADESCOPE_USERNAME')
    password = os.getenv('GRADESCOPE_PASSWORD')
    
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
        password = getpass("Enter your QUT password: ").strip()
        if not password:
            raise ValueError("❌ Password cannot be empty")
    
    # If we prompted for credentials and user wants session vars, set them
    if prompted_for_credentials and set_session_vars:
        os.environ['GRADESCOPE_USERNAME'] = username
        os.environ['GRADESCOPE_PASSWORD'] = password
        print("✅ Credentials set for this session only")
        print("💡 For persistence, use environment variables or .env file")
    
    return username, password



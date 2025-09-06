"""Configuration management for Gradescope Auto Submitter."""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path


class Config:
    """Configuration manager supporting YAML files and environment variables."""
    
    DEFAULT_CONFIG_FILES = [
        "gradescope.yml",
        "gradescope.yaml", 
        ".gradescope.yml",
        ".gradescope.yaml",
        "gradescope.json",  # Legacy support
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _find_config_file(self) -> Optional[Path]:
        """Find the first available config file."""
        if self.config_path:
            path = Path(self.config_path)
            if path.exists():
                return path
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        # Search for default config files
        for filename in self.DEFAULT_CONFIG_FILES:
            path = Path(filename)
            if path.exists():
                return path
        
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        config_file = self._find_config_file()
        
        if not config_file:
            # Return minimal default config
            return {
                "zip_name": "submission.zip",
                "bundle": ["*"],
                "notify_when_graded": True
            }
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yml', '.yaml']:
                return yaml.safe_load(f) or {}
            else:
                # Legacy JSON support
                import json
                return json.load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with environment variable override."""
        # Handle backward compatibility for 'file' -> 'zip_name'
        if key == 'file':
            # Check for new key first, then fall back to old key
            zip_name = self._get_raw('zip_name', default)
            if zip_name != default:
                return zip_name
            return self._get_raw('file', default)
        elif key == 'zip_name':
            # Check for new key first, then fall back to old key
            zip_name = self._get_raw('zip_name', default)
            if zip_name != default:
                return zip_name
            return self._get_raw('file', default)
        
        return self._get_raw(key, default)
    
    def _get_raw(self, key: str, default: Any = None) -> Any:
        """Get configuration value with environment variable override (internal)."""
        # Check environment variables first (with GRADESCOPE_ prefix)
        env_key = f"GRADESCOPE_{key.upper()}"
        env_value = os.getenv(env_key)
        
        if env_value is not None:
            # Convert string to appropriate type for known keys
            boolean_keys = ['notify_when_graded', 'headless', 'always_fresh_login', 'manual_login', 'no_session_save']
            if key in boolean_keys and env_value.lower() in ['false', '0', 'no']:
                return False
            elif key in boolean_keys and env_value.lower() in ['true', '1', 'yes']:
                return True
            elif key == 'bundle':
                return env_value.split(',') if env_value else default
            return env_value
        
        return self.config.get(key, default)
    
    def validate(self) -> None:
        """Validate required configuration."""
        required_fields = ['course', 'assignment']
        missing_fields = []
        
        for field in required_fields:
            if not self.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required config fields: {', '.join(missing_fields)}")
    
    def create_example_config(self, path: str = "gradescope.yml") -> None:
        """Create an example configuration file."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write("# Gradescope Auto Submitter Configuration\n")
            f.write("# Save this as 'gradescope.yml' in your project root\n")
            f.write("\n")
            f.write("# Required: Course and assignment details (replace example comment values)\n")
            f.write("course: #cab201              # Course code (must partially match Gradescope course name)\n")
            f.write("assignment: #t6q1            # Assignment name (must partially match Gradescope assignment name)\n")
            f.write("\n")
            f.write("# Optional: Submission settings\n")
            f.write("zip_name: submission.zip    # Name of the zip file to create and submit\n")
            f.write("bundle:                     # File patterns to include in submission\n")
            f.write("  - \"*\"                    # Everything (respects .gitignore)\n")
            f.write("  # - \"*.py\"               # All Python files\n")
            f.write("  # - \"*.cpp\"              # All C++ files\n")
            f.write("  # - \"*.h\"                # All header files\n")
            f.write("  # - \"src/**/*\"           # Everything in src directory\n")
            f.write("\n")
            f.write("# Optional: Behaviour settings\n")
            f.write("notify_when_graded: true    # Wait for and display grade (default: true)\n")
            f.write("headless: false             # Run browser in background (default: false)\n")
            f.write("always_fresh_login: false   # Always login fresh\n")
            f.write("manual_login: false         # Open browser for manual login \n")
            f.write("no_session_save: false      # Don't save credentials to session env vars\n")
            f.write("\n")
            f.write("# Next Steps: Just run 'gradescope submit' - it will prompt for credentials!\n")
            f.write("# The tool automatically saves them for your session.\n")
            f.write("\n")
            f.write("# Credential Options (choose one):\n")
            f.write("# 1. Interactive: 'gradescope credentials' - manage credentials easily\n")
            f.write("# 2. Auto-prompt: 'gradescope submit' - prompts on first run\n")
            f.write("# 3. Environment variables: Set GRADESCOPE_USERNAME and GRADESCOPE_PASSWORD\n")
            f.write("# 4. .env file: Create .env file with credentials (auto-loaded)\n")
            f.write("\n")
            f.write("# Environment Variables (choose your platform):\n")
            f.write("\n")
            f.write("# Linux/Mac:\n")
            f.write("# export GRADESCOPE_USERNAME=\"n12345678\"\n")
            f.write("# export GRADESCOPE_PASSWORD=\"your_password\"\n")
            f.write("\n")
            f.write("# Windows PowerShell:\n")
            f.write("# $env:GRADESCOPE_USERNAME = \"n12345678\"\n")
            f.write("# $env:GRADESCOPE_PASSWORD = \"your_password\"\n")
            f.write("\n")
        
        print(f"✅ Created example config: {path}")
        print("Edit this file with your course and assignment details.")



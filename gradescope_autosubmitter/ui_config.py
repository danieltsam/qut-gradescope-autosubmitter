"""
UI Configuration and Customization for Rich Console Experience
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Default UI configuration
DEFAULT_UI_CONFIG = {
    "theme": "default",  # default, minimal, colorful, professional
    "progress_style": "bar",  # bar, spinner, dots, minimal
    "log_timestamps": True,
    "log_level": "info",  # debug, info, warning, error
    "colors": {
        "primary": "salmon1",
        "success": "medium_spring_green", 
        "warning": "khaki1",
        "error": "light_coral"
    },
    "animations": True,  # Enable/disable progress animations
    "compact_mode": False,  # Reduced spacing and output
    "show_step_timings": True,  # Show completion times for steps
    "grade_wait_display": "timer",  # timer, spinner, minimal, none
    "grade_blink_interval": 1.2,  # seconds between blink toggles during grade wait
}

# Available color options for UI customization - Top 10 beautiful and distinct colors
AVAILABLE_COLORS = {
    "red": "light_coral",
    "green": "medium_spring_green", 
    "blue": "blue",
    "yellow": "khaki1",
    "sky_blue": "light_sky_blue1",     # Beautiful pastel blue
    "sage_green": "dark_sea_green2",   # Soft sage green
    "lavender": "medium_purple1",      # Gentle lavender purple
    "gold": "gold1",                   # Rich gold
    "mint": "aquamarine1",             # Fresh mint green
    "rose": "hot_pink2",               # Elegant rose pink
    "salmon": "salmon1",               # New default primary option
    "peach": "navajo_white1",          # Soft peach
    "teal": "dark_turquoise",          # Sophisticated teal
    "periwinkle": "cornflower_blue"    # Soft periwinkle blue
}

def get_config_path() -> Path:
    """Get the path to the UI config file."""
    # Use same directory as credentials for consistency
    if os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('LOCALAPPDATA', '~')) / 'qut_gradescope_autosubmitter'
    else:  # Linux/Mac
        config_dir = Path.home() / '.qut-gradescope-autosubmitter'
    
    config_dir.mkdir(exist_ok=True)
    return config_dir / 'ui_config.json'

def load_ui_config() -> Dict[str, Any]:
    """Load UI configuration from file or return defaults."""
    config_path = get_config_path()
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                
            # Merge with defaults to ensure all keys exist
            config = DEFAULT_UI_CONFIG.copy()
            config.update(user_config)
            
            # Ensure colors dict exists and has all required keys
            if 'colors' in user_config:
                config['colors'] = {**DEFAULT_UI_CONFIG['colors'], **user_config.get('colors', {})}
                
            return config
        except (json.JSONDecodeError, FileNotFoundError):
            return DEFAULT_UI_CONFIG.copy()
    
    return DEFAULT_UI_CONFIG.copy()

def save_ui_config(config: Dict[str, Any]) -> None:
    """Save UI configuration to file."""
    config_path = get_config_path()
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

def get_available_colors() -> dict:
    """Get dictionary of available colors."""
    return AVAILABLE_COLORS.copy()

def get_current_colors() -> dict:
    """Get the current color configuration."""
    config = load_ui_config()
    return config.get('colors', DEFAULT_UI_CONFIG['colors'])

def set_color(color_type: str, color_value: str) -> bool:
    """Set a specific color in the UI configuration."""
    if color_value not in AVAILABLE_COLORS.values():
        return False
    
    try:
        config = load_ui_config()
        config['colors'][color_type] = color_value
        save_ui_config(config)
        return True
    except Exception:
        return False

def reset_colors_to_default() -> bool:
    """Reset all colors to default values."""
    try:
        config = load_ui_config()
        config['colors'] = DEFAULT_UI_CONFIG['colors'].copy()
        save_ui_config(config)
        return True
    except Exception:
        return False

def update_setting(key: str, value: Any) -> None:
    """Update a single UI setting."""
    config = load_ui_config()
    
    # Handle nested keys like 'colors.primary'
    if '.' in key:
        parts = key.split('.')
        if len(parts) == 2 and parts[0] == 'colors':
            config['colors'][parts[1]] = value
        else:
            config[key] = value
    else:
        config[key] = value
    
    save_ui_config(config)

def reset_to_defaults() -> None:
    """Reset UI configuration to defaults."""
    config_path = get_config_path()
    if config_path.exists():
        config_path.unlink()

def get_color_categories() -> list:
    """Get list of color categories that can be customized."""
    return ["primary", "success", "warning", "error"]

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate a UI configuration dict."""
    required_keys = ['theme', 'progress_style', 'log_timestamps', 'colors', 'animations']
    
    if not all(key in config for key in required_keys):
        return False
    
    if not isinstance(config['colors'], dict):
        return False
    
    required_colors = ['primary', 'success', 'warning', 'error', 'info', 'accent']
    if not all(color in config['colors'] for color in required_colors):
        return False
    
    return True

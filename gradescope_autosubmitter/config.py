"""Load gradescope.yml and optional GRADESCOPE_* environment overrides."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

EXAMPLE_CONFIG = """\
# Partial match on names shown in Gradescope (quotes optional but recommended)

course: "cab201"
assignment: "t6q1"

zip_name: submission.zip

# Files to include (globs). In a git repo, only tracked/unignored files are considered.
include:
  - "*.py"
  - "*.h"
  # - "*"   # everything git would list

notify_when_graded: true
headless: false
"""


class Config:
    CONFIG_NAMES = ("gradescope.yml", "gradescope.yaml", ".gradescope.yml")

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config = self._load()

    def _find_file(self) -> Optional[Path]:
        if self.config_path:
            path = Path(self.config_path)
            if not path.exists():
                raise FileNotFoundError(f"Config not found: {path}")
            return path
        for name in self.CONFIG_NAMES:
            path = Path(name)
            if path.exists():
                return path
        return None

    def _load(self) -> Dict[str, Any]:
        path = self._find_file()
        if not path:
            return {}
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        env_key = f"GRADESCOPE_{key.upper()}"
        env_val = os.getenv(env_key)
        if env_val is not None:
            if key in ("notify_when_graded", "headless"):
                return env_val.lower() in ("true", "1", "yes")
            if key in ("include", "bundle"):
                return [p.strip() for p in env_val.split(",") if p.strip()]
            return env_val

        if key == "zip_name":
            return self.config.get("zip_name", self.config.get("file", default))

        return self.config.get(key, default)

    def include_patterns(self) -> List[str]:
        patterns = self.get("include")
        if patterns is None:
            patterns = self.get("bundle")
        if not patterns:
            return ["*"]
        if isinstance(patterns, str):
            return [patterns]
        return list(patterns)

    def validate(self) -> None:
        missing = [k for k in ("course", "assignment") if not self.get(k)]
        if missing:
            raise ValueError(f"Missing in config: {', '.join(missing)}")

    def create_example_config(self, path: str = "gradescope.yml") -> None:
        Path(path).write_text(EXAMPLE_CONFIG, encoding="utf-8")

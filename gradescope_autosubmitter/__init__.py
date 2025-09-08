"""
QUT Gradescope Auto Submitter

A secure, production-ready tool for automating Gradescope submissions for QUT students.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("qut-gradescope-autosubmitter")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development mode
    __version__ = "1.2.0-dev"

__author__ = "Daniel Sam"
__email__ = "daniel.sam@gmx.com"

from .core import GradescopeSubmitter
from .config import Config

__all__ = ["GradescopeSubmitter", "Config"]



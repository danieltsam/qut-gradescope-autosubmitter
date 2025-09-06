"""
QUT Gradescope Auto Submitter

A secure, production-ready tool for automating Gradescope submissions for QUT students.
"""

__version__ = "1.0.0"
__author__ = "Daniel Sam"
__email__ = "daniel.sam@gmx.com"

from .core import GradescopeSubmitter
from .config import Config

__all__ = ["GradescopeSubmitter", "Config"]



"""
__init__.py

This file makes the 'learning' directory a Python package.
It also serves as a central point to import and register all available learning modules.
"""

from .youtube import YouTubeLearner
from .web_scraper import WebScraper

__all__ = [
    "YouTubeLearner",
    "WebScraper",
]

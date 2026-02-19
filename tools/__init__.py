"""
__init__.py

This file makes the 'tools' directory a Python package.
It also serves as a central point to import and register all available tools.
"""

from .base import Tool
from .shell import ShellTool
from .filesystem import FileSystemTool
from .browser import BrowserTool
from .web_search import WebSearchTool
from .app_control import AppControlTool
from .deep_search import DeepSearchTool

# List of all available tools
ALL_TOOLS = [
    ShellTool(),
    FileSystemTool(),
    BrowserTool(),
    WebSearchTool(),
    AppControlTool(),
    DeepSearchTool(),
]

__all__ = [
    "Tool",
    "ShellTool",
    "FileSystemTool",
    "BrowserTool",
    "WebSearchTool",
    "AppControlTool",
    "DeepSearchTool",
    "ALL_TOOLS",
]

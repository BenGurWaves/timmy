"""
__init__.py

This file makes the 'skills' directory a Python package.
It also serves as a central point to import and register all available skills.
"""

from .base import Skill
from .web_search import WebSearchSkill
from .file_manager import FileManagerSkill
from .note_taking import NoteTakingSkill
from .system_info import SystemInfoSkill
from .code_writer import CodeWriterSkill

# List of all available skills (excluding CodeWriterSkill as it needs a Brain instance)
ALL_SKILLS = [
    WebSearchSkill(),
    FileManagerSkill(),
    NoteTakingSkill(),
    SystemInfoSkill(),
]

__all__ = [
    "Skill",
    "WebSearchSkill",
    "FileManagerSkill",
    "NoteTakingSkill",
    "SystemInfoSkill",
    "CodeWriterSkill",
    "ALL_SKILLS",
]

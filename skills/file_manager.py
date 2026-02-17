"""
file_manager.py

This skill allows the Timmy AI agent to manage files and directories using the FileSystemTool.
"""

from typing import Any, Dict
from skills.base import Skill
from tools.filesystem import FileSystemTool

class FileManagerSkill(Skill):
    """
    A skill to manage files and directories.
    """

    def __init__(self):
        super().__init__(
            name="File Manager",
            description="Performs file system operations like read, write, create, delete, and search."
        )
        self.filesystem_tool = FileSystemTool()

    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Executes a file system operation.

        Args:
            operation (str): The type of file system operation (e.g., "read", "write", "delete").
            **kwargs: Arguments specific to the operation.

        Returns:
            Dict[str, Any]: The result of the file system operation.
        """
        print(f"Executing File Manager Skill for operation: {operation}")
        return self.filesystem_tool.execute(operation=operation, **kwargs)

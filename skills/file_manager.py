from ..tools.filesystem import FileSystemTool
from .base import BaseSkill
import logging

logger = logging.getLogger(__name__)

class FileManagerSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="file_manager",
            description="Manages files and directories: read, write, create, delete, search."
        )
        self.filesystem_tool = FileSystemTool()

    def execute(self, operation: str, path: str, content: str = None, confirm: bool = True) -> str:
        logger.info(f"Executing file_manager skill: operation={operation}, path={path}")
        return self.filesystem_tool.execute(operation, path, content, confirm)

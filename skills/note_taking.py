from .base import BaseSkill
from ..tools.filesystem import FileSystemTool
import datetime
import os
import logging

logger = logging.getLogger(__name__)

class NoteTakingSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="note_taking",
            description="Takes notes and saves them to a timestamped file in the data/knowledge directory."
        )
        self.filesystem_tool = FileSystemTool()
        self.notes_dir = "./data/knowledge/notes"
        self.filesystem_tool.execute("create_dir", self.notes_dir, confirm=False) # Ensure notes directory exists

    def execute(self, note_content: str) -> str:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.notes_dir, f"note_{timestamp}.txt")
        
        logger.info(f"Saving note to {filename}")
        return self.filesystem_tool.execute("write", filename, note_content, confirm=False)

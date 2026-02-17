import os
import shutil
import logging
from .base import BaseTool
from config import config

logger = logging.getLogger(__name__)

class FileSystemTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="filesystem",
            description="Perform file system operations: read, write, create, delete, search files and folders."
        )

    def execute(self, operation: str, path: str, content: str = None, confirm: bool = config.CONFIRM_DESTRUCTIVE_ACTIONS) -> str:
        if operation == "read":
            return self._read_file(path)
        elif operation == "write":
            return self._write_file(path, content, confirm)
        elif operation == "create_dir":
            return self._create_directory(path)
        elif operation == "delete":
            return self._delete_path(path, confirm)
        elif operation == "search":
            return self._search_path(path)
        else:
            return f"Error: Unknown file system operation: {operation}"

    def _read_file(self, path: str) -> str:
        try:
            with open(path, 'r') as f:
                file_content = f.read()
            logger.info(f"Read file: {path}")
            return file_content
        except FileNotFoundError:
            return f"Error: File not found at {path}"
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return f"Error reading file: {e}"

    def _write_file(self, path: str, content: str, confirm: bool) -> str:
        if confirm:
            logger.warning(f"Writing to file {path} requires confirmation. Assuming confirmed for now.")

        try:
            with open(path, 'w') as f:
                f.write(content)
            logger.info(f"Wrote to file: {path}")
            return f"Successfully wrote to {path}"
        except Exception as e:
            logger.error(f"Error writing to file {path}: {e}")
            return f"Error writing to file: {e}"

    def _create_directory(self, path: str) -> str:
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Created directory: {path}")
            return f"Successfully created directory {path}"
        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            return f"Error creating directory: {e}"

    def _delete_path(self, path: str, confirm: bool) -> str:
        if confirm:
            logger.warning(f"Deleting {path} requires confirmation. Assuming confirmed for now.")

        try:
            if os.path.isfile(path):
                os.remove(path)
                logger.info(f"Deleted file: {path}")
                return f"Successfully deleted file {path}"
            elif os.path.isdir(path):
                shutil.rmtree(path)
                logger.info(f"Deleted directory: {path}")
                return f"Successfully deleted directory {path}"
            else:
                return f"Error: Path not found or not a file/directory: {path}"
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
            return f"Error deleting path: {e}"

    def _search_path(self, path: str) -> str:
        results = []
        for root, dirs, files in os.walk(path):
            for name in files:
                results.append(os.path.join(root, name))
            for name in dirs:
                results.append(os.path.join(root, name))
        logger.info(f"Searched path {path}. Found {len(results)} items.")
        return "\n".join(results) if results else f"No items found in {path}"

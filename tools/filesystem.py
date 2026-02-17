"""
filesystem.py

This tool provides functionalities for the Timmy AI agent to interact with the file system.
It allows reading, writing, creating, deleting, and searching files and directories.
"""

import os
import shutil
import glob
from typing import List, Dict, Any, Union
from tools.base import Tool

class FileSystemTool(Tool):
    """
    A tool for performing file system operations.
    """

    def __init__(self):
        super().__init__(
            name="File System Manager",
            description="Manages files and folders: read, write, create, delete, search."
        )

    def _confirm_destructive_action(self, action_description: str) -> bool:
        """
        Placeholder for a user confirmation prompt for destructive actions.
        In a real interactive system, this would ask the user for confirmation.
        For now, it will print a warning and proceed.
        """
        print(f"WARNING: Potentially destructive file system action: {action_description}")
        print("Please implement a user confirmation mechanism for such actions.")
        return True # For now, always proceed

    def read_file(self, path: str) -> Dict[str, Any]:
        """
        Reads the content of a file.
        """
        try:
            with open(path, 'r') as f:
                content = f.read()
            return {"status": "success", "path": path, "content": content}
        except FileNotFoundError:
            return {"status": "error", "message": f"File not found: {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def write_file(self, path: str, content: str, overwrite: bool = True) -> Dict[str, Any]:
        """
        Writes content to a file. Creates the file if it doesn't exist.
        If overwrite is False and the file exists, it will not write.
        """
        if not overwrite and os.path.exists(path):
            return {"status": "error", "message": f"File already exists and overwrite is False: {path}"}
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return {"status": "success", "path": path, "message": "File written successfully."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def append_file(self, path: str, content: str) -> Dict[str, Any]:
        """
        Appends content to an existing file. Creates the file if it doesn't exist.
        """
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'a') as f:
                f.write(content)
            return {"status": "success", "path": path, "message": "Content appended successfully."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_directory(self, path: str, exist_ok: bool = True) -> Dict[str, Any]:
        """
        Creates a new directory.
        """
        try:
            os.makedirs(path, exist_ok=exist_ok)
            return {"status": "success", "path": path, "message": "Directory created successfully."}
        except FileExistsError:
            return {"status": "error", "message": f"Directory already exists: {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_path(self, path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Deletes a file or an empty directory. If recursive is True, deletes non-empty directories.
        """
        if not self._confirm_destructive_action(f"Delete path: {path}"):
            return {"status": "aborted", "message": "Deletion aborted by user confirmation policy."}

        try:
            if os.path.isfile(path):
                os.remove(path)
                return {"status": "success", "path": path, "message": "File deleted successfully."}
            elif os.path.isdir(path):
                if recursive:
                    shutil.rmtree(path)
                    return {"status": "success", "path": path, "message": "Directory and its contents deleted successfully."}
                else:
                    os.rmdir(path) # Only deletes empty directories
                    return {"status": "success", "path": path, "message": "Empty directory deleted successfully."}
            else:
                return {"status": "error", "message": f"Path does not exist or is not a file/directory: {path}"}
        except FileNotFoundError:
            return {"status": "error", "message": f"Path not found: {path}"}
        except OSError as e:
            return {"status": "error", "message": f"OS error: {e}. Directory might not be empty or permissions issue."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_directory(self, path: str) -> Dict[str, Any]:
        """
        Lists the contents of a directory.
        """
        try:
            contents = os.listdir(path)
            return {"status": "success", "path": path, "contents": contents}
        except FileNotFoundError:
            return {"status": "error", "message": f"Directory not found: {path}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_files(self, pattern: str, root_dir: str = '.') -> Dict[str, Any]:
        """
        Searches for files matching a glob pattern within a root directory.
        """
        try:
            # glob.glob does not support recursive search in older Python versions without **
            # For a more robust recursive search, os.walk can be used.
            # For now, assuming modern Python with ** support or simple patterns.
            full_pattern = os.path.join(root_dir, pattern)
            found_files = glob.glob(full_pattern, recursive=True)
            return {"status": "success", "pattern": pattern, "root_dir": root_dir, "files": found_files}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Executes a file system operation based on the 'operation' argument.
        """
        if operation == "read":
            return self.read_file(kwargs.get("path"))
        elif operation == "write":
            return self.write_file(kwargs.get("path"), kwargs.get("content"), kwargs.get("overwrite", True))
        elif operation == "append":
            return self.append_file(kwargs.get("path"), kwargs.get("content"))
        elif operation == "create_dir":
            return self.create_directory(kwargs.get("path"), kwargs.get("exist_ok", True))
        elif operation == "delete":
            return self.delete_path(kwargs.get("path"), kwargs.get("recursive", False))
        elif operation == "list":
            return self.list_directory(kwargs.get("path"))
        elif operation == "search":
            return self.search_files(kwargs.get("pattern"), kwargs.get("root_dir", "."))
        else:
            return {"status": "error", "message": f"Unknown file system operation: {operation}"}


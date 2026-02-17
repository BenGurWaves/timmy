"""
shell.py

This tool allows the Timmy AI agent to execute arbitrary shell commands on the macOS system.
It uses Python's `subprocess` module to run commands and capture their output.
"""

import subprocess
from typing import Dict, Any
from tools.base import Tool

class ShellTool(Tool):
    """
    A tool for executing shell commands.
    """

    def __init__(self):
        super().__init__(
            name="Shell Executor",
            description="Executes any terminal command via subprocess. Use with caution."
        )

    def execute(self, command: str, confirm_destructive: bool = True) -> Dict[str, Any]:
        """
        Executes a given shell command.

        Args:
            command (str): The shell command to execute.
            confirm_destructive (bool): If True, prompts for confirmation for potentially destructive commands.
                                        Currently, this is a placeholder for future implementation.

        Returns:
            Dict[str, Any]: A dictionary containing the command, stdout, stderr, and return code.
        """
        print(f"Executing shell command: {command}")

        # Basic check for destructive commands (can be expanded)
        destructive_commands = ["rm -rf", "format", "mkfs"]
        if confirm_destructive and any(dc in command for dc in destructive_commands):
            # In a real interactive system, this would prompt the user.
            # For now, we'll just log a warning.
            print(f"WARNING: Potentially destructive command detected: {command}")
            print("Please implement a user confirmation mechanism for such commands.")
            # For automated execution, we'll proceed, but this is where a human would intervene.

        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True, # Decode stdout/stderr as text
                check=False # Do not raise an exception for non-zero exit codes
            )
            return {
                "command": command,
                "stdout": process.stdout.strip(),
                "stderr": process.stderr.strip(),
                "returncode": process.returncode
            }
        except Exception as e:
            return {
                "command": command,
                "stdout": "",
                "stderr": str(e),
                "returncode": 1
            }


import subprocess
import logging
from .base import BaseTool
from config import config

logger = logging.getLogger(__name__)

class ShellTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="shell",
            description="Execute shell commands. Use with caution, especially for destructive commands."
        )

    def execute(self, command: str, confirm: bool = config.CONFIRM_DESTRUCTIVE_ACTIONS) -> str:
        if any(dangerous_cmd in command for dangerous_cmd in config.COMMAND_BLACKLIST):
            return f"Error: Command '{command}' is blacklisted for safety reasons."

        if confirm:
            # In a real terminal, this would be an interactive prompt.
            # For now, we'll assume confirmation is handled by the agent's higher-level logic or user.
            logger.warning(f"Shell command '{command}' requires confirmation. Assuming confirmed for now.")

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            if result.stdout:
                logger.info(f"Shell command output: {result.stdout.strip()}")
                return result.stdout.strip()
            if result.stderr:
                logger.warning(f"Shell command error output: {result.stderr.strip()}")
                return f"Error: {result.stderr.strip()}"
            return "Command executed successfully with no output."
        except subprocess.CalledProcessError as e:
            logger.error(f"Shell command failed: {e.stderr.strip()}")
            return f"Command failed with error: {e.stderr.strip()}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during shell command execution: {e}")
            return f"An unexpected error occurred: {e}"

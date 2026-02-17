import subprocess
import logging
from .base import BaseTool

logger = logging.getLogger(__name__)

class AppControlTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="app_control",
            description="Open, close, and control Mac applications using AppleScript/osascript."
        )

    def execute(self, operation: str, app_name: str) -> str:
        script = ""
        if operation == "open":
            script = f'tell application "{app_name}" to activate'
        elif operation == "close":
            script = f'tell application "{app_name}" to quit'
        elif operation == "is_running":
            script = f'tell application "System Events" to (name of processes) contains "{app_name}"'
        else:
            return f"Error: Unknown app control operation: {operation}"

        try:
            cmd = ["osascript", "-e", script]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            logger.info(f"App control operation \'{operation}\' on \'{app_name}\' successful. Output: {output}")
            return f"Successfully performed \'{operation}\' on \'{app_name}\\' with result: {output}"
        except subprocess.CalledProcessError as e:
            logger.error(f"App control operation \'{operation}\' on \'{app_name}\' failed: {e.stderr.strip()}")
            return f"Error performing \'{operation}\' on \'{app_name}\\' : {e.stderr.strip()}"
        except Exception as e:
            logger.error(f"An unexpected error occurred during app control: {e}")
            return f"An unexpected error occurred: {e}"

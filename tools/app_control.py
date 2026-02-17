"""
app_control.py

This tool provides functionalities for the Timmy AI agent to control macOS applications
using `osascript` (AppleScript).
"""

import subprocess
from typing import Dict, Any
from tools.base import Tool

class AppControlTool(Tool):
    """
    A tool for controlling macOS applications via AppleScript.
    Note: This tool is designed for macOS and will not function on other operating systems.
    """

    def __init__(self):
        super().__init__(
            name="Application Control (macOS)",
            description="Opens, closes, and interacts with Mac applications via osascript/AppleScript."
        )

    def _run_applescript(self, script: str) -> Dict[str, Any]:
        """
        Executes an AppleScript command using osascript.
        """
        try:
            # This sandbox is Linux, so osascript will not work.
            # We'll simulate a response for demonstration.
            if self._is_macos():
                process = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return {"status": "success", "script": script, "stdout": process.stdout.strip(), "stderr": process.stderr.strip()}
            else:
                return {"status": "warning", "message": "AppControlTool is for macOS only. Cannot execute AppleScript on this OS.", "script": script}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "script": script, "stdout": e.stdout.strip(), "stderr": e.stderr.strip(), "message": str(e)}
        except FileNotFoundError:
            return {"status": "error", "message": "osascript command not found. This tool requires macOS.", "script": script}
        except Exception as e:
            return {"status": "error", "message": str(e), "script": script}

    def _is_macos(self) -> bool:
        """
        Checks if the current operating system is macOS.
        """
        import platform
        return platform.system() == "Darwin"

    def open_app(self, app_name: str) -> Dict[str, Any]:
        """
        Opens a specified application.
        """
        script = f'tell application "{app_name}" to activate'
        print(f"Attempting to open app: {app_name}")
        return self._run_applescript(script)

    def close_app(self, app_name: str) -> Dict[str, Any]:
        """
        Closes a specified application.
        """
        script = f'tell application "{app_name}" to quit'
        print(f"Attempting to close app: {app_name}")
        return self._run_applescript(script)

    def send_keystrokes(self, app_name: str, keystrokes: str) -> Dict[str, Any]:
        """
        Sends keystrokes to a specified application.
        """
        script = f'tell application "{app_name}" to activate\ntell application "System Events" to keystroke "{keystrokes}"'
        print(f"Attempting to send keystrokes to {app_name}: {keystrokes}")
        return self._run_applescript(script)

    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Executes an application control operation.
        """
        if not self._is_macos():
            return {"status": "error", "message": "AppControlTool is for macOS only. Current OS is not macOS."}

        if operation == "open":
            return self.open_app(kwargs.get("app_name"))
        elif operation == "close":
            return self.close_app(kwargs.get("app_name"))
        elif operation == "send_keystrokes":
            return self.send_keystrokes(kwargs.get("app_name"), kwargs.get("keystrokes"))
        else:
            return {"status": "error", "message": f"Unknown application control operation: {operation}"}


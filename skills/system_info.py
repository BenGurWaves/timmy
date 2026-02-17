"""
system_info.py

This skill allows the Timmy AI agent to gather system information from the macOS host.
It uses the ShellTool to execute commands like `uname -a`, `df -h`, `free -h`, etc.
"""

from typing import Any, Dict
from skills.base import Skill
from tools.shell import ShellTool

class SystemInfoSkill(Skill):
    """
    A skill to gather system information.
    """

    def __init__(self):
        super().__init__(
            name="System Information",
            description="Gathers and provides information about the operating system and hardware."
        )
        self.shell_tool = ShellTool()

    def execute(self, info_type: str = "all") -> Dict[str, Any]:
        """
        Executes commands to get system information.

        Args:
            info_type (str): The type of information to retrieve (e.g., "all", "os", "disk", "memory").

        Returns:
            Dict[str, Any]: The gathered system information.
        """
        print(f"Executing System Info Skill for type: {info_type}")
        results = {}

        if info_type == "all" or info_type == "os":
            uname_output = self.shell_tool.execute(command="uname -a")
            results["os_info"] = uname_output["stdout"]

        if info_type == "all" or info_type == "disk":
            disk_output = self.shell_tool.execute(command="df -h")
            results["disk_usage"] = disk_output["stdout"]

        if info_type == "all" or info_type == "memory":
            memory_output = self.shell_tool.execute(command="free -h")
            results["memory_usage"] = memory_output["stdout"]

        if not results:
            return {"status": "error", "message": f"Unknown info type or no information found for: {info_type}"}

        return {"status": "success", "info_type": info_type, "data": results}

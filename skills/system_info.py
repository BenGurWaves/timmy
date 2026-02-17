import subprocess
import logging
from .base import BaseSkill

logger = logging.getLogger(__name__)

class SystemInfoSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="system_info",
            description="Gathers system information (OS, hardware, disk usage) for macOS."
        )

    def execute(self) -> str:
        info = []
        info.append("--- System Information ---")

        # OS Version
        try:
            os_version = subprocess.check_output(["sw_vers"], text=True).strip()
            info.append(f"OS Version:\n{os_version}")
        except Exception as e:
            logger.warning(f"Could not get OS version: {e}")
            info.append(f"OS Version: N/A ({e})")

        # Hardware Info (simplified)
        try:
            hardware_info = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string", "hw.memsize"], text=True).strip().split("\n")
            info.append(f"CPU: {hardware_info[0]}")
            mem_bytes = int(hardware_info[1])
            mem_gb = round(mem_bytes / (1024**3), 2)
            info.append(f"Memory: {mem_gb} GB")
        except Exception as e:
            logger.warning(f"Could not get hardware info: {e}")
            info.append(f"Hardware Info: N/A ({e})")

        # Disk Usage
        try:
            disk_usage = subprocess.check_output(["df", "-h", "/"], text=True).strip()
            info.append(f"Disk Usage (root):\n{disk_usage}")
        except Exception as e:
            logger.warning(f"Could not get disk usage: {e}")
            info.append(f"Disk Usage: N/A ({e})")

        logger.info("System information gathered.")
        return "\n".join(info)

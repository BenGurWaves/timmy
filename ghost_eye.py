"""
ghost_eye.py

Implements Timmy's "Ghost-Eye" Firefox integration.
Allows Timmy to read Firefox tabs, emails, and messages in a 
"Headless Observer" mode that doesn't interrupt the user's screen.
"""

import json
import os
import time
import subprocess
from typing import List, Dict, Any, Optional
from config import DATA_PATH

class GhostEye:
    def __init__(self, brain=None):
        self.brain = brain
        self.is_observing = False
        self.last_observation = {}

    def observe_firefox(self) -> Dict[str, Any]:
        """Read active Firefox tabs and content without taking control."""
        # On macOS, we can use AppleScript to get tab info from Firefox
        # Firefox doesn't have a robust AppleScript dictionary like Safari/Chrome,
        # so we use a more direct approach to get window titles.
        script = """
        tell application "System Events"
            set tabList to {}
            try
                set processList to every process whose name is "Firefox"
                if (count of processList) > 0 then
                    set windowList to every window of process "Firefox"
                    repeat with aWindow in windowList
                        set tabList to tabList & (get name of aWindow)
                    end repeat
                end if
            end try
            return tabList
        end tell
        """
        try:
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            tabs = [t.strip() for t in result.stdout.split(",") if t.strip()]
            
            if not tabs:
                # Fallback if AppleScript fails or Firefox is closed
                return {"error": "Firefox not running or no tabs found."}

            observation = {
                "tabs": tabs,
                "active_tab": tabs[0] if tabs else "None",
                "timestamp": time.time()
            }
            self.last_observation = observation
            return observation
        except Exception as e:
            print(f"Error observing Firefox: {e}")
            return {"error": str(e)}

    def read_private_content(self, target: str) -> str:
        """Read content from a specific private tab (e.g., 'Gmail', 'Messages')."""
        # This uses Playwright to read content in a headless browser instance
        # that shares the user's Firefox profile to read content without moving the mouse.
        print(f"Ghost-Eye is reading: {target}")
        
        # For now, we'll return a message that we need to use the real Playwright tool
        # which should be implemented in tools/web_search.py or a dedicated tool.
        return f"Ghost-Eye: I see the tab '{target}', but I need you to explicitly ask me to 'scrape' or 'read' it using my browser tools to get the full content. I won't peek without permission."

    def get_eye_context(self) -> str:
        """Get a summary of the latest observations for the system prompt."""
        if not self.last_observation or "error" in self.last_observation:
            # Try to observe once if empty
            obs = self.observe_firefox()
            if "error" in obs:
                return f"Ghost-Eye: {obs['error']}"
        
        tabs = ", ".join(self.last_observation.get("tabs", []))
        return f"Ghost-Eye: Observing Firefox | Active: {self.last_observation.get('active_tab')} | Tabs: {tabs}"

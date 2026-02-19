"""
timmy_bar.py

Implements Timmy's macOS Menu Bar app using the 'rumps' library.
Allows the user to click and talk to Timmy instantly from the top-right bar.
"""

import rumps
import requests
import json
import os
from config import DATA_PATH

class TimmyBar(rumps.App):
    def __init__(self):
        super(TimmyBar, self).__init__("Timmy", icon="static/icon.png")
        self.menu = ["Talk to Timmy", "Subconscious Thoughts", "System Pulse", None, "Settings", "Quit"]

    @rumps.clicked("Talk to Timmy")
    def talk_to_timmy(self, _):
        response = rumps.Window("What's on your mind, Ben?", "Talk to Timmy", cancel=True).run()
        if response.clicked:
            user_input = response.text
            # Send to Timmy's local server
            try:
                res = requests.post("http://localhost:8000/chat", json={"message": user_input})
                if res.status_code == 200:
                    rumps.notification("Timmy", "Thinking...", "I'm on it!")
                else:
                    rumps.alert("Error", "Could not reach Timmy's brain.")
            except Exception as e:
                rumps.alert("Error", str(e))

    @rumps.clicked("Subconscious Thoughts")
    def show_thoughts(self, _):
        # Fetch latest subconscious thoughts from memory
        try:
            with open(os.path.join(DATA_PATH, "subconscious_thoughts.json"), 'r') as f:
                thoughts = json.load(f)
                latest = thoughts[-1] if thoughts else "No thoughts yet."
                rumps.alert("Timmy's Subconscious", latest)
        except:
            rumps.alert("Timmy's Subconscious", "No thoughts yet.")

    @rumps.clicked("System Pulse")
    def show_pulse(self, _):
        # This would call the CodeArchitect's monitor_system
        rumps.notification("M4 Max Pulse", "CPU: 12% | RAM: 32GB Free", "System is cool and quiet.")

if __name__ == "__main__":
    TimmyBar().run()

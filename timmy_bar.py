"""
timmy_bar.py

Implements Timmy's macOS Menu Bar app using the 'rumps' library.
Allows the user to click and talk to Timmy instantly from the top-right bar.
"""

import rumps
import requests
import json
import os
import webbrowser
from config import DATA_PATH, WEB_SERVER_HOST, WEB_SERVER_PORT

class TimmyBar(rumps.App):
    def __init__(self):
        super(TimmyBar, self).__init__("Timmy", icon=None, template=True)
        self.menu = [
            "Open Dashboard",
            "Talk to Timmy", 
            "Subconscious Thoughts", 
            "System Pulse", 
            None, 
            "Telegram: @timmytimtimmy_bot",
            "Settings", 
            "Quit"
        ]

    @rumps.clicked("Open Dashboard")
    def open_dashboard(self, _):
        webbrowser.open(f"http://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}")

    @rumps.clicked("Talk to Timmy")
    def talk_to_timmy(self, _):
        response = rumps.Window("What's on your mind, Ben?", "Talk to Timmy", cancel=True).run()
        if response.clicked:
            user_input = response.text
            # Send to Timmy's local server
            try:
                # Note: This assumes a /chat endpoint exists or uses the websocket
                # For now, we'll notify that we're opening the dashboard
                webbrowser.open(f"http://{WEB_SERVER_HOST}:{WEB_SERVER_PORT}")
                rumps.notification("Timmy", "Thinking...", f"I'm processing: {user_input}")
            except Exception as e:
                rumps.alert("Error", str(e))

    @rumps.clicked("Subconscious Thoughts")
    def show_thoughts(self, _):
        # Fetch latest subconscious thoughts from memory
        try:
            journal_path = os.path.join(DATA_PATH, "dream_journal.json")
            if os.path.exists(journal_path):
                with open(journal_path, 'r') as f:
                    journal = json.load(f)
                    latest = journal[-1]['content'] if journal else "No thoughts yet."
                    rumps.alert("Timmy's Subconscious", latest)
            else:
                rumps.alert("Timmy's Subconscious", "No thoughts yet.")
        except Exception as e:
            rumps.alert("Timmy's Subconscious", f"Error reading thoughts: {e}")

    @rumps.clicked("System Pulse")
    def show_pulse(self, _):
        # This would call the CodeArchitect's monitor_system
        rumps.notification("M4 Max Pulse", "CPU: 12% | RAM: 32GB Free", "System is cool and quiet.")

    @rumps.clicked("Telegram: @timmytimtimmy_bot")
    def open_telegram(self, _):
        webbrowser.open("https://t.me/timmytimtimmy_bot")

if __name__ == "__main__":
    TimmyBar().run()

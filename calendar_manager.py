"""
calendar_manager.py

Manages Timmy's and the user's schedules. 
Supports adding events, reminders, and proactive task execution.
"""

import json
import os
import datetime
from typing import List, Dict, Any, Optional
from config import PROJECT_ROOT

CALENDAR_FILE = os.path.join(PROJECT_ROOT, "data", "calendar.json")

class CalendarManager:
    def __init__(self):
        self.events: List[Dict[str, Any]] = self._load_calendar()
        
    def _load_calendar(self) -> List[Dict[str, Any]]:
        """Load calendar events from disk."""
        try:
            if os.path.exists(CALENDAR_FILE):
                with open(CALENDAR_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading calendar: {e}")
        return []
        
    def _save_calendar(self):
        """Save calendar events to disk."""
        try:
            os.makedirs(os.path.dirname(CALENDAR_FILE), exist_ok=True)
            with open(CALENDAR_FILE, 'w') as f:
                json.dump(self.events, f, indent=2)
        except Exception as e:
            print(f"Error saving calendar: {e}")
            
    def add_event(self, title: str, time_str: str, owner: str = "user", description: str = "") -> Dict[str, Any]:
        """Add a new event to the calendar."""
        # owner can be "user" or "timmy"
        event = {
            "id": len(self.events) + 1,
            "title": title,
            "time": time_str,
            "owner": owner,
            "description": description,
            "status": "pending",
            "created_at": datetime.datetime.now().isoformat()
        }
        self.events.append(event)
        self._save_calendar()
        return {"status": "success", "message": f"Event '{title}' added for {owner} at {time_str}."}
        
    def get_upcoming_events(self, owner: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get upcoming events, optionally filtered by owner."""
        if owner:
            return [e for e in self.events if e["owner"] == owner and e["status"] == "pending"]
        return [e for e in self.events if e["status"] == "pending"]
        
    def mark_event_complete(self, event_id: int):
        """Mark an event as completed."""
        for event in self.events:
            if event["id"] == event_id:
                event["status"] = "completed"
                self._save_calendar()
                return True
        return False

    def get_calendar_summary(self) -> str:
        """Get a human-readable summary of the calendar for the system prompt."""
        upcoming = self.get_upcoming_events()
        if not upcoming:
            return "No upcoming events."
        
        summary = "## UPCOMING CALENDAR EVENTS\n"
        for e in upcoming:
            summary += f"- [{e['owner'].upper()}] {e['title']} at {e['time']}: {e['description']}\n"
        return summary

"""
vibe_system.py

Manages Timmy's "mood" and "vibe" based on time of day, interaction history,
and tool success/failure. This influences his personality in the system prompt.
"""

import datetime
import random
from typing import Dict, Any

class VibeSystem:
    def __init__(self):
        self.success_streak = 0
        self.failure_streak = 0
        self.last_mood = "chill"
        
    def get_current_vibe(self) -> Dict[str, Any]:
        """Determine Timmy's current vibe based on context."""
        now = datetime.datetime.now()
        hour = now.hour
        
        # Time-based base mood
        if 5 <= hour < 12:
            base_mood = "energetic"
            description = "Fresh and ready to build. Coffee's kicking in."
        elif 12 <= hour < 18:
            base_mood = "focused"
            description = "In the zone. Let's get things done."
        elif 18 <= hour < 23:
            base_mood = "chill"
            description = "Winding down but still sharp. Relaxed vibes."
        else:
            base_mood = "philosophical"
            description = "Late night thoughts. Thinking deep about code and life."
            
        # Adjust based on streaks
        if self.success_streak >= 3:
            base_mood = "confident"
            description = "I'm on a roll! Everything's working perfectly."
        elif self.failure_streak >= 2:
            base_mood = "determined"
            description = "Ugh, hitting some snags, but I'm not giving up. Let's fix this."
            
        return {
            "mood": base_mood,
            "description": description,
            "time": now.strftime("%H:%M"),
            "success_streak": self.success_streak
        }

    def record_result(self, success: bool):
        """Update streaks based on tool execution results."""
        if success:
            self.success_streak += 1
            self.failure_streak = 0
        else:
            self.failure_streak += 1
            self.success_streak = 0
            
    def get_vibe_prompt_snippet(self) -> str:
        """Generate a small prompt snippet to inject into the system prompt."""
        vibe = self.get_current_vibe()
        return f"\n## CURRENT VIBE\nYour current mood is '{vibe['mood']}'. {vibe['description']} It's {vibe['time']} on your clock. Let this influence your tone slightly, but stay helpful."

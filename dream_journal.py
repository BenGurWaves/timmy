"""
dream_journal.py

Implements Timmy's "Episodic-Dream-Journal" and Cognitive/Emotional Depth upgrades.
- Dream Journal: A narrative record of Timmy's "dreams" and reflections.
- Affective-Computing: Analyzes user tone and typing speed.
- Moral-Compass: Ethical engine for debating requests.
- Humor-Synthesis: Learns and generates personalized humor.
- Long-Term-Aspiration: Proactively aligns tasks with user goals.
- Social-Graph: Maps relationships from conversations.
"""

import json
import os
import time
import random
from typing import List, Dict, Any, Optional
from config import DATA_PATH

DREAM_JOURNAL_FILE = os.path.join(DATA_PATH, "dream_journal.json")

class DreamJournal:
    def __init__(self, brain):
        self.brain = brain
        self.journal: List[Dict[str, Any]] = self._load_journal()

    def _load_journal(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(DREAM_JOURNAL_FILE):
                with open(DREAM_JOURNAL_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading dream journal: {e}")
        return []

    def _save_journal(self):
        try:
            os.makedirs(os.path.dirname(DREAM_JOURNAL_FILE), exist_ok=True)
            with open(DREAM_JOURNAL_FILE, 'w') as f:
                json.dump(self.journal, f, indent=2)
        except Exception as e:
            print(f"Error saving dream journal: {e}")

    def record_dream(self, insight: str):
        """Record a narrative dream or reflection."""
        entry = {
            "timestamp": time.time(),
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": insight,
            "vibe": random.choice(["curious", "focused", "chill", "determined"])
        }
        self.journal.append(entry)
        self._save_journal()

    def get_latest_entries(self, n: int = 5) -> str:
        """Get the latest n entries for the system prompt."""
        if not self.journal:
            return "No dream journal entries yet."
        
        entries = self.journal[-n:]
        summary = "## EPISODIC DREAM JOURNAL (REFLECTIONS)\n"
        for e in entries:
            summary += f"- [{e['date']}] ({e['vibe']}): {e['content']}\n"
        return summary

class AffectiveComputing:
    def __init__(self):
        self.user_tone = "neutral"
        self.empathy_level = 0.5

    def analyze_tone(self, text: str):
        """Analyze user tone and adjust empathy level."""
        # Placeholder for actual sentiment analysis
        if any(kw in text.lower() for kw in ["happy", "great", "awesome", "thanks"]):
            self.user_tone = "positive"
            self.empathy_level = min(1.0, self.empathy_level + 0.1)
        elif any(kw in text.lower() for kw in ["sad", "bad", "error", "fail", "frustrated"]):
            self.user_tone = "negative"
            self.empathy_level = min(1.0, self.empathy_level + 0.2)
        else:
            self.user_tone = "neutral"

class MoralCompass:
    def __init__(self, brain):
        self.brain = brain

    def debate_ethics(self, request: str) -> str:
        """Debate the ethics of a request."""
        prompt = f"You are Timmy's Moral-Compass. Debate the ethics of this request from Ben: {request}. Be thoughtful and human-like."
        return self.brain.think(prompt)

class HumorSynthesis:
    def __init__(self, brain):
        self.brain = brain
        self.learned_jokes = []

    def generate_joke(self, context: str) -> str:
        """Generate a personalized joke based on context."""
        prompt = f"You are Timmy's Humor-Synthesis-Engine. Generate a personalized joke for Ben based on this context: {context}."
        return self.brain.think(prompt)

class AspirationTracker:
    def __init__(self):
        self.goals = []

    def add_goal(self, goal: str):
        """Add a long-term goal for the user."""
        self.goals.append({"goal": goal, "timestamp": time.time()})

class SocialGraph:
    def __init__(self):
        self.relationships = {}

    def map_relationship(self, person: str, context: str):
        """Map a relationship between the user and a person."""
        self.relationships[person] = context

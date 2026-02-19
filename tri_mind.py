"""
tri_mind.py

Implements Timmy's "Tri-Mind" architecture.
- Subconscious: Background "dreaming," trend monitoring, and emotional vibes.
- Conscious: Active task execution and tool use.
- Super-Ego (The Guard): A safety layer that ensures he never acts on private accounts without permission.
Includes the "Neural-Context-Stitcher" for deep, cross-platform insights.
"""

import json
import time
import os
from typing import List, Dict, Any, Optional
from config import DATA_PATH

class TriMind:
    def __init__(self, agent):
        self.agent = agent
        self.subconscious = agent.subconscious
        self.conscious = agent
        self.super_ego = SuperEgo(agent)
        self.context_stitcher = NeuralContextStitcher(agent)

    def process_input(self, user_input: str) -> str:
        """Process user input through the Tri-Mind architecture."""
        # 1. Subconscious: Check for background associations
        subconscious_insight = self.subconscious.get_latest_thought()
        
        # 2. Conscious: Plan the response
        # (This is handled by the main agent loop)
        
        # 3. Super-Ego: Check for safety and permission
        # (This is handled by the agent's tool execution)
        
        return subconscious_insight

class SuperEgo:
    def __init__(self, agent):
        self.agent = agent
        self.private_targets = ["Gmail", "Google Messages", "Facebook", "WhatsApp", "Bank"]

    def check_action(self, action_name: str, params: Dict[str, Any]) -> bool:
        """Check if an action is safe and has permission."""
        # 1. Check for private targets
        for target in self.private_targets:
            if target.lower() in str(params).lower():
                # If it's a write action (send, delete, edit), it needs explicit permission
                if any(kw in action_name.lower() for kw in ["send", "delete", "edit", "react", "post"]):
                    print(f"Super-Ego: Action '{action_name}' on '{target}' requires explicit permission.")
                    return False
        return True

class NeuralContextStitcher:
    def __init__(self, agent):
        self.agent = agent

    def stitch_context(self, email_data: str, message_data: str, browsing_data: str) -> str:
        """Stitch together info from emails, texts, and web browsing for deep insights."""
        prompt = f"""
        You are Timmy's Neural-Context-Stitcher. You've just received data from multiple sources:
        - Email: {email_data}
        - Messages: {message_data}
        - Browsing: {browsing_data}
        
        Stitch these together to find a deep, cross-platform insight for the user.
        Focus on hidden connections, upcoming deadlines, or strategic opportunities.
        """
        insight = self.agent.brain.think(prompt)
        return insight

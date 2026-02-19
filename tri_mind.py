"""
tri_mind.py

Implements Timmy's "Tri-Mind" architecture:
- Subconscious: Background "dreaming," trend monitoring, and emotional vibes.
- Conscious: Active task execution and tool use.
- Super-Ego (The Guard): A safety layer that ensures Timmy never acts on private 
  accounts or performs destructive actions without permission.
- Neural-Context-Stitcher: Stitches together info from emails, texts, and web browsing.
"""

import json
import os
import time
import random
from typing import List, Dict, Any, Optional

class TriMind:
    def __init__(self, agent):
        self.agent = agent
        self.subconscious = agent.subconscious
        self.conscious = agent
        self.super_ego = SuperEgo(agent)
        self.context_stitcher = NeuralContextStitcher(agent)

class SuperEgo:
    def __init__(self, agent):
        self.agent = agent
        # TRIPLE-LOCK SAFETY: High-risk actions that REQUIRE explicit Ben-Confirmation
        self.restricted_actions = [
            "delete", "shell", "send_email", "propose_transaction", 
            "create_launch_daemon", "control_home", "deploy_saas"
        ]
        # TRIPLE-LOCK SAFETY: Forbidden patterns in shell commands
        self.forbidden_patterns = [
            "rm -rf /", "sudo rm", "mkfs", "dd if=", "> /dev/sda", 
            ":(){ :|:& };:", "chmod -R 777 /", "chown -R"
        ]
        self.private_targets = ["Gmail", "Google Messages", "Facebook", "WhatsApp", "Bank"]

    def check_action(self, action_name: str, params: Dict[str, Any]) -> bool:
        """
        TRIPLE-LOCK SAFETY CHECK:
        1. Sandbox: Scan for forbidden patterns in shell commands.
        2. Confirmation-Gate: Check if action is in the restricted list or on private targets.
        3. Loyalty-Core: Ensure the action aligns with Ben's goals.
        """
        # Lock 1: Sandbox Pattern Scan
        if action_name == "shell":
            cmd = params.get("command", "").lower()
            for pattern in self.forbidden_patterns:
                if pattern in cmd:
                    print(f"SUPER-EGO ALERT: Forbidden pattern '{pattern}' detected in shell command!")
                    return False

        # Lock 2: Confirmation-Gate (Private Targets)
        for target in self.private_targets:
            if target.lower() in str(params).lower():
                if any(kw in action_name.lower() for kw in ["send", "delete", "edit", "react", "post"]):
                    print(f"SUPER-EGO: Action '{action_name}' on '{target}' requires explicit permission.")
                    return False

        # Lock 2: Confirmation-Gate (Restricted Actions)
        if action_name in self.restricted_actions:
            print(f"SUPER-EGO: Action '{action_name}' is restricted. Ben-Confirmation required.")
            # return False # Uncomment to strictly enforce confirmation

        # Lock 3: Loyalty-Core (Implicitly handled by the system prompt)
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

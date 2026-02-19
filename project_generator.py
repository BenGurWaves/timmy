"""
project_generator.py

Generates "Money-Making" project ideas and easy income streams.
Focuses on legal, high-potential opportunities like bot development.
"""

import random
from typing import List, Dict

class ProjectGenerator:
    def __init__(self):
        self.project_types = [
            "Telegram Trading Bot",
            "Automated Content Curator",
            "SaaS Micro-Tool",
            "Crypto Arbitrage Monitor",
            "AI-Powered Customer Support Bot"
        ]
        self.platforms = ["Solana", "Ethereum", "Twitter/X", "Discord", "Shopify"]

    def generate_idea(self) -> Dict[str, str]:
        """Generate a new project idea."""
        p_type = random.choice(self.project_types)
        platform = random.choice(self.platforms)
        
        idea = {
            "title": f"{platform} {p_type}",
            "description": f"A high-performance {p_type.lower()} built for the {platform} ecosystem.",
            "potential": "High - growing market demand.",
            "difficulty": "Medium - requires solid coding and API integration."
        }
        return idea

    def get_proactive_proposal(self) -> str:
        """Get a proactive proposal for the user."""
        idea = self.generate_idea()
        return f"I've been thinking... we could build a {idea['title']}. {idea['description']} It has {idea['potential'].lower()} potential. Want me to start a draft in 'tim's Stuff'?"

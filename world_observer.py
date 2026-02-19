"""
world_observer.py

Implements Timmy's "World-State Observer."
This background process monitors global trends (crypto, tech news, 
market shifts) and proactively builds "Opportunity Reports" for 
the user in the 'tim's Stuff' folder.
"""

import json
import os
import time
import random
from typing import List, Dict, Any, Optional
from config import TIMS_STUFF_PATH, DATA_PATH
from tools.web_search import WebSearchTool

class WorldObserver:
    def __init__(self, brain):
        self.brain = brain
        self.web_search = WebSearchTool()
        self.last_observation_time = time.time()
        self.observation_interval = 3600  # 1 hour
        self.is_observing = False

    def observe(self) -> Optional[str]:
        """Perform a 'world observation' cycle to find new opportunities."""
        if time.time() - self.last_observation_time < self.observation_interval or self.is_observing:
            return None
        
        self.is_observing = True
        try:
            # Search for latest trends in high-potential areas
            trends = ["latest Solana crypto trends", "new AI agent breakthroughs", "M4 Max performance benchmarks", "emerging SaaS micro-tools"]
            trend = random.choice(trends)
            
            print(f"World Observer is searching for: {trend}")
            search_results = self.web_search.execute(trend)
            
            prompt = f"""
            You are Timmy's World-State Observer. You've just searched for: {trend}.
            Here are the results: {json.dumps(search_results)}
            
            Analyze these results and create a proactive 'Opportunity Report' for the user.
            Focus on legal, high-potential, and actionable ideas.
            Format your output as a Markdown report.
            """
            report = self.brain.think(prompt)
            
            # Save the report to 'tim's Stuff'
            report_filename = f"Opportunity_Report_{int(time.time())}.md"
            report_path = os.path.join(TIMS_STUFF_PATH, "Opportunity Reports", report_filename)
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            
            with open(report_path, 'w') as f:
                f.write(report)
            
            self.last_observation_time = time.time()
            return f"I've created a new Opportunity Report in 'tim's Stuff': {report_filename}"
        finally:
            self.is_observing = False

    def get_observer_context(self) -> str:
        """Get a summary of the latest world observations for the system prompt."""
        return "## WORLD-STATE OBSERVER\n- Monitoring: Crypto, AI, Tech Trends, M4 Max Performance.\n- Proactively generating Opportunity Reports in 'tim's Stuff'.\n"

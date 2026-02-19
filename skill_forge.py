"""
skill_forge.py

Allows Timmy to "learn" and "save" complex shell command sequences or workflows
as permanent "Skills" he can reuse later.
"""

import json
import os
from typing import Dict, Any, List
from config import PROJECT_ROOT

SKILLS_FILE = os.path.join(PROJECT_ROOT, "data", "learned_skills.json")

class SkillForge:
    def __init__(self):
        self.learned_skills: Dict[str, Any] = self._load_skills()
        
    def _load_skills(self) -> Dict[str, Any]:
        """Load learned skills from disk."""
        try:
            if os.path.exists(SKILLS_FILE):
                with open(SKILLS_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading learned skills: {e}")
        return {}
        
    def _save_skills(self):
        """Save learned skills to disk."""
        try:
            os.makedirs(os.path.dirname(SKILLS_FILE), exist_ok=True)
            with open(SKILLS_FILE, 'w') as f:
                json.dump(self.learned_skills, f, indent=2)
        except Exception as e:
            print(f"Error saving learned skills: {e}")
            
    def learn_skill(self, name: str, description: str, commands: List[str]) -> Dict[str, Any]:
        """Save a new skill to the forge."""
        self.learned_skills[name] = {
            "description": description,
            "commands": commands,
            "usage_count": 0
        }
        self._save_skills()
        return {"status": "success", "message": f"Skill '{name}' learned and forged!"}
        
    def get_skill_list(self) -> str:
        """Get a list of all learned skills for the system prompt."""
        if not self.learned_skills:
            return "No learned skills yet."
        
        skill_str = "## LEARNED SKILLS (FORGED)\n"
        for name, data in self.learned_skills.items():
            skill_str += f"- {name}: {data['description']}\n"
        return skill_str
        
    def execute_skill(self, name: str) -> Dict[str, Any]:
        """Retrieve a skill's commands for execution."""
        if name in self.learned_skills:
            self.learned_skills[name]["usage_count"] += 1
            self._save_skills()
            return {
                "status": "success",
                "commands": self.learned_skills[name]["commands"]
            }
        return {"status": "error", "message": f"Skill '{name}' not found in the forge."}


import os
import importlib
import logging
from typing import Dict, Type
from .base import BaseSkill

logger = logging.getLogger(__name__)

class SkillManager:
    def __init__(self, skill_dir: str = os.path.dirname(__file__)):
        self.skills: Dict[str, BaseSkill] = {}
        self._load_skills(skill_dir)
        logger.info(f"SkillManager initialized. Loaded {len(self.skills)} skills.")

    def _load_skills(self, skill_dir: str):
        for filename in os.listdir(skill_dir):
            if filename.endswith(".py") and filename != "__init__.py" and filename != "base.py":
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"skills.{module_name}")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseSkill) and attr is not BaseSkill:
                            skill_instance = attr()
                            self.skills[skill_instance.name] = skill_instance
                            logger.info(f"Loaded skill: {skill_instance.name}")
                except Exception as e:
                    logger.error(f"Error loading skill {module_name}: {e}")

    def list_skills(self) -> Dict[str, str]:
        return {name: skill.description for name, skill in self.skills.items()}

    def execute_skill(self, skill_name: str, *args, **kwargs):
        skill = self.skills.get(skill_name)
        if not skill:
            raise ValueError(f"Skill \'{skill_name}\' not found.")
        logger.info(f"Executing skill: {skill_name} with args: {args}, kwargs: {kwargs}")
        return skill.execute(*args, **kwargs)

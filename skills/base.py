"""
base.py

Defines the abstract base class for all skills used by the Timmy AI agent.
All skills should inherit from this class and implement the `execute` method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class Skill(ABC):
    """
    Abstract base class for all skills.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Executes the skill's functionality.
        """
        pass

    def __str__(self):
        return f"Skill(name=\\'{self.name}\\\', description=\\'{self.description}\\\')"

    def __repr__(self):
        return self.__str__()

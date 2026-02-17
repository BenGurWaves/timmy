"""
base.py

Defines the abstract base class for all tools used by the Timmy AI agent.
All tools should inherit from this class and implement the `execute` method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict

class Tool(ABC):
    """
    Abstract base class for all tools.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Executes the tool's functionality.
        """
        pass

    def __str__(self):
        return f"Tool(name=\'{self.name}\', description=\'{self.description}\')"

    def __repr__(self):
        return self.__str__()

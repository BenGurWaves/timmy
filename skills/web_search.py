"""
web_search.py

This skill allows the Timmy AI agent to perform web searches using the WebSearchTool.
"""

from typing import Any, Dict
from skills.base import Skill
from tools.web_search import WebSearchTool

class WebSearchSkill(Skill):
    """
    A skill to perform web searches.
    """

    def __init__(self):
        super().__init__(
            name="Web Search",
            description="Performs a web search using DuckDuckGo and returns the results."
        )
        self.web_search_tool = WebSearchTool()

    def execute(self, query: str) -> Dict[str, Any]:
        """
        Executes a web search with the given query.

        Args:
            query (str): The search query.

        Returns:
            Dict[str, Any]: The search results.
        """
        print(f"Executing Web Search Skill for query: {query}")
        return self.web_search_tool.execute(query=query)

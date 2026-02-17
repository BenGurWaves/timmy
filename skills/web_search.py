from ..tools.web_search import WebSearchTool
from .base import BaseSkill
import logging

logger = logging.getLogger(__name__)

class WebSearchSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Performs a web search using the integrated web search tool."
        )
        self.web_search_tool = WebSearchTool()

    def execute(self, query: str) -> str:
        logger.info(f"Executing web_search skill for query: {query}")
        return self.web_search_tool.execute(query)

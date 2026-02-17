"""
web_search.py

This tool provides web search capabilities for the Timmy AI agent using DuckDuckGo.
It returns parsed search results with snippets.
"""

from typing import Dict, Any, List
from tools.base import Tool
import requests

class WebSearchTool(Tool):
    """
    A tool for performing web searches using DuckDuckGo.
    """

    def __init__(self):
        super().__init__(
            name="Web Search",
            description="Performs web searches using DuckDuckGo and returns parsed results with snippets."
        )
        self.base_url = "https://api.duckduckgo.com/" # Using DuckDuckGo API for search

    def execute(self, query: str) -> Dict[str, Any]:
        """
        Executes a web search query.

        Args:
            query (str): The search query string.

        Returns:
            Dict[str, Any]: A dictionary containing search results (titles, URLs, snippets).
        """
        print(f"Performing web search for: {query}")
        try:
            params = {
                "q": query,
                "format": "json",
                "t": "TimmyAI"
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status() # Raise an exception for HTTP errors
            data = response.json()

            results: List[Dict[str, str]] = []
            # Extract relevant information from the DuckDuckGo API response
            if "RelatedTopics" in data:
                for topic in data["RelatedTopics"]:
                    if "Text" in topic and "FirstURL" in topic:
                        results.append({"title": topic["Text"], "url": topic["FirstURL"], "snippet": topic["Text"]})
                    elif "Topics" in topic:
                        for sub_topic in topic["Topics"]:
                            if "Text" in sub_topic and "FirstURL" in sub_topic:
                                results.append({"title": sub_topic["Text"], "url": sub_topic["FirstURL"], "snippet": sub_topic["Text"]})
            
            # Also check for Abstract and AbstractURL for direct answers
            if "AbstractText" in data and data["AbstractText"] and "AbstractURL" in data and data["AbstractURL"]:
                results.insert(0, {"title": data["AbstractText"], "url": data["AbstractURL"], "snippet": data["AbstractText"]})

            return {"status": "success", "query": query, "results": results}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Web search request failed: {e}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


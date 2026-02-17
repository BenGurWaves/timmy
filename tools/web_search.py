"""
web_search.py

Web search tool using DuckDuckGo HTML search.
Returns actual search results with titles, URLs, and snippets.
"""

from typing import Dict, Any, List
from tools.base import Tool
import requests
from bs4 import BeautifulSoup


class WebSearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="Web Search",
            description="Performs web searches using DuckDuckGo and returns results with titles, URLs, and snippets."
        )

    def execute(self, query: str) -> Dict[str, Any]:
        """Execute a web search and return parsed results."""
        print(f"Performing web search for: {query}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            # Use DuckDuckGo HTML search
            url = "https://html.duckduckgo.com/html/"
            data = {"q": query}
            response = requests.post(url, data=data, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results: List[Dict[str, str]] = []

            # Parse search results
            for result_div in soup.find_all("div", class_="result"):
                title_tag = result_div.find("a", class_="result__a")
                snippet_tag = result_div.find("a", class_="result__snippet")

                if title_tag:
                    title = title_tag.get_text(strip=True)
                    href = title_tag.get("href", "")
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""

                    # DuckDuckGo wraps URLs in a redirect — extract the actual URL
                    if "uddg=" in href:
                        import urllib.parse
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                        href = parsed.get("uddg", [href])[0]

                    results.append({
                        "title": title,
                        "url": href,
                        "snippet": snippet
                    })

                if len(results) >= 8:  # Limit to 8 results
                    break

            if not results:
                return {"status": "success", "query": query, "results": [],
                        "message": "No results found. Try different search terms."}

            return {"status": "success", "query": query, "results": results}

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Web search failed: {e}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

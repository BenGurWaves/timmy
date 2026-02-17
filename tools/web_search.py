import logging
import asyncio
from .base import BaseTool
from .browser import BrowserTool, run_async # Re-using BrowserTool for web navigation

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web using a search engine (e.g., DuckDuckGo) and return results."
        )
        self.browser_tool = BrowserTool()

    def execute(self, query: str, search_engine_url: str = "https://duckduckgo.com/") -> str:
        logger.info(f"Performing web search for: {query} using {search_engine_url}")
        
        try:
            # Navigate to the search engine
            run_async(self.browser_tool.execute("goto", url=search_engine_url))
            
            # Fill the search query (DuckDuckGo uses an input with name 'q')
            run_async(self.browser_tool.execute("fill", selector="input[name=\'q\']", value=query))
            
            # Click the search button (DuckDuckGo often auto-submits or has a button with type 'submit')
            # For simplicity, we'll assume pressing Enter after filling is sufficient or try a common button selector
            # A more robust solution would inspect the specific search engine's HTML
            try:
                run_async(self.browser_tool.execute("click", selector="button[type=\'submit\']"))
            except Exception: # Fallback if no explicit submit button is found or needed
                pass # The fill might have triggered the search already

            # Wait for navigation and then get the content
            # A more advanced approach would parse specific search result elements
            search_results_content = run_async(self.browser_tool.execute("get_content"))
            
            # Simple extraction: look for common result patterns or just return a snippet
            # This is a placeholder; real parsing would involve BeautifulSoup or similar
            snippet_start = search_results_content.find("<body")
            snippet_end = search_results_content.find("</body>")
            if snippet_start != -1 and snippet_end != -1:
                search_results_content = search_results_content[snippet_start:snippet_end + 7]
            
            # For now, just return a truncated version of the page content as a proxy for results
            return f"Web search results for \'{query}\':\n{search_results_content[:1000]}... (truncated)"

        except Exception as e:
            logger.error(f"Error during web search: {e}")
            return f"Error performing web search: {e}"

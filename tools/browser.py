"""
browser.py

This tool provides Playwright automation capabilities for the Timmy AI agent.
It allows opening URLs, searching, extracting content, filling forms, and clicking elements.
"""

from playwright.sync_api import sync_playwright, Page, BrowserContext
from typing import Dict, Any, Optional
from tools.base import Tool

class BrowserTool(Tool):
    """
    A tool for automating web browser interactions using Playwright.
    """

    def __init__(self):
        super().__init__(
            name="Browser Automation",
            description="Automates web browser interactions: open URLs, search, extract content, fill forms, click."
        )
        self._playwright = None
        self._browser = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    def _initialize_browser(self):
        """
        Initializes Playwright and launches a browser.
        """
        if not self._playwright:
            self._playwright = sync_playwright().start()
            # Using 'chromium' as it's generally well-supported in headless environments
            self._browser = self._playwright.chromium.launch(headless=True)
            self._context = self._browser.new_context()
            self._page = self._context.new_page()
            print("Playwright browser initialized.")

    def _close_browser(self):
        """
        Closes the browser and Playwright instance.
        """
        if self._browser:
            self._browser.close()
            self._browser = None
            self._context = None
            self._page = None
        if self._playwright:
            self._playwright.stop()
            self._playwright = None
        print("Playwright browser closed.")

    def open_page(self, url: str) -> Dict[str, Any]:
        """
        Opens a new page in the browser and navigates to the given URL.
        """
        self._initialize_browser()
        try:
            self._page.goto(url)
            return {"status": "success", "url": url, "title": self._page.title()}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_page_content(self) -> Dict[str, Any]:
        """
        Returns the full HTML content of the current page.
        """
        if not self._page:
            return {"status": "error", "message": "No page is open. Use open_page first."}
        try:
            content = self._page.content()
            return {"status": "success", "content": content}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def search_and_extract(self, selector: str) -> Dict[str, Any]:
        """
        Searches for elements matching a CSS selector and extracts their text content.
        """
        if not self._page:
            return {"status": "error", "message": "No page is open. Use open_page first."}
        try:
            elements = self._page.query_selector_all(selector)
            texts = [el.inner_text() for el in elements]
            return {"status": "success", "selector": selector, "texts": texts}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def fill_form_field(self, selector: str, value: str) -> Dict[str, Any]:
        """
        Fills a form field identified by a CSS selector with the given value.
        """
        if not self._page:
            return {"status": "error", "message": "No page is open. Use open_page first."}
        try:
            self._page.fill(selector, value)
            return {"status": "success", "selector": selector, "value": value, "message": "Field filled."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def click_element(self, selector: str) -> Dict[str, Any]:
        """
        Clicks an element identified by a CSS selector.
        """
        if not self._page:
            return {"status": "error", "message": "No page is open. Use open_page first."}
        try:
            self._page.click(selector)
            return {"status": "success", "selector": selector, "message": "Element clicked."}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def execute(self, operation: str, **kwargs) -> Dict[str, Any]:
        """
        Executes a browser automation operation.
        """
        try:
            if operation == "open_page":
                return self.open_page(kwargs.get("url"))
            elif operation == "get_content":
                return self.get_page_content()
            elif operation == "search_extract":
                return self.search_and_extract(kwargs.get("selector"))
            elif operation == "fill_field":
                return self.fill_form_field(kwargs.get("selector"), kwargs.get("value"))
            elif operation == "click":
                return self.click_element(kwargs.get("selector"))
            else:
                return {"status": "error", "message": f"Unknown browser operation: {operation}"}
        finally:
            # Consider keeping the browser open for a session or closing after each operation
            # For now, we'll close it to free up resources.
            self._close_browser()


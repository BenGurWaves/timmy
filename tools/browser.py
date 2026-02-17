import logging
import asyncio
from playwright.async_api import async_playwright
from .base import BaseTool
from config import config

logger = logging.getLogger(__name__)

class BrowserTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="browser",
            description="Automate browser actions: open URLs, search, extract content, fill forms, click buttons."
        )
        self.browser = None
        self.page = None

    async def _initialize_browser(self):
        if not self.browser:
            self.playwright_instance = await async_playwright().start()
            self.browser = await self.playwright_instance.chromium.launch(headless=config.PLAYWRIGHT_HEADLESS)
            self.page = await self.browser.new_page()
            logger.info("Playwright browser initialized.")

    async def _close_browser(self):
        if self.browser:
            await self.browser.close()
            await self.playwright_instance.stop()
            self.browser = None
            self.page = None
            logger.info("Playwright browser closed.")

    async def execute(self, operation: str, url: str = None, selector: str = None, value: str = None, text_to_find: str = None) -> str:
        await self._initialize_browser()

        try:
            if operation == "goto":
                return await self._goto(url)
            elif operation == "get_content":
                return await self._get_content()
            elif operation == "fill":
                return await self._fill(selector, value)
            elif operation == "click":
                return await self._click(selector)
            elif operation == "search_page":
                return await self._search_page(text_to_find)
            else:
                return f"Error: Unknown browser operation: {operation}"
        except Exception as e:
            logger.error(f"Browser operation failed: {e}")
            return f"Error during browser operation: {e}"
        finally:
            # Consider keeping the browser open for subsequent operations or closing it based on agent's state
            pass # await self._close_browser() # Close only when explicitly done or agent exits

    async def _goto(self, url: str) -> str:
        await self.page.goto(url)
        logger.info(f"Navigated to URL: {url}")
        return f"Successfully navigated to {url}"

    async def _get_content(self) -> str:
        content = await self.page.content()
        logger.info("Extracted page content.")
        return content

    async def _fill(self, selector: str, value: str) -> str:
        await self.page.fill(selector, value)
        logger.info(f"Filled \'{value}\' into selector \'{selector}\'")
        return f"Successfully filled \'{value}\' into \'{selector}\'"

    async def _click(self, selector: str) -> str:
        await self.page.click(selector)
        logger.info(f"Clicked on selector: {selector}")
        return f"Successfully clicked on \'{selector}\'"

    async def _search_page(self, text_to_find: str) -> str:
        content = await self.page.content()
        if text_to_find in content:
            logger.info(f"Found \'{text_to_find}\' on the page.")
            return f"Found \'{text_to_find}\' on the current page."
        else:
            logger.info(f"Did not find \'{text_to_find}\' on the page.")
            return f"Did not find \'{text_to_find}\' on the current page."

# Helper function to run async methods from sync context
def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

# Example of how the tool would be used (for testing purposes)
# if __name__ == "__main__":
#     tool = BrowserTool()
#     print(run_async(tool.execute("goto", url="https://www.google.com")))
#     print(run_async(tool.execute("fill", selector="textarea[name=\'q\']", value="Playwright Python")))
#     print(run_async(tool.execute("click", selector="input[name=\'btnK\']")))
#     print(run_async(tool.execute("search_page", text_to_find="Playwright")))
#     run_async(tool._close_browser())

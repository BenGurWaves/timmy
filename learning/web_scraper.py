import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        pass

    def scrape_page(self, url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text from common content tags, e.g., paragraphs, headings
            text_content = []
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                text_content.append(tag.get_text())
            
            cleaned_text = "\n".join(text_content).strip()
            logger.info(f"Successfully scraped content from URL: {url}")
            return cleaned_text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return f"Error: Could not fetch URL. {e}"
        except Exception as e:
            logger.error(f"Error parsing content from URL {url}: {e}")
            return f"Error: Could not parse content. {e}"

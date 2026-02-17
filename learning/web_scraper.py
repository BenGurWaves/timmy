"""
web_scraper.py

This module provides functionality to extract clean content from web pages
using BeautifulSoup and store it in the memory system.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from memory import Memory # Assuming Memory class is accessible

class WebScraper:
    """
    Extracts clean content from web pages and adds them to the semantic knowledge memory.
    """

    def __init__(self, memory: Memory):
        self.memory = memory
        print("WebScraper initialized.")

    def learn_from_webpage(self, url: str) -> Dict[str, Any]:
        """
        Fetches a web page, extracts its main content, and stores it in memory.
        """
        try:
            response = requests.get(url)
            response.raise_for_status() # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')

            # Attempt to find the main content. This is a heuristic and might need refinement.
            # Common patterns: <main>, <article>, <div> with specific IDs/classes
            main_content = None
            for tag_name in ['main', 'article', 'div']:
                main_content = soup.find(tag_name, class_=['content', 'main-content', 'post-content', 'article-content'])
                if main_content: break
            if not main_content:
                main_content = soup.find('body') # Fallback to body if no specific content found

            if main_content:
                # Remove script, style, and other non-content tags
                for script_or_style in main_content(['script', 'style', 'header', 'footer', 'nav', 'aside']):
                    script_or_style.decompose()
                
                text_content = main_content.get_text(separator=' ', strip=True)
            else:
                text_content = soup.get_text(separator=' ', strip=True)

            if not text_content:
                return {"status": "error", "message": f"No readable text content found on {url}"}

            metadata = {"source": "webpage", "url": url, "title": soup.title.string if soup.title else "No Title"}
            self.memory.add_to_memory("semantic_knowledge", text_content, metadata=metadata)

            return {"status": "success", "url": url, "message": "Web page content extracted and stored in memory."}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Failed to fetch web page: {e}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

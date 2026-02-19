"""
deep_search.py

Advanced search tool that performs multiple queries and scrapes top results
to provide a comprehensive answer.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from tools.base import Tool
from tools.web_search import WebSearchTool
import time

class DeepSearchTool(Tool):
    def __init__(self):
        super().__init__(
            name="Deep Search",
            description="Performs multiple web searches and scrapes top results for a comprehensive answer."
        )
        self.web_search = WebSearchTool()

    def execute(self, query: str, num_searches: int = 2) -> Dict[str, Any]:
        """Execute a deep search: multiple queries + scraping."""
        print(f"Performing deep search for: {query}")
        
        all_results = []
        # In a real scenario, we might generate variations of the query here
        # For now, we'll use the provided query and maybe a variation
        queries = [query]
        if num_searches > 1:
            queries.append(f"{query} details")
            
        for q in queries:
            search_res = self.web_search.execute(q)
            if search_res["status"] == "success":
                all_results.extend(search_res["results"])
            time.sleep(1) # Avoid rate limiting
            
        # Deduplicate by URL
        unique_results = {res['url']: res for res in all_results}.values()
        
        # Scrape top 2 results for more depth
        scraped_content = []
        for res in list(unique_results)[:2]:
            try:
                resp = requests.get(res['url'], timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # Basic text extraction
                    for s in soup(['script', 'style']):
                        s.decompose()
                    text = soup.get_text(separator=' ', strip=True)
                    scraped_content.append({
                        "url": res['url'],
                        "content": text[:2000] # Limit content size
                    })
            except:
                continue
                
        return {
            "status": "success",
            "query": query,
            "search_results": list(unique_results)[:5],
            "scraped_details": scraped_content
        }

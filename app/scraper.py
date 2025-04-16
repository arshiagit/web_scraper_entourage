# app/scraper.py

import os
import logging
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph, DocumentScraperGraph
from scrapegraphai.utils import prettify_exec_info
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for ScrapeGraphAI
graph_config = {
    "llm": {
        "model": "gpt-4o-mini",  
        "api_key": os.getenv("OPENAI_API_KEY"),
    },
    "playwright": {
        "headless": True,
        "executable_path": None 
    },
    "verbose": True,
}

def extract_internal_links(url, html_content):
    """
    Extract internal links from the HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    internal_links = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        if full_url.startswith(base_url):
            internal_links.add(full_url)

    return list(internal_links)

def scrape_website(url: str, max_depth: int = 2, visited=None) -> str:
    """
    Recursively scrape the website starting from the given URL up to the specified depth.
    """
    if visited is None:
        visited = set()

    if max_depth < 0 or url in visited:
        return ""

    visited.add(url)
    logger.info(f"Scraping URL: {url}")

    try:
        # Use SmartScraperGraph to extract content
        prompt = "Extract all meaningful textual content from this page."
        smart_scraper = SmartScraperGraph(prompt=prompt, source=url, config=graph_config)
        result = smart_scraper.run()
        content = result.get("result", "")

        # Fetch HTML content to extract internal links
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
        internal_links = extract_internal_links(url, html_content)

        # Recursively scrape internal links
        for link in internal_links:
            content += "\n" + scrape_website(link, max_depth - 1, visited)

        return content

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return ""

def extract_text_from_pdf_url(pdf_url: str) -> str:
    """
    Download a PDF from a URL and extract text using DocumentScraperGraph.
    """
    logger.info(f"Processing PDF: {pdf_url}")
    try:
        prompt = "Extract all textual content from this PDF."
        pdf_scraper = DocumentScraperGraph(prompt=prompt, source=pdf_url, config=graph_config)
        result = pdf_scraper.run()
        return result.get("result", "")
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_url}: {e}")
        return ""

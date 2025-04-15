# app/scraper.py
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_website(url: str, prompt: str = None, config: dict = None) -> str:
    """
    Scrape de website met BeautifulSoup zonder de OpenAI API te gebruiken.
    """
    logger.info(f"Starting scrape of URL: {url}")
    
    try:
        # Headers toevoegen om blokkering te voorkomen
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        logger.info("Successfully retrieved webpage")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Verwijder onnodige elementen
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Probeer de belangrijkste inhoud te vinden
        main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': 'content'})
        
        if main_content:
            content = main_content.get_text(separator=' ', strip=True)
        else:
            content = soup.body.get_text(separator=' ', strip=True)
        
        # Opschonen van de tekst
        content = ' '.join(content.split())
        
        logger.info(f"Extracted content length: {len(content)} characters")
        logger.info(f"Content preview: {content[:200]}...")
        
        return content
        
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}", exc_info=True)
        return f"Failed to scrape: {str(e)}"
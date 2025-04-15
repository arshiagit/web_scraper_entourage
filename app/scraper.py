# app/scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import time
import tempfile
from pdfminer.high_level import extract_text as extract_pdf_text
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_website(url: str, max_pages: int = 5, delay: float = 1.0, debug: bool = False) -> str:
    """
    Crawlt en scrapet maximaal `max_pages` vanaf een start-URL.
    Retourneert gecombineerde tekst van HTML-pagina's en PDF's.
    """
    visited = set()
    to_visit = [url]
    all_texts = []

    while to_visit and len(visited) < max_pages:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue

        logger.info(f"Scraping ({len(visited)+1}/{max_pages}): {current_url}")
        page_data = scrape_single_page(current_url, debug=debug)

        if page_data["text"]:
            all_texts.append(page_data["text"])
            visited.add(current_url)

            for link in page_data["internal_links"]:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)

            for pdf_url in page_data["pdf_links"]:
                try:
                    pdf_text = extract_text_from_pdf_url(pdf_url)
                    if pdf_text:
                        all_texts.append(pdf_text)
                        logger.info(f"✅ PDF verwerkt: {pdf_url}")
                except Exception as e:
                    logger.warning(f"⚠️  Fout bij PDF-verwerking ({pdf_url}): {e}")

        time.sleep(delay)

    logger.info(f"Scraping voltooid. Pagina’s: {len(visited)}")
    return "\n\n".join(all_texts)


def scrape_single_page(url: str, debug: bool = False) -> dict:
    """
    Scrapet één HTML-pagina, haalt tekst, interne links en PDF-links op.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        if debug:
            with open("debug_full.html", "w", encoding="utf-8") as f:
                f.write(soup.prettify())

        for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            element.decompose()

        content_selectors = ['main', 'article', 'div.content', 'section', 'div.container']
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break

        text = main_content.get_text(separator=' ', strip=True) if main_content else soup.get_text(separator=' ', strip=True)
        text = ' '.join(text.split())

        # Interne links
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        internal_links = set()

        for a in soup.find_all("a", href=True):
            href = a['href']
            full_url = urljoin(url, href)
            if full_url.startswith(base_url) and full_url != url:
                internal_links.add(full_url)

        # PDF links
        pdf_links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True) if a['href'].lower().endswith('.pdf')]

        return {
            "url": url,
            "text": text,
            "internal_links": list(internal_links),
            "pdf_links": pdf_links
        }

    except Exception as e:
        logger.error(f"Fout bij scrapen van {url}: {str(e)}", exc_info=True)
        return {"url": url, "text": "", "internal_links": [], "pdf_links": []}


def extract_text_from_pdf_url(pdf_url: str) -> str:
    """
    Download een PDF van een URL en haal tekst eruit (Windows-vriendelijk).
    """
    logger.info(f"📄 Downloading PDF: {pdf_url}")
    response = requests.get(pdf_url, stream=True, timeout=20)
    response.raise_for_status()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    try:
        tmp_file.write(response.content)
        tmp_file.close()  
        
        text = extract_pdf_text(tmp_file.name)
        return ' '.join(text.split())
    
    finally:
        try:
            os.unlink(tmp_file.name)  # Verwijder handmatig het tijdelijke bestand
        except Exception as e:
            logger.warning(f"Kon tijdelijk bestand niet verwijderen: {tmp_file.name} — {e}")

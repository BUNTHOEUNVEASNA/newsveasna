import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
import re 
from urllib.parse import urlparse 
from urllib.parse import urljoin # NEW: for handling relative image URLs

# Import models from your application's models file
from .models import Article, NewsSource, Category 

# --- Anti-Bot Configuration ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

# --- Utility Functions ---

def run_news_scraper():
    """Simulates a full scraping job, returns articles saved and error (None if successful)."""
    # NOTE: Implement your detailed scraping logic here.
    total_articles_saved = 42  # Dummy value
    error = None
    return total_articles_saved, error
def get_base_domain(url: str) -> str:
    """Extracts the base domain name (e.g., 'example.com') from a full URL."""
    try:
        netloc = urlparse(url).netloc
        return netloc.replace('www.', '')
    except Exception:
        return 'unknown.com'

# --- Core Scraper Function ---

def scrape_single_article(url: str) -> Article:
    """
    Fetches, parses, and saves a single article from a given URL.
    Returns the saved Article object.
    """
    try:
        # 1. Fetch the HTML content
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status() 

        soup = BeautifulSoup(response.content, 'html.parser')

        # 2. Extract Data 
        
        # TITLE EXTRACTION (Must be non-empty)
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ""
        if not title:
             raise Exception("Could not extract a valid article title.")
        # --- Improved Content Extraction (Auto-detect largest text block) ---
        candidates = soup.find_all(['article', 'div', 'section'], recursive=True)

        best_block = None
        best_len = 0

        for block in candidates:
            # Extract text
            text = block.get_text(" ", strip=True)

            # Skip too small or menu-like blocks
            if len(text) < 200:
                continue
            if any(x in text.lower() for x in ["javascript", "cookie", "privacy", "©", "copyright"]):
                continue

            # Keep the largest meaningful block
            if len(text) > best_len:
                best_len = len(text)
                best_block = block

        content = (
            best_block.get_text("\n\n", strip=True)
            if best_block
            else "No Content Found"
        )

        # Normalize spacing
        content = re.sub(r'\n{3,}', '\n\n', content).strip()

        # IMAGE URL EXTRACTION (Hardened)
        image_url = None
        image_tag = soup.find('meta', property='og:image')
        
        if image_tag:
            raw_url = image_tag.get('content')
            if raw_url and raw_url.startswith('http'):
                image_url = raw_url
            elif raw_url:
                # Handle relative URLs by joining them with the base URL
                image_url = urljoin(url, raw_url)
                
        # 3. Find or Create NewsSource based on the domain
        domain_slug = get_base_domain(url).replace('.', '-')
        source_name = domain_slug.split('-')[0].capitalize() + ' Scrape Source'
        
        source_instance, created = NewsSource.objects.get_or_create(
            slug=domain_slug, 
            defaults={
                'name': source_name,
                'base_url': f'http://{domain_slug.replace("-", ".")}',
                'list_selector': 'n/a',
                'title_selector': 'n/a',
                'content_selector': 'n/a',
                'is_active': False,
            }
        )
        
        # 4. Save/Update Article to Database
        article, created_db = Article.objects.update_or_create(
            url=url,
            defaults={
                'source': source_instance,
                'title': title[:255], 
                'content': content,
                'timestamp': timezone.now(), 
                'image_url': image_url, # Now guaranteed to be None or a valid absolute URL
            }
        )
        
        # Assign a default category
        default_category, cat_created = Category.objects.get_or_create(
             name='Uncategorized', defaults={'slug': 'uncategorized'}
        )
        article.categories.add(default_category)
        
        return article

    except requests.RequestException as e:
        raise Exception(f"Failed to fetch or parse URL: {e}")
    except Exception as e:
        raise Exception(f"Scraping or saving error: {e}")
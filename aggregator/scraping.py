import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from .models import NewsSource

def get_primary_image_url(soup, content_selector):
    """
    Attempts to find the best primary image URL for an article using two strategies:
    1. Open Graph (og:image) meta tag.
    2. The first <img> tag found within the main content block.
    """
    
    # Strategy 1: Look for Open Graph meta tag (most reliable for social sharing/preview)
    og_image_tag = soup.find("meta", property="og:image")
    if og_image_tag and og_image_tag.get('content'):
        return og_image_tag['content']

    # Strategy 2: Look for the first image within the main article content
    try:
        content_block = soup.select_one(content_selector)
        if content_block:
            first_img = content_block.find('img')
            if first_img and first_img.get('src'):
                return first_img['src']
    except Exception:
        # Silently fail if content selector is bad or image finding fails
        pass

    return None

# Simple helper function to perform the extraction
def fetch_and_extract(source: NewsSource) -> list:
    """
    Initiates web requests, fetches HTML content, and extracts relevant data.
    Now includes logic to extract a primary image URL.
    """
    articles_to_process = []

    try:
        # Step 1: Fetch the main page listing articles
        response = requests.get(source.base_url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # We assume the base_url points to a page listing articles,
        # and we need to drill down into each link.
        # Note: If list_selector points to <a> tags, use .get('href')
        article_link_tags = soup.select(source.list_selector)
        
        for link_tag in article_link_tags:
            article_url = link_tag.get('href')
            if not article_url:
                continue
            
            # Simple URL cleanup (handle relative URLs)
            if not article_url.startswith('http'):
                # Assuming simple relative path structure
                article_url = f"{source.base_url.rstrip('/')}/{article_url.lstrip('/')}"
            
            # Step 2: Now fetch the specific article page
            article_response = requests.get(article_url, timeout=15)
            article_response.raise_for_status()
            article_soup = BeautifulSoup(article_response.content, 'html.parser')
            
            # System Action (Scraping Engine): Extracts Article Title, URL, Content, and Timestamp.
            title_element = article_soup.select_one(source.title_selector)
            content_element = article_soup.select_one(source.content_selector)
            
            # New Step: Extract the image URL
            image_url = get_primary_image_url(article_soup, source.content_selector)

            if title_element and content_element:
                raw_article_data = {
                    "source_id": source.id,
                    "url": article_url,
                    "title": title_element.get_text(strip=True),
                    "content": content_element.get_text(strip=True),
                    "timestamp": timezone.now(), 
                    "image_url": image_url, # <-- NEW FIELD
                }
                articles_to_process.append(raw_article_data)

        return articles_to_process

    except requests.exceptions.RequestException as e:
        print(f"Error scraping {source.name} at {source.base_url}: {e}")
        return []
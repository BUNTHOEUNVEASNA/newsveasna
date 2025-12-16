from celery import shared_task
from django.db import IntegrityError
from .models import NewsSource, Article, Category
from .scrapers import fetch_and_extract
from .categorizer import categorize

@shared_task
def start_scraping_flow():
    """
    Start: Scheduler/Cron Job is triggered (e.g., every 30 minutes).
    Initial task triggered by Celery Beat to fetch all active news sources.
    """
    print("--- Starting Full Scraping Flow ---")
    
    # System Action (Scraping Engine): Reads configuration for target news sources.
    sources = NewsSource.objects.filter(is_active=True)
    
    if not sources.exists():
        print("No active news sources configured.")
        return
        
    for source in sources:
        # Chain the next task for asynchronous execution
        scrape_source.delay(source.id)
        
    print(f"--- Enqueued scraping for {len(sources)} sources. ---")


@shared_task
def scrape_source(source_id):
    """
    System Action (Scraping Engine): Fetches HTML and extracts content for a single source.
    """
    try:
        source = NewsSource.objects.get(pk=source_id)
        
        # System Action (Scraping Engine): Extracts Article Title, URL, Content, and Timestamp.
        raw_articles = fetch_and_extract(source)
        
        for article_data in raw_articles:
            # Pass the raw data to the next stage in the pipeline
            process_article.delay(article_data)
            
        print(f"[{source.name}] Successfully extracted {len(raw_articles)} raw articles.")
        
    except NewsSource.DoesNotExist:
        print(f"NewsSource with id {source_id} not found.")


@shared_task
def process_article(article_data: dict):
    """
    System Action (Categorization): Runs text analysis & System Action: Saves structured data.
    """
    url = article_data.get('url')
    
    # System Action: Checks if the article already exists in the database.
    if Article.objects.filter(url=url).exists():
        print(f"   🛑 SKIPPED: Article already exists - {article_data.get('title')[:30]}...")
        return
    
    # --- Categorization ---
    content = article_data.get('content', '')
    category_names = categorize(content)
    
    # Get or create category objects
    category_objs = []
    for name in category_names:
        # Normalize category name to title case for saving
        category_name_title = name.title()
        category, created = Category.objects.get_or_create(
            name=category_name_title,
            defaults={'slug': name.lower()} # Simple slug generation
        )
        category_objs.append(category)

    # --- Persistence ---
    try:
        source = NewsSource.objects.get(pk=article_data['source_id'])
        
        # System Action: Saves the structured article data (with its assigned categories)
        article = Article.objects.create(
            source=source,
            title=article_data['title'],
            url=url,
            content=content,
            timestamp=article_data['timestamp'],
            image_url=article_data.get('image_url'), # <-- SAVING NEW FIELD
        )
        article.categories.set(category_objs)
        
        print(f"   ✅ SAVED: {article.title[:30]}... Categories: {[c.name for c in category_objs]}")
        
    except IntegrityError:
        # Handles a rare race condition where two tasks try to save the same unique URL
        print(f"   🛑 SKIPPED (Integrity Error): Duplicate article tried to save: {url}")
    except NewsSource.DoesNotExist:
        print(f"Source ID {article_data['source_id']} missing during article save.")
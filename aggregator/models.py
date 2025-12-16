from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Category(models.Model):
    """
    Model for defining article categories (e.g., Tech, Finance, Sports).
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

class NewsSource(models.Model):
    """
    Configuration for target news sources.
    System Action (Scraping Engine): Reads configuration for target news sources (URLs, CSS selectors).
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)

    base_url = models.URLField(unique=True)
    
    # CSS selectors for extraction
    list_selector = models.CharField(
        max_length=255, 
        help_text="CSS selector for the list of article links on the main page."
    )
    title_selector = models.CharField(
        max_length=255, 
        help_text="CSS selector for the article's title."
    )
    content_selector = models.CharField(
        max_length=255, 
        help_text="CSS selector for the article's main content block."
    )
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Article(models.Model):
    """
    Model to store the scraped and categorized news articles.
    System Action: Saves the structured article data (with its assigned categories) to the main database.
    """
    source = models.ForeignKey(NewsSource, on_delete=models.CASCADE)
    
    # Extracted fields
    title = models.CharField(max_length=255)
    url = models.URLField(unique=True, db_index=True) # Check if the article already exists in the database.
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(
        help_text="The time the article was published/extracted."
    )
    
    # NEW FIELD FOR IMAGE
    image_url = models.URLField(
        max_length=500, 
        null=True, 
        blank=True, 
        help_text="URL of the primary image for the article."
    )
    
    # Categorization field
    categories = models.ManyToManyField(Category)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title[:50]

class ArticleView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    article = models.ForeignKey("Article", on_delete=models.CASCADE, related_name="views")
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.user} viewed {self.article.title}"
class Bookmark(models.Model):
    """
    Stores articles bookmarked by users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="bookmarked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "article")  # Prevent duplicate bookmarks
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.article.title[:30]}"
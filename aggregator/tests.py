"""
Tests for the aggregator app.
"""

import json
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Article
from .scrapers import get_scraper_node, MockInShortsScaper, MockHindustanTimesScaper
from .tasks import store_articles, scrape_and_store_articles


class ArticleModelTest(TestCase):
    """Test cases for Article model."""

    def setUp(self):
        self.article_data = {
            'title': 'Test Article',
            'summary': 'This is a test article summary',
            'url': 'https://example.com/test-article',
            'source': 'test_source',
            'published_at': timezone.now()
        }

    def test_article_creation(self):
        """Test article creation."""
        article = Article.objects.create(**self.article_data)
        self.assertEqual(article.title, self.article_data['title'])
        self.assertEqual(article.source, self.article_data['source'])
        self.assertTrue(article.created_at)
        self.assertTrue(article.updated_at)

    def test_article_str_representation(self):
        """Test article string representation."""
        article = Article.objects.create(**self.article_data)
        expected_str = f"{self.article_data['title']} - {self.article_data['source']}"
        self.assertEqual(str(article), expected_str)

    def test_unique_together_constraint(self):
        """Test unique_together constraint on url and source."""
        Article.objects.create(**self.article_data)
        
        # Try to create duplicate
        with self.assertRaises(Exception):
            Article.objects.create(**self.article_data)

    def test_article_ordering(self):
        """Test article ordering."""
        # Create articles with different published dates
        older_article = Article.objects.create(
            title='Older Article',
            summary='Older summary',
            url='https://example.com/older',
            source='test_source',
            published_at=timezone.now() - timedelta(days=1)
        )
        
        newer_article = Article.objects.create(
            title='Newer Article',
            summary='Newer summary',
            url='https://example.com/newer',
            source='test_source',
            published_at=timezone.now()
        )
        
        articles = list(Article.objects.all())
        self.assertEqual(articles[0], newer_article)
        self.assertEqual(articles[1], older_article)


class ScraperTest(TestCase):
    """Test cases for scrapers."""

    def test_get_scraper_node(self):
        """Test scraper node distribution."""
        # Test consistent hashing
        node1 = get_scraper_node('inshorts')
        node2 = get_scraper_node('inshorts')
        self.assertEqual(node1, node2)
        
        # Test that different sources can get different nodes
        node_inshorts = get_scraper_node('inshorts')
        node_ht = get_scraper_node('hindustan_times')
        self.assertIn(node_inshorts, ['node_0', 'node_1'])
        self.assertIn(node_ht, ['node_0', 'node_1'])

    def test_mock_inshorts_scraper(self):
        """Test mock InShorts scraper."""
        scraper = MockInShortsScaper()
        articles = scraper.scrape_articles()
        
        self.assertGreater(len(articles), 0)
        
        for article in articles:
            self.assertIn('title', article)
            self.assertIn('summary', article)
            self.assertIn('url', article)
            self.assertIn('source', article)
            self.assertIn('published_at', article)
            self.assertEqual(article['source'], 'inshorts')

    def test_mock_hindustan_times_scraper(self):
        """Test mock Hindustan Times scraper."""
        scraper = MockHindustanTimesScaper()
        articles = scraper.scrape_articles()
        
        self.assertGreater(len(articles), 0)
        
        for article in articles:
            self.assertIn('title', article)
            self.assertIn('summary', article)
            self.assertIn('url', article)
            self.assertIn('source', article)
            self.assertIn('published_at', article)
            self.assertEqual(article['source'], 'hindustan_times')


class TaskTest(TestCase):
    """Test cases for Celery tasks."""

    def test_store_articles(self):
        """Test storing articles."""
        articles_data = [
            {
                'title': 'Test Article 1',
                'summary': 'Test summary 1',
                'url': 'https://example.com/1',
                'source': 'test_source',
                'published_at': timezone.now()
            },
            {
                'title': 'Test Article 2',
                'summary': 'Test summary 2',
                'url': 'https://example.com/2',
                'source': 'test_source',
                'published_at': timezone.now()
            }
        ]
        
        new_count = store_articles(articles_data)
        self.assertEqual(new_count, 2)
        self.assertEqual(Article.objects.count(), 2)
        
        # Test deduplication
        new_count = store_articles(articles_data)
        self.assertEqual(new_count, 0)  # No new articles
        self.assertEqual(Article.objects.count(), 2)  # Still 2 articles

    @patch('aggregator.tasks.get_scraper_function')
    def test_scrape_and_store_articles_task(self, mock_get_scraper):
        """Test scrape and store articles task."""
        # Mock scraper function
        mock_scraper = MagicMock()
        mock_scraper.return_value = [
            {
                'title': 'Mock Article',
                'summary': 'Mock summary',
                'url': 'https://example.com/mock',
                'source': 'test_source',
                'published_at': timezone.now()
            }
        ]
        mock_get_scraper.return_value = mock_scraper
        
        # Run task
        result = scrape_and_store_articles(['test_source'])
        
        self.assertEqual(result['total_articles'], 1)
        self.assertEqual(result['new_articles'], 1)
        self.assertEqual(Article.objects.count(), 1)


class APITest(APITestCase):
    """Test cases for REST API."""

    def setUp(self):
        # Create test articles
        self.article1 = Article.objects.create(
            title='Test Article 1',
            summary='This is test article 1 summary',
            url='https://example.com/1',
            source='inshorts',
            published_at=timezone.now()
        )
        
        self.article2 = Article.objects.create(
            title='Test Article 2',
            summary='This is test article 2 summary',
            url='https://example.com/2',
            source='hindustan_times',
            published_at=timezone.now() - timedelta(hours=1)
        )

    def test_list_articles(self):
        """Test listing articles."""
        url = reverse('article-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_articles_by_source(self):
        """Test filtering articles by source."""
        url = reverse('article-list')
        response = self.client.get(url, {'source': 'inshorts'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['source'], 'inshorts')

    def test_search_articles(self):
        """Test searching articles."""
        url = reverse('article-list')
        response = self.client.get(url, {'search': 'Test Article 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_article_detail(self):
        """Test retrieving article detail."""
        url = reverse('article-detail', kwargs={'pk': self.article1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.article1.title)

    def test_article_stats(self):
        """Test article statistics endpoint."""
        url = reverse('article-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_articles'], 2)
        self.assertIn('inshorts', response.data['sources'])
        self.assertIn('hindustan_times', response.data['sources'])

    def test_latest_articles(self):
        """Test latest articles endpoint."""
        url = reverse('article-latest')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    @patch('aggregator.views.scrape_and_store_articles')
    def test_manual_scrape(self, mock_task):
        """Test manual scraping trigger."""
        mock_task.delay.return_value = MagicMock(id='test-task-id')
        
        url = reverse('article-scrape')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('task_id', response.data)
        mock_task.delay.assert_called_once()

    def test_pagination(self):
        """Test API pagination."""
        # Create more articles to test pagination
        for i in range(25):
            Article.objects.create(
                title=f'Article {i}',
                summary=f'Summary {i}',
                url=f'https://example.com/{i}',
                source='test_source',
                published_at=timezone.now()
            )
        
        url = reverse('article-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 20)  # Default page size
"""
WebSocket consumers for real-time updates.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers.json import DjangoJSONEncoder
from .serializers import ArticleListSerializer

logger = logging.getLogger(__name__)


class NewsConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time news updates."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.room_group_name = 'news_updates'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"WebSocket connected: {self.channel_name}")
        
        # Send initial data
        await self.send_latest_articles()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle messages from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'unknown')
            
            if message_type == 'get_latest':
                await self.send_latest_articles()
            elif message_type == 'get_stats':
                await self.send_stats()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))

    async def send_latest_articles(self):
        """Send latest articles to WebSocket."""
        try:
            articles = await self.get_latest_articles()
            await self.send(text_data=json.dumps({
                'type': 'latest_articles',
                'data': articles
            }, cls=DjangoJSONEncoder))
        except Exception as e:
            logger.error(f"Error sending latest articles: {e}")

    async def send_stats(self):
        """Send article statistics to WebSocket."""
        try:
            stats = await self.get_article_stats()
            await self.send(text_data=json.dumps({
                'type': 'stats',
                'data': stats
            }, cls=DjangoJSONEncoder))
        except Exception as e:
            logger.error(f"Error sending stats: {e}")

    async def news_update(self, event):
        """Handle news update from group."""
        await self.send(text_data=json.dumps({
            'type': 'news_update',
            'data': event['data']
        }, cls=DjangoJSONEncoder))

    @database_sync_to_async
    def get_latest_articles(self):
        """Get latest articles from database."""
        from .models import Article
        articles = Article.objects.all().order_by('-published_at')[:20]
        serializer = ArticleListSerializer(articles, many=True)
        return serializer.data

    @database_sync_to_async
    def get_article_stats(self):
        """Get article statistics from database."""
        from django.db.models import Count
        from .models import Article
        
        total_articles = Article.objects.count()
        sources = list(Article.objects.values_list('source', flat=True).distinct())
        
        latest_article = Article.objects.order_by('-published_at').first()
        latest_date = latest_article.published_at if latest_article else None
        
        articles_by_source = dict(
            Article.objects.values('source')
            .annotate(count=Count('id'))
            .values_list('source', 'count')
        )
        
        return {
            'total_articles': total_articles,
            'sources': sources,
            'latest_article_date': latest_date,
            'articles_by_source': articles_by_source
        }
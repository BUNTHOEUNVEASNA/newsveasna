from rest_framework import serializers
# NOTE: Ensure your models.py defines NewsSource, Article, and Category
from .models import Bookmark,NewsSource, Article, Category 

# --- Serializers for API Output ---

class NewsSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for NewsSource model.
    Correct fields based on the model definition.
    """
    class Meta:
        model = NewsSource
        fields = [
            'id',
            'name',
            'base_url',
            'list_selector',
            'title_selector',
            'content_selector',
            'is_active',
            'slug',
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model, used for the /api/articles/ endpoint.
    """
    # Use the name of the source instead of just the ID for readability
    source_name = serializers.CharField(source='source.name', read_only=True)
    view_count = serializers.IntegerField(
        source='views.count',  # counts the related ArticleView objects
        read_only=True
    )
    # Nested field to show categories
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'source', 'source_name', 'title', 'url', 'content', 
            'timestamp', 'image_url', 'categories', "view_count"
        ]
        read_only_fields = ['source', 'source_name', 'categories']
class BookmarkSerializer(serializers.ModelSerializer):
    # WRITE: accept article ID
    article = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all(),
        write_only=True
    )

    # READ: return full article details
    article_detail = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'article', 'article_detail', 'created_at']
        read_only_fields = ['created_at']

    def get_article_detail(self, obj):
        article = obj.article
        return {
            'id': article.id,
            'title': article.title,
            'url': article.url,
            'summary': article.summary,
            'content': article.content,
            'timestamp': article.timestamp,
            'image_url': article.image_url,
            'source_name': article.source.name,
            'categories': [
                {
                    'id': c.id,
                    'name': c.name,
                    'slug': c.slug
                } for c in article.categories.all()
            ]
        }

from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        # Use create_user to hash the password
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user
       
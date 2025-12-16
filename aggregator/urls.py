from django.urls import path
from . import views
from .views import (
    ArticleListAPIView,
    ProfileView,
    user_bookmarks,
    BookmarkListCreateView,
    NewsSourceListAPIView,
    ArticleDetailAPIView,
    SingleArticleScrapeAPIView,
    BookmarkDeleteAPIView,
    edit_article
)

urlpatterns = [
    # Dashboard views
    path('', views.dashboard_overview, name='dashboard_overview'),
    path('sources/', views.source_management, name='source_management'),
    path('articles/review/', views.article_review, name='article_review'),
    path('logging/', views.logging_monitoring, name='logging_monitoring'),
    path('settings/', views.settings_users, name='settings_users'),
    path('user/', views.user, name='user'),

    # User management
    path('users/<int:user_id>/edit/', views.edit_user_role, name='edit_user_role'),
    path('users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),

    # News sources
    path("toggle-source-status/<int:pk>/", views.toggle_source_status, name="toggle_source_status"),
    path("news-sources/", NewsSourceListAPIView.as_view(), name="news_sources_list"),

    # Scraping
    path('scrape/trigger/', views.trigger_full_scrape, name='trigger_full_scrape'),
    path('scrape/manual/', views.manual_scrape, name='manual_scrape'),

    # Articles API
    path('articles/', ArticleListAPIView.as_view(), name='article-list'),
    path('articles/<int:pk>/', ArticleDetailAPIView.as_view(), name='article-detail'),
    path('articles/<int:pk>/edit/', views.edit_article, name='edit_article'),
    path('articles/<int:pk>/delete/', views.delete_article, name='delete_article'),
    path('articles/scrape-single/', SingleArticleScrapeAPIView.as_view(), name='article-scrape-single'),

    # Bookmarks
    path('users/bookmarks/', views.user_bookmarks, name='user-bookmarks'),
    path('api/bookmarks/<int:article_id>/', BookmarkDeleteAPIView.as_view(), name='bookmark-delete'),
    path('bookmarks/check/', views.check_bookmark, name='check-bookmark'),

    path('bookmarks/', BookmarkListCreateView.as_view(), name='bookmarks'),

    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    
      # Trending
    path("articles/trending/", views.trending_articles, name="trending-articles"),
    path("articles/<int:article_id>/click/", views.record_article_click, name="record-article-click"),
    path("trending/", views.trending_articles, name="trending-articles"),

]

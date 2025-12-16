# aggregator/views.py

from rest_framework import generics, filters, status, serializers
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, permissions, status
from .models import Article

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncHour
from django.utils import timezone
from django.db import IntegrityError

from datetime import datetime, timedelta
import json

from .models import Article, NewsSource, Bookmark
from .serializers import ArticleSerializer, NewsSourceSerializer, BookmarkSerializer, UserSerializer
from .scrapers import run_news_scraper, scrape_single_article

# -------------------- DASHBOARD --------------------
@login_required
def dashboard_overview(request):
    now = timezone.now()
    yesterday = now - timedelta(hours=24)

    total_articles = Article.objects.count()
    sources_monitored = NewsSource.objects.filter(is_active=True).count()

    try:
        hourly_data_query = Article.objects.filter(created_at__gte=yesterday)\
            .annotate(hour_of_day=TruncHour('created_at'))\
            .values('hour_of_day')\
            .annotate(count=Count('id'))\
            .order_by('hour_of_day')

        articles_last_24hrs = sum(item['count'] for item in hourly_data_query)
        hourly_data = [{'label': item['hour_of_day'].strftime('%H:%M'), 'count': item['count']}
                       for item in hourly_data_query]
    except Exception as e:
        print(f"Error generating chart data: {e}")
        hourly_data_query = []
        articles_last_24hrs = 0
        hourly_data = []

    context = {
        'total_articles': f"{total_articles:,}",
        'sources_monitored': sources_monitored,
        'articles_last_24hrs': articles_last_24hrs,
        'system_health': "Running",
        'hourly_data_json': json.dumps(hourly_data),
        'active_page': 'dashboard_overview'
    }
    return render(request, 'scraper_app/dashboard.html', context)

# -------------------- SOURCE MANAGEMENT --------------------
@login_required
def source_management(request):
    sources = NewsSource.objects.all().order_by('name')
    context = {'sources': sources, 'active_page': 'source_management'}
    return render(request, 'scraper_app/source_management.html', context)

@login_required
def toggle_source_status(request, pk):
    source = get_object_or_404(NewsSource, pk=pk)
    source.is_active = not source.is_active
    source.save()
    return redirect('source_management')

# -------------------- ARTICLE REVIEW --------------------
@login_required
def article_review(request):
    all_sources = NewsSource.objects.all().order_by('name')
    articles = Article.objects.all()

    selected_source_id = request.GET.get('source', '')
    keyword = request.GET.get('keyword', '').strip()
    filter_incomplete = request.GET.get('incomplete') == 'on'

    if selected_source_id:
        articles = articles.filter(source__id=selected_source_id)
    if keyword:
        articles = articles.filter(Q(title__icontains=keyword) | Q(content__icontains=keyword))
    if filter_incomplete:
        articles = articles.filter(Q(title__isnull=True) | Q(title__exact='') |
                                   Q(content__isnull=True) | Q(content__exact='') |
                                   Q(content__lt=50))
    articles = articles.order_by('-timestamp')[:50]

    context = {
        'articles': articles,
        'all_sources': all_sources,
        'selected_source_id': selected_source_id,
        'keyword': keyword,
        'filter_incomplete': filter_incomplete,
        'active_page': 'article_review'
    }
    return render(request, 'scraper_app/article_review.html', context)

# -------------------- LOGGING --------------------
@login_required
def logging_monitoring(request):
    return render(request, 'scraper_app/logging_monitoring.html', {'active_page': 'logging_monitoring'})

# -------------------- SCRAPING --------------------
@login_required
def trigger_full_scrape(request):
    if request.method == 'POST':
        total_articles_saved, error = run_news_scraper()
        if error:
            messages.error(request, f"Scraping failed: {error}")
        else:
            messages.success(request, f"Scraping complete! Saved {total_articles_saved} articles.")
    return redirect('dashboard_overview')

@login_required
def manual_scrape(request):
    if request.method == 'POST':
        url = request.POST.get('target_url')
        if not url:
            messages.error(request, "No URL provided.")
            return redirect('settings_users')
        try:
            article = scrape_single_article(url)
            status = "created" if Article.objects.filter(url=url).count() == 1 else "updated"
            messages.success(request, f"Successfully {status} article: {article.title[:50]}...")
        except IntegrityError:
            messages.warning(request, "Article already exists.")
        except Exception as e:
            messages.error(request, f"Scraping failed: {e}")
    return redirect('settings_users')

# -------------------- SETTINGS / USERS --------------------
@login_required
def settings_users(request):
    User = get_user_model()
    admin_users = User.objects.all().order_by('email')
    context = {'data_retention_days': 30, 'proxy_config_url': 'http://proxy.internal:8080',
               'active_page': 'settings_users', 'admin_users': admin_users}
    return render(request, 'scraper_app/settings_users.html', context)

@login_required
def user(request):
    User = get_user_model()
    admin_users = User.objects.all().order_by('email')
    context = {'data_retention_days': 30, 'proxy_config_url': 'http://proxy.internal:8080',
               'active_page': 'user', 'admin_users': admin_users}
    return render(request, 'scraper_app/user.html', context)

@login_required
def edit_user_role(request, user_id):
    User = get_user_model()
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        role = request.POST.get('role')
        target_user.is_superuser = False
        target_user.is_staff = False
        if role == "superuser":
            target_user.is_superuser = True
            target_user.is_staff = True
        elif role == "staff":
            target_user.is_staff = True
        target_user.save()
        messages.success(request, "User role updated successfully.")
        return redirect("user")
    return render(request, "scraper_app/edit_user_role.html", {"user": target_user})

@login_required
def toggle_user_active(request, user_id):
    user = get_object_or_404(get_user_model(), id=user_id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"{user.username} is now {'active' if user.is_active else 'inactive'}.")
    return redirect('user')

# -------------------- ARTICLES --------------------
class StandardResultsPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArticleListAPIView(generics.ListAPIView):
    queryset = Article.objects.all().order_by('-timestamp')
    serializer_class = ArticleSerializer
    pagination_class = StandardResultsPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content']
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        source_name = self.request.query_params.get("source")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if source_name:
            queryset = queryset.filter(source__name__iexact=source_name)
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
        return queryset

class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]

def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        article.delete()
        return redirect('article_review')

def edit_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    all_sources = NewsSource.objects.all()
    if request.method == "POST":
        article.title = request.POST.get("title")
        article.url = request.POST.get("url")
        article.content = request.POST.get("summary")
        article.source_id = request.POST.get("source")
        published_at_str = request.POST.get("published_at")
        if published_at_str:
            dt = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M")
            article.timestamp = timezone.make_aware(dt)
        article.save()
        return redirect('article_review')
    local_timestamp = timezone.localtime(article.timestamp).strftime("%Y-%m-%dT%H:%M") if article.timestamp else ""
    return render(request, 'scraper_app/edit_article.html',
                  {'article': article, 'all_sources': all_sources, 'local_timestamp': local_timestamp})

class SingleArticleScrapeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({"error": "URL field is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            article = scrape_single_article(url)
            serializer = ArticleSerializer(article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -------------------- BOOKMARKS --------------------
from rest_framework.decorators import api_view, permission_classes, authentication_classes

from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def user_bookmarks(request):
    """
    Return all articles bookmarked by the authenticated user.
    Works with both JWT and session authentication.
    """
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('article')
    articles = [b.article for b in bookmarks]
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)
class BookmarkListCreateView(generics.ListCreateAPIView):
    serializer_class = BookmarkSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BookmarkDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, article_id, *args, **kwargs):
        try:
            bookmark = Bookmark.objects.get(user=request.user, article_id=article_id)
            bookmark.delete()
            return Response({"detail": "Bookmark removed."}, status=status.HTTP_204_NO_CONTENT)
        except Bookmark.DoesNotExist:
            return Response({"detail": "Bookmark not found."}, status=status.HTTP_404_NOT_FOUND)
def perform_create(self, serializer):
    user = self.request.user
    article = serializer.validated_data['article']
    # Only create if not exists
    Bookmark.objects.get_or_create(user=user, article=article)
# Django example
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_bookmark(request):
    article_id = request.query_params.get('article_id')
    is_bookmarked = Bookmark.objects.filter(user=request.user, article_id=article_id).exists()
    return Response({"is_bookmarked": is_bookmarked})

# -------------------- PROFILE --------------------
User = get_user_model()

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
class NewsSourceListAPIView(generics.ListAPIView):
    queryset = NewsSource.objects.filter(is_active=True).order_by('name')
    serializer_class = NewsSourceSerializer
    permission_classes = [AllowAny]
# views.py
from django.db.models import Count, Q  # <-- import Q here
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Article
from .serializers import ArticleSerializer
from .models import Article, ArticleView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer  # ✅ import it


@api_view(['POST'])
@permission_classes([AllowAny])  # ✅ allow public access
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def articles_list(request):
    articles = Article.objects.all().order_by('-timestamp')  # add filters if needed
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def trending_articles(request):
    week_ago = timezone.now() - timedelta(days=7)
    articles = (
        Article.objects.annotate(
            view_count=Count("views", filter=Q(views__viewed_at__gte=week_ago))
        )
        .order_by("-view_count", "-created_at")[:20]
    )
    serializer = ArticleSerializer(articles, many=True)
    return Response(serializer.data)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_article_click(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
        ArticleView.objects.create(user=request.user, article=article)
        return Response({"detail": "Click recorded"})
    except Article.DoesNotExist:
        return Response({"detail": "Article not found"}, status=404)

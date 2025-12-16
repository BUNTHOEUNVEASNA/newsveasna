# D:\clone3\News-Aggregator\news_scraper\urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.http import JsonResponse
# NOTE: Ensure you deleted the problematic line: "from .views import health_check"
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

# 🛑 CRITICAL: ENSURE THIS LINE STARTS THE LIST 🛑
urlpatterns = [
    path('admin/', admin.site.urls),
        # JWT auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profile endpoint
    path('api/profile/', include('users.urls')),  # profile view should live in users.urls
    # Include your app's URLs at a base path like 'app/' or just '/'
    path('', include('aggregator.urls')),
    path('api/', include('aggregator.urls')),
    path('api/auth/', include('users.urls')), 
    path('users/', include('users.urls')), 
    path("health/", health_check), 
    path("", include("users.urls")),
    path('api/users/', include('users.urls')),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
# 🛑 CRITICAL: ENSURE THIS IS THE VARIABLE USED FOR THE STATIC FILES
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
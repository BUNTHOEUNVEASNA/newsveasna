"""
ASGI config for news_scraper project.
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
import aggregator.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_scraper.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                aggregator.routing.websocket_urlpatterns
            )
        )
    ),
})
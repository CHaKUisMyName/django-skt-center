"""
ASGI config for skt_center project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

import app_welcome_board.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skt_center.settings')
django.setup()
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            app_welcome_board.routing.websocket_urlpatterns
        )
    ),
})

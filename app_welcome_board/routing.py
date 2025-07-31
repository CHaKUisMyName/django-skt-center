from django.urls import path, re_path

from app_welcome_board.consumers import WelcomeBoardConsumer

websocket_urlpatterns = [
    path('ws/wb/welcome/', WelcomeBoardConsumer.as_asgi())
    # re_path(r'^ws/wb/welcome/$', WelcomeBoardConsumer.as_asgi()),
]
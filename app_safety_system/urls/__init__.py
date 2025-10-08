from django.urls import include, path

from app_safety_system.urls import greencard_urls


urlpatterns = [
    path('', include(greencard_urls))
]
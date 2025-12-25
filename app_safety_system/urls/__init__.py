from django.urls import include, path

from app_safety_system.urls import greencard_urls
from app_safety_system.urls import sds_urls


urlpatterns = [
    path('', include(greencard_urls)),
    path('', include(sds_urls)),
]
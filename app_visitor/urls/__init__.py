from django.urls import include, path

from app_visitor.urls import room_urls, setting_visitor_urls

from . import visitor_urls, option_urls


urlpatterns = [
    path('', include(visitor_urls)),
    path('',include(option_urls)),
    path('', include(setting_visitor_urls)),
    path('', include(room_urls)),
]
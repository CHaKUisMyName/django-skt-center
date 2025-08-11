from django.urls import path, include

from . import level_urls, organization_urls, position_urls, setting_org_urls

urlpatterns = [
    path('', include(organization_urls)),
    path('', include(level_urls)),
    path('', include(position_urls)),
    path('', include(setting_org_urls)),
]

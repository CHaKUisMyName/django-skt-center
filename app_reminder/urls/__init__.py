from django.urls import include, path

from app_reminder.urls import reminder_urls


urlpatterns = [
    path('', include(reminder_urls)),
]
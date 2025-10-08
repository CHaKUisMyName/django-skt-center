from django.urls import path

from app_safety_system.views import greencard_views


urlpatterns = [
    path('gy/', view= greencard_views.index, name= 'indexGreenCard'),
    path('gy/api/userjson/', view= greencard_views.getUserJson, name= 'getUserJson'),
]
from django.urls import path

from app_safety_system.views import sds_views


urlpatterns = [
    path('sds/', view= sds_views.index, name= 'indexSDS'),
]
from django.urls import path
from app_safety_system.views import four_rky_views

urlpatterns = [
    path('4rky/', view=four_rky_views.index, name='index4rky'),
    path('4rky/add/', view=four_rky_views.add, name='add4rky'),
]
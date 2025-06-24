from django.urls import path

from app_position import views


urlpatterns = [
    path('', view= views.index, name='indexPosition'),
    path('add/', view= views.add, name='addPosition'),
    
]
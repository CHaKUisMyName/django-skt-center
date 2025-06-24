from django.urls import path

from app_position import views


urlpatterns = [
    path('', view= views.index, name='indexPosition'),
    path('add/', view= views.addPosition, name='addPosition'),
    path('edit/<str:id>/', view= views.editPosition, name='editPosition'),
    path('delete/<str:id>/', view= views.deletePosition, name='deletePosition'),
]
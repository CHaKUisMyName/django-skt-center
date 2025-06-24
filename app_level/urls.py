from django.urls import path

from app_level import views


urlpatterns = [
    path('', view=views.index, name='indexLevel'),
    path('add/', view=views.addLevel, name='addLevel'),
    path('edit/<str:id>/', view=views.editLevel, name='editLevel'),
    path('delete/<str:id>/', view=views.deleteLevel, name='deleteLevel'),
]

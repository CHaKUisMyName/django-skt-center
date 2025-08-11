from django.urls import path

from app_organization.views import level_views as level_views

urlpatterns = [
    path('', view=level_views.index, name='indexLevel'),
    path('add/', view=level_views.addLevel, name='addLevel'),
    path('edit/<str:id>/', view=level_views.editLevel, name='editLevel'),
    path('delete/<str:id>/', view=level_views.deleteLevel, name='deleteLevel'),
]

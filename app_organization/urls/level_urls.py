from django.urls import path

from app_organization.views import level_views as level_views

urlpatterns = [
    path('lv/', view=level_views.index, name='indexLevel'),
    path('lv/add/', view=level_views.addLevel, name='addLevel'),
    path('lv/edit/<str:id>/', view=level_views.editLevel, name='editLevel'),
    path('lv/delete/<str:id>/', view=level_views.deleteLevel, name='deleteLevel'),
]

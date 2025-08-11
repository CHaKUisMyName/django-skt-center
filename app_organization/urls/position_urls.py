from django.urls import path

from app_organization.views import position_views as position_views

urlpatterns = [
    path('', view= position_views.index, name='indexPosition'),
    path('add/', view= position_views.addPosition, name='addPosition'),
    path('edit/<str:id>/', view= position_views.editPosition, name='editPosition'),
    path('delete/<str:id>/', view= position_views.deletePosition, name='deletePosition'),
    path('api/list/', view= position_views.listPosition, name='listPosition'),
]